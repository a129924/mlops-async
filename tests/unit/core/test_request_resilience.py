from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import pytest

from mlops_async.core.auth import AuthProvider, TokenManager
from mlops_async.core.request_execution import (
    AuthRecoveryAttempt,
    AuthRecoveryExecutor,
    RequestExecutor,
    RequestFailureClassifier,
    RequestInvocation,
    thaw_json_body,
)
from mlops_async.core.request_failure import RequestFailure, ResponseFailureMetadata
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.requester import Requester
from mlops_async.core.token_storage import AccessToken, InMemoryTokenStorage
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from mlops_async.resilience import (
    PolicyRequestExecutor,
    RequestPolicy,
    TransientRetryPolicy,
    UnauthorizedRecoveryPolicy,
)
import mlops_async.resilience.policies as policies_mod


def _response(method: HttpMethod = HttpMethod.GET) -> RawClientResponse:
    return RawClientResponse(204, ResponseHeaders(), b"", method, "https://example.test/items")


def _token(value: str) -> AccessToken:
    return AccessToken(
        value=value,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        refresh_token=f"{value}-refresh",
    )


class _FailureMap(RequestFailureClassifier):
    def __init__(self, failures: Mapping[BaseException, RequestFailure]) -> None:
        self._failures = failures
        self.seen: list[BaseException] = []

    def classify(self, error: BaseException) -> RequestFailure | None:
        self.seen.append(error)
        return self._failures.get(error)


class _FalseyFailureMap(_FailureMap):
    def __bool__(self) -> bool:
        return False


class _RawExecutor(RequestExecutor):
    def __init__(self, outcomes: list[RawClientResponse | BaseException]) -> None:
        self._outcomes = outcomes
        self.requests: list[RequestInvocation] = []

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
        self.requests.append(
            RequestInvocation(method, path, headers, params, json_body, content, options)
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class _AuthRecordingExecutor(AuthRecoveryExecutor):
    def __init__(self) -> None:
        self.prepared: list[RequestInvocation] = []
        self.sent: list[RequestInvocation] = []

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
        attempt = await self.prepare_auth_recovery_attempt(
            RequestInvocation(method, path, headers, params, json_body, content, options)
        )
        return await attempt.send()

    async def prepare_auth_recovery_attempt(
        self, invocation: RequestInvocation
    ) -> AuthRecoveryAttempt:
        self.prepared.append(invocation)

        async def send() -> RawClientResponse:
            self.sent.append(invocation)
            return _response()

        return AuthRecoveryAttempt(token=_token("managed"), send=send)

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None:
        return token


class _RecordingPolicy(RequestPolicy):
    def __init__(self, name: str, events: list[str]) -> None:
        self._name = name
        self._events = events

    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        *_: object,
    ) -> RawClientResponse:
        self._events.append(f"{self._name}:before")
        response = await downstream.request(
            invocation.method,
            invocation.path,
            headers=invocation.headers,
            params=invocation.params,
            json_body=invocation.json_body,
            content=invocation.content,
            options=invocation.options,
        )
        self._events.append(f"{self._name}:after")
        return response


class _RewritingPolicy(RequestPolicy):
    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        *_: object,
    ) -> RawClientResponse:
        return await downstream.request(
            invocation.method,
            "/rewritten",
            headers={"x-inner-policy": "applied"},
            json_body={"rewritten": True},
        )


class _ShortCircuitingPolicy(RequestPolicy):
    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        *_: object,
    ) -> RawClientResponse:
        del invocation, downstream
        return _response()


class _DerivedTransientRetryPolicy(TransientRetryPolicy):
    pass


class _OtherDerivedTransientRetryPolicy(TransientRetryPolicy):
    pass


class _DerivedUnauthorizedRecoveryPolicy(UnauthorizedRecoveryPolicy):
    pass


class _OtherDerivedUnauthorizedRecoveryPolicy(UnauthorizedRecoveryPolicy):
    pass


