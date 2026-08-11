from __future__ import annotations

import asyncio
from collections.abc import Mapping
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

import mlops_async.core.requester as requester_mod
import pytest

from mlops_async.core.auth import AuthProvider, TokenManager
from mlops_async.core.request_failure import RequestFailure, ResponseFailureMetadata
from mlops_async.core.request_options import ClientRequestOptions, RequestTimeouts
from mlops_async.core.requester import Requester
from mlops_async.core.token_storage import AccessToken, InMemoryTokenStorage
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders


class _RecordedTransport:
    def __init__(self, outcomes: list[object], failures: Mapping[BaseException, object]) -> None:
        self._outcomes = outcomes
        self._failures = failures
        self.requests: list[tuple[HttpMethod, ClientRequestOptions | None]] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        del path, headers, params, json_body, content
        self.requests.append((method, options))
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, RawClientResponse)
        return outcome

    def failure_for(self, exception: BaseException) -> object | None:
        return self._failures.get(exception)


def _response(method: HttpMethod = HttpMethod.GET) -> RawClientResponse:
    return RawClientResponse(204, ResponseHeaders(), b"", method, "https://example.test/items")


def _failure(
    kind: str,
    *,
    status_code: int | None = None,
    retry_after: str | None = None,
) -> object:
    metadata = (
        ResponseFailureMetadata(status_code=status_code, retry_after=retry_after)
        if status_code is not None
        else None
    )
    return RequestFailure(kind=kind, metadata=metadata)


@pytest.mark.asyncio
@pytest.mark.parametrize("method", (HttpMethod.GET, HttpMethod.HEAD))
async def test_eligible_get_and_head_retry_a_classified_temporary_failure(
    method: HttpMethod,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_error = RuntimeError("temporary connection failure")
    transport = _RecordedTransport(
        [original_error, _response(method)],
        {original_error: _failure("connection")},
    )
    requester = requester_mod.Requester(transport)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)
    options = ClientRequestOptions(timeout=RequestTimeouts(total=1.5))

    response = await requester.request(method, "/items", options=options)

    assert response.status_code == 204
    assert transport.requests == [(method, options), (method, options)]
    assert len(delays) == 1
    assert 0.0 <= delays[0] <= 2.0


@pytest.mark.asyncio
async def test_post_is_the_default_noneligible_branch_and_never_retries_or_sleeps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_error = RuntimeError("retryable only for safe methods")
    transport = _RecordedTransport([original_error], {original_error: _failure("connection")})
    requester = requester_mod.Requester(transport)
    sleep_calls = 0

    async def fail_sleep(_delay: float) -> None:
        nonlocal sleep_calls
        sleep_calls += 1

    monkeypatch.setattr(requester_mod.asyncio, "sleep", fail_sleep)

    with pytest.raises(RuntimeError) as exc_info:
        await requester.request(HttpMethod.POST, "/items")

    assert exc_info.value is original_error
    assert len(transport.requests) == 1
    assert sleep_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", (429, 502, 503, 504))
async def test_eligible_response_failures_retry_only_for_the_locked_statuses(
    status_code: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_error = RuntimeError(f"HTTP {status_code}")
    transport = _RecordedTransport(
        [original_error, _response()],
        {original_error: _failure("response", status_code=status_code)},
    )
    requester = requester_mod.Requester(transport)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)

    await requester.request(HttpMethod.GET, "/items")

    assert len(transport.requests) == 2
    assert len(delays) == 1


