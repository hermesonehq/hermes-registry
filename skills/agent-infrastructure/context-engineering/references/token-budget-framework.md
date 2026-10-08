# Token Budget Framework

## Purpose

This document defines a practical framework for managing token budgets in AI-agent workflows.

The objective is not to maximize the amount of information placed into a model context. The objective is to provide the **minimum sufficient context required to complete the task correctly**, while preserving critical instructions, relevant evidence, useful history, and enough capacity for tool interaction and model output.

This framework is designed to be:

* **Model-agnostic** — it does not assume a specific context-window size or tokenizer.
* **Runtime-aware** — system instructions, tool definitions, retrieved content, and output requirements consume context.
* **Progressive** — information should be loaded when needed rather than preloaded indiscriminately.
* **Measurable** — token usage should be estimated or counted and reported with its method.
* **Configurable** — budgets should adapt to the model, runtime, task, and available context.
* **Compatible with Hermes Agent** — detailed reference material can remain outside `SKILL.md` and be loaded on demand.

---

## 1. Core Principle

A large context window is a capacity limit, not a recommendation to fill the entire window.

The target is:

> **Maximum useful information density within the minimum sufficient context.**

More context can be useful when it contains information required to solve the task. It can also be wasteful when it contains:

* duplicated instructions,
* irrelevant history,
* obsolete information,
* low-value examples,
* unnecessary tool output,
* repeated documentation,
* speculative material,
* or content unrelated to the current task.

Therefore:

```text
Context quality ≠ Context size
```

A better approximation is:

```text
Context quality
≈
relevance
× completeness
× accuracy
× findability
× freshness
```

while unnecessary context increases:

```text
token cost
+
retrieval noise
+
instruction competition
+
processing overhead
```

The framework therefore optimizes for **sufficient context**, not maximum context utilization.

---

# 2. Context Budget Terminology

A token budget should distinguish between several different quantities.

## 2.1 Model Context Window

The maximum amount of context supported by the target model for a request.

```text
C = model context window
```

The value is model-specific and may differ between providers, models, APIs, and runtime configurations.

Do not hard-code a context-window size into the framework unless it is explicitly supplied by the runtime.

---

## 2.2 Input Context

The information supplied to the model before generation.

This may include:

* system instructions,
* runtime instructions,
* tool definitions,
* skill instructions,
* conversation history,
* retrieved documents,
* user input,
* tool results,
* application state,
* structured metadata.

Represent this as:

```text
I = input tokens
```

---

## 2.3 Output Reserve

The capacity reserved for the model's generated response.

```text
O = output reserve
```

This should not automatically be treated as a fixed percentage.

The appropriate reserve depends on the task.

Examples:

* short classification → small reserve
* code generation → larger reserve
* report generation → large reserve
* multi-step tool workflow → reserve appropriate for expected intermediate/final output

---

## 2.4 Runtime Overhead

Tokens consumed by the agent runtime independently of the task-specific context.

This can include:

* system prompts,
* tool definitions,
* tool instructions,
* platform policies,
* skill metadata,
* runtime state,
* orchestration messages.

Represent this as:

```text
R = runtime overhead
```

The exact amount may vary between requests.

---

## 2.5 Safety Margin

A configurable buffer that protects against estimation error, unexpected tool output, or dynamic context growth.

```text
M = safety margin
```

The safety margin should be configurable.

Do not assume that a universal value such as 10%, 15%, or 20% is always correct.

---

## 2.6 Usable Context

A practical working budget can be expressed as:

```text
U = C - R - O - M
```

Where:

```text
C = model context capacity
R = runtime/system overhead
O = output reserve
M = safety margin
U = usable task context
```

If any component is unknown, the implementation should mark the resulting value as an estimate rather than presenting it as an exact budget.

---

# 3. Context Composition

The usable task context can be divided into several logical categories.