def test_stable_non_root_contracts_are_not_promoted_to_package_root() -> None:
    import mlops_async

    assert RequestExecutor.__module__ == "mlops_async.core.request_execution"
    assert RequestInvocation.__module__ == "mlops_async.core.request_execution"
    assert AuthRecoveryAttempt.__module__ == "mlops_async.core.request_execution"
    assert not hasattr(mlops_async, "PolicyRequestExecutor")
    assert not hasattr(mlops_async, "RequestExecutor")


@pytest.mark.asyncio
async def test_raw_requester_has_no_implicit_policy_and_sends_exactly_once() -> None:
    class _Transport:
        def __init__(self) -> None:
            self.sends = 0

        async def request(self, method: HttpMethod, path: str, **_: object) -> RawClientResponse:
            del path
            self.sends += 1
            raise RuntimeError("raw transport failure")

    transport = _Transport()
    requester = Requester(transport)

    with pytest.raises(RuntimeError, match="raw transport failure"):
        await requester.request(HttpMethod.GET, "/items")

    assert transport.sends == 1


@pytest.mark.asyncio
async def test_custom_policies_are_injected_and_run_left_to_right_outermost() -> None:
    events: list[str] = []
    raw = _RawExecutor([_response()])
    executor = PolicyRequestExecutor(
        raw,
        [_RecordingPolicy("outer", events), _RecordingPolicy("inner", events)],
    )

    response = await executor.request(HttpMethod.GET, "/items", params={"tag": "one"})

    assert response.status_code == 204
    assert events == ["outer:before", "inner:before", "inner:after", "outer:after"]
    assert raw.requests == [
        RequestInvocation(HttpMethod.GET, "/items", None, {"tag": "one"}, None, None, None)
    ]


@pytest.mark.asyncio
async def test_nested_pipeline_prepares_auth_after_inner_policy_rewrites_invocation() -> None:
    auth_raw = _AuthRecordingExecutor()
    inner = PolicyRequestExecutor(auth_raw, [_RewritingPolicy()])
    outer = PolicyRequestExecutor(inner, [])

    response = await outer.request(
        HttpMethod.GET,
        "/original",
        headers={"x-request": "original"},
        json_body={"original": True},
    )

    expected = RequestInvocation(
        HttpMethod.GET,
        "/rewritten",
        {"x-inner-policy": "applied"},
        None,
        {"rewritten": True},
        None,
        None,
    )
    assert response.status_code == 204
    assert auth_raw.prepared == [expected]
    assert auth_raw.sent == [expected]


@pytest.mark.asyncio
async def test_nested_pipeline_short_circuit_does_not_prepare_auth_attempt() -> None:
    auth_raw = _AuthRecordingExecutor()
    inner = PolicyRequestExecutor(auth_raw, [_ShortCircuitingPolicy()])
    outer = PolicyRequestExecutor(inner, [])

    response = await outer.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert auth_raw.prepared == []
    assert auth_raw.sent == []


@pytest.mark.asyncio
async def test_invocation_is_an_immutable_snapshot_of_caller_owned_request_data() -> None:
    class _MutationAttemptPolicy(RequestPolicy):
        async def execute(
            self,
            invocation: RequestInvocation,
            downstream: RequestExecutor,
            *_: object,
        ) -> RawClientResponse:
            assert invocation.headers is not None
            assert invocation.params is not None
            assert invocation.json_body is not None
            with pytest.raises(TypeError):
                invocation.headers["x-policy"] = "mutated"  # type: ignore[index]
            with pytest.raises(TypeError):
                invocation.params["page"] = "2"  # type: ignore[index]
            with pytest.raises(TypeError):
                invocation.json_body["nested"] = None  # type: ignore[index]
            return await downstream.request(
                invocation.method,
                invocation.path,
                headers=invocation.headers,
                params=invocation.params,
                json_body=invocation.json_body,
            )

    headers = {"x-request": "original"}
    params = {"page": "1"}
    json_body = {"nested": {"items": ["original"]}}
    raw = _RawExecutor([_response()])
    executor = PolicyRequestExecutor(raw, [_MutationAttemptPolicy()])

    await executor.request(
        HttpMethod.GET,
        "/items",
        headers=headers,
        params=params,
        json_body=json_body,
    )

    assert headers == {"x-request": "original"}
    assert params == {"page": "1"}
    assert json_body == {"nested": {"items": ["original"]}}
    assert raw.requests[0].headers == headers
    assert raw.requests[0].params == params
    assert thaw_json_body(raw.requests[0].json_body) == json_body


