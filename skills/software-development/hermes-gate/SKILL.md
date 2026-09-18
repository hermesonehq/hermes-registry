---
name: hermes-gate
description: Run a repository's declared checks with receipt-bound evidence. Use when a coding task needs a bounded, repeatable local completion check before review or a repository boundary.
version: 0.1.5
author: Hermes Labs
license: Apache-2.0
platforms: [linux, macos, windows]
prerequisites:
  commands: [python, git]
source: https://github.com/hermes-labs-ai/hermes-gate
metadata:
  hermes:
    icon: lucide:shield-check
    tags: [quality-gate, testing, receipts, git, coding-agents]
    category: software-development
---

# HermesGate

Use this skill when a repository needs an inspectable record that its own
declared checks passed for the exact content under review. HermesGate is a
local completion rail: it does not repair code, invoke a model, approve a
merge, or authorize a push, pull request, or release.

## Install

Install the published package in the environment that will run the checks:

```bash
python -m pip install hermes-gate
```

HermesGate requires Python 3.11+ and Git. It has no runtime dependencies.

## First use in a repository

1. Enter the target Git repository.
2. Run `hermes-gate init` to detect existing Python or JavaScript checks and
   write a reviewable `.hermes/gate.toml`, runner, and CI workflow. It does
   not overwrite existing integration files unless `--force` is explicit.
3. Inspect the generated profile. Keep commands as argv arrays and remove or
   adjust any check that is not the repository's own intended contract.
4. Run the smallest appropriate ceremony:

   ```bash
   hermes-gate fast
   hermes-gate review
   hermes-gate full
   ```

   - `fast` checks the selected changed paths.
   - `review` requires an exact `fast` PASS and records one bounded semantic
     review when its configured provider is available.
   - `full` runs the repository-local full contract.

5. Before a configured repository boundary, verify the matching receipt:

   ```bash
   hermes-gate boundary commit
   # or: hermes-gate boundary push
   # or: hermes-gate boundary pr-create
   ```

## Interpret results precisely

A `PASS` means the configured commands passed for the receipt-bound content,
with the recorded tool versions. It is not a universal correctness, security,
mergeability, publication, adoption, or authorization claim.

If the repository has never adopted HermesGate, do not run `init` merely to
satisfy a boundary. If an adopted repository is missing its profile, restore
the profile or run `hermes-gate uninstall-repo`; it remains fail-closed until
one of those deliberate actions occurs.

## Diagnose without bypassing

Run `hermes-gate doctor` to inspect profile and tool availability. Keep
failures actionable: repair the repository's check or profile, re-run the
needed ceremony, and let the new receipt replace the stale one. Do not treat a
missing, unavailable, or non-PASS receipt as permission to skip the boundary.

For the complete CLI, integration details, and receipt semantics, use the
canonical source: https://github.com/hermes-labs-ai/hermes-gate