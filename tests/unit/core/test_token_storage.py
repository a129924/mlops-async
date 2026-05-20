from __future__ import annotations

import importlib
from datetime import datetime, timedelta, timezone

import pytest


def _token_storage_module():
    try:
        return importlib.import_module("mlops_async.core.token_storage")
    except ModuleNotFoundError as exc:
        pytest.fail(
            "Token storage module must live at mlops_async.core.token_storage; "
            f"import failed: {exc}"
        )


def test_access_token_rejects_naive_expires_at() -> None:
    module = _token_storage_module()

    with pytest.raises(ValueError, match="expires_at must be timezone-aware"):
        module.AccessToken(
            value="managed-token",
            expires_at=datetime(2026, 5, 20, 12, 0, 0),
        )


def test_access_token_rejects_naive_now_argument() -> None:
    module = _token_storage_module()
    access_token = module.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    with pytest.raises(ValueError, match="now must be timezone-aware"):
        access_token.is_expired(now=datetime(2026, 5, 20, 12, 0, 0))


def test_access_token_is_expired_with_default_60_second_skew() -> None:
    module = _token_storage_module()
    access_token = module.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    assert access_token.is_expired() is True


def test_access_token_respects_explicit_skew_override() -> None:
    module = _token_storage_module()
    access_token = module.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    assert access_token.is_expired(skew=timedelta(seconds=5)) is False


def test_in_memory_token_storage_round_trips_and_clears_token_state() -> None:
    module = _token_storage_module()
    token = module.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    storage = module.InMemoryTokenStorage()

    assert storage.get_token() is None

    storage.set_token(token)
    assert storage.get_token() == token

    storage.set_token(None)
    assert storage.get_token() is None