@pytest.mark.parametrize(
    "policies",
    ([object()], [TransientRetryPolicy(), TransientRetryPolicy()]),
)
def test_pipeline_rejects_nonpolicies_and_duplicate_builtin_policies_before_io(
    policies: list[object],
) -> None:
    raw = _RawExecutor([_response()])

    with pytest.raises((TypeError, ValueError), match=r"policy|Policy|duplicate|Duplicate"):
        PolicyRequestExecutor(raw, policies)

    assert raw.requests == []


@pytest.mark.parametrize(
    "policies",
    (
        [TransientRetryPolicy(), _DerivedTransientRetryPolicy()],
        [_DerivedTransientRetryPolicy(), _OtherDerivedTransientRetryPolicy()],
    ),
)
def test_pipeline_rejects_builtin_retry_family_subclasses_before_io(
    policies: list[RequestPolicy],
) -> None:
    raw = _RawExecutor([_response()])

    with pytest.raises(ValueError, match="duplicate built-in request policy"):
        PolicyRequestExecutor(raw, policies)

    assert raw.requests == []


@pytest.mark.parametrize(
    "policies",
    (
        [UnauthorizedRecoveryPolicy(), _DerivedUnauthorizedRecoveryPolicy()],
        [_DerivedUnauthorizedRecoveryPolicy(), _OtherDerivedUnauthorizedRecoveryPolicy()],
    ),
)
def test_pipeline_rejects_builtin_unauthorized_family_subclasses_before_io(
    policies: list[RequestPolicy],
) -> None:
    raw = _AuthRecordingExecutor()

    with pytest.raises(ValueError, match="duplicate built-in request policy"):
        PolicyRequestExecutor(raw, policies)

    assert raw.prepared == []


@pytest.mark.parametrize(
    ("outer_policy", "inner_policy"),
    (
        (TransientRetryPolicy(), _DerivedTransientRetryPolicy()),
        (_DerivedTransientRetryPolicy(), _OtherDerivedTransientRetryPolicy()),
    ),
)
def test_nested_pipeline_rejects_builtin_retry_family_subclasses_before_io(
    outer_policy: RequestPolicy,
    inner_policy: RequestPolicy,
) -> None:
    raw = _RawExecutor([_response()])
    inner = PolicyRequestExecutor(raw, [inner_policy])

    with pytest.raises(ValueError, match="duplicate built-in request policy"):
        PolicyRequestExecutor(inner, [outer_policy])

    assert raw.requests == []


@pytest.mark.parametrize(
    ("outer_policy", "inner_policy"),
    (
        (UnauthorizedRecoveryPolicy(), _DerivedUnauthorizedRecoveryPolicy()),
        (_DerivedUnauthorizedRecoveryPolicy(), _OtherDerivedUnauthorizedRecoveryPolicy()),
    ),
)
def test_nested_pipeline_rejects_builtin_unauthorized_family_subclasses_before_io(
    outer_policy: RequestPolicy,
    inner_policy: RequestPolicy,
) -> None:
    raw = _AuthRecordingExecutor()
    inner = PolicyRequestExecutor(raw, [inner_policy])

    with pytest.raises(ValueError, match="duplicate built-in request policy"):
        PolicyRequestExecutor(inner, [outer_policy])

    assert raw.prepared == []