@pytest.mark.asyncio
async def test_nonclassified_and_retry_budget_exhausted_failures_propagate_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nonclassified = RuntimeError("no carrier")
    requester = requester_mod.Requester(_RecordedTransport([nonclassified], {}))

    with pytest.raises(RuntimeError) as exc_info:
        await requester.request(HttpMethod.GET, "/items")

    assert exc_info.value is nonclassified

    exhausted = RuntimeError("still unavailable")
    transport = _RecordedTransport(
        [exhausted, exhausted, exhausted],
        {exhausted: _failure("timeout")},
    )
    requester = requester_mod.Requester(transport)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)
    with pytest.raises(RuntimeError) as exhausted_info:
        await requester.request(HttpMethod.GET, "/items")

    assert exhausted_info.value is exhausted
    assert len(transport.requests) == 3
    assert len(delays) == 2
    assert all(0.0 <= delay <= 2.0 for delay in delays)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("retry_after", "expected"),
    (
        ("60", 30.0),
        ("-4", 0.0),
        (format_datetime(datetime.now(timezone.utc) + timedelta(days=1), usegmt=True), 30.0),
    ),
)
async def test_retry_after_delta_or_http_date_is_clamped(
    retry_after: str,
    expected: float,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_error = RuntimeError("retry later")
    transport = _RecordedTransport(
        [original_error, _response()],
        {original_error: _failure("response", status_code=503, retry_after=retry_after)},
    )
    requester = requester_mod.Requester(transport)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)
    await requester.request(HttpMethod.GET, "/items")

    assert delays == [expected]


@pytest.mark.asyncio
async def test_invalid_retry_after_uses_ordinary_bounded_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_error = RuntimeError("retry later")
    transport = _RecordedTransport(
        [original_error, _response()],
        {original_error: _failure("response", status_code=503, retry_after="not-a-date")},
    )
    requester = requester_mod.Requester(transport)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)
    await requester.request(HttpMethod.GET, "/items")

    assert len(delays) == 1
    assert 0.0 <= delays[0] <= 2.0


class _AuthenticatedResilienceTransport:
    def __init__(
        self,
        outcomes: list[object],
        failures: Mapping[BaseException, RequestFailure],
    ) -> None:
        self._outcomes = outcomes
        self._failures = failures
        self.requests: list[Mapping[str, str] | None] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        del method, path, params, json_body, content, options
        self.requests.append(None if headers is None else dict(headers))
        outcome = self._outcomes.pop(0)
        if callable(outcome):
            outcome = outcome()
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, RawClientResponse)
        return outcome

    def failure_for(self, exception: BaseException) -> RequestFailure | None:
        return self._failures.get(exception)


class _RefreshRecordingFetcher:
    def __init__(self, refresh_outcomes: list[AccessToken | BaseException]) -> None:
        self._refresh_outcomes = refresh_outcomes
        self.fetch_calls = 0
        self.refresh_inputs: list[AccessToken] = []

    async def fetch_access_token(self) -> AccessToken:
        self.fetch_calls += 1
        raise AssertionError("requester resilience must not fetch a replacement token")

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        self.refresh_inputs.append(token)
        outcome = self._refresh_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _access_token(value: str) -> AccessToken:
    return AccessToken(
        value=value,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        refresh_token=f"{value}-refresh",
    )


def _authenticated_requester(
    transport: _AuthenticatedResilienceTransport,
    storage: InMemoryTokenStorage,
    fetcher: _RefreshRecordingFetcher,
) -> Requester:
    return Requester(transport, auth_provider=AuthProvider(TokenManager(storage, fetcher)))


