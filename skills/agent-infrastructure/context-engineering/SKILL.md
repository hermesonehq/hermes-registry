---
name: context-engineering
description: "Diagnose and improve context usage in AI agent sessions. Use when context grows large, instructions are being missed, output quality degrades, token usage rises, or a project needs deliberate context organization."
version: 1.1.0
author: Himadri Ganguly
license: MIT
source: https://github.com/himadriganguly/context-engineering/tree/main/skills/context_engineering
platforms: [linux, macos, windows]
compatibility: The Markdown guidance is runtime-agnostic. Optional Python scripts require Python 3.9+ and a session directory matching the documented input layout; they do not provide native integration with every agent runtime.
prerequisites:
  commands: [python3]
metadata:
  hermes:
    tags: [context-engineering, context, token-management, agent-optimization, progressive-disclosure]
    category: agent-infrastructure
    homepage: https://github.com/himadriganguly/context-engineering
    icon: lucide:brain
---

# Context Engineering

Context is the information an agent can access while working on a task.
As a session grows, more instructions, conversation history, tool
output, files, and skills may compete for that working context.

This skill provides a structured procedure for diagnosing context
pressure, identifying likely failure modes, applying structural fixes,
and verifying the result.

The measurements produced by the bundled scripts are heuristics and
proxies, not direct measurements of model attention, reasoning quality,
or semantic understanding.

## Safety and Scope

Use this skill as decision support, not as an authoritative diagnostic
system.

Before running the bundled scripts:

- Review the script source if the session directory contains sensitive
  information.
- Confirm that the supplied path contains only data you are comfortable
  allowing the script to read.
- Back up important data before applying automated or agent-assisted
  changes.
- Treat all token counts and ratios as estimates.
- Do not assume that a threshold in this skill is appropriate for every
  model or runtime.
- Do not expose private session contents in reports, examples, or bug
  reports.

The scripts are designed to read local files. They do not require
network access or third-party Python packages.

## When to Use

Load this skill when one or more of these signals appear:

- **Output quality drop** — responses become vague, repetitive, or
  miss constraints that were previously stated.
- **Instruction drift** — the agent stops following important project
  or task constraints.
- **Token cost increase** — context or output usage grows without an
  obvious increase in task complexity.
- **Long-context retrieval problems** — information becomes difficult
  for the agent to locate in a large context.
- **Context overload** — the runtime is approaching its available
  context capacity.
- **Skill overload** — too many skills or references are being loaded
  for the current task.
- **Session handoff** — a long session needs to be compressed into a
  useful resume brief.
- **New project setup** — the project needs an explicit context
  organization strategy.

Do not use this skill as a substitute for:

- choosing a model;
- evaluating model quality;
- debugging a runtime implementation;
- prompt wording for a single isolated instruction;
- measuring model attention directly;
- claiming that a particular context threshold is universally optimal.

## Procedure

### Step 1 — Audit the Available Context

If the runtime exposes a session directory that matches the documented
input layout, run:

```bash
python scripts/context_audit.py \
  --session-dir PATH \
  --window-size WINDOW_SIZE
```

For example:

```bash
python scripts/context_audit.py \
  --session-dir ./session-fixture \
  --window-size 128000
```

The `--window-size` value should correspond to the effective context
capacity relevant to the session being analyzed.

Do not assume that 128,000 tokens is universally correct.

The audit reports:

- estimated context size;
- estimated window utilization;
- instruction-survival proxy;
- stale-content proxy;
- repetition proxy;
- largest context contributors.

The audit cannot observe information that is not represented in the
supplied session directory.

If a runtime does not expose its session data in the expected layout,
do not attempt to guess its private storage format.

Use the estimator instead:

```bash
python scripts/token_estimator.py \
  --dir . \
  --recursive \
  --top 20
```

This gives a static estimate of the largest files in a project.

### Step 2 — Classify the Problem

Use the measurements together with the actual task behavior.

The five working categories used by this skill are:

| Class | Typical signal | Possible cause |
|---|---|---|
| **Poisoning** | Incorrect information continues to influence later work | An incorrect or obsolete statement entered the working context |
| **Clash** | The agent alternates between incompatible rules | Conflicting instructions or sources |
| **Confusion** | Old or irrelevant details influence the current task | Stale context remains active |
| **Lost-in-middle** | Important information becomes harder to retrieve from long context | Relevant information is buried among unrelated material |
| **Overload** | Context becomes truncated, crowded, or difficult to manage | Too much information is active at once |

These are practical categories, not established clinical or scientific
diagnoses.

A session may have more than one category.

When overload is clearly present, reducing unnecessary context is
usually a sensible first intervention because it can simplify other
problems.

### Step 3 — Apply a Structural Fix

Prefer structural changes over repeatedly rewriting the same prompt.

Load:

```
references/progressive-disclosure-patterns.md
```

when deciding how to reorganize context.

Common interventions include:

- Move stable project knowledge into reference files.
- Compress obsolete conversation history into a concise resume brief.
- Summarize large tool outputs and retain the full output on disk
  when appropriate.
- Load skills and references only when they are relevant.
- Keep critical constraints in a location the runtime reliably
  exposes.
- Remove duplicated or superseded instructions.
- Separate temporary task state from durable project knowledge.

Do not blindly apply every intervention.

The correct intervention depends on the runtime, model, task, and
evidence available.

### Step 4 — Rebuild the Context Profile

Create or update:

```
context-profile.yaml
```

in the project root.

Use:

```
templates/context-profile.yaml
```

as the starting point.

The profile should describe:

- durable project knowledge;
- temporary task state;
- reference material;
- context-budget preferences;
- conflict-resolution rules;
- conditions that should trigger compression or cleanup.