def test_pipeline_rejects_reverse_builtin_order_before_io() -> None:
    raw = _AuthRecordingExecutor()

    with pytest.raises(ValueError, match="UnauthorizedRecoveryPolicy must be outermost"):
        PolicyRequestExecutor(
            raw,
            [_DerivedTransientRetryPolicy(), _DerivedUnauthorizedRecoveryPolicy()],
        )

    assert raw.prepared == []


def test_nested_pipeline_rejects_reverse_builtin_order_before_io() -> None:
    raw = _AuthRecordingExecutor()
    inner = PolicyRequestExecutor(raw, [_DerivedUnauthorizedRecoveryPolicy()])

    with pytest.raises(ValueError, match="UnauthorizedRecoveryPolicy must be outermost"):
        PolicyRequestExecutor(inner, [_DerivedTransientRetryPolicy()])

    assert raw.prepared == []


def test_unauthorized_policy_requires_auth_recovery_capability_before_io() -> None:
    raw = _RawExecutor([_response()])

    with pytest.raises((TypeError, ValueError), match=r"recovery|Recovery|auth"):
        PolicyRequestExecutor(raw, [UnauthorizedRecoveryPolicy()])

    assert raw.requests == []


@pytest.mark.asyncio
async def test_classifier_none_leaves_original_error_unchanged_without_retry() -> None:
    error = RuntimeError("unclassified")
    raw = _RawExecutor([error])
    classifier = _FailureMap({})
    executor = PolicyRequestExecutor(raw, [TransientRetryPolicy()], classifier=classifier)

    with pytest.raises(RuntimeError) as captured:
        await executor.request(HttpMethod.GET, "/items")

    assert captured.value is error
    assert classifier.seen == [error]
    assert len(raw.requests) == 1


@pytest.mark.asyncio
async def test_falsey_injected_classifier_is_not_replaced_by_default_classifier() -> None:
    error = RuntimeError("unclassified")
    classifier = _FalseyFailureMap({})
    executor = PolicyRequestExecutor(
        _RawExecutor([error]),
        [TransientRetryPolicy()],
        classifier=classifier,
    )

    with pytest.raises(RuntimeError) as captured:
        await executor.request(HttpMethod.GET, "/items")

    assert captured.value is error
    assert classifier.seen == [error]


def test_raw_only_nested_decorators_do_not_advertise_auth_recovery_capability() -> None:
    raw = _RawExecutor([_response()])
    inner = PolicyRequestExecutor(raw, [])
    outer = PolicyRequestExecutor(inner, [])

    assert not isinstance(inner, AuthRecoveryExecutor)
    assert not isinstance(outer, AuthRecoveryExecutor)
    with pytest.raises(TypeError, match="auth recovery capability"):
        PolicyRequestExecutor(outer, [UnauthorizedRecoveryPolicy()])


@pytest.mark.parametrize(
    "policy_type",
    (TransientRetryPolicy, UnauthorizedRecoveryPolicy),
)
def test_nested_pipeline_rejects_duplicate_builtin_policy_types(
    policy_type: type[TransientRetryPolicy] | type[UnauthorizedRecoveryPolicy],
) -> None:
    raw: RequestExecutor
    if policy_type is UnauthorizedRecoveryPolicy:
        storage = InMemoryTokenStorage()
        storage.set_token(_token("initial"))
        raw = Requester(
            _AuthenticatedTransport([_response()]),
            auth_provider=AuthProvider(TokenManager(storage, _RefreshFetcher(_token("next")))),
        )
    else:
        raw = _RawExecutor([_response()])
    inner = PolicyRequestExecutor(raw, [policy_type()])

    with pytest.raises(ValueError, match="duplicate built-in request policy"):
        PolicyRequestExecutor(inner, [policy_type()])


@pytest.mark.asyncio
@pytest.mark.parametrize("method", (HttpMethod.GET, HttpMethod.HEAD))
async def test_transient_policy_retries_only_get_and_head_with_match_case_eligibility(
    method: HttpMethod,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = RuntimeError("temporary")
    raw = _RawExecutor([error, _response(method)])
    classifier = _FailureMap({error: RequestFailure(kind="connection")})
    executor = PolicyRequestExecutor(raw, [TransientRetryPolicy()], classifier=classifier)
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(policies_mod.asyncio, "sleep", record_sleep)

    response = await executor.request(method, "/items")

    assert response.status_code == 204
    assert len(raw.requests) == 2
    assert len(delays) == 1


@pytest.mark.asyncio
async def test_transient_policy_never_retries_post() -> None:
    error = RuntimeError("temporary")
    raw = _RawExecutor([error])
    classifier = _FailureMap({error: RequestFailure(kind="connection")})
    executor = PolicyRequestExecutor(raw, [TransientRetryPolicy()], classifier=classifier)

    with pytest.raises(RuntimeError) as captured:
        await executor.request(HttpMethod.POST, "/items")

    assert captured.value is error
    assert len(raw.requests) == 1


class _RefreshFetcher:
    def __init__(self, replacement: AccessToken) -> None:
        self.replacement = replacement
        self.refreshes: list[AccessToken] = []

    async def fetch_access_token(self) -> AccessToken:
        raise AssertionError("401 recovery must not use a password-grant fetch")

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        self.refreshes.append(token)
        return self.replacement


class _CancellingRefreshFetcher:
    def __init__(self, cancellation: asyncio.CancelledError) -> None:
        self._cancellation = cancellation
        self.refreshes: list[AccessToken] = []

    async def fetch_access_token(self) -> AccessToken:
        raise AssertionError("401 recovery must not use a password-grant fetch")

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        self.refreshes.append(token)
        raise self._cancellation


class _AuthenticatedTransport:
    def __init__(self, outcomes: list[RawClientResponse | BaseException]) -> None:
        self._outcomes = outcomes
        self.headers: list[Mapping[str, str] | None] = []
        self.on_before_next_outcome: Callable[[], None] | None = None

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        **_: object,
    ) -> RawClientResponse:
        del path
        self.headers.append(None if headers is None else dict(headers))
        if self.on_before_next_outcome is not None:
            callback = self.on_before_next_outcome
            self.on_before_next_outcome = None
            callback()
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _authenticated_executor(
    outcomes: list[RawClientResponse | BaseException],
    initial: AccessToken,
    replacement: AccessToken,
    failures: Mapping[BaseException, RequestFailure],
) -> tuple[PolicyRequestExecutor, _AuthenticatedTransport, _RefreshFetcher, InMemoryTokenStorage]:
    storage = InMemoryTokenStorage()
    storage.set_token(initial)
    fetcher = _RefreshFetcher(replacement)
    transport = _AuthenticatedTransport(outcomes)
    requester = Requester(
        transport,
        auth_provider=AuthProvider(TokenManager(storage, fetcher)),
    )
    executor = PolicyRequestExecutor(
        requester,
        [UnauthorizedRecoveryPolicy(), TransientRetryPolicy()],
        classifier=_FailureMap(failures),
    )
    return executor, transport, fetcher, storage


@pytest.mark.asyncio
async def test_unauthenticated_401_is_passthrough_without_refresh_or_replay() -> None:
    unauthorized = RuntimeError("401")
    raw = _RawExecutor([unauthorized])
    classifier = _FailureMap(
        {
            unauthorized: RequestFailure(
                kind="response", metadata=ResponseFailureMetadata(status_code=401, retry_after=None)
            )
        }
    )
    executor = PolicyRequestExecutor(raw, [TransientRetryPolicy()], classifier=classifier)

    with pytest.raises(RuntimeError) as captured:
        await executor.request(HttpMethod.GET, "/items")

    assert captured.value is unauthorized
    assert len(raw.requests) == 1


