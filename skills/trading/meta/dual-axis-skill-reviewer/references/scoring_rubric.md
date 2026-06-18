# Scoring Rubric Rationale

This document explains why each auto-axis component has its current weight.

## Weights

- `metadata_use_case` (20)
Why: bad frontmatter and unclear trigger conditions make a skill hard to invoke correctly.

- `workflow_coverage` (25)
Why: operators need executable flow; missing core sections creates ambiguity in real use.

- `execution_safety_reproducibility` (25)
Why: command examples and path hygiene determine whether results are repeatable and safe.

- `supporting_artifacts` (10)
Why: scripts/references/tests provide baseline maintainability, but should not dominate scoring.

- `test_health` (20)
Why: runtime confidence is critical; passing tests strongly increases trust in automation.

## Threshold Policy

- `90+`: production-ready baseline
- `80-89`: usable with targeted improvements
- `70-79`: notable gaps; strengthen before regular use
- `<70`: high risk; treat as draft and prioritize fixes

## Improvement Trigger

When final score is `< 90`, improvement items are mandatory in report output.

## Knowledge-Only Skill Handling

For skills with no executable scripts (`scripts/*.py` absent) but with reference docs:

- Classify as `knowledge_only`.
- Do not penalize missing bash command examples.
- Treat script/test artifacts as mostly not-applicable (`supporting_artifacts` and `test_health` adjusted).
- Still require clear `When to Use`, `Prerequisites`, and workflow structure.
