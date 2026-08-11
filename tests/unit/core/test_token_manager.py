from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import mlops_async.core.auth as auth
import mlops_async.core.token_storage as token_storage
import pytest

from mlops_async.core.token_endpoint_client import TokenEndpointClientError


def _access_token(
    value: str,
    *,
    refresh_token: str | None = "refresh-token",
) -> token_storage.AccessToken:
    return token_storage.AccessToken(
        value=value,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        refresh_token=refresh_token,
    )


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
        refresh_token="previous-refresh-token",
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
        refresh_token="previous-refresh-token",
    )
    refreshed_token = token_storage.AccessToken(
        value="refreshed-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        refresh_token="rotated-refresh-token",
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
    assert results[0].refresh_token == "rotated-refresh-token"


@pytest.mark.asyncio
async def test_token_manager_preserves_refresh_token_when_refresh_response_omits_it() -> None:
    previous_token = token_storage.AccessToken(
        value="previous-access-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
        refresh_token="previous-refresh-token",
    )
    refreshed_token_without_rotation = token_storage.AccessToken(
        value="replacement-access-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        refresh_token=None,
    )
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=refreshed_token_without_rotation,
        refresh_token=refreshed_token_without_rotation,
    )
    manager = auth.TokenManager(storage, fetcher)

    resolved = await manager.get_access_token()

    assert resolved.value == "replacement-access-token"
    assert resolved.expires_at == refreshed_token_without_rotation.expires_at
    assert resolved.refresh_token == "previous-refresh-token"
    assert storage.get_token() == resolved
    assert fetcher.refresh_calls == 1


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
        refresh_token="previous-refresh-token",
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
    assert storage.get_token() is previous_token
    assert storage.get_token().refresh_token == "previous-refresh-token"


@pytest.mark.asyncio
async def test_token_manager_chains_schema_failure_preserving_complete_state() -> None:
    previous_token = token_storage.AccessToken(
        value="previous-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=5),
        refresh_token="previous-refresh-token",
    )
    original_error = TokenEndpointClientError("refresh_token must be a non-empty string")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(previous_token)
    fetcher = _FailingTokenEndpointClient(original_error)
    manager = auth.TokenManager(storage, fetcher)

    with pytest.raises(auth.TokenFetchException, match="TokenEndpointClientError") as exc_info:
        await manager.get_access_token()

    assert exc_info.value.__cause__ is original_error
    assert storage.get_token() is previous_token
    assert storage.get_token().refresh_token == "previous-refresh-token"
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1


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
        refresh_token="previous-refresh-token",
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
    assert storage.get_token() is previous_token
    assert storage.get_token().refresh_token == "previous-refresh-token"


@pytest.mark.asyncio
async def test_refresh_if_current_refreshes_once_and_returns_the_replacement_token() -> None:
    current_token = _access_token("current-token")
    replacement_token = _access_token("replacement-token", refresh_token="rotated-refresh")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(current_token)
    fetcher = _RecordingTokenEndpointClient(
        fetch_token=_access_token("unused-fetch"),
        refresh_token=replacement_token,
    )
    manager = auth.TokenManager(storage, fetcher)

    resolved = await manager.refresh_if_current(current_token)

    assert resolved is replacement_token
    assert storage.get_token() is replacement_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1
    assert fetcher.refresh_inputs == [current_token]


@pytest.mark.asyncio
async def test_refresh_if_current_reuses_changed_state_and_never_fetches_for_cleared_storage(
) -> None:
    initial_token = _access_token("initial-token")
    changed_token = _access_token("changed-token")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(changed_token)
    fetcher = _RecordingTokenEndpointClient(fetch_token=_access_token("unexpected-fetch"))
    manager = auth.TokenManager(storage, fetcher)

    changed_result = await manager.refresh_if_current(initial_token)
    storage.set_token(None)
    cleared_result = await manager.refresh_if_current(changed_token)

    assert changed_result is changed_token
    assert cleared_result is None
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 0


@pytest.mark.asyncio
async def test_refresh_if_current_coordinates_concurrent_same_token_callers() -> None:
    current_token = _access_token("current-token")
    replacement_token = _access_token("replacement-token")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(current_token)
    fetcher = _BlockingTokenEndpointClient(
        fetch_token=_access_token("unused-fetch"),
        refresh_token=replacement_token,
    )
    manager = auth.TokenManager(storage, fetcher)

    tasks = [asyncio.create_task(manager.refresh_if_current(current_token)) for _ in range(5)]
    await asyncio.wait_for(fetcher.started.wait(), timeout=1)
    fetcher.release.set()
    results = await asyncio.gather(*tasks)

    assert results == [replacement_token] * 5
    assert storage.get_token() is replacement_token
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_calls == 1


@pytest.mark.asyncio
async def test_refresh_if_current_preserves_storage_on_failure_and_cancellation() -> None:
    current_token = _access_token("current-token")
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(current_token)
    failure = RuntimeError("refresh failed")
    manager = auth.TokenManager(storage, _FailingTokenEndpointClient(failure))

    with pytest.raises(auth.TokenFetchException) as failure_info:
        await manager.refresh_if_current(current_token)

    assert failure_info.value.__cause__ is failure
    assert storage.get_token() is current_token

    blocking_fetcher = _BlockingTokenEndpointClient(
        fetch_token=_access_token("unused-fetch"),
        refresh_token=_access_token("replacement-token"),
    )
    cancelled_manager = auth.TokenManager(storage, blocking_fetcher)
    task = asyncio.create_task(cancelled_manager.refresh_if_current(current_token))
    await asyncio.wait_for(blocking_fetcher.started.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert storage.get_token() is current_token
    assert blocking_fetcher.fetch_calls == 0
    assert blocking_fetcher.refresh_calls == 1
