from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol, runtime_checkable

__all__ = ["AccessToken", "InMemoryTokenStorage", "TokenStorage"]

DEFAULT_EXPIRY_SKEW = timedelta(seconds=60)


def _validate_timezone_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class AccessToken:
    """Immutable access-token value object with expiry metadata."""

    value: str
    expires_at: datetime

    def __post_init__(self) -> None:
        """Reject naive expiry datetimes so expiry checks stay deterministic."""
        _validate_timezone_aware(self.expires_at, field_name="expires_at")

    def is_expired(
        self,
        *,
        now: datetime | None = None,
        skew: timedelta = DEFAULT_EXPIRY_SKEW,
    ) -> bool:
        """Return whether the token should be treated as expired."""
        resolved_now = datetime.now(timezone.utc) if now is None else now
        _validate_timezone_aware(resolved_now, field_name="now")
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