```text
Usable Context
│
├── Mandatory Context
│   ├── task requirements
│   ├── safety constraints
│   ├── critical instructions
│   └── required state
│
├── Persistent Context
│   ├── project conventions
│   ├── user-provided requirements
│   └── stable task state
│
├── Retrieved Context
│   ├── references
│   ├── documentation
│   ├── search results
│   └── tool results
│
├── Historical Context
│   ├── previous conversation
│   └── previous decisions
│
└── Optional Context
    ├── examples
    ├── background information
    └── supplementary material
```

These categories should not necessarily receive equal allocation.

The task determines their relative importance.

---

# 4. Context Priority Model

When context must be reduced, preserve information according to task value.

A recommended priority order is:

```text
Priority 1
Current task requirements

Priority 2
Explicit user constraints

Priority 3
Safety and operational constraints

Priority 4
Required project/runtime instructions

Priority 5
Information required to produce a correct result

Priority 6
Relevant retrieved references

Priority 7
Recent relevant conversation state

Priority 8
Useful examples

Priority 9
General background information

Priority 10
Redundant or low-value content
```

This is a prioritization heuristic, not a universal law.

Some tasks may legitimately require historical context or large reference sets.

---

# 5. Budget Allocation Strategy

A robust allocation process should be dynamic.

## Step 1 — Determine the available capacity

Identify:

```text
C = target model context capacity
```

If the runtime does not expose the capacity, record:

```text
context_window = unknown
```

Do not invent a value.

---

## Step 2 — Estimate runtime overhead

Estimate or measure:

```text
R = system + runtime + tools + framework overhead
```

If the runtime provides an actual token count, prefer that over estimation.

---

## Step 3 — Reserve output capacity

Determine how much generation capacity the task is likely to require.

```text
O = expected output reserve
```

For dynamic agent workflows, reserve enough space for the expected response and tool-driven interaction.

---

## Step 4 — Apply the safety margin

Reserve:

```text
M = configurable safety margin
```

The margin should account for:

* estimation error,
* dynamic tool results,
* additional retrieved content,
* runtime variation,
* unexpected task expansion.

---

## Step 5 — Calculate the working budget

```text
U = C - R - O - M
```

If:

```text
U <= 0
```

the task is already over budget before task-specific content is added.

The system should reduce optional runtime content, increase available capacity, use a smaller workflow, or select another execution strategy.

---

## Step 6 — Allocate mandatory content

Reserve space for:

* the current request,
* explicit constraints,
* required instructions,
* critical state.

Mandatory content should not be sacrificed merely to preserve optional references.

---

## Step 7 — Retrieve supporting information

Load only the references required for the task.

Prefer:

```text
targeted retrieval
```

over:

```text
load everything
```

---

## Step 8 — Add optional context

Only after mandatory and required supporting context are available should optional context be added.

Optional material includes:

* additional examples,
* historical discussion,
* background documentation,
* alternative approaches,
* supplementary evidence.

---

## Step 9 — Verify

Before execution, check:

* required instructions remain present,
* task constraints remain present,
* critical references remain available,
* estimated context is within budget,
* output reserve remains available.

---

# 6. Progressive Disclosure

Progressive disclosure is a primary mechanism for controlling context growth.

Instead of loading every piece of information at the beginning:

```text
discover
   ↓
load primary instructions
   ↓
identify required knowledge
   ↓
load targeted reference
   ↓
retrieve additional information only if required
```

This reduces unnecessary context consumption.

## Hermes Agent

Hermes Agent currently uses a progressive-disclosure skill model:

```text
Level 0:
skills_list()
        ↓
compact skill metadata

Level 1:
skill_view(name)
        ↓
SKILL.md

Level 2:
skill_view(name, path)
        ↓
specific reference/support file
```

The agent therefore does not need to load every reference file when discovering or activating a skill.

For a Hermes skill:

```text
SKILL.md
    ↓
procedure and always-on rules

references/
    ↓
detailed knowledge loaded on demand

scripts/
    ↓
executable helpers when required

templates/
    ↓
output/configuration structures when required
```

