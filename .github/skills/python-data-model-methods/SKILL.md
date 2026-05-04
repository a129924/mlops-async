---
name: python-data-model-methods
description: Choose clear Python data-model methods. Use this when deciding whether an ordinary class should define foundational dunder methods, expose base container protocols, or rely on dataclass-generated behavior.
---

# Purpose

Choose when an ordinary Python class should implement foundational dunder
methods and base container protocols, and keep those choices semantically
explicit, safe, and easy to review.

# Trigger / When to use

Use this skill when:
- deciding whether a class should define `__repr__`, `__str__`, `__eq__`,
  `__hash__`, or `__bool__`
- deciding whether a class should behave like a container through `__len__`,
  `__getitem__`, `__contains__`, or `__iter__`
- reviewing whether `@dataclass`-generated dunders are sufficient or should be
  overridden
- checking whether equality, hashing, or truthiness semantics match the real
  domain meaning of an object
- reviewing ordinary Python classes whose dunder behavior is starting to feel
  accidental or inconsistent

Do not use this skill when:
- the main decision is whether the type should be a `dataclass`, `ABC`,
  `Protocol`, or `Enum`; use `python-model-selection`
- the main task is broad class public-surface design or constructor/factory
  design; use `python-class-design`
- the main task is iterator strategy, exhaustion, generator choice, or custom
  iterator design; use `python-generators-iterators`
- the main task is async protocols such as `__aiter__` or `__anext__`; use
  `python-async-await`
- the main task is operator overloading or descriptor behavior

# Inputs

- what the object represents in the domain
- whether the object is mutable or immutable
- whether the object should compare by identity or by value
- whether the object should be hashable and where it will be stored
- whether the object truly behaves like a collection or sequence
- whether `@dataclass` is generating any relevant dunder methods already
- whether callers need developer diagnostics, user-facing text, or explicit
  truth semantics

# Process

1. **Start from omission, not decoration** — Do not add dunder methods just
   because Python allows them. Define one only when it expresses real object
   semantics that callers should be able to rely on.
2. **Keep `__init__` on final object state** — Use `__init__` to accept final
   inputs, do cheap invariant checks, and assign attributes. If creation needs
   heavy parsing or named intent, keep that design pressure with
   `python-class-design` instead of burying it in data-model rules.
3. **Treat `__repr__` as diagnostics first** — Make `__repr__` useful to a
   developer reading logs, traces, or a debugger. Add `__str__` only when
   user-facing text is materially different from diagnostic representation.
4. **Treat `__eq__` and `__hash__` as one safety decision** — If objects compare
   by value, decide explicitly whether hashing remains valid. Mutable value
   objects often should not be hashable. Do not let generated or inherited hash
   behavior slip through unreviewed.
5. **Define `__bool__` only for substantive truth semantics** — Use `__bool__`
   when the object has a real empty/present, usable/unusable, or valid/invalid
   meaning. Do not add it for cosmetic readability when ordinary object truth
   would be clearer.
6. **Use container protocols as semantic declarations** — Implement `__len__`,
   `__getitem__`, `__contains__`, or `__iter__` only when the object truly acts
   like a collection. Do not bolt on container behavior just to make loops or
   membership tests shorter.
7. **Audit `@dataclass` output explicitly** — Accept generated `__repr__`,
   `__eq__`, and hash behavior only when they match the intended semantics.
   Override or disable them when mutability, hidden fields, or domain meaning
   requires clearer control.

# Examples

- Positive: Give a value object a diagnostic `__repr__`, value-based `__eq__`,
  and explicit no-hash decision because the object mutates after creation.
- Positive: Add `__iter__` and `__len__` to a domain collection whose primary
  meaning is "a collection of items", while handing deeper iteration strategy to
  `python-generators-iterators`.
- Negative: Add `__str__`, `__bool__`, and `__contains__` just to make the class
  feel more Pythonic when none of those methods express real domain semantics.
- Negative: Keep `@dataclass`-generated equality and hashing on a mutable object
  without checking whether it can safely live in sets or dict keys.

# Outputs

- a decision on which foundational dunder methods should exist and why
- a safe equality / hashing stance for the class
- a decision on whether the class should expose base container protocols
- a clear boundary on when `@dataclass` generation is sufficient versus risky

# Verification

- `__repr__` exposes developer-meaningful diagnostics instead of generic noise
- `__str__` exists only when it adds a real user-facing view beyond `__repr__`
- `__eq__` and `__hash__` were reviewed together, especially for mutable objects
- `__bool__` reflects real truth semantics, not a cosmetic shortcut
- container protocols describe what the object is, not just how callers want to
  loop over it
- any `@dataclass`-generated dunder behavior was accepted or overridden
  deliberately

# Red Flags

- `__repr__` only echoes the class name or hides the fields a developer needs
- a mutable object remains hashable without explicit justification
- `__bool__` means "has a name" or some other cosmetic convenience instead of a
  substantive state
- `__iter__` or `__getitem__` appears on a class that is not semantically a
  collection
- `@dataclass` generation is accepted by default without checking equality/hash
  consequences

# Common Rationalizations

- "Dataclass already generated it, so it must be fine."
- "Adding `__bool__` makes the API nicer."
- "Every custom class should have a custom `__str__`."
- "If membership testing is handy, the class should probably implement
  `__contains__`."
- "Hashing is okay because we rarely mutate this object."

# Boundaries

- Do not define general class-shape or factory rules; use `python-class-design`.
- Do not define construct-selection rules for `dataclass`, `ABC`, or `Protocol`;
  use `python-model-selection`.
- Do not define generator, exhaustion, or custom iterator strategy rules; use
  `python-generators-iterators`.
- Do not define async protocol behavior such as `__aiter__` or `__anext__`; use
  `python-async-await`.
- Do not define operator-overloading or descriptor policy.

# Local references

- `reference.md`: focused overview and navigation entry for this skill's local
  reference layer
- `references/construction-and-representation.md`: `__init__`, `__repr__`,
  `__str__`, and `__bool__` guidance
- `references/equality-hash-and-dataclass.md`: equality / hashing safety rules
  and `@dataclass` boundary guidance
- `references/container-protocols.md`: when `__len__`, `__getitem__`,
  `__contains__`, and `__iter__` express real container semantics
- `examples.md`: detailed scenarios, anti-patterns, and split signals for major
  decision paths
