from __future__ import annotations

import asyncio
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


class _RecordingTokenFetcher:
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


class _FailingTokenFetcher:
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


class _BlockingTokenFetcher:
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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()

    class _CustomAuthException(auth_module.AuthException):
        pass

    previous_token = token_storage_module.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    original_error = _CustomAuthException("auth boundary failed")
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _FailingTokenFetcher(original_error)
    manager = auth_module.TokenManager(storage, fetcher)

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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    near_expiry_token = token_storage_module.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenFetcher(
        fetch_token=token_storage_module.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=token_storage_module.AccessToken(
            value="unused-refresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        ),
    )
    manager = auth_module.TokenManager(storage, fetcher, expiry_skew=timedelta(0))

    resolved = await manager.get_access_token()

    assert resolved == near_expiry_token
    assert storage.get_token() == near_expiry_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_reuses_non_expired_token_without_fetch_or_refresh() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    token = token_storage_module.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(token)
    fetcher = _RecordingTokenFetcher(
        fetch_token=token_storage_module.AccessToken(
            value="new-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
    )
    manager = auth_module.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved == token
    assert storage.get_token() == token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_fetches_when_storage_is_empty() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    fetched_token = token_storage_module.AccessToken(
        value="fetched-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    fetcher = _RecordingTokenFetcher(fetch_token=fetched_token)
    manager = auth_module.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved == fetched_token
    assert storage.get_token() == fetched_token
    assert fetcher.fetch_calls == 1
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_treats_default_skew_window_as_expired_and_refreshes() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    near_expiry_token = token_storage_module.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    refreshed_token = token_storage_module.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenFetcher(
        fetch_token=token_storage_module.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=refreshed_token,
    )
    manager = auth_module.TokenManager(storage, fetcher)

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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    near_expiry_token = token_storage_module.AccessToken(
        value="cached-token",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    refreshed_token = token_storage_module.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(near_expiry_token)
    fetcher = _RecordingTokenFetcher(
        fetch_token=token_storage_module.AccessToken(
            value="unused-fetch-token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        ),
        refresh_token=refreshed_token,
    )
    manager = auth_module.TokenManager(storage, fetcher, expiry_skew=timedelta(minutes=5))

    resolved = await manager.get_access_token()

    assert resolved == refreshed_token
    assert storage.get_token() == refreshed_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [near_expiry_token]


@pytest.mark.asyncio
async def test_token_manager_refreshes_once_for_ten_concurrent_waiters() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    expired_token = token_storage_module.AccessToken(
        value="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    refreshed_token = token_storage_module.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(expired_token)
    fetcher = _BlockingTokenFetcher(fetch_token=refreshed_token, refresh_token=refreshed_token)
    manager = auth_module.TokenManager(storage, fetcher)

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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    fetched_token = token_storage_module.AccessToken(
        value="fetched-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    fetcher = _BlockingTokenFetcher(fetch_token=fetched_token)
    manager = auth_module.TokenManager(storage, fetcher)

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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    previous_token = token_storage_module.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    original_error = RuntimeError("token endpoint unavailable")
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _FailingTokenFetcher(original_error)
    manager = auth_module.TokenManager(storage, fetcher)

    with pytest.raises(
        auth_module.TokenFetchException,
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
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    original_error = RuntimeError()
    storage = token_storage_module.InMemoryTokenStorage()
    fetcher = _FailingTokenFetcher(original_error)
    manager = auth_module.TokenManager(storage, fetcher)

    with pytest.raises(auth_module.TokenFetchException, match="RuntimeError") as exc_info:
        await manager.get_access_token()

    assert str(exc_info.value) == "RuntimeError during token fetch/refresh"
    assert exc_info.value.__cause__ is original_error
    assert fetcher.fetch_calls == 1
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_token_manager_preserves_previous_token_state_on_refresh_cancellation() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()
    previous_token = token_storage_module.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
    )
    refreshed_token = token_storage_module.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    storage = token_storage_module.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _BlockingTokenFetcher(fetch_token=refreshed_token, refresh_token=refreshed_token)
    manager = auth_module.TokenManager(storage, fetcher)

    task = asyncio.create_task(manager.get_access_token())
    await fetcher.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert storage.get_token() == previous_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [previous_token]
