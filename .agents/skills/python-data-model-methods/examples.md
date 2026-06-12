# Python Data Model Methods Examples

This file covers representative scenarios, anti-patterns, and split signals for
choosing foundational data-model methods and base container protocols.

Examples in this skill use Python 3.10+ typing syntax to match the repository's
current Python baseline.

## Scenario A: `__repr__` versus `__str__`

**Good**: Diagnostic `__repr__`, user-facing `__str__`

```py
class Invoice:
    def __init__(self, invoice_id: str, total_cents: int) -> None:
        self.invoice_id = invoice_id
        self.total_cents = total_cents

    def __repr__(self) -> str:
        return f"Invoice(invoice_id={self.invoice_id!r}, total_cents={self.total_cents})"

    def __str__(self) -> str:
        return f"Invoice {self.invoice_id} (${self.total_cents / 100:.2f})"
```

**Good**: Let `str(obj)` fall back when diagnostics are enough

```py
class Money:
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency!r})"
```

**Anti-pattern**: Placeholder representation

```py
class Money:
    def __repr__(self) -> str:
        return "<Money object>"
```

## Scenario B: `@dataclass` with safe generated behavior

**Good**: Frozen value object with generated equality and hash

```py
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

**Why this works**:
- value semantics are intentional
- fields are immutable
- generated `__repr__`, `__eq__`, and hash behavior match the type meaning

## Scenario C: Mutable dataclass with risky hashing

**Anti-pattern**: Forcing hash on mutable state

```py
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class SearchFilter:
    tags: list[str]
    limit: int
```

If `tags` changes after the object is used as a key, hash-based collections can
silently break.

**Better**: Keep equality but no hash

```py
from dataclasses import dataclass


@dataclass
class SearchFilter:
    tags: list[str]
    limit: int
```

## Scenario D: Manual equality when domain identity is selective

**Good**: Explicit value identity on meaningful fields only

```py
class CatalogItem:
    def __init__(self, sku: str, name: str, cached_label: str) -> None:
        self.sku = sku
        self.name = name
        self.cached_label = cached_label

    def __repr__(self) -> str:
        return f"CatalogItem(sku={self.sku!r}, name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CatalogItem):
            return NotImplemented
        return (self.sku, self.name) == (other.sku, other.name)
```

**Split signal**:
- if all fields are meaningful and immutable, generated dataclass equality may
  be enough
- if some fields are caches, transport detail, or operational state, manual
  equality is usually clearer

## Scenario E: `__bool__` for substantive emptiness

**Good**: Truthiness matches real domain meaning

```py
class ValidationErrors:
    def __init__(self, messages: list[str]) -> None:
        self._messages = messages

    def __len__(self) -> int:
        return len(self._messages)
```

Here no separate `__bool__` is needed; emptiness already has a natural meaning.

**Good**: Explicit truth semantics when length is not the right model

```py
class AuthResult:
    def __init__(self, token: str | None) -> None:
        self.token = token

    def __bool__(self) -> bool:
        return self.token is not None
```

**Anti-pattern**: Cosmetic truthiness

```py
class User:
    def __init__(self, name: str) -> None:
        self.name = name

    def __bool__(self) -> bool:
        return bool(self.name)
```

This makes control flow depend on display data rather than on the object's real
status.

## Scenario F: Container protocols as semantic declaration

**Good**: Domain collection behaves like a collection

```py
class OrderLines:
    def __init__(self, lines: list[str]) -> None:
        self._lines = list(lines)

    def __len__(self) -> int:
        return len(self._lines)

    def __contains__(self, item: object) -> bool:
        return item in self._lines

    def __iter__(self):
        return iter(self._lines)
```

The type's primary meaning is "a collection of order lines", so base container
protocols fit naturally.

**Anti-pattern**: Service object pretending to be a container

```py
class ReportService:
    def __init__(self, reports: list[str]) -> None:
        self._reports = reports

    def __iter__(self):
        return iter(self._reports)
```

If the object is really a service, iteration leaks implementation detail and
confuses the public meaning.

## Scenario G: `__getitem__` only when indexing is part of the contract

**Good**: Read-only indexed access is intentional

```py
class Leaderboard:
    def __init__(self, entries: list[str]) -> None:
        self._entries = list(entries)

    def __getitem__(self, index: int) -> str:
        return self._entries[index]
```

**Anti-pattern**: Indexing added because internal storage is a list

```py
class ImportJob:
    def __init__(self, staged_files: list[str]) -> None:
        self._staged_files = staged_files

    def __getitem__(self, index: int) -> str:
        return self._staged_files[index]
```

If callers should not think of the job as a sequence, expose a semantic method
instead.

## Scenario H: `__init__` boundary versus factory pressure

**Better**: Constructor accepts final values

```py
class CustomerId:
    def __init__(self, value: str) -> None:
        self.value = value
```

**Anti-pattern**: Parsing and orchestration hidden in `__init__`

```py
class CustomerId:
    def __init__(self, payload: dict[str, object]) -> None:
        raw = str(payload["customer_id"]).strip().upper()
        self.value = raw.removeprefix("CUST-")
```

When creation logic becomes named or parsing-heavy, hand off to
`python-class-design` for factory guidance.

## Scenario I: `__iter__` boundary to generators skill

**Good**: Simple iteration declaration

```py
class Batch:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)

    def __iter__(self):
        return iter(self._items)
```

**Split signal**:
- stay in this skill when the question is whether the class should be iterable
  at all
- hand off to `python-generators-iterators` when the question becomes reset
  semantics, lazy production, custom iterator state, or generator choice

## Anti-pattern Summary

| Pattern | Why it fails |
| --- | --- |
| Placeholder `__repr__` | removes diagnostic value |
| Hashable mutable value object | breaks equality/hash safety |
| Cosmetic `__bool__` | hides real truth semantics |
| Container methods on non-containers | misrepresents object meaning |
| Blind trust in generated dataclass dunders | accepts semantics without review |
