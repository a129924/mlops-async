from __future__ import annotations

from datetime import datetime, timedelta, timezone

import mlops_async.core.auth as auth
import mlops_async.core.token_storage as token_storage
import pytest


class _StubTokenManager:
    def __init__(self, access_token: object) -> None:
        self.access_token = access_token
        self.calls = 0

    async def get_access_token(self) -> object:
        self.calls += 1
        return self.access_token


@pytest.mark.asyncio
async def test_auth_provider_turns_token_manager_output_into_bearer_header() -> None:
    access_token = token_storage.AccessToken(
        value="managed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    token_manager = _StubTokenManager(access_token)
    auth_provider = auth.AuthProvider(token_manager)

    headers = await auth_provider.get_auth_headers()

    assert headers == {"Authorization": "Bearer managed-token"}
    assert token_manager.calls == 1