This separation is important.

### Keep in `SKILL.md`

* activation guidance,
* task procedure,
* essential rules,
* critical constraints,
* references to supporting material.

### Keep in `references/`

* detailed frameworks,
* decision tables,
* provider-specific behavior,
* long explanations,
* domain knowledge,
* troubleshooting information.

Hermes' current documentation specifically describes `references/` as supporting knowledge that the agent can load on demand.

---

# 7. Context Density

Token count alone does not measure context quality.

A useful concept is:

```text
Information Density =
Useful Information / Total Context
```

High-density context tends to contain:

* relevant facts,
* explicit constraints,
* actionable instructions,
* verified evidence,
* concise examples.

Low-density context tends to contain:

* repetition,
* conversational filler,
* outdated information,
* excessive prose,
* irrelevant examples,
* duplicated documentation.

The goal of compression is therefore not simply:

```text
reduce tokens
```

but:

```text
increase useful information per token
```

---

# 8. Context Compression

When the context exceeds its budget, compress in stages.

## Stage 1 — Remove exact duplicates

Remove:

* repeated instructions,
* duplicated tool output,
* repeated documentation,
* identical examples.

---

## Stage 2 — Remove obsolete information

Remove information that has been superseded by later information.

For example:

```text
old configuration
    ↓
new configuration
```

If the old configuration no longer matters, preserve only the current state.

---

## Stage 3 — Remove irrelevant history

Conversation history should be retained because it affects the current task, not merely because it exists.

Prefer:

```text
decision + current state
```

over:

```text
entire historical conversation
```

---

## Stage 4 — Compress verbose explanations

Transform:

```text
long explanation
```

into:

```text
rule
+
condition
+
important exception
```

Preserve meaning rather than wording.

---

## Stage 5 — Reduce examples

Examples should be retained when they clarify a difficult rule.

Otherwise:

```text
many similar examples
```

should become:

```text
one representative example
```

---

## Stage 6 — Remove optional background information

Background material is the final category to remove before mandatory task information.

---

# 9. What Must Not Be Compressed Away

The following should generally be preserved:

* explicit user requirements,
* safety constraints,
* critical tool restrictions,
* authentication requirements,
* output-format requirements,
* important negative constraints,
* required file paths,
* required API parameters,
* decisions that materially affect the current task.

A shorter context that loses a critical constraint is not an optimization.

---

# 10. Retrieval Budget

Retrieval itself should be budgeted.

A useful model is:

```text
Retrieval Budget
=
maximum tokens allocated to external/reference material
```

Do not retrieve large documents merely because they are available.

Prefer:

```text
query
→ identify relevant section
→ retrieve section
→ evaluate
→ retrieve more only if necessary
```

over:

```text
retrieve entire document
→ place entire document into context
```

For large references, use:

* headings,
* semantic search,
* exact matching,
* section-level retrieval,
* summaries,
* structured metadata.

---

# 11. Tool Output Budget

Tool output can become one of the largest sources of unexpected context growth.

A tool may return:

```text
small result
```

or:

```text
thousands of lines
```

The agent should therefore distinguish between:

```text
tool result generated
```

and:

```text
tool result actually required in context
```

Prefer:

```text
execute tool
    ↓
inspect result
    ↓
retain relevant subset
```

rather than blindly carrying the entire result through subsequent turns.

For large outputs, use:

* pagination,
* filtering,
* structured output,
* summaries,
* targeted extraction,
* file-based persistence.

---

# 12. Historical Context Budget

Conversation history should be treated as a resource.

A useful model is:

```text
Historical Value =
relevance × recency × decision impact
```

High-value history includes:

* current requirements,
* decisions,
* unresolved issues,
* constraints,
* previous failures that change the next action.

Low-value history includes:

* greetings,
* repeated explanations,
* obsolete alternatives,
* intermediate reasoning that no longer affects the task.

When compressing history, preserve the **state produced by the conversation**, not necessarily the entire conversation itself.

