# Context Degradation Signals — Full Taxonomy

Context does not fail all at once. It degrades along five distinct
paths, each with its own symptoms, causes, and fixes. This document is
the field guide. Use it after running the audit in Step 1 of the skill
procedure to classify what the numbers are telling you.

---

## Class 1: Poisoning

**What it is:** A false, outdated, or hallucinated statement enters the
context and is treated as ground truth for the rest of the session.
Every subsequent turn builds on the bad foundation.

### Signals

- The agent cites a fact consistently that you know is wrong.
- Correcting the fact once does not fix subsequent turns — the agent
  reverts to the poisoned statement within one or two turns.
- The agent's confidence in the wrong fact increases over time.
- The agent produces downstream reasoning that only makes sense if the
  false statement were true.

### Common sources

- A hallucinated tool output that was never verified.
- A user statement that was true at the time but has since changed
  (e.g., "the API returns a list" after the API was updated to return
  a dict).
- A summarization step that introduced a distortion.
- A retrieved document that is outdated or from a different project.

### Fix

1. **Locate the entry point.** Scan backwards from the first wrong
   citation to find the turn where the bad fact entered.
2. **Replace, do not append.** Appending a correction at the end does
   not work — the model's attention still weights the original
   statement. Edit the history if the runtime allows it. Replace the
   poisoned turn with:

   ```
   [CORRECTION] The previous statement about X was wrong.
   The correct value is Y. All reasoning that assumed X must be
   re-evaluated.
   ```

3. **If the poisoning came from tool output**, re-run the tool. If the
   tool is non-deterministic, summarize its output explicitly with the
   correction applied, rather than pasting the raw output again.

4. **If the runtime does not allow editing history**, start a new
   session. Place the corrected fact in the system prompt or the first
   user message. Do not try to talk the agent out of the poison — the
   cost of a fresh session is almost always lower than the cost of
   repeated correction.

### Verification

Ask the agent: "What is the current value of X?" The answer must
match the correction. Then ask a downstream question that depends on
X. The reasoning must be consistent with the corrected value.

---

## Class 2: Clash

**What it is:** Two sources in the context give contradictory
instructions, and the agent oscillates between them. Unlike poisoning,
no single statement is false — the problem is that both cannot be
true at once.

### Signals

- The agent follows rule A on one turn and contradicting rule B on the
  next, without any user instruction to switch.
- The agent asks for clarification on something that was already
  specified earlier.
- Output format changes between turns without a stated reason.
- The agent produces hedged output that tries to satisfy both rules
  ("I will use tabs, though I note the project uses spaces").

### Common sources

- `AGENTS.md` says one thing; a loaded skill says another.
- The system prompt says one thing; an earlier user turn says another.
- Two reference files were written at different times and never
  reconciled.
- A skill description promises behavior that conflicts with a project
  rule.

### Fix

1. **Enumerate every source.** Grep the context for the topic of the
   clash. Common locations: `AGENTS.md`, system prompt, loaded skills,
   `context-profile.yaml`, reference files, earlier user turns.

2. **Decide precedence explicitly.** Do not leave both rules in place
   with a "prefer X" note. Models do not reliably follow precedence
   notes when the losing rule is still present. Pick a winner.

3. **Remove or amend the loser.** If the losing rule lives in a
   reference file, delete it or rewrite it to align. If it lives in a
   skill, either edit the skill or do not load it for this task.

4. **Document the precedence rule** in `context-profile.yaml` under
   `rules`. This prevents the clash from recurring in future sessions
   that load the same sources.

   ```yaml
   rules:
     - "Precedence, highest first: user instruction, then AGENTS.md, then loaded skill, then reference file."
   ```

### Verification

Ask the agent to state the rule for the clashing topic. It must
produce exactly one answer, not a hedge. Then give it a task that
triggers the rule and confirm the output matches the winning rule.

---

## Class 3: Confusion

**What it is:** The agent treats stale content as relevant. Details
from completed sub-tasks, closed questions, or obsolete drafts remain
in context and get pulled into the current task.

### Signals

- The agent references a file, variable, or decision from a sub-task
  that finished several turns ago.
- The agent re-opens a question that was already resolved.
- The agent's output contains details from a previous task that are
  irrelevant to the current one.
- The agent asks "should I still do X?" where X was already completed.

### Common sources

- A long session that moved through multiple sub-tasks without
  marking any as complete.
- Tool outputs from earlier in the session that are still occupying
  space but no longer relevant.
- A scratchpad or planning block that was never cleaned up.
- Reference material loaded for a previous sub-task and never unloaded.

### Fix

1. **Mark completed sub-tasks explicitly.** In the conversation,
   insert a marker:

   ```
   [COMPLETED] Sub-task: refactor auth module. Result: merged in
   commit abc123. No longer active.
   ```

   This tells the model that the details above are historical, not
   active.

2. **Move details to a reference file if they may be needed later.**
   A "session log" reference file is often the right home for
   completed-work details. It is loaded only when the task touches
   that history.

3. **Remove from active context.** If the runtime supports context
   editing, drop the turn range that contains the completed sub-task
   entirely. If it does not, at minimum summarize the sub-task to a
   single line and replace the verbose version.

4. **Clean the scratchpad.** If the agent uses a planning block or
   TODO list, ensure completed items are removed, not just marked
   done. A growing TODO list is a stale-content generator.

### Verification

Ask the agent: "What is the current active task?" It must name only
the current sub-task, not a completed one. Then ask it to list any
open questions. Items from closed sub-tasks must not appear.

---

## Class 4: Lost-in-Middle

