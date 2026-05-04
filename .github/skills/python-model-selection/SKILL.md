---
name: python-model-selection
description: Choose the right general-purpose Python construct for structured data and contracts. Use this when drafting or reviewing whether code should use Enum, dataclass, ABC, or Protocol.
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

# Local references
- `examples.md`: construct-based examples, anti-patterns, edge notes, and split signals
