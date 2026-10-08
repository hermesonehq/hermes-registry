# Progressive Disclosure Patterns

Progressive disclosure is the practice of loading information only when
it is needed. It is the single most effective technique for keeping
context small while preserving access to deep knowledge.

This document describes six patterns. Each one is a reusable solution
to a specific context problem. Use them together, or pick the ones that
fit your project.

---

## Pattern 1: The Three-Tier Context

Every project should have three context tiers, each with a distinct
loading rule and token budget.

| Tier | Contents | Loaded | Budget |
|---|---|---|---|
| **Always-on** | Project rules, identity, active task | Every turn | 10–15% of window |
| **On-demand** | Architecture docs, conventions, decision logs | When task touches that domain | 30–40% of window |
| **Ephemeral** | Current tool output, recent conversation, scratchpad | Current turn + 3–5 turns | 20–30% of window |

The remaining **20–40% is headroom** — empty space the model uses for
its own reasoning. Headroom is not waste. A context that is 100% full
performs worse than one that is 70% full, because the model has no
room to think.

### How to apply it

1. List every piece of content the agent currently loads.
2. Assign each piece to a tier:
   - **Always-on** if it is needed on every turn (identity, active
     task, hard constraints).
   - **On-demand** if it is needed only for certain tasks
     (architecture, domain knowledge, past decisions).
   - **Ephemeral** if it is transient (tool output, recent turns,
     scratchpad).
3. Declare the tiers in `context-profile.yaml`.
4. Enforce the budget. If a tier exceeds its budget, move content
   down a tier or delete it.

### Example

```yaml
tiers:
  always_on:
    files:
      - AGENTS.md
      - context/task.md
    budget_tokens: 6000

  on_demand:
    files:
      - references/architecture.md
      - references/api-conventions.md
      - references/decision-log.md
    budget_tokens: 40000

  ephemeral:
    budget_tokens: 20000
```

---

## Pattern 2: The Resume Brief

When a session exceeds ~20 turns, the raw conversation history becomes
a liability. It grows without bound, contains narration that is no
longer relevant, and buries the decisions that actually matter.

The fix is to **compress history into a structured resume brief.**
The brief replaces the raw turn log. It captures decisions, not
narration.

### Template

```markdown
## Resume Brief

### Task
[One sentence: what are we doing and why?]

### Decisions
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

### Constraints
- [Constraint 1] (source: [user message / AGENTS.md / discovered])
- [Constraint 2]

### Open Questions
- [Question 1]
- [Question 2]

### Files
- [Path]: [Current state — modified, created, read-only]
- [Path]: [Current state]

### Active Sub-task
[What the agent was doing when the session paused, and its
acceptance criteria]
```

### What to include

- **Decisions and their rationale.** Not just "we chose X" but "we
  chose X because Y."
- **Constraints discovered.** Anything that limits the solution space
  and is not obvious from the code.
- **Open questions.** Things that are unresolved and might affect
  future turns.
- **Files touched and their state.** So the agent knows what has been
  changed and what has not.
- **The active sub-task.** What the agent was working on, and how it
  will know when it is done.

### What NOT to include

- Narration of what happened ("first I read the file, then I...")
- Raw tool outputs
- Intermediate reasoning
- Dead ends (unless a dead end contains a useful lesson — in which
  case promote the lesson to a constraint)
- Apologies, acknowledgments, or conversational filler

### How to apply it

1. **End every session by writing the brief.** Make it the final
   action of the session.
2. **Start every session by loading the brief.** Put it in the
   always-on tier, capped at ~1,500 tokens.
3. **Never accumulate raw history across sessions.** If a session
   runs long, compress mid-session. Do not wait until the end.

### Why it works

A 50-turn conversation can easily reach 40,000 tokens. The same
information compressed into a resume brief is usually 1,000–2,000
tokens — a 95% reduction. And the brief is *better* than the raw
history, because it is structured: the agent can find decisions,
constraints, and open questions by section, rather than by scanning
turn-by-turn.

---

## Pattern 3: Reference File Structure

A reference file that the agent loads on demand should be navigable
by structure. The agent should be able to find the relevant section
without reading the whole file.

### Recommended structure