---

# 13. Output Reservation

The output reserve should reflect the expected task.

Examples:

| Task                      | Typical output requirement |
| ------------------------- | -------------------------- |
| Classification            | Small                      |
| Short answer              | Small                      |
| Configuration change      | Small–medium               |
| Code patch                | Medium–large               |
| Detailed analysis         | Medium–large               |
| Long document             | Large                      |
| Multi-file implementation | Large                      |
| Tool-driven workflow      | Dynamic                    |

These categories are qualitative guidance.

They are not fixed token allocations.

The implementation should prefer an explicit task-specific value when available.

---

# 14. Overflow Handling

When the estimated context exceeds the available budget:

```text
IF context <= budget
    proceed

ELSE
    remove duplicates
    ↓
    remove obsolete information
    ↓
    remove irrelevant history
    ↓
    compress verbose material
    ↓
    reduce optional references
    ↓
    reduce retrieval scope
    ↓
    verify critical instructions
    ↓
    proceed if within budget
```

If the context remains over budget:

```text
split the task
OR
retrieve information incrementally
OR
summarize intermediate state
OR
use a model/runtime with greater capacity
```

Do not silently discard critical requirements.

---

# 15. Task Decomposition for Large Contexts

Large tasks should be decomposed when their required context cannot fit comfortably into a single request.

Example:

```text
Large project
     │
     ├── Phase 1: discovery
     │
     ├── Phase 2: analysis
     │
     ├── Phase 3: implementation
     │
     ├── Phase 4: validation
     │
     └── Phase 5: final synthesis
```

Each phase should retain a compact state representation:

```yaml
task_state:
  objective: "..."
  completed:
    - "..."
  decisions:
    - "..."
  constraints:
    - "..."
  unresolved:
    - "..."
  artifacts:
    - "..."
```

This is generally more efficient than carrying the entire execution history indefinitely.

---

# 16. Token Estimation

Token estimates should always identify their method.

Recommended categories:

```text
exact
approximate
heuristic
unknown
```

## Exact

An actual tokenizer compatible with the target model/provider was used.

Example:

```yaml
tokens:
  value: 18420
  method: exact
```

---

## Approximate

A tokenizer or encoding approximation was used, but it may not exactly match the target runtime.

```yaml
tokens:
  value: 19000
  method: approximate
```

---

## Heuristic

A character-, word-, or byte-based estimation was used.

```yaml
tokens:
  value: 19500
  method: heuristic
```

---

## Unknown

No reliable estimate is available.

```yaml
tokens:
  value: null
  method: unknown
```

Never present a heuristic estimate as an exact token count.

---

# 17. Estimation Confidence

A useful report should expose estimation quality.

Example:

```yaml
token_estimate:
  value: 18420
  method: heuristic
  confidence: low
```

or:

```yaml
token_estimate:
  value: 18374
  method: exact
  confidence: high
```

Confidence should describe the **measurement method**, not the quality of the underlying content.

---

# 18. Recommended Machine-Readable Budget Model

Implementations can represent a budget using a structure similar to:

```yaml
context_budget:
  model_context_window: null

  reservations:
    runtime: auto
    output: auto
    safety_margin: auto

  allocation:
    mandatory: auto
    task_context: auto
    retrieval: auto
    history: auto
    optional: auto

  estimation:
    method: heuristic
    confidence: low
```

Values should be resolved by the runtime when possible.

---

# 19. Worked Example

Assume a hypothetical model exposes:

```text
Context capacity = 200,000 tokens
```

Assume the runtime estimates:

```text
Runtime overhead = 15,000
Output reserve   = 20,000
Safety margin    = 10,000
```

Then:

```text
Usable Context
= 200,000
  - 15,000
  - 20,000
  - 10,000

= 155,000 tokens
```

The 155,000-token working budget can then be allocated according to the task.

For example:

