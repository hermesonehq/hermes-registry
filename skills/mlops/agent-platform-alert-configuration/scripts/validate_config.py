#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""HCL configuration and PromQL validation script for agent platform metrics.

Parses Terraform HCL alert policy resource blocks, detects duplicate targets
for reasoning engines, and lints Prometheus queries for correct syntax, time
windows, and essential label filters.
"""

import argparse
import glob
import json
import os
import re
import sys


def check_balanced_chars(query, open_char, close_char):
  """Checks if parenthesis or braces are balanced."""
  count = 0
  for i, char in enumerate(query):
    if char == open_char:
      count += 1
    elif char == close_char:
      count -= 1
      if count < 0:
        return f"Unbalanced '{close_char}' at position {i}"
  if count != 0:
    return f"Unbalanced '{open_char}' (net count: {count})"
  return None


def lint_query(query):
  """Runs a suite of sanity lint checks on a PromQL query.

  Args:
      query: The PromQL query string to lint.

  Returns:
      A list of string lint error messages. Empty if valid.
  """
  errors = []

  # 1. Balanced parentheses
  paren_err = check_balanced_chars(query, "(", ")")
  if paren_err:
    errors.append(f"Parentheses error: {paren_err}")

  # 2. Balanced curly braces
  brace_err = check_balanced_chars(query, "{", "}")
  if brace_err:
    errors.append(f"Curly braces error: {brace_err}")

  # 3. Time window validations (e.g., [5m], [1w:5m], [3d], [1h])
  window_matches = re.finditer(r"\[([^\]]+)\]", query)
  for match in window_matches:
    window_str = match.group(1)
    if not re.match(r"^\d+[smhdw](:(\d+[smhdw])?)?$", window_str):
      errors.append(
          "Invalid Prometheus time window/subquery interval:"
          f" '[{window_str}]' at position {match.start()}"
      )

  # 4. Lookback offset range validation (e.g. offset 1w, offset 1d)
  offset_matches = re.finditer(r"\boffset\s+(\S+)", query)
  for match in offset_matches:
    offset_str = match.group(1)
    if not re.match(r"^\d+[smhdw]$", offset_str):
      errors.append(
          f"Invalid lookback offset format: 'offset {offset_str}' at position"
          f" {match.start()}"
      )

  # 5. Ensure the query references reasoning_engine_id in a label filter
  # or grouping aggregation.
  has_group = bool(
      re.search(r"\b(by|without)\s*\([^)]*reasoning_engine_id[^)]*\)", query)
  )

  has_filter = False
  brace_matches = re.finditer(r"\{([^}]+)\}", query)
  for match in brace_matches:
    if "reasoning_engine_id" in match.group(1):
      has_filter = True
      break

  if not (has_group or has_filter):
    errors.append(
        "Query is missing 'reasoning_engine_id' reference. It must either"
        " group by 'reasoning_engine_id' using aggregations (e.g., 'by"
        " (reasoning_engine_id)') or filter on it (e.g.,"
        " '{reasoning_engine_id=\"...\"}')."
    )

  return errors


def extract_alert_policies(hcl_content):
  """Extracts resource 'google_monitoring_alert_policy' blocks and metadata."""
  policies = []
  pattern = re.compile(
      r'resource\s+"google_monitoring_alert_policy"\s+"([^"]+)"\s*\{'
  )

  for match in pattern.finditer(hcl_content):
    resource_name = match.group(1)
    start_pos = match.start()

    brace_count = 0
    end_pos = -1
    in_string = False
    escape = False

    for i in range(match.end() - 1, len(hcl_content)):
      char = hcl_content[i]
      if escape:
        escape = False
        continue
      if char == "\\":
        escape = True
        continue
      if char == '"':
        in_string = not in_string
        continue
      if not in_string:
        if char == "{":
          brace_count += 1
        elif char == "}":
          brace_count -= 1
          if brace_count == 0:
            end_pos = i + 1
            break

    if end_pos == -1:
      continue

    block_content = hcl_content[start_pos:end_pos]

    # Extract display_name
    display_name_match = re.search(
        r'display_name\s*=\s*"([^"]+)"', block_content
    )
    display_name = display_name_match.group(1) if display_name_match else ""

    # Extract PromQL queries
    queries = [
        q.group(1)
        for q in re.finditer(
            r"query\s*=\s*<<-?EOT\n(.*?)\n\s*EOT",
            block_content,
            re.DOTALL,
        )
    ]
    if not queries:
      for match in re.finditer(
          r"query\s*=\s*\"((?:[^\"\\]|\\[\s\S])*)\"", block_content
      ):
        raw_query = match.group(1)
        clean_query = re.sub(r"\\+\"", '"', raw_query).replace("\\\\", "\\")
        queries.append(clean_query)

    # Extract threshold filters
    filters = []
    filter_matches = re.finditer(
        r'filter\s*=\s*"((?:[^"\\]|\\.)*)"', block_content
    )
    for f_match in filter_matches:
      filters.append(f_match.group(1))

    # Infer signal type
    signal_type = "unknown"
    res_lower, disp_lower = resource_name.lower(), display_name.lower()
    rules = [
        ("latency", "latency", "latency"),
        ("slo_burn_rate_fast", "fast", "slo_fast"),
        ("slo_burn_rate_slow", "slow", "slo_slow"),
    ]
    for res_pat, disp_pat, sig in rules:
      if res_pat in res_lower or disp_pat in disp_lower:
        signal_type = sig
        break
    else:
      # Check threshold filters for quality metric name
      for flt in filters:
        metric_match = re.search(
            r"metric\.labels\.evaluation_metric_name\s*=\s*\\*\"([^\"\\]+)\\*\"",
            flt,
        )
        if metric_match:
          signal_type = metric_match.group(1)
          break

    engine_ids = []
    for query in queries:
      for engine_id in re.findall(
          r"reasoning_engine_id\s*=\s*\"([^\"]+)\"", query
      ):
        if engine_id not in engine_ids:
          engine_ids.append(engine_id)

    for flt in filters:
      id_matches = re.findall(
          r'reasoning_engine_id\s*=\s*\\*"([^"\\]+)\\*"', flt
      )
      for engine_id in id_matches:
        if engine_id not in engine_ids:
          engine_ids.append(engine_id)
      resource_matches = re.findall(r"reasoningEngines/([0-9]+)", flt)
      for engine_id in resource_matches:
        if engine_id not in engine_ids:
          engine_ids.append(engine_id)

    policies.append({
        "resource_name": resource_name,
        "display_name": display_name,
        "signal_type": signal_type,
        "engine_ids": engine_ids,
        "queries": queries,
        "filters": filters,
        "start_pos": start_pos,
        "end_pos": end_pos,
        "block_content": block_content,
    })

  return policies


def validate_directory_tf_files(directory, expected_engine_var=None):
  """Scans and validates all *.tf files in a given directory."""
  tf_files = glob.glob(os.path.join(directory, "*.tf"))
  all_errors = []
  all_policies = []
  duplicates = []

  target_map = {}

  for filepath in tf_files:
    filename = os.path.basename(filepath)
    try:
      with open(filepath, "r") as f:
        content = f.read()
    except Exception as e:
      all_errors.append(f"File error in '{filename}': {e}")
      continue

    policies = extract_alert_policies(content)
    for policy in policies:
      policy["filename"] = filename
      all_policies.append(policy)

      for query in policy["queries"]:
        lint_errs = lint_query(query)
        for err in lint_errs:
          all_errors.append(
              f"Lint error in '{filename}' -> resource"
              f" '{policy['resource_name']}': {err}"
          )

      engine_key = (
          policy["engine_ids"][0]
          if policy["engine_ids"]
          else expected_engine_var or "default"
      )
      key = (engine_key, policy["signal_type"])

      if key not in target_map:
        target_map[key] = []
      target_map[key].append(policy)

  for (engine, signal_type), matches in target_map.items():
    if len(matches) > 1 and signal_type != "unknown":
      duplicates.append({
          "engine_id": engine,
          "signal_type": signal_type,
          "policies": [
              {
                  "filename": p["filename"],
                  "resource_name": p["resource_name"],
                  "display_name": p["display_name"],
              }
              for p in matches
          ],
      })

  for dup in duplicates:
    policy_list = ", ".join(
        f"'{p['resource_name']}' in '{p['filename']}'" for p in dup["policies"]
    )
    all_errors.append(
        "Duplicate Target Error: Multiple alert policies are targeting the"
        f" same engine '{dup['engine_id']}' and signal '{dup['signal_type']}':"
        f" [{policy_list}]. Please apply the in-place upgrade protocol instead"
        " of appending new blocks!"
    )

  return {
      "valid": len(all_errors) == 0,
      "errors": all_errors,
      "policies_scanned_count": len(all_policies),
      "duplicates_found": duplicates,
  }


def main():
  parser = argparse.ArgumentParser(
      description=(
          "Lints HCL alerts and PromQL query targets in standard tf templates."
      )
  )
  parser.add_argument(
      "--directory",
      type=str,
      default=".",
      help="Directory containing *.tf files to scan.",
  )
  parser.add_argument(
      "--engine-var",
      type=str,
      default="${var.reasoning_engine_id}",
      help="The expected variable or literal for the reasoning engine ID.",
  )
  parser.add_argument(
      "--file",
      type=str,
      help="Validate a single specific HCL file instead of scanning directory.",
  )
  args = parser.parse_args()

  if args.file:
    try:
      with open(args.file, "r") as f:
        content = f.read()
      policies = extract_alert_policies(content)
      errors = []
      for p in policies:
        for q in p["queries"]:
          errors.extend(lint_query(q))
      if errors:
        print(f"Validation failed for '{args.file}':", file=sys.stderr)
        for err in errors:
          print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
      else:
        print(f"Validation passed for '{args.file}'!")
        sys.exit(0)
    except Exception as e:
      print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
      sys.exit(1)

  results = validate_directory_tf_files(args.directory, args.engine_var)
  print(json.dumps(results, indent=2))
  if not results["valid"]:
    sys.exit(1)


if __name__ == "__main__":
  main()
