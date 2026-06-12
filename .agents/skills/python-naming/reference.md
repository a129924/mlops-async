# Python naming reference

## Core matrix
| Surface | Preferred form | Notes |
| --- | --- | --- |
| variables, functions, methods, modules, directories | `snake_case` | default for runtime symbols and paths |
| classes, exceptions, protocols, enums | `PascalCase` | keep names noun-like and intention-revealing |
| constants | `UPPER_CASE` | use for stable module-level values |
| non-public helpers and attributes | `_single_leading_underscore` | internal-only signal |
| boolean flags | `is_*`, `has_*`, `can_*` | prefer predicate names |

## Default rules
- Use ASCII names and avoid mixed separators.
- Prefer whole words over unclear abbreviations.
- Keep file and folder names aligned with the responsibility they expose.
- Exception classes should end with `Error` when they model an error condition.

## Avoid
- `camelCase` functions or modules in normal Python code.
- Class names that hide verbs or implementation detail.
- Catch-all names such as `utils`, `helpers`, or `misc` when a specific noun fits better.
- Repository-specific exceptions unless the local policy names them explicitly.
