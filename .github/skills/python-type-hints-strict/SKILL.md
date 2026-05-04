---
name: python-type-hints-strict
description: Define or enforce Python type-hint rules for projects that run pyright in strict mode. Use this when drafting typing guidance or reviewing code against a strict typing baseline.
---

# Purpose
Define one strict typing contract for Python code that must pass `pyright --strict`.

# Trigger / When to use
Use this skill when:
- a project mandates `pyright --strict`
- code review must decide whether a typing pattern is acceptable
- a coding standard needs a strict type-hint section

Do not use this skill when:
- the task is only about naming conventions
- the task mainly chooses runtime models or control-flow style

# Inputs
- the Python version and typing baseline
- any allowed escape hatches
- repository policy or examples that already constrain typing

# Process
1. Start from `pyright --strict` as the default baseline.
2. Require explicit parameter and return annotations on public functions and methods.
3. Match syntax to the supported Python version: for Python 3.10+ prefer `User | None`; for Python 3.9+ prefer `list[str]`; for Python 3.8/3.9 compatibility use `Optional[User]`, `Union[...]`, and `List[str]` where needed.
4. Limit `Any`, `cast`, and ignore comments to explicit, justified edge cases.
5. Put reusable compatibility notes and escape-hatch rules in `reference.md`, and put version-path examples and anti-patterns in `examples.md`.

# Examples
- Positive: Require version-appropriate strict annotations (for example, `User | None` and `list[str]` on Python 3.10+, or `Optional[User]` and `List[str]` on Python 3.8/3.9); use a named alias when supported by the baseline and helpful for repeated complex types.
- Negative: Allow implicit `Any`, untyped public APIs, or routine ignore comments with no justification.

# Outputs
- a review-ready strict typing rule set or skill draft
- explicit allowed and disallowed typing patterns
- local reference files for compatibility rules, edge cases, and anti-patterns

# Boundaries
- Do not choose between `Enum`, `dataclass`, `ABC`, or `Protocol`.
- Do not define naming policy or branch-selection rules.
- Do not relax strict typing without an explicit repository-level exception.

# Local references
- `reference.md`: strict typing defaults, compatibility rules, and allowed exceptions
- `examples.md`: version-path examples and strict typing anti-patterns
