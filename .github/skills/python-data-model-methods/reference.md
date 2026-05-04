# Reference Overview

This folder provides focused guidance on foundational Python data-model methods
for ordinary classes. The reference is split into topic files so equality/hash
rules, representation semantics, and container behavior stay portable and easy
to navigate.

Examples in this skill use Python 3.10+ typing syntax to match the repository's
current Python baseline.

## Reference Files

| File | Role |
| --- | --- |
| **construction-and-representation.md** | `__init__`, `__repr__`, `__str__`, and `__bool__` guidance for explicit semantics and diagnostics |
| **equality-hash-and-dataclass.md** | linked `__eq__` / `__hash__` safety rules plus `@dataclass` generation boundaries |
| **container-protocols.md** | when base container protocols declare real collection-like meaning and when they overreach |

## When to Use Each File

- **Unsure what belongs in `__init__` or `__repr__`?** →
  **construction-and-representation.md**
- **Reviewing equality, hashing, or dataclass-generated behavior?** →
  **equality-hash-and-dataclass.md**
- **Unsure whether a class should act like a container?** →
  **container-protocols.md**

## Quick Navigation

1. Read **SKILL.md** first for trigger, process, and boundaries.
2. Use **construction-and-representation.md** to lock the class's basic semantic
   shape.
3. Use **equality-hash-and-dataclass.md** to verify value semantics and hashing
   safety.
4. Use **container-protocols.md** when deciding whether the class should expose
   sequence- or collection-like behavior.
5. Use **examples.md** for concrete scenarios, anti-patterns, and split signals.
