# Python model-selection examples

Use these examples after `SKILL.md` narrows the question to general Python construct choice.

## `dataclass`

### Use
```py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

- Prefer `frozen=True` when instances should not mutate.
- Use plain `@dataclass` only when state changes are an intentional part of the design.

### Avoid
```py
from dataclasses import dataclass

@dataclass
class EmailSender:
    smtp_client: object

    def send(self, message: str) -> None:
        ...
```

- Behavior-heavy service objects should usually stay plain classes.
- Tiny throwaway payloads do not always need a `dataclass`.
- `slots=True`, `kw_only=True`, `default_factory`, and `__post_init__` stay at examples-level detail, not the core selection rule.

## `Enum`

### Use
```py
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
```

- Use `Enum` for closed named states or symbolic choices.
- If semantics matter or future expansion is plausible, prefer `Enum`.

### Edge note
- Keep a plain `bool` for a truly tiny binary state.
- Upgrade to `Enum` when names matter more than brevity or when the state may grow.
- Leave `Literal` guidance to `python-type-hints-strict`.

## `ABC` vs `Protocol`

### Choose `ABC`
```py
from abc import ABC, abstractmethod
from typing_extensions import override

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None:
        ...

    def has_key(self, key: str) -> bool:
        return self.get(key) is not None

class RedisCacheBackend(CacheBackend):
    @override
    def get(self, key: str) -> str | None:
        return None
```

- Use `ABC` for an explicit nominal contract.
- Use it when shared base behavior or `super()` participation matters.
- Default to `ABC` when both `ABC` and `Protocol` seem equally valid.

### Choose `Protocol`
```py
from typing import Protocol

class SupportsRender(Protocol):
    def render(self) -> str:
        ...

def render_to_html(obj: SupportsRender) -> str:
    return obj.render()
```

- Use `Protocol` when structural compatibility is the real goal.
- Use it when unrelated or third-party classes just need the same shape.
- Do not pick `Protocol` only because it looks lighter if the design really wants one owned contract.

### Edge note
- If abstraction pressure comes from architecture-specific rules rather than general Python modeling, keep that decision outside this skill.

## None of the above

- A plain class may be enough when behavior is the center of the object.
- A local tuple or dict may be enough for short-lived internal glue code.
- Do not add abstraction only to make the design look more formal.

## Split signals

Stop and hand off to a future follow-up skill when the main question becomes:

- which framework model or validation tool to use
- how to model schema or serialization boundaries
- how to choose between ecosystem-specific constructs rather than Python core constructs

## Out of scope for now

- `NamedTuple`
- `TypedDict`
- framework-specific model classes
