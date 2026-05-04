# Strict typing examples

Use these examples after `SKILL.md` narrows the task to strict, version-aware Python typing.

## Python 3.10+

### Use
```py
from typing import TypeAlias

UserId: TypeAlias = int

def find_user(user_id: UserId) -> User | None:
    ...

def group_names(users: list[User]) -> dict[str, list[str]]:
    ...
```

- Use PEP 604 unions such as `User | None`.
- Use built-in generics such as `list[str]` and `dict[str, list[str]]`.
- Use stdlib `TypeAlias` when the project baseline supports it.

### Avoid
```py
from typing import Dict, List, Optional

def find_user(user_id: int) -> Optional[User]:
    ...

def group_names(users: List[User]) -> Dict[str, List[str]]:
    ...
```

- Do not keep `Optional`, `List`, or `Dict` out of habit when the supported version already allows modern syntax.

## Python 3.8/3.9 shared-compatibility path

### Use
```py
from typing import Dict, List, Optional, Union
from typing_extensions import TypeAlias

Payload: TypeAlias = Union[str, bytes]

def find_user(user_id: int) -> Optional[User]:
    ...

def group_names(users: List[User]) -> Dict[str, List[str]]:
    ...
```

- If one rule set must stay source-compatible with Python 3.8 and 3.9, keep the older spellings consistently.
- Use `typing_extensions.TypeAlias` when stdlib `TypeAlias` is not available on the supported baseline.

## Avoid routine escape hatches

```py
from typing import Any, cast

def load_user(raw: Any) -> User:
    user = cast(User, raw)
    return user  # pyright: ignore[reportReturnType]
```

- Do not use `Any`, `cast(...)`, or ignore comments as the normal typing strategy.
- Keep them isolated to justified dynamic boundaries, then narrow back to precise types quickly.