```markdown
# [Topic]

## Quick Reference
[The 3–5 facts an agent needs 80% of the time. This section should
fit on one screen. If the answer is here, the agent stops reading.]

## Detailed Guide
[The full explanation, organized by sub-topic with headers.]

## Decision Table
[When to use X vs. Y, in table form.]

## Pitfalls
[Known failure modes and how to avoid them.]

## Examples
[Concrete examples, not abstract descriptions.]

## Changelog
[When the file was last updated and why.]
```

### How the agent uses it

The agent reads the **Quick Reference** first. If the answer is there,
it stops. If not, it navigates to the relevant section by header.

This is the same pattern the Agent Skills specification uses for
`SKILL.md` itself. The `SKILL.md` is the Quick Reference; the
`references/` directory is the Detailed Guide.

### Antipatterns to avoid

- **A wall of prose.** No headers, no structure. The agent must read
  the whole file to find anything.
- **Critical information buried in the middle.** Use the Quick
  Reference section for anything time-sensitive or high-importance.
- **Multiple topics in one file.** If a file covers three unrelated
  topics, split it into three files. The agent loads only the one it
  needs.
- **Duplicated content.** If the same fact appears in two reference
  files, the agent may load both and waste tokens on the duplicate.

### Example

```markdown
# API Conventions

## Quick Reference
- All endpoints are versioned under `/v2/`.
- Auth is Bearer token in the `Authorization` header.
- Errors return `{ "error": "message", "code": "E_XXX" }`.

## Detailed Guide

### Versioning
...

### Authentication
...

### Error Format
...

## Decision Table

| Scenario | Endpoint style | Auth |
|---|---|---|
| Public read | `GET /v2/resource` | None |
| Private read | `GET /v2/resource` | Bearer |
| Write | `POST /v2/resource` | Bearer + CSRF |

## Pitfalls
- Do not use `/v1/` — it is deprecated.
- Do not send auth in query strings — header only.
```

---

## Pattern 4: Skill Description as Loading Signal

A skill's `description` field is the agent's only signal for when to
load it. It is not a summary. It is a **trigger condition.**

A vague description causes two failure modes:

- **False positives** — the agent loads the skill when it is not
  needed, wasting context.
- **False negatives** — the agent never loads the skill, even when it
  would help.

### Bad example

```yaml
description: Helps with database stuff.
```

Problems: What kind of database? What does "helps" mean? When should
the agent load it? The agent has no way to decide.

### Good example

```yaml
description: Generate, review, and debug SQL queries. Use when the
  user mentions SQL, queries, database schema, migrations, or asks to
  "write a query." Do not use for ORM configuration or connection
  pooling — those are handled by the database-config skill.
```

Why it works: It names the trigger conditions explicitly ("mentions
SQL, queries, database schema...") and the anti-triggers ("do not use
for ORM configuration"). The agent can decide with high confidence.

### Pattern

```yaml
description: [What the skill does in one sentence]. Use when
  [trigger condition 1], [trigger condition 2], or [trigger condition
  3]. Do not use for [anti-trigger 1] or [anti-trigger 2] — those are
  handled by [other skill or tool].
```

### Length budget

Aim for 200–400 characters. Long enough to name triggers and
anti-triggers. Short enough to fit in the skill index without
consuming significant context.

If you find yourself writing more than 500 characters, the skill
probably covers too much. Split it into two skills with distinct
triggers.

---

## Pattern 5: Conditional Activation

If the runtime supports it, gate skills behind conditions. A skill
that only applies in certain situations should not occupy space in
the always-on skill index.

### Fallback activation

Use this when a skill provides a local alternative to a tool that may
not always be available:

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]
```

The skill appears in the index **only when the `web` toolset is
unavailable.** When `web` is present, the skill is hidden. This keeps
the index small in the common case.

### Required activation

Use this when a skill depends on a tool that must be present:

```yaml
metadata:
  hermes:
    requires_toolsets: [filesystem]
```

The skill appears **only when the required toolset is available.**
This prevents the agent from loading a skill it cannot actually use.

### Category-based activation

Some runtimes support loading skills by category on demand:

```yaml
metadata:
  category: agent-infrastructure
  auto_load: false
