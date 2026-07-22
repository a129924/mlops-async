from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import mlops_async.core.auth as auth
import mlops_async.core.token_storage as token_storage
import pytest


class _RecordingTokenEndpointClient:
    def __init__(self, *, fetch_token: object, refresh_token: object | None = None) -> None:
        self.fetch_token = fetch_token
        self.refresh_token = fetch_token if refresh_token is None else refresh_token
        self.fetch_calls = 0
        self.refresh_calls = 0
        self.refresh_inputs: list[object] = []

    async def fetch_access_token(self) -> object:
        self.fetch_calls += 1
        await asyncio.sleep(0)
        return self.fetch_token

    async def refresh_access_token(self, token: object) -> object:
        self.refresh_calls += 1
        self.refresh_inputs.append(token)
        await asyncio.sleep(0)
        return self.refresh_token


class _FailingTokenEndpointClient:
    def __init__(self, exc: BaseException) -> None:
        self.exc = exc
        self.fetch_calls = 0
        self.refresh_calls = 0
        self.refresh_inputs: list[object] = []

    async def fetch_access_token(self) -> object:
        self.fetch_calls += 1
        raise self.exc

    async def refresh_access_token(self, token: object) -> object:
        self.refresh_calls += 1
        self.refresh_inputs.append(token)
        raise self.exc


class _BlockingTokenEndpointClient:
    def __init__(self, *, fetch_token: object, refresh_token: object | None = None) -> None:
        self.fetch_token = fetch_token
        self.refresh_token = fetch_token if refresh_token is None else refresh_token
        self.fetch_calls = 0
        self.refresh_calls = 0
        self.refresh_inputs: list[object] = []
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def fetch_access_token(self) -> object:
        self.fetch_calls += 1
        self.started.set()
        await self.release.wait()
        return self.fetch_token

    async def refresh_access_token(self, token: object) -> object:
        self.refresh_calls += 1
        self.refresh_inputs.append(token)
        self.started.set()
        await self.release.wait()
        return self.refresh_token


@pytest.mark.asyncio
async def test_token_manager_re_raises_auth_exception_without_wrapping() -> None:

    class _CustomAuthException(auth.AuthException):
        pass

    previous_token = token_storage.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    original_error = _CustomAuthException("auth boundary failed")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _FailingTokenEndpointClient(original_error)
    manager = auth.TokenManager(storage, fetcher)

    with pytest.raises(_CustomAuthException) as exc_info:
        await manager.get_access_token()

    assert exc_info.value is original_error
    assert exc_info.value.__cause__ is None
    assert storage.get_token() == previous_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [previous_token]


@pytest.mark.asyncio
async def test_token_manager_reuses_near_expiry_token_when_custom_manager_skew_is_zero() -> None:
    near_expiry_token = token_storage.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=token_storage.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=token_storage.AccessToken(
            value="unused-refresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        ),
    )
    manager = auth.TokenManager(storage, fetcher, expiry_skew=timedelta(0))

    resolved = await manager.get_access_token()

    assert resolved == near_expiry_token
    assert storage.get_token() == near_expiry_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_reuses_non_expired_token_without_fetch_or_refresh() -> None:
    token = token_storage.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=token_storage.AccessToken(
            value="new-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
    )
    manager = auth.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved == token
    assert storage.get_token() == token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_fetches_when_storage_is_empty() -> None:
    fetched_token = token_storage.AccessToken(
        value="fetched-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    fetcher = _RecordingTokenEndpointClient(fetch_token=fetched_token)
    manager = auth.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved == fetched_token
    assert storage.get_token() == fetched_token
    assert fetcher.fetch_calls == 1
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_treats_default_skew_window_as_expired_and_refreshes() -> None:
    near_expiry_token = token_storage.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    refreshed_token = token_storage.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=token_storage.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=refreshed_token,
    )
    manager = auth.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved == refreshed_token
    assert storage.get_token() == refreshed_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [near_expiry_token]


@pytest.mark.asyncio
async def test_token_manager_refreshes_near_expiry_token_when_custom_manager_skew_is_large() -> (
    None
):
    near_expiry_token = token_storage.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    refreshed_token = token_storage.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=token_storage.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=refreshed_token,
    )
    manager = auth.TokenManager(storage, fetcher, expiry_skew=timedelta(minutes=5))

    resolved = await manager.get_access_token()

    assert resolved == refreshed_token
    assert storage.get_token() == refreshed_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [near_expiry_token]


@pytest.mark.asyncio
async def test_token_manager_refreshes_once_for_ten_concurrent_waiters() -> None:
    expired_token = token_storage.AccessToken(
        value="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    refreshed_token = token_storage.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(expired_token)
    fetcher = _BlockingTokenEndpointClient(
        fetch_token=refreshed_token,
        refresh_token=refreshed_token,
    )
    manager = auth.TokenManager(storage, fetcher)

    tasks = [asyncio.create_task(manager.get_access_token()) for _ in range(10)]
    await fetcher.started.wait()
    fetcher.release.set()
    results = await asyncio.gather(*tasks)

    assert results == [refreshed_token] * 10
    assert storage.get_token() == refreshed_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [expired_token]


@pytest.mark.asyncio
async def test_token_manager_fetches_once_for_ten_concurrent_waiters_when_storage_is_empty() -> (
    None
):
    fetched_token = token_storage.AccessToken(
        value="fetched-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    fetcher = _BlockingTokenEndpointClient(fetch_token=fetched_token)
    manager = auth.TokenManager(storage, fetcher)

    tasks = [asyncio.create_task(manager.get_access_token()) for _ in range(10)]
    try:
        await asyncio.wait_for(fetcher.started.wait(), timeout=1)
        fetcher.release.set()
        results = await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        raise

    assert results == [fetched_token] * 10
    assert storage.get_token() == fetched_token
    assert fetcher.fetch_calls == 1
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_translates_refresh_failure_preserving_previous_token() -> None:
    previous_token = token_storage.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    original_error = RuntimeError("token endpoint unavailable")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _FailingTokenEndpointClient(original_error)
    manager = auth.TokenManager(storage, fetcher)

    with pytest.raises(
        auth.TokenFetchException,
        match="RuntimeError: token endpoint unavailable",
    ) as exc_info:
        await manager.get_access_token()

    assert exc_info.value.__cause__ is original_error
    assert storage.get_token() == previous_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [previous_token]


@pytest.mark.asyncio
async def test_token_manager_uses_fallback_message_for_empty_generic_fetch_failure() -> None:
    original_error = RuntimeError()
    storage = token_storage.InMemoryTokenStorage()
    fetcher = _FailingTokenEndpointClient(original_error)
    manager = auth.TokenManager(storage, fetcher)

    with pytest.raises(auth.TokenFetchException, match="RuntimeError") as exc_info:
        await manager.get_access_token()

    assert str(exc_info.value) == "RuntimeError during token fetch/refresh"
    assert exc_info.value.__cause__ is original_error
    assert fetcher.fetch_calls == 1
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_preserves_previous_token_state_on_refresh_cancellation() -> None:
    previous_token = token_storage.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    refreshed_token = token_storage.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _BlockingTokenEndpointClient(
        fetch_token=refreshed_token,
        refresh_token=refreshed_token,
    )
    manager = auth.TokenManager(storage, fetcher)

    task = asyncio.create_task(manager.get_access_token())
    await fetcher.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert storage.get_token() == previous_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [previous_token]