```text
Mandatory task context       10,000
Project/persistent context   20,000
Required references           45,000
Relevant history              25,000
Current evidence              40,000
Optional context              15,000
                              ------
Total                        155,000
```

These values are **illustrative only**.

They are not recommended universal percentages.

A different task could legitimately allocate most of the budget to retrieved evidence and almost none to conversation history.

---

# 20. Context Audit Metrics

A context-management system should measure more than total tokens.

Recommended metrics include:

## Token Metrics

```text
total_tokens
mandatory_tokens
history_tokens
reference_tokens
tool_output_tokens
estimated_output_tokens
available_budget
budget_utilization
```

---

## Structural Metrics

```text
duplicate_content_ratio
stale_content_ratio
optional_content_ratio
reference_count
tool_output_count
history_depth
```

---

## Quality Metrics

```text
instruction_coverage
constraint_coverage
reference_relevance
context_density
retrieval_precision
```

These metrics should be described as measurements or proxies.

Do not claim that a heuristic metric directly measures model reasoning quality unless it has been empirically validated for that purpose.

---

# 21. Instruction Coverage

Instruction coverage should answer:

> Are the requirements necessary to perform the current task still present and findable?

A useful report can contain:

```yaml
instruction_coverage:
  required: 12
  present: 12
  missing: 0
  coverage: 1.0
```

This is a **findability/presence metric**, not a guarantee that the model will follow every instruction.

A context can have:

```text
100% instruction presence
```

while still producing an incorrect result.

---

# 22. Context Density

A practical heuristic:

```text
Context Density =
relevant information tokens
/
total context tokens
```

This should be treated as an estimate.

For example:

```yaml
context_density:
  value: 0.72
  method: heuristic
```

A higher density is not automatically better if important context has been removed.

The correct objective is:

```text
high useful density
+
complete critical requirements
```

---

# 23. Repetition Detection

Repeated content consumes budget without necessarily adding information.

Useful signals include:

* exact duplicate blocks,
* near-duplicate instructions,
* repeated tool output,
* repeated documentation,
* repeated examples.

A repetition detector should report:

```yaml
repetition:
  duplicate_blocks: 4
  estimated_duplicate_tokens: 3200
  method: exact
```

Near-duplicate detection should be clearly labelled as approximate.

---

# 24. Staleness Detection

Context should be evaluated for information that has been superseded.

Examples:

```text
old API version
old configuration
old project decision
obsolete file path
previous requirement
```

A stale-content metric should not assume that older information is always useless.

Instead, classify it as:

```text
current
potentially stale
superseded
unknown
```

Preserve historical information when it is explicitly required for understanding the current state.

---

# 25. Context Rebuild Procedure

When a context audit identifies problems, rebuild the context in this order:

```text
1. Preserve the current objective
2. Preserve explicit constraints
3. Preserve safety/operational requirements
4. Preserve required project state
5. Remove exact duplicates
6. Remove superseded information
7. Compress historical context
8. Retrieve only required references
9. Reduce optional context
10. Recalculate the budget
11. Verify critical instructions
12. Execute
```

This provides a deterministic relationship between the audit and rebuild stages of the Context Engineering workflow.

---

# 26. Anti-Patterns

## Anti-pattern 1 — Fill the context window

```text
"If the model supports 1M tokens, use 1M tokens."
```

Why it is problematic:

* increases cost,
* increases irrelevant material,
* complicates retrieval,
* may reduce information density,
* creates unnecessary processing.

---

## Anti-pattern 2 — Fixed percentage allocation

```text
"Always allocate 30% to history."
```

Why it is problematic:

Tasks have different context requirements.

Use dynamic allocation instead.

---

## Anti-pattern 3 — Load every reference

```text
SKILL.md
+
all references
+
all examples
+
all templates
```

Why it is problematic:

It defeats progressive disclosure.

---

## Anti-pattern 4 — Treat token estimates as exact

```text
Estimated tokens = 32,400
```

without specifying the estimation method.

Instead:

