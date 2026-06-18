# Skill Quality Checklist

Derived from the dual-axis-skill-reviewer scoring rubric (100 points total).

## 1. Metadata & Use Case (20 points)

- [ ] YAML frontmatter has `name:` matching directory name
- [ ] `description:` is a clear, concise trigger condition
- [ ] "When to Use" section lists specific trigger scenarios
- [ ] "Prerequisites" section documents Python version, API keys, dependencies
- [ ] No ambiguity about when the skill should activate

## 2. Workflow Coverage (25 points)

- [ ] "Overview" section explains what the skill does (2-3 sentences)
- [ ] "Workflow" has numbered steps with imperative verbs
- [ ] Each step has concrete actions (not vague guidance)
- [ ] Bash command examples use full relative paths
- [ ] "Output Format" section shows JSON/Markdown structure
- [ ] "Resources" section lists all reference files and scripts

## 3. Execution Safety & Reproducibility (25 points)

- [ ] Bash commands are copy-pasteable (correct paths, flags)
- [ ] Scripts use `--output-dir reports/` as default
- [ ] No hardcoded absolute paths (use relative or dynamic resolution)
- [ ] API keys read from environment variables first, CLI args as fallback
- [ ] Error handling with proper exit codes documented
- [ ] Date/time stamps in all output files

## 4. Supporting Artifacts (10 points)

- [ ] At least one reference document in `references/`
- [ ] At least one executable script in `scripts/` (unless knowledge_only)
- [ ] Scripts have `#!/usr/bin/env python3` shebang
- [ ] `__init__.py` not required (scripts are standalone)

## 5. Test Health (20 points)

- [ ] Test directory exists: `scripts/tests/`
- [ ] `conftest.py` with sys.path setup present
- [ ] At least 3 meaningful tests covering core logic
- [ ] Tests use pytest fixtures and tmp_path
- [ ] Tests pass with `python -m pytest scripts/tests/ -v`

## Threshold Policy

| Score | Status |
|-------|--------|
| 90+   | Production-ready |
| 80-89 | Usable with targeted improvements |
| 70-79 | Notable gaps; strengthen before regular use |
| <70   | High risk; treat as draft and prioritize fixes |

## Knowledge-Only Skills

For skills with no executable scripts but with reference docs:
- Classify as `knowledge_only`
- Do not penalize missing bash command examples
- Adjust `supporting_artifacts` and `test_health` expectations
- Still require clear "When to Use", "Prerequisites", and workflow structure
