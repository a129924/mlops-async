---
name: python-naming
description: Define or normalize Python naming conventions for identifiers, files, folders, and visibility boundaries. Use this when drafting or reviewing Python code style rules centered on names.
complexity: low
risk_profile: []
inputs:
  - the Python surfaces being named
  - any existing repository naming policy
  - explicit exceptions, if they already exist
outputs:
  - a single-purpose naming rule set or skill draft
  - explicit allowed and disallowed naming patterns
  - a local reference file with examples and edge cases
use_when:
  - a project needs Python naming rules
  - code review or scaffolding must choose compliant names
  - a draft guideline mixes naming cases or visibility signals
do_not_use_when:
  - the question is mainly about type strictness or pyright rules
  - the task is to choose between Enum, dataclass, ABC, or Protocol
---

# Purpose
Define one consistent naming contract for Python code.

# Trigger / When to use
Use this skill when:
- a project needs Python naming rules
- code review or scaffolding must choose compliant names
- a draft guideline mixes naming cases or visibility signals

Do not use this skill when:
- the question is mainly about type strictness or pyright rules
- the task is to choose between `Enum`, `dataclass`, `ABC`, or `Protocol`

# Inputs
- the Python surfaces being named
- any existing repository naming policy
- explicit exceptions, if they already exist

# Process
1. Read the repository policy and extract naming rules only.
2. Map each code surface to one naming form and one visibility rule.
3. Reject mixed conventions that leave multiple valid names for the same job.
4. Put stable detail and edge cases in `reference.md`.
5. Stop at a review-ready naming rule set or skill draft.

# Examples
- Positive: Draft rules that keep modules in `snake_case`, classes in `PascalCase`, constants in `UPPER_CASE`, and internal helpers with a single leading underscore.
- Negative: Produce one rule set that mixes `camelCase`, `PascalCase`, and `snake_case` for functions or treats visibility as optional.

# Outputs
- a single-purpose naming rule set or skill draft
- explicit allowed and disallowed naming patterns
- a local reference file with examples and edge cases

# Boundaries
- Do not define strict typing policy, control-flow policy, or model-selection rules.
- Do not create new exceptions unless the repository already requires them.
- Do not rely on unstated style guides outside this skill folder.

# Local references
- `reference.md`: naming matrix, approved examples, and edge-case guidance
