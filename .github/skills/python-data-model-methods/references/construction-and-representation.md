# Construction and Representation

This file covers `__init__`, `__repr__`, `__str__`, and `__bool__` for ordinary
Python classes.

## `__init__`

**Mainline rule**: Keep `__init__` focused on final object state.

- Accept already-meaningful inputs.
- Perform cheap invariant checks.
- Assign instance attributes deliberately.
- Do not turn `__init__` into a parsing pipeline, hidden factory, or
  environment-dependent setup hook.

**Why this rule**: The constructor should make object state explicit. Heavy
creation logic belongs with clearer construction APIs, not hidden inside
data-model semantics.

**Anti-pattern**:

```py
class UserReport:
    def __init__(self, payload: dict[str, object]) -> None:
        self.user_id = int(payload["user_id"])
        self.name = str(payload["name"]).strip().title()
        self.start_network_session()
```

## `__repr__`

**Mainline rule**: `__repr__` is for developer diagnostics.

- Show the fields or identifiers a developer needs to understand the instance.
- Prefer unambiguous values over friendly prose.
- Keep it cheap and deterministic.

**Why this rule**: `__repr__` appears in logs, tracebacks, debuggers, and test
failures. It should help a developer identify what object they are looking at.

**Anti-pattern**:

```py
class Money:
    def __repr__(self) -> str:
        return "<Money object>"
```

## `__str__`

**Mainline rule**: Add `__str__` only when user-facing text is materially
different from `__repr__`.

- If `__repr__` is already readable and useful, let `str(obj)` fall back to it.
- Use `__str__` for display-oriented text, not for a second diagnostic channel.

**Why this rule**: Two text forms create maintenance cost. Keep both only when
they serve different audiences.

## `__bool__`

**Mainline rule**: Define `__bool__` only for substantive truth semantics.

- Use it when the object has a real empty/present or valid/invalid meaning.
- Prefer `__len__`-driven truthiness for genuine containers.
- Omit it when the object is just "an object that exists."

**Why this rule**: Truthiness influences control flow everywhere. Cosmetic
truthiness hides meaning and makes reviews harder.

**Anti-pattern**:

```py
class User:
    def __bool__(self) -> bool:
        return bool(self.name)
```

If the important question is how the class should be shaped overall, or whether
construction should move to a named factory, hand off to `python-class-design`.