```

The skill is registered but not loaded into the index. The agent
loads it when the description matches the task. Use this for skills
that are useful but not frequently needed.

### How to decide

Ask: **Would I want this skill loaded on every single session?**

- **Yes, always** → no gating. Let it load.
- **Only when a tool is missing** → `fallback_for_toolsets`.
- **Only when a tool is present** → `requires_toolsets`.
- **Only on certain tasks** → `auto_load: false` with a strong
  description (Pattern 4).

---

## Pattern 6: Tool Output Summarization

Tool outputs are the single largest source of context bloat in most
sessions. A single `read_file` on a large source file can consume 30%
of the context window. Twelve log files can fill the window entirely.

The rule: **any tool output larger than 2,000 tokens must be
summarized before it enters context.**

### Four strategies

Choose the strategy that fits the output type:

#### 1. Extract

Pull only the fields the task needs.

**Before:**
```json
{
  "id": "user_123",
  "name": "Alice",
  "email": "alice@example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-06-15T10:23:11Z",
  "settings": { /* 50 fields */ },
  "history": [ /* 200 events */ ]
}
```

**After (extracting only what the task needs):**
```
user_123: name=Alice, email=alice@example.com
```

#### 2. Diff

If the tool output is a new version of something already in context,
include only the diff.

**Before:** Re-pasting the entire config file.

**After:**
```
config.yaml changed:
  - port: 8080
  + port: 9090
```

#### 3. Chunk

Split the output into sections and load only the relevant section.

**Before:** All 12 chapters of a manual.

**After:** Chapter 7 only (the one about the error code in question).

#### 4. Cache

Write the full output to a file. Put a one-line reference in context.

**Before:** 48,000 lines of log output.

**After:**
```
logs/api-errors.log — 48,201 lines, 312 errors, peak at 14:02 UTC.
Full file: /tmp/INC-4421/api-errors.log
```

The agent can re-read the file if it needs details, but the context
holds only the summary.

### When to break the rule

The 2,000-token limit has exactly two exceptions:

1. **The task requires exact reproduction.** If the user asked for
   the full file contents to be returned, include them — but do so in
   a single turn and then drop them from subsequent turns.
2. **The output is smaller than the summary would be.** Rare, but if
   the output is a 500-byte JSON and the summary would be 600 bytes,
   just include the original.

### Implementation

The `scripts/token_estimator.py` tool predicts the token cost of any
file before it is read:

```bash
python scripts/token_estimator.py --file path/to/large-file.log
# Output: 47,203 tokens (path/to/large-file.log)
```

Use it as a pre-flight check. If the estimated cost exceeds 2,000
tokens, summarize before reading.

---

## Applying the Patterns Together

These six patterns are not independent. They reinforce each other:

| Pattern | Solves | Works with |
|---|---|---|
| 1. Three-tier context | Everything | All other patterns |
| 2. Resume brief | Overload in long sessions | Pattern 1 (always-on tier) |
| 3. Reference file structure | Lost-in-middle | Pattern 1 (on-demand tier) |
| 4. Skill description | Wrong skill loading | Pattern 5 (conditional activation) |
| 5. Conditional activation | Skill index bloat | Pattern 4 (strong descriptions) |
| 6. Tool summarization | Overload from tool output | Pattern 1 (ephemeral tier) |

The three-tier context (Pattern 1) is the foundation. The other five
patterns are specific techniques for deciding what goes in each tier.

---

## Checklist

Before declaring a project "context-engineered," verify each pattern:

- [ ] **Three-tier context** — `context-profile.yaml` declares the
      tiers, files, and budgets.
- [ ] **Resume brief** — sessions longer than 20 turns are compressed,
      and cross-session work uses a brief.
- [ ] **Reference structure** — every reference file has a Quick
      Reference section at the top.
- [ ] **Skill descriptions** — every skill's description names
      explicit trigger and anti-trigger conditions.
- [ ] **Conditional activation** — skills that do not apply to every
      session are gated by toolset or category.
- [ ] **Tool summarization** — no tool output larger than 2,000
      tokens enters context without being summarized first.

If all six are checked, the project is well-architected. If any are
unchecked, that is the next thing to fix.