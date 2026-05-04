---
name: python-context-management
description: Choose and design synchronous Python context managers for resource lifetime and temporary state restoration. Use this when drafting or reviewing `with` usage, `@contextmanager` versus class-based design, setup/cleanup failure handling, and ambient-state restoration.
---

# Purpose
Guide the choice and design of synchronous Python context managers for resource
lifetime management and temporary state restoration.

# Trigger / When to use
Use this skill when:
- Deciding whether to use `with`, `@contextmanager`, or a class-based
  `__enter__` / `__exit__` manager.
- Designing a custom context manager that must handle acquisition, cleanup,
  rollback, or ambient-state restoration.
- Reviewing code that uses manual `close()` and deciding if `with` is more
  appropriate.
- Connecting setup or cleanup failures to the existing semantic error model.
- Using `ExitStack` for dynamic or multi-resource cleanup.

Do not use this skill when:
- The resource involves `async with`, `async for`, or cancellation patterns.
- The task is generic dependency injection, bootstrap, or runtime
  orchestration.
- The task is pytest fixture design beyond lifetime discipline compatibility.
- The task is decorator-driven implicit lifetime management (`ContextDecorator`
  dual-use).

# Inputs
- The resource or state being managed (file, lock, connection, cwd, env var, etc.).
- Whether acquisition is stateful, multi-step, or failure-prone.
- Whether the resource must be cleaned up on both normal and error paths.
- Whether ambient state must be fully restored after the block.
- Whether the manager may be reused across multiple `with` invocations.

# Process
1. **Lifetime scope** — Does the lifetime fit one block and does the object
   support the protocol? Default to `with`. If the lifetime genuinely crosses
   function boundaries, allow manual `close()` paired with `finally`.
2. **Manager form** — Is the flow stateless and single-path? Use
   `@contextmanager`. Does it need internal state, multiple cooperating
   methods, or richer exception translation? Use a class-based manager with
   `__enter__` / `__exit__`.
3. **Acquisition placement** — Effectful or failure-prone acquisition belongs
   in `__enter__`, not `__init__`. `__enter__` returns the resource or facade,
   not `self` unless the manager is the resource.
4. **Cleanup and error policy** — Do not suppress exceptions by default.
   If cleanup fails while a primary error is active, log it and let the
   original propagate; do not replace it. Translate known errors with
   `raise X from Y`; propagate unknowns untouched.
5. **Advanced patterns** — Use `ExitStack` for dynamic resource sets or
   partial-acquisition rollback only. Ambient-state managers must restore prior
   state in `finally`. Treat instances as one-shot unless reuse is explicit.

# Examples
- Positive: `with open(path) as f:` — the protocol handles `close()` even on
  exceptions; no manual cleanup needed.
- Negative: `f = open(path)` followed by `try: ... finally: f.close()` when
  the lifetime fits a block and `with` is supported — the manual pattern adds
  noise and is error-prone.

# Outputs
- Decision: `with`, `@contextmanager`, or class-based manager, with clear
  rationale.
- Correct acquisition, cleanup, and error-handling code.
- Guidance on suppression policy, cause chaining, and cleanup-failure
  handling.
- `ExitStack` usage when dynamic or multi-resource cleanup is needed.

# Boundaries
- Do not cover: `async with` / cancellation, dependency injection /
  orchestration, pytest fixture design, or `ContextDecorator` dual-use.
  Hand off to specialized skills instead.

# Local references
- `examples.md`: detailed positive and negative patterns covering all
  multi-path decisions — `@contextmanager` versus class-based choice, cleanup
  failure handling, exception suppression, `ExitStack`, ambient-state
  restoration, and one-shot behavior.
