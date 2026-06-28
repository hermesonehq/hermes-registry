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

"""Unit tests for HCL configuration alert policies parsing.

Also tests duplicate detection, and PromQL query syntax validation linting.
"""

import os
import tempfile
import unittest

import validate_config


class ValidateConfigTest(unittest.TestCase):

  def test_lint_query_valid(self):
    query = (
        "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m]))"
        " by (reasoning_engine_id)"
    )
    self.assertEqual(validate_config.lint_query(query), [])

  def test_lint_query_unbalanced_parentheses(self):
    query = (
        "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m]))"
        " by (reasoning_engine_id"
    )
    errors = validate_config.lint_query(query)
    self.assertTrue(any("Parentheses error" in e for e in errors))

  def test_lint_query_unbalanced_braces(self):
    query = (
        'sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2.."[5m]))'
        " by (reasoning_engine_id)"
    )
    errors = validate_config.lint_query(query)
    self.assertTrue(any("Curly braces error" in e for e in errors))

  def test_lint_query_invalid_window(self):
    for invalid_suffix in ("5x", "5y"):
      query = (
          "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count"
          f"[{invalid_suffix}])) by (reasoning_engine_id)"
      )
      errors = validate_config.lint_query(query)
      self.assertTrue(
          any("Invalid Prometheus time window" in e for e in errors)
      )

  def test_lint_query_valid_subquery_intervals(self):
    queries = [
        # With resolution
        (
            "avg_over_time((sum(rate("
            "aiplatform_googleapis_com:reasoning_engine_request_count[5m]"
            ")) by (reasoning_engine_id))[1w:5m])"
        ),
        # Without resolution
        (
            "avg_over_time((sum(rate("
            "aiplatform_googleapis_com:reasoning_engine_request_count[5m]"
            ")) by (reasoning_engine_id))[1w:])"
        ),
    ]
    for query in queries:
      self.assertEqual(validate_config.lint_query(query), [])

  def test_lint_query_invalid_subquery_intervals(self):
    queries = [
        # Invalid resolution format: number only (no unit)
        (
            "avg_over_time((sum(rate("
            "aiplatform_googleapis_com:reasoning_engine_request_count[5m]"
            ")) by (reasoning_engine_id))[1w:5])"
        ),
        # Invalid resolution format: unit only (no number)
        (
            "avg_over_time((sum(rate("
            "aiplatform_googleapis_com:reasoning_engine_request_count[5m]"
            ")) by (reasoning_engine_id))[1w:m])"
        ),
    ]
    for query in queries:
      errors = validate_config.lint_query(query)
      self.assertTrue(
          any("Invalid Prometheus time window" in e for e in errors)
      )

  def test_lint_query_missing_reference(self):
    query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m]))"
    errors = validate_config.lint_query(query)
    self.assertTrue(
        any("missing 'reasoning_engine_id' reference" in e for e in errors)
    )

  def test_lint_query_valid_with_filter(self):
    query = 'sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id="12345"}[5m]))'
    self.assertEqual(validate_config.lint_query(query), [])

  def test_lint_query_valid_with_regex_or_prefix_filter(self):
    query = (
        'sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id!~"dev-.*"}[5m]))'
        " by (reasoning_engine_id)"
    )
    self.assertEqual(validate_config.lint_query(query), [])

  def test_scanner_extract_valid_hcl(self):
    hcl_content = """
        resource "google_monitoring_alert_policy" "agent_latency_anomaly" {
          project      = var.project_id
          display_name = "[Agent Alert] Latency Anomaly - ${var.agent_name}"
          combiner     = "OR"

          conditions {
            display_name = "p95 Latency exceeds 3x Standard Deviation (1w baseline)"
            condition_prometheus_query_language {
              query    = <<-EOT
                sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m])) by (reasoning_engine_id)
              EOT
              duration = "300s"
            }
          }
        }
        """
    policies = validate_config.extract_alert_policies(hcl_content)
    self.assertEqual(len(policies), 1)
    self.assertEqual(policies[0]["resource_name"], "agent_latency_anomaly")
    self.assertEqual(policies[0]["signal_type"], "latency")

  def test_scanner_extract_escaped_inline_query(self):
    hcl_content = r"""
        resource "google_monitoring_alert_policy" "agent_latency_anomaly" {
          display_name = "[Agent Alert] Latency Anomaly - ${var.agent_name}"
          conditions {
            condition_prometheus_query_language {
              query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id=\"12345\"}[5m]))"
            }
          }
        }
        """
    policies = validate_config.extract_alert_policies(hcl_content)
    self.assertEqual(len(policies), 1)
    self.assertEqual(len(policies[0]["queries"]), 1)
    self.assertEqual(
        policies[0]["queries"][0],
        'sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id="12345"}[5m]))',
    )
    self.assertEqual(policies[0]["engine_ids"], ["12345"])

    hcl_content_three_backslash = r"""
        resource "google_monitoring_alert_policy" "agent_latency_anomaly" {
          display_name = "[Agent Alert] Latency Anomaly - ${var.agent_name}"
          conditions {
            condition_prometheus_query_language {
              query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id=\\\"12345\\\"}[5m]))"
            }
          }
        }
        """
    policies_three = validate_config.extract_alert_policies(
        hcl_content_three_backslash
    )
    self.assertEqual(len(policies_three), 1)
    self.assertEqual(len(policies_three[0]["queries"]), 1)
    self.assertEqual(
        policies_three[0]["queries"][0],
        'sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id="12345"}[5m]))',
    )
    self.assertEqual(policies_three[0]["engine_ids"], ["12345"])

  def test_validator_detects_duplicates(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      tf_content_1 = """
            resource "google_monitoring_alert_policy" "agent_latency_anomaly_1" {
              display_name = "[Agent Alert] Latency Anomaly - ${var.agent_name}"
              conditions {
                condition_prometheus_query_language {
                  query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m])) by (reasoning_engine_id)"
                }
              }
            }
            """
      tf_content_2 = """
            resource "google_monitoring_alert_policy" "agent_latency_anomaly_2" {
              display_name = "[Agent Alert] Latency Anomaly - Alternative"
              conditions {
                condition_prometheus_query_language {
                  query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m])) by (reasoning_engine_id)"
                }
              }
            }
            """
      with open(os.path.join(tmpdir, "policy1.tf"), "w") as f:
        f.write(tf_content_1)
      with open(os.path.join(tmpdir, "policy2.tf"), "w") as f:
        f.write(tf_content_2)

      results = validate_config.validate_directory_tf_files(
          tmpdir, "${var.reasoning_engine_id}"
      )
      self.assertFalse(results["valid"])
      self.assertEqual(len(results["duplicates_found"]), 1)
      self.assertEqual(results["duplicates_found"][0]["signal_type"], "latency")

  def test_scanner_extracts_quality_metric_signal_type(self):
    hcl_content = """
        resource "google_monitoring_alert_policy" "agent_final_response_quality" {
          project      = var.project_id
          display_name = "Agent Final Response Quality (Median < 0.8)"
          combiner     = "OR"
          enabled      = true

          conditions {
            display_name = "Final Response Quality Score"
            condition_threshold {
              filter          = "resource.type=\\"aiplatform.googleapis.com/OnlineEvaluator\\" AND metric.type=\\"aiplatform.googleapis.com/online_evaluator/scores\\" AND metric.labels.evaluation_metric_name=\\"final_response_quality_v1\\""
              comparison      = "COMPARISON_LT"
              threshold_value = 0.8
              duration        = "300s"
              aggregations {
                alignment_period   = "300s"
                per_series_aligner = "ALIGN_PERCENTILE_50"
              }
              trigger {
                count = 1
              }
            }
          }
        }
        """
    policies = validate_config.extract_alert_policies(hcl_content)
    self.assertEqual(len(policies), 1)
    self.assertEqual(
        policies[0]["resource_name"], "agent_final_response_quality"
    )
    self.assertEqual(policies[0]["signal_type"], "final_response_quality_v1")

  def test_validator_detects_quality_duplicates(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      tf_content_1 = """
            resource "google_monitoring_alert_policy" "q1" {
              display_name = "Quality Alert 1"
              conditions {
                condition_threshold {
                  filter = "resource.type=\\"aiplatform.googleapis.com/OnlineEvaluator\\" AND metric.type=\\"aiplatform.googleapis.com/online_evaluator/scores\\" AND metric.labels.evaluation_metric_name=\\"tool_use_quality_v1\\""
                }
              }
            }
            """
      tf_content_2 = """
            resource "google_monitoring_alert_policy" "q2" {
              display_name = "Quality Alert 2"
              conditions {
                condition_threshold {
                  filter = "resource.type=\\"aiplatform.googleapis.com/OnlineEvaluator\\" AND metric.type=\\"aiplatform.googleapis.com/online_evaluator/scores\\" AND metric.labels.evaluation_metric_name=\\"tool_use_quality_v1\\""
                }
              }
            }
            """
      with open(os.path.join(tmpdir, "policy1.tf"), "w") as f:
        f.write(tf_content_1)
      with open(os.path.join(tmpdir, "policy2.tf"), "w") as f:
        f.write(tf_content_2)

      results = validate_config.validate_directory_tf_files(
          tmpdir, "${var.reasoning_engine_id}"
      )
      self.assertFalse(results["valid"])
      self.assertEqual(len(results["duplicates_found"]), 1)
      self.assertEqual(
          results["duplicates_found"][0]["signal_type"], "tool_use_quality_v1"
      )


if __name__ == "__main__":
  unittest.main()
