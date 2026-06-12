# Python Context-Management Examples

Snippets assume these imports where applicable:

```py
import logging
import os
from contextlib import ExitStack, contextmanager
from types import TracebackType
```

---

## 1. Ordinary `with` over manual `close()`

**Positive — use `with`:**
```py
# Correct: protocol handles close on both normal and error exit
with open(path, "r") as f:
    data = f.read()
```

**Negative — manual close when `with` fits:**
```py
# Wrong: manual pattern adds noise and can miss close on some error paths
f = open(path, "r")
try:
    data = f.read()
finally:
    f.close()
```

---

## 2. Narrow legitimate manual-cleanup exception

Manual `close()` is allowed only when the resource lifetime genuinely crosses
function boundaries and a `with` block cannot contain it. This is a deliberate
exception to the default `with`-first rule.

Note: `StreamHandler` below does **not** implement the context-manager
protocol, so the rule "effectful acquisition belongs in `__enter__`, not
`__init__`" does not apply here — that rule governs classes that implement
`__enter__` and `__exit__`.

```py
# Acceptable: lifetime spans __init__ and close(), not one block
class StreamHandler:
    def __init__(self, path: str) -> None:
        self._file = open(path, "rb")

    def read_chunk(self) -> bytes:
        return self._file.read(4096)

    def close(self) -> None:
        self._file.close()
```

Always pair cross-boundary lifetime with explicit cleanup in `finally` at the
call site:

```py
handler = StreamHandler(path)
try:
    process(handler)
finally:
    handler.close()
```

**Anti-pattern:** Using cross-boundary lifetime when a single `with` block
would cleanly contain the lifetime.

---

## 3. `@contextmanager` versus class-based manager

### Choose `@contextmanager` when the flow is short and mostly stateless

```py
@contextmanager
def temporary_cwd(path: str):
    original = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)
```

Use `@contextmanager` when:
- There is one clear yield point.
- The manager does not need to store state between `__enter__` and methods.
- No object identity or reuse contract is required.

### Choose a class-based manager when state or richer behavior matters

```py
class ManagedConnection:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: Connection | None = None

    def __enter__(self) -> Connection:
        self._conn = connect(self._dsn)   # effectful acquisition here, not __init__
        return self._conn

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
```

Use a class-based manager when:
- State must be inspected or modified between `__enter__` and methods.
- Object identity matters (e.g., the instance is passed around).
- Multiple cooperating methods share manager state.
- Richer exception translation is needed in `__exit__`.

**Anti-pattern:** Using a class-based manager for a two-line stateless flow
that `@contextmanager` would express more clearly.

---

## 4. Setup failure translation and preserved cause chains

Translate known setup errors using the semantic custom-error model and
preserve the original cause with `raise X from Y`.

```py
class DatabaseSession:
    def __enter__(self) -> Session:
        try:
            self._session = self._pool.acquire()
        except PoolExhaustedError as exc:
            raise ResourceUnavailableError(
                "Database session pool is exhausted"
            ) from exc
        return self._session
```

**Anti-pattern — swallowing the cause:**
```py
    def __enter__(self) -> Session:
        try:
            self._session = self._pool.acquire()
        except PoolExhaustedError:
            raise ResourceUnavailableError("pool exhausted")  # cause lost
```

Propagate unknown errors without wrapping:
```py
    def __enter__(self) -> Session:
        try:
            self._session = self._pool.acquire()
        except PoolExhaustedError as exc:
            raise ResourceUnavailableError("pool exhausted") from exc
        # All other exceptions propagate untouched
        return self._session
```

---

## 5. Cleanup failure must not replace the primary business error

When a business error is raised inside the `with` block and cleanup also
fails, the cleanup error must not silently replace the primary error.

**Correct — log cleanup error, re-raise original:**
```py
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            self._conn.close()
        except Exception as cleanup_exc:
            if exc_val is not None:
                # Primary error is active; do not hide it
                logger.warning("Cleanup failed: %s", cleanup_exc)
            else:
                raise
```

**Anti-pattern — cleanup error silently hides business error:**
```py
    def __exit__(self, exc_type, exc_val, tb) -> None:
        self._conn.close()   # if this raises, the original exc_val is lost
```