@pytest.mark.asyncio
async def test_401_refresh_uses_attempt_local_token_and_replay_reenters_inner_retry_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial = _token("initial")
    replacement = _token("replacement")
    unauthorized = RuntimeError("401")
    replay_timeout_one = RuntimeError("replay timeout 1")
    replay_timeout_two = RuntimeError("replay timeout 2")
    executor, transport, fetcher, _ = _authenticated_executor(
        [unauthorized, replay_timeout_one, replay_timeout_two, _response()],
        initial,
        replacement,
        {
            unauthorized: RequestFailure(
                kind="response", metadata=ResponseFailureMetadata(status_code=401, retry_after=None)
            ),
            replay_timeout_one: RequestFailure(kind="timeout"),
            replay_timeout_two: RequestFailure(kind="timeout"),
        },
    )
    delays: list[float] = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(policies_mod.asyncio, "sleep", record_sleep)

    response = await executor.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert fetcher.refreshes == [initial]
    assert [headers["authorization"] for headers in transport.headers if headers is not None] == [
        "Bearer initial",
        "Bearer replacement",
        "Bearer replacement",
        "Bearer replacement",
    ]
    assert len(delays) == 2


@pytest.mark.asyncio
async def test_changed_token_after_the_observed_attempt_skips_stale_refresh_and_replays() -> None:
    initial = _token("initial")
    changed = _token("changed")
    unauthorized = RuntimeError("401")
    executor, transport, fetcher, storage = _authenticated_executor(
        [unauthorized, _response()],
        initial,
        changed,
        {
            unauthorized: RequestFailure(
                kind="response", metadata=ResponseFailureMetadata(status_code=401, retry_after=None)
            )
        },
    )
    transport.on_before_next_outcome = lambda: storage.set_token(changed)

    response = await executor.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert fetcher.refreshes == []
    assert [headers["authorization"] for headers in transport.headers if headers is not None] == [
        "Bearer initial",
        "Bearer changed",
    ]


@pytest.mark.asyncio
async def test_cleared_token_after_the_observed_attempt_does_not_refresh_or_replay() -> None:
    initial = _token("initial")
    unauthorized = RuntimeError("401")
    executor, transport, fetcher, storage = _authenticated_executor(
        [unauthorized],
        initial,
        _token("unused"),
        {
            unauthorized: RequestFailure(
                kind="response", metadata=ResponseFailureMetadata(status_code=401, retry_after=None)
            )
        },
    )
    transport.on_before_next_outcome = lambda: storage.set_token(None)

    with pytest.raises(RuntimeError) as captured:
        await executor.request(HttpMethod.GET, "/items")

    assert captured.value is unauthorized
    assert fetcher.refreshes == []
    assert [headers["authorization"] for headers in transport.headers if headers is not None] == [
        "Bearer initial"
    ]


@pytest.mark.asyncio
async def test_401_refresh_cancellation_propagates_without_replay() -> None:
    initial = _token("initial")
    unauthorized = RuntimeError("401")
    cancellation = asyncio.CancelledError()
    storage = InMemoryTokenStorage()
    storage.set_token(initial)
    fetcher = _CancellingRefreshFetcher(cancellation)
    transport = _AuthenticatedTransport([unauthorized, _response()])
    requester = Requester(
        transport,
        auth_provider=AuthProvider(TokenManager(storage, fetcher)),
    )
    executor = PolicyRequestExecutor(
        requester,
        [UnauthorizedRecoveryPolicy()],
        classifier=_FailureMap(
            {
                unauthorized: RequestFailure(
                    kind="response",
                    metadata=ResponseFailureMetadata(status_code=401, retry_after=None),
                )
            }
        ),
    )

    with pytest.raises(asyncio.CancelledError) as captured:
        await executor.request(HttpMethod.GET, "/items")

    assert captured.value is cancellation
    assert fetcher.refreshes == [initial]
    assert len(transport.headers) == 1


