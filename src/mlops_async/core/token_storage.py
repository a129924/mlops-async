from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol, runtime_checkable

__all__ = ["AccessToken", "InMemoryTokenStorage", "TokenStorage"]

_DEFAULT_EXPIRY_SKEW = timedelta(seconds=60)


@dataclass(frozen=True, slots=True)
class AccessToken:
    """Immutable access-token value object with expiry metadata."""

    value: str
    expires_at: datetime

    def is_expired(
        self,
        *,
        now: datetime | None = None,
        skew: timedelta = _DEFAULT_EXPIRY_SKEW,
    ) -> bool:
        """Return whether the token should be treated as expired."""
        resolved_now = datetime.now(timezone.utc) if now is None else now
        return resolved_now + skew >= self.expires_at


@runtime_checkable
class TokenStorage(Protocol):
    """Internal token-state storage boundary."""

    def get_token(self) -> AccessToken | None: ...

    def set_token(self, token: AccessToken | None) -> None: ...


class InMemoryTokenStorage(TokenStorage):
    """Minimal in-process token storage for auth-boundary orchestration."""

    def __init__(self) -> None:
        """Initialize storage with no token state."""
        self._token: AccessToken | None = None

    def get_token(self) -> AccessToken | None:
        """Return the current token state, if any."""
        return self._token

    def set_token(self, token: AccessToken | None) -> None:
        """Replace the current token state."""
        self._token = token