For Python 3.11+ only, `ExceptionGroup` is an advanced option when both
errors genuinely need to surface together (rare). Do not use it as the default
cleanup-failure strategy; the log-and-re-raise pattern above covers most cases.
```py
        except Exception as cleanup_exc:
            if exc_val is not None:
                raise ExceptionGroup(
                    "primary and cleanup errors", [exc_val, cleanup_exc]
                ) from exc_val
```

---

## 6. No-suppression default versus narrow documented suppression

### Default: do not suppress

```py
    def __exit__(self, exc_type, exc_val, tb) -> None:
        self._resource.release()
        # Returns None implicitly — exception propagates
```

### Narrow, explicit, documented suppression

Suppress only a specific, well-understood exception type and document the
reason clearly.

```py
class SuppressNotFound:
    """
    Suppresses FileNotFoundError only.

    Used when the caller treats a missing file as a no-op, not an error.
    Must be tested to confirm no other exception type is silently lost.
    """

    def __enter__(self) -> "SuppressNotFound":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        return exc_type is FileNotFoundError  # True suppresses; False propagates
```

**Anti-pattern — broad suppression:**
```py
    def __exit__(self, exc_type, exc_val, tb) -> bool:
        return True  # Silently swallows all exceptions — dangerous
```

---

## 7. `ExitStack` for dynamic or partial-acquisition rollback

Use `ExitStack` when the set of resources is determined at runtime or when
partial acquisition must roll back already-acquired resources.

### Dynamic resource set

```py
from contextlib import ExitStack

def process_files(paths: list[str]) -> None:
    with ExitStack() as stack:
        handles = [stack.enter_context(open(p)) for p in paths]
        for h in handles:
            process(h)
```

### Partial-acquisition rollback (atomic entry)

```py
class MultiLock:
    def __init__(self, locks: list[Lock]) -> None:
        self._locks = locks
        self._stack: ExitStack | None = None

    def __enter__(self) -> "MultiLock":
        stack = ExitStack()
        try:
            for lock in self._locks:
                stack.enter_context(lock)
        except Exception:
            stack.close()   # rolls back all locks acquired so far
            raise
        self._stack = stack
        return self

    def __exit__(self, *args: object) -> None:
        if self._stack is not None:
            self._stack.close()
            self._stack = None
```

**Anti-pattern:** Using `ExitStack` as the default style for simple,
fixed-resource pairs that a plain `with` statement handles cleanly.

---

## 8. Ambient-state restoration

Ambient-state managers must restore prior state completely on both normal and
error exit.

### Current working directory

```py
@contextmanager
def working_directory(path: str):
    original = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)   # always restores, even on exception
```

### Environment variable

```py
@contextmanager
def env_override(key: str, value: str):
    original = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if original is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original
```

### Logging level

```py
@contextmanager
def log_level(logger: logging.Logger, level: int):
    original = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(original)
```

**Anti-pattern — partial restoration:**
```py
@contextmanager
def bad_env_override(key: str, value: str):
    os.environ[key] = value
    yield
    os.environ.pop(key, None)  # Only runs on normal exit; exception skips it
```

---

## 9. One-shot manager behavior and fresh-instance preference

Context-manager instances are one-shot by default. Reusing an instance across
multiple `with` blocks is not safe unless the class contract explicitly allows
and tests it.

**Anti-pattern — reusing a one-shot instance:**
```py
mgr = ManagedConnection(dsn)
with mgr:
    mgr.execute("SELECT 1")

with mgr:              # Second use: _conn may be None or stale
    mgr.execute("SELECT 2")
```

**Correct — fresh instance per block:**
```py
with ManagedConnection(dsn) as conn:
    conn.execute("SELECT 1")

with ManagedConnection(dsn) as conn:
    conn.execute("SELECT 2")
```

If a class is designed for reuse, state it explicitly in the docstring and
reset all internal state in `__exit__` before returning:

```py
class ReusableSession:
    """
    Reusable context manager.

    Each `with` block opens a fresh session. Re-entry is safe because
    __exit__ resets internal state completely.
    """

    def __enter__(self) -> "ReusableSession":
        self._session = self._pool.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self._session.close()
        self._session = None   # reset ensures re-entry is safe
```