@pytest.mark.asyncio
async def test_nested_pipeline_forwards_auth_recovery_without_skipping_inner_policy() -> None:
    initial = _token("initial")
    replacement = _token("replacement")
    unauthorized = RuntimeError("401")
    events: list[str] = []
    storage = InMemoryTokenStorage()
    storage.set_token(initial)
    fetcher = _RefreshFetcher(replacement)
    transport = _AuthenticatedTransport([unauthorized, _response()])
    requester = Requester(
        transport,
        auth_provider=AuthProvider(TokenManager(storage, fetcher)),
    )
    inner = PolicyRequestExecutor(requester, [_RecordingPolicy("inner", events)])
    outer = PolicyRequestExecutor(
        inner,
        [UnauthorizedRecoveryPolicy()],
        classifier=_FailureMap(
            {
                unauthorized: RequestFailure(
                    kind="response",
                    metadata=ResponseFailureMetadata(status_code=401, retry_after=None),
                )
            }
        ),
    )

    response = await outer.request(HttpMethod.GET, "/items")

    assert response.status_code == 204
    assert fetcher.refreshes == [initial]
    assert events == ["inner:before", "inner:before", "inner:after"]
    assert [headers["authorization"] for headers in transport.headers if headers is not None] == [
        "Bearer initial",
        "Bearer replacement",
    ]


@pytest.mark.asyncio
async def test_cancellation_from_retry_wait_or_refresh_is_never_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retry_error = RuntimeError("retry")
    raw = _RawExecutor([retry_error])
    retry_executor = PolicyRequestExecutor(
        raw,
        [TransientRetryPolicy()],
        classifier=_FailureMap({retry_error: RequestFailure(kind="timeout")}),
    )

    async def cancel_sleep(_: float) -> None:
        raise asyncio.CancelledError()

    monkeypatch.setattr(policies_mod.asyncio, "sleep", cancel_sleep)
    with pytest.raises(asyncio.CancelledError):
        await retry_executor.request(HttpMethod.GET, "/items")
    assert len(raw.requests) == 1


@pytest.mark.asyncio
async def test_token_manager_coordinates_conditional_refresh_for_policy_recovery() -> None:
    initial = _token("initial")
    replacement = _token("replacement")
    storage = InMemoryTokenStorage()
    storage.set_token(initial)
    fetcher = _RefreshFetcher(replacement)
    manager = TokenManager(storage, fetcher)

    results = await asyncio.gather(*(manager.refresh_if_current(initial) for _ in range(5)))

    assert fetcher.refreshes == [initial]
    assert results == [replacement] * 5


@pytest.mark.parametrize(
    "retry_after",
    ("NaN", "Infinity", "-1", "1.5", "1e2", "not-a-retry-after"),
)
def test_retry_after_rejects_non_integer_delta_values_and_uses_jitter(
    retry_after: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = TransientRetryPolicy()
    failure = RequestFailure(
        kind="response",
        metadata=ResponseFailureMetadata(status_code=429, retry_after=retry_after),
    )
    monkeypatch.setattr(policies_mod.random, "uniform", lambda *_: 0.125)

    assert policy._delay_for(failure, 0) == 0.125


@pytest.mark.parametrize(
    ("retry_after", "expected"),
    (("0", 0.0), ("5", 5.0), ("999", 30.0)),
)
def test_retry_after_accepts_ascii_nonnegative_integer_delta(
    retry_after: str,
    expected: float,
) -> None:
    assert TransientRetryPolicy()._parse_retry_after(retry_after) == expected


def test_retry_after_retains_valid_http_date() -> None:
    future = datetime.now(timezone.utc) + timedelta(seconds=10)

    delay = TransientRetryPolicy()._parse_retry_after(format_datetime(future, usegmt=True))

    assert delay is not None
    assert 0.0 < delay <= 10.0
