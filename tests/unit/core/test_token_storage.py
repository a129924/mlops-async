from __future__ import annotations

from datetime import datetime, timedelta, timezone

import mlops_async.core.token_storage as token_storage
import pytest


def test_access_token_rejects_naive_expires_at() -> None:
    with pytest.raises(ValueError, match="expires_at must be timezone-aware"):
        token_storage.AccessToken(
            value="managed-token",
            expires_at=datetime(2026, 5, 20, 12, 0, 0),
        )


def test_access_token_rejects_naive_now_argument() -> None:
    access_token = token_storage.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    with pytest.raises(ValueError, match="now must be timezone-aware"):
        access_token.is_expired(now=datetime(2026, 5, 20, 12, 0, 0))


def test_access_token_is_expired_with_default_60_second_skew() -> None:
    access_token = token_storage.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    assert access_token.is_expired() is True


def test_access_token_respects_explicit_skew_override() -> None:
    access_token = token_storage.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    assert access_token.is_expired(skew=timedelta(seconds=5)) is False


def test_in_memory_token_storage_round_trips_and_clears_token_state() -> None:
    token = token_storage.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    storage = token_storage.InMemoryTokenStorage()

    assert storage.get_token() is None

    storage.set_token(token)
    assert storage.get_token() == token

    storage.set_token(None)
    assert storage.get_token() is None