The profile is project-specific. Do not place it inside this installed
skill unless the project explicitly wants that.

### Step 5 — Verify

Re-run the audit using the same measurement configuration:

```bash
python scripts/context_audit.py \
  --session-dir PATH \
  --window-size WINDOW_SIZE \
  --compare
```

Look for meaningful changes in:

- estimated context size;
- estimated utilization;
- instruction-survival proxy;
- stale-content proxy;
- repetition proxy.

Then evaluate the actual task result.

A smaller context is not automatically a better context.

A successful intervention should:

- reduce unnecessary context where appropriate;
- preserve important constraints;
- avoid introducing new contradictions;
- maintain or improve task quality;
- remain understandable to future sessions.

Record useful before/after measurements in the project's own
documentation when reproducibility matters.

## Progressive Disclosure Patterns

When reorganizing context, prefer:

### 1. Stable knowledge in references

Move information that remains true across sessions into reference
files.

Examples:

- architecture;
- API conventions;
- domain terminology;
- decision records;
- project policies.

### 2. Resume briefs for long sessions

When a session becomes difficult to navigate, create a concise brief
containing:

- current objective;
- decisions already made;
- constraints;
- files changed;
- unresolved questions;
- next actions.

Do not preserve every conversational detail merely for completeness.

### 3. Summarize large tool output

For large command output, logs, or documents:

- extract the fields relevant to the task;
- store the full result on disk when needed;
- retain a concise summary in active context;
- avoid repeatedly injecting the same large output.

### 4. Make skill descriptions precise

A skill description should clearly communicate:

- what the skill does;
- when it should activate;
- when it should not activate.

Avoid descriptions that cause unrelated tasks to trigger the skill.

### 5. Use runtime-specific activation features only when supported

If a runtime provides conditional activation or tool requirements, use
them only in runtime-specific documentation or metadata.

Do not assume that one runtime's activation mechanism exists in
another.

### 6. Re-state critical constraints when necessary

For long-running tasks, keep the most important constraints in a
durable location or use the runtime's supported mechanism for
persistent instructions.

Do not repeatedly duplicate the entire instruction set.

## Pitfalls

### 1. Over-compressing

A summary that removes a critical constraint can be worse than the
original context.

Preserve decisions, constraints, assumptions, and unresolved questions.

### 2. Treating all references as always-on

A reference file that is loaded for every task is no longer providing
much progressive-disclosure benefit.

Load detailed references when the task requires them.

### 3. Ignoring tool-output size

Large command output, logs, generated files, and source files can
dominate context.

Estimate their size before repeatedly loading them.

### 4. Fixing symptoms instead of structure

Moving an instruction to a different position may help temporarily.

Prefer reducing irrelevant context, eliminating contradictions, or
improving information organization when those are the underlying
causes.

### 5. Forgetting that skills consume context

A skill itself can contain substantial instructions and references.

Only load skills relevant to the current task.

## Interpretation Notes

### Metrics are proxies

The audit's instruction-survival measurement is based on textual
matching.

The stale-content measurement is based on lexical overlap.

The repetition measurement is based on n-gram counting.

None of these measure semantic understanding, model attention, or
reasoning quality directly.

Use the metrics to detect trends and to compare before/after states,
not to make absolute claims about a session's quality.

### Thresholds are defaults, not laws

The degradation thresholds suggested by this skill are conservative
starting points. They may not fit every model, runtime, or task.

Tighten them for quality-critical work. Loosen them for exploratory
work. The correct threshold is the one that catches the failure before
it affects output.

### Headroom matters

A context that is nearly full tends to perform worse than one with
room to spare.

Leave room for the model's own reasoning. Do not allocate the last
portion of the window to content that is not essential.

### Measurements depend on what is supplied

The audit reads the session directory it is given. If the directory is
incomplete, the measurements will be incomplete. If it contains
irrelevant files, the measurements will be skewed.

Always confirm that the supplied directory matches the runtime's
actual session state before drawing conclusions.

## Reference Files

Load these on demand, as the corresponding step is reached:

| File | Load when |
|---|---|
| `references/degradation-signals.md` | Classifying the problem (Step 2) |
| `references/progressive-disclosure-patterns.md` | Applying a structural fix (Step 3) |
| `references/token-budget-framework.md` | Rebuilding the context profile (Step 4) |

## Scripts

Both scripts use only the Python standard library. They require Python
3.9 or later. No external dependencies are required.

### `scripts/context_audit.py`

Produce a quantitative audit of a session directory.

```bash
python scripts/context_audit.py \
  --session-dir PATH \
  --window-size WINDOW_SIZE

python scripts/context_audit.py \
  --session-dir PATH \
  --window-size WINDOW_SIZE \
  --json

python scripts/context_audit.py \
  --session-dir PATH \
  --window-size WINDOW_SIZE \
  --compare
```

### `scripts/token_estimator.py`

Estimate the token cost of text, a file, or a directory.

```bash
python scripts/token_estimator.py --text "string"
python scripts/token_estimator.py --file path/to/file
python scripts/token_estimator.py --dir . --recursive --top 20
```

The estimator uses a calibrated character-based heuristic. Treat the
results as estimates, not exact token counts.

## Summary

Five steps for diagnosing and improving context usage:

1. **Audit** the available context.
2. **Classify** the likely problem.
3. **Apply** a structural fix.
4. **Rebuild** the context profile.
5. **Verify** the result.

The procedure is intended to be applied thoughtfully, not mechanically.

Measurements are proxies. Thresholds are defaults. The correct
intervention depends on the runtime, model, task, and evidence
available.