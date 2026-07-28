from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Protocol, cast, runtime_checkable

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
    refresh_token: str | None = None

    def __post_init__(self) -> None:
        """Reject naive expiry datetimes so expiry checks stay deterministic."""
        _validate_timezone_aware(self.expires_at, field_name="expires_at")
        # Preserve runtime validation for values supplied by untyped callers.
        refresh_token = cast(object, self.refresh_token)
        if refresh_token is not None and (
            not isinstance(refresh_token, str) or not refresh_token.strip()
        ):
            raise ValueError("refresh_token must be a non-empty string when provided")

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
        """Replace the current token state while preserving an omitted refresh token."""
        if (
            token is not None
            and token.refresh_token is None
            and self._token is not None
            and self._token.refresh_token is not None
        ):
            token = replace(token, refresh_token=self._token.refresh_token)
        self._token = token
