---
name: python-model-selection
description: Choose the right general-purpose Python construct for structured data and contracts. Use this when drafting or reviewing whether code should use Enum, dataclass, ABC, or Protocol.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - the object or contract being modeled
  - whether the value set is closed or open
  - whether the design needs shared base behavior, nominal inheritance, or duck typing
  - whether mutation is intentional
outputs:
  - a review-ready model-selection rule set or skill draft
  - a construct-selection matrix with positive and negative patterns
  - local examples for normal cases and edge cases
use_when:
  - code review or design work must choose between Enum, dataclass, ABC, and Protocol
  - a draft mixes plain classes, ad-hoc constants, and abstract interfaces without clear criteria
  - a project wants general Python model-selection rules
do_not_use_when:
  - the main question is about type-hint syntax or pyright strictness
  - the main question is about if/elif, match/case, or other control-flow style
  - the main question is about a framework or schema-validation tool
---

# Purpose
Choose one Python modeling construct for the job without drifting into framework or architecture policy.

# Trigger / When to use
Use this skill when:
- code review or design work must choose between `Enum`, `dataclass`, `ABC`, and `Protocol`
- a draft mixes plain classes, ad-hoc constants, and abstract interfaces without clear criteria
- a project wants general Python model-selection rules

Do not use this skill when:
- the main question is about type-hint syntax or pyright strictness
- the main question is about `if/elif`, `match/case`, or other control-flow style
- the main question is about a framework or schema-validation tool

# Inputs
- the object or contract being modeled
- whether the value set is closed or open
- whether the design needs shared base behavior, nominal inheritance, or duck typing
- whether mutation is intentional

# Process
1. Check whether the right answer is actually no extra construct yet.
2. Choose `Enum` for closed symbolic values and named states.
3. Choose `dataclass` for structured in-memory data; prefer `frozen=True` unless mutation is intentional.
4. Choose `ABC` for explicit nominal contracts or shared base behavior; choose `Protocol` for structural compatibility.
5. Put branching examples, anti-patterns, edge notes, and split signals in `examples.md`.

# Examples
- Positive: Use `Enum` for named states, `@dataclass(frozen=True)` for immutable structured data, and `Protocol` only when unrelated classes just need the same callable shape.
- Negative: Force `ABC` before there is any contract pressure, use `dataclass` for a behavior-heavy service object, or turn a plain boolean flag into `Enum` without a semantic reason.

# Outputs
- a review-ready model-selection rule set or skill draft
- a construct-selection matrix with positive and negative patterns
- local examples for normal cases and edge cases

# Boundaries
- Do not define naming policy, type-hint syntax policy, or control-flow rules.
- Do not define framework-specific schema or validation choices.
- Do not turn architecture-specific interface patterns into a universal Python rule.

# Validation
Before proceeding, confirm:
- The task is about choosing between `Enum`, `dataclass`, `ABC`, or `Protocol`
- The object's mutation intent and value-set openness are known or can be inferred

**SOFT FAIL** — ask and wait before continuing:
- Whether mutation is intentional is unstated → ask before recommending `frozen=True` vs mutable `dataclass`
- Whether the value set is closed or open is unclear → ask before choosing `Enum` vs plain constants or `dataclass`

**BLOCKED** — stop and redirect:
- The main question is about type-hint syntax or pyright strictness → redirect to `python-type-hints-strict`
- The main question is about a framework-specific schema or validation tool → out of scope for this skill

# Failure Handling
- **Missing Context**: if mutation intent, value-set openness, or the object being modeled are unknown, ask once clearly before applying construct-selection defaults.
- **Ambiguous Requirement**: if the stated goal conflicts with model-selection scope (e.g., the task is really about control-flow style or framework validation), name the conflict and redirect.
- **Execution Limitation**: if the task involves framework-specific schema tools or architecture-specific interface patterns, stop and redirect to the appropriate skill.

# Local references
- `examples.md`: construct-based examples, anti-patterns, edge notes, and split signals
