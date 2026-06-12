# Equality, Hashing, and Dataclass Boundaries

This file covers `__eq__`, `__hash__`, and the boundary between generated and
manual dunder behavior in `@dataclass`.

## `__eq__`

**Mainline rule**: Define `__eq__` only when value-based comparison is part of
the type's meaning.

- Use it for value objects where two instances with the same meaningful fields
  should compare equal.
- Leave identity-based behavior alone for service objects, stateful controllers,
  or entities whose identity matters more than field equality.

**Why this rule**: Equality changes how instances behave in tests, collections,
and business rules. It is a semantic commitment, not a convenience feature.

## `__hash__`

**Mainline rule**: Review `__hash__` together with `__eq__`.

- If objects compare by value and are immutable, hashing may be appropriate.
- If objects are mutable, default away from hashing unless mutation cannot break
  hash stability.
- If you disable or override equality, make the hash outcome explicit too.

**Why this rule**: Hash-based collections assume equality and hash stability are
compatible. A mutable hashable value object is a common silent bug source.

**Anti-pattern**:

```py
from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class UserFilter:
    tags: list[str]
```

`unsafe_hash=True` does not make mutation safe; it only suppresses the default
protection.

## `@dataclass` boundary

**Mainline rule**: Accept generated behavior only when it matches the intended
semantics.

- Generated `__repr__` is often fine for transparent data carriers.
- Generated `__eq__` is appropriate when all compared fields are truly part of
  value identity.
- Generated hash behavior must still be reviewed against mutability and set/dict
  usage.
- Override or disable generated behavior when hidden fields, caches, mutable
  state, or domain identity make the defaults misleading.

**Why this rule**: `@dataclass` reduces boilerplate, but it does not decide the
meaning of equality, hashing, or diagnostics for you.

## Safe defaults

- Prefer `@dataclass(frozen=True)` when value semantics and hashing are both
  intended.
- Prefer a plain `@dataclass` with explicit hash disabled when mutation is
  intentional.
- Prefer manual methods when the class must hide internal fields or when
  equality uses a subset of attributes.

If the real question is whether the type should be a `dataclass` at all, hand
off to `python-model-selection`.
