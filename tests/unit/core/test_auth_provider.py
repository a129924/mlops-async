from __future__ import annotations

import importlib
from datetime import datetime, timedelta, timezone

import pytest


def _auth_module():
    try:
        return importlib.import_module("mlops_async.core.auth")
    except ModuleNotFoundError as exc:
        pytest.fail(
            f"Internal auth contracts must live at mlops_async.core.auth; import failed: {exc}"
        )


def _token_storage_module():
    try:
        return importlib.import_module("mlops_async.core.token_storage")
    except ModuleNotFoundError as exc:
        pytest.fail(
            "Token storage contracts must live at mlops_async.core.token_storage; "
            f"import failed: {exc}"
        )


class _StubTokenManager:
    def __init__(self, access_token: object) -> None:
        self.access_token = access_token
        self.calls = 0

    async def get_access_token(self) -> object:
        self.calls += 1
        return self.access_token


@pytest.mark.asyncio
async def test_auth_provider_turns_token_manager_output_into_bearer_header() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    access_token = token_storage_module.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    token_manager = _StubTokenManager(access_token)
    auth_provider = auth_module.AuthProvider(token_manager)

    headers = await auth_provider.get_auth_headers()

    assert headers == {"Authorization": "Bearer managed-token"}
    assert token_manager.calls == 1