**What it is:** The agent ignores information placed in the middle of
a long context. This is a known attention-pattern limitation of
transformer models, not a bug in the agent or the runtime. Information
at the beginning and end of the context is weighted more heavily than
information in the middle.

### Signals

- Instructions at the top and bottom of the context are followed;
  instructions in the middle are not.
- The agent "discovers" a constraint late in the session that was
  stated early but buried.
- Retrieval from a long reference file misses the relevant section,
  even when the section is clearly present.
- The agent's behavior changes depending on where in the conversation
  a rule was introduced.

### Common sources

- A long conversation where an important rule was stated at turn 2
  and never repeated.
- A reference file with critical information in the middle rather
  than at the top.
- A skill bundle where the relevant skill is listed 8th out of 12.
- A system prompt where the most important instruction sits between
  two less-important ones.

### Fix

1. **Reduce total context length first.** Position matters less when
   the context is short. The most effective fix for lost-in-middle is
   to shrink the context so that everything is effectively at the
   beginning or end.

2. **Move critical instructions to the edges.** Place must-follow
   rules either at the very beginning of the context (primacy bias)
   or at the very end (recency bias). Do not place them in the middle.

   For a system prompt, this means: most important rule first, next
   most important rule last, everything else in between.

3. **Use explicit section headers in reference files.** A file with
   clear `##` headers is navigable by structure rather than by
   position. The agent can find the relevant section even if it is in
   the middle.

4. **Add a table of contents to long reference files.** A TOC at the
   top tells the agent what sections exist and where to look. The
   agent reads the TOC first, then loads only the relevant section.

5. **Re-inject critical rules periodically.** In long sessions,
   repeat the most important constraints every N turns, or have the
   runtime re-inject them at the top of every turn.

### Verification

Ask the agent to state the rule that was buried in the middle. If it
cannot, the rule is not surviving. After the fix, ask again — the
answer must be immediate and correct.

---

## Class 5: Overload

**What it is:** The context window is near capacity. The model is
forced to drop, compress, or distort information to fit, and every
capability degrades. This is the most common failure mode and the one
most directly measurable.

### Signals

- The agent summarizes when it should quote.
- The agent skips steps in a procedure it normally follows.
- Token count per turn grows without bound.
- The agent's output grows shorter and less specific over time.
- The agent truncates its own reasoning ("...and so on").
- Response latency increases noticeably.
- Token cost per turn spikes unexpectedly.

### Common sources

- A long session with no history compression.
- Large tool outputs pasted directly into context.
- Too many skills loaded at once.
- Reference material loaded for the whole session rather than for the
  relevant sub-task.
- Retrieved documents included in full rather than summarized.

### Fix

1. **Measure the token budget per tier.** Run
   `scripts/token_estimator.py --dir . --recursive` to see which
   files are consuming the most space.

2. **Move at least 30% of context into `on_demand` references.**
   Anything that is not needed on every turn belongs in a reference
   file. The agent loads it only when the task touches that domain.

3. **Compress conversation history to a resume brief.** After 20
   turns, replace the raw history with a structured brief. See
   `references/progressive-disclosure-patterns.md` for the template.

4. **Summarize tool outputs.** Any tool output larger than 2,000
   tokens must be summarized before entering context. Write the full
   output to a file and include a reference path plus a one-line
   summary.

5. **Split the task.** If the task genuinely requires more context
   than the window allows, split it into sub-tasks and run them in
   separate sessions, passing a structured handoff brief between
   them.

6. **Enforce headroom.** Never let total utilization exceed 80% of
   the window. A context that is 100% full performs worse than one
   that is 70% full, because the model has no room to reason.

### Verification

Re-run the audit. Total tokens must be lower at the same task stage.
Utilization must be below 80%. Task quality must not regress — run
the same task before and after and compare output.

---

## Mixed Failures

A single session can exhibit more than one class at once. The most
common combinations:

| Combination | Typical scenario |
|---|---|
| **Overload + Lost-in-Middle** | Long session where an early rule got buried |
| **Confusion + Overload** | Multi-task session with no cleanup between tasks |
| **Poisoning + Confusion** | A wrong fact entered early and stale reasoning built on it |
| **Clash + Overload** | Too many skills loaded, with contradictory descriptions |

When multiple classes are present, **fix Overload first.** Reducing
total context length often resolves or reduces the severity of the
other classes on its own. Then re-classify and address what remains.

---

## Diagnostic Order

When the audit shows degradation but the class is not obvious, check
in this order:

1. **Is utilization above 80%?** → Overload. Fix first.
2. **Is instruction survival below 70%?** → Check for Lost-in-Middle
   (rule position) and Clash (contradictory rules).
3. **Is stale content above 40%?** → Confusion. Mark completed
   sub-tasks and clean the scratchpad.
4. **Is repetition above 30%?** → Confusion or Clash. Deduplicate
   reference files and reconcile contradictory sources.
5. **Does the agent cite a fact you know is wrong, consistently?**
   → Poisoning. Locate the entry point and replace it.

This order matters because Overload amplifies every other failure
mode. A short context with a clash is easier to debug than a full
context with the same clash.

---

## Summary Table

| Class | Primary signal | First fix |
|---|---|---|
| **Poisoning** | Consistent wrong fact | Replace the entry turn |
| **Clash** | Oscillating instructions | Pick a winner, remove the loser |
| **Confusion** | References to stale content | Mark completed sub-tasks |
| **Lost-in-Middle** | Middle instructions ignored | Shrink context, move rules to edges |
| **Overload** | Utilization > 80% | Move content to `on_demand` |

Every class has a measurable signal and a structural fix. That is the
point of this taxonomy: turn a vague feeling that "the agent is
getting worse" into a named, diagnosable, fixable condition.