# Container Protocols

This file covers `__len__`, `__getitem__`, `__contains__`, and `__iter__` as
base container behavior declarations.

## Mainline rule

Implement base container protocols only when the object truly behaves like a
collection, sequence, or membership-bearing container in the domain.

- Use `__len__` when object size or emptiness is a real semantic property.
- Use `__getitem__` when positional or key-based access is part of the public
  meaning of the type.
- Use `__contains__` when membership reads naturally and correctly.
- Use `__iter__` when iterating over contained items is a normal primary use.

**Why this rule**: These methods are not just ergonomic helpers. They tell
callers what kind of thing the object is.

## Good uses

- A `DomainCollection` that owns a list of domain items and should support
  iteration, length, and membership naturally.
- A read-only view object whose main purpose is indexed access over contained
  elements.

## Anti-patterns

- Add `__iter__` to a service object only because it internally stores a list.
- Add `__contains__` because `if x in obj` reads nicely even though membership is
  not a core semantic operation.
- Add `__getitem__` to expose implementation detail instead of an intentional
  public contract.

## `__iter__` boundary

Treat `__iter__` here as a behavior declaration only.

- If the next question becomes generator design, exhaustion, reset semantics, or
  custom iterator strategy, hand off to `python-generators-iterators`.
- If iteration would involve async I/O or async protocols, hand off to
  `python-async-await`.

## Truthiness note

For true containers, `__len__` often supplies the right truth semantics without
needing a separate `__bool__`. Prefer the simpler model when it already matches
the domain meaning.