@pytest.mark.asyncio
async def test_initial_401_replay_has_an_independent_three_send_transient_retry_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial_token = _access_token("initial")
    refreshed_token = _access_token("refreshed")
    storage = InMemoryTokenStorage()
    storage.set_token(initial_token)
    unauthorized = RuntimeError("initial 401")
    first_replay_failure = RuntimeError("first replay timeout")
    second_replay_failure = RuntimeError("second replay timeout")
    transport = _AuthenticatedResilienceTransport(
        [unauthorized, first_replay_failure, second_replay_failure, _response()],
        {
            unauthorized: RequestFailure(
                kind="response",
                metadata=ResponseFailureMetadata(status_code=401, retry_after=None),
            ),
            first_replay_failure: RequestFailure(kind="timeout"),
            second_replay_failure: RequestFailure(kind="timeout"),
        },
    )
    fetcher = _RefreshRecordingFetcher([refreshed_token])
    requester = _authenticated_requester(transport, storage, fetcher)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(requester_mod.asyncio, "sleep", record_sleep)

    response = await requester.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert len(transport.requests) == 4
    assert transport.requests[0] == {
        "accept": "application/json",
        "authorization": "Bearer initial",
    }
    assert transport.requests[1:] == [
        {"accept": "application/json", "authorization": "Bearer refreshed"},
        {"accept": "application/json", "authorization": "Bearer refreshed"},
        {"accept": "application/json", "authorization": "Bearer refreshed"},
    ]
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_inputs == [initial_token]
    assert len(delays) == 2


@pytest.mark.asyncio
async def test_changed_token_401_skips_refresh_and_replays_using_current_token() -> None:
    initial_token = _access_token("initial")
    current_token = _access_token("current")
    storage = InMemoryTokenStorage()
    storage.set_token(initial_token)
    unauthorized = RuntimeError("initial 401")

    def replace_stored_token() -> BaseException:
        storage.set_token(current_token)
        return unauthorized

    transport = _AuthenticatedResilienceTransport(
        [replace_stored_token, _response()],
        {
            unauthorized: RequestFailure(
                kind="response",
                metadata=ResponseFailureMetadata(status_code=401, retry_after=None),
            )
        },
    )
    fetcher = _RefreshRecordingFetcher([])
    requester = _authenticated_requester(transport, storage, fetcher)

    response = await requester.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert transport.requests == [
        {"accept": "application/json", "authorization": "Bearer initial"},
        {"accept": "application/json", "authorization": "Bearer current"},
    ]
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_inputs == []
    assert storage.get_token() is current_token


@pytest.mark.asyncio
async def test_retry_path_cancellation_propagates_without_another_send_or_refresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial_token = _access_token("initial")
    storage = InMemoryTokenStorage()
    storage.set_token(initial_token)
    retryable_error = RuntimeError("transient timeout")
    transport = _AuthenticatedResilienceTransport(
        [retryable_error],
        {retryable_error: RequestFailure(kind="timeout")},
    )
    fetcher = _RefreshRecordingFetcher([])
    requester = _authenticated_requester(transport, storage, fetcher)
    cancellation = asyncio.CancelledError()

    async def cancel_sleep(_delay: float) -> None:
        raise cancellation

    monkeypatch.setattr(requester_mod.asyncio, "sleep", cancel_sleep)

    with pytest.raises(asyncio.CancelledError) as error_info:
        await requester.request(HttpMethod.GET, "/items")

    assert error_info.value is cancellation
    assert len(transport.requests) == 1
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_inputs == []


@pytest.mark.asyncio
async def test_401_refresh_cancellation_propagates_without_replay_or_another_refresh() -> None:
    initial_token = _access_token("initial")
    storage = InMemoryTokenStorage()
    storage.set_token(initial_token)
    unauthorized = RuntimeError("initial 401")
    cancellation = asyncio.CancelledError()
    transport = _AuthenticatedResilienceTransport(
        [unauthorized],
        {
            unauthorized: RequestFailure(
                kind="response",
                metadata=ResponseFailureMetadata(status_code=401, retry_after=None),
            )
        },
    )
    fetcher = _RefreshRecordingFetcher([cancellation])
    requester = _authenticated_requester(transport, storage, fetcher)

    with pytest.raises(asyncio.CancelledError) as error_info:
        await requester.request(HttpMethod.GET, "/items")

    assert error_info.value is cancellation
    assert len(transport.requests) == 1
    assert fetcher.fetch_calls == 0
    assert fetcher.refresh_inputs == [initial_token]
    assert storage.get_token() is initial_token