```text
Estimated tokens = 32,400
Method = heuristic
Confidence = low
```

---

## Anti-pattern 5 — Compress critical instructions

Reducing tokens by removing constraints is not optimization.

The result may be shorter but incorrect.

---

## Anti-pattern 6 — Preserve entire conversation history

Historical context should preserve task state, decisions, and relevant constraints—not necessarily every previous message.

---

## Anti-pattern 7 — Assume larger context means better reasoning

Context capacity describes how much information can be supplied.

It does not establish that every additional token will improve task performance.

---

# 27. Hermes Skill Design Guidelines

When this framework is implemented as a Hermes skill:

### Keep `SKILL.md` concise

The main skill should contain:

* the workflow,
* decision rules,
* critical constraints,
* commands,
* links to relevant references.

### Keep detailed token theory here

This file belongs in:

```text
references/token-budget-framework.md
```

and should be loaded when detailed budget analysis is required.

### Avoid duplicating this document in `SKILL.md`

The main skill should point to this reference rather than reproduce it.

For example:

```text
For detailed token-budget allocation and context compression rules,
load:

skill_view("context-engineering", "references/token-budget-framework.md")
```

### Keep scripts separate from conceptual guidance

Use:

```text
scripts/token_estimator.py
```

for computation.

Use this reference for:

```text
why
what
when
how to interpret the results
```

---

# 28. Runtime-Aware Implementation

The framework should prefer runtime-provided information.

Recommended precedence:

```text
1. Runtime-measured value
2. Provider/model metadata
3. Tokenizer-based calculation
4. Approximate calculation
5. Heuristic estimate
6. Unknown
```

Never replace a known runtime value with a weaker estimate.

---

# 29. Configuration Principles

Budget configuration should support:

```yaml
context:
  model_context_window: auto

  output_reserve: auto

  safety_margin: auto

  history:
    max_tokens: auto

  retrieval:
    max_tokens: auto

  tool_output:
    max_tokens: auto
```

The implementation should allow task-specific overrides.

For example:

```yaml
task_profiles:
  coding:
    output_reserve: auto
    retrieval: high

  summarization:
    output_reserve: high
    history: high

  classification:
    output_reserve: low
    retrieval: low
```

These are configuration examples, not mandatory defaults.

---

# 30. Verification Checklist

Before execution:

```text
[ ] Context capacity is known or explicitly marked unknown
[ ] Runtime overhead is measured or estimated
[ ] Output capacity is reserved
[ ] Safety margin is applied
[ ] Mandatory requirements are present
[ ] Critical constraints are present
[ ] Required references are loaded
[ ] Irrelevant history has been reduced
[ ] Duplicate content has been removed
[ ] Tool output has been bounded
[ ] Token estimates identify their method
[ ] Context is within the calculated working budget
```

After execution:

```text
[ ] Output was not truncated
[ ] Critical requirements were addressed
[ ] Retrieved evidence was actually used where required
[ ] Unexpected context growth is recorded
[ ] Budget estimates can be improved for future runs
```

---

# 31. Relationship to the Context Engineering Lifecycle

This framework supports the five-stage workflow:

```text
AUDIT
  ↓
measure context composition
  ↓
CLASSIFY
  ↓
identify mandatory / relevant / optional / stale content
  ↓
FIX
  ↓
remove duplication and unnecessary material
  ↓
REBUILD
  ↓
construct a task-specific context within budget
  ↓
VERIFY
  ↓
measure budget and requirement coverage
```

Token management is therefore not a one-time optimization.

It is a continuous context-management process.

---

# 32. Final Principle

The correct question is not:

> "How much context can the model handle?"

The better question is:

> "What is the smallest set of accurate, relevant, findable information required to complete this task reliably?"

A production context-management system should therefore optimize:

```text
correctness
+
relevance
+
completeness
+
findability
+
freshness
+
budget efficiency
```

rather than token count alone.

The target is not the largest context.

The target is the **most useful context for the task**.
