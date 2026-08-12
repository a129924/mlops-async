"""Stable internal contracts for request execution and recovery policies."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from mlops_async.core.request_failure import RequestFailure
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = [
    "AuthRecoveryAttempt",
    "AuthRecoveryExecutor",
    "RequestExecutor",
    "RequestFailureClassifier",
    "RequestInvocation",
]


@dataclass(frozen=True, slots=True)
class RequestInvocation:
    """One immutable request invocation passed through policy decorators."""

    method: HttpMethod
    path: str
    headers: Mapping[str, str] | None = None
    params: Mapping[str, str] | None = None
    json_body: JSONValue | None = None
    content: bytes | None = None
    options: ClientRequestOptions | None = None


@dataclass(frozen=True, slots=True)
class AuthRecoveryAttempt:
    """One prepared send and the exact managed token used for that send."""

    token: AccessToken | None
    send: Callable[[], Awaitable[RawClientResponse]]


@runtime_checkable
class RequestExecutor(Protocol):
    """Internal request surface consumed by endpoint clients and policies."""

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse: ...


@runtime_checkable
class AuthRecoveryExecutor(RequestExecutor, Protocol):
    """Request executor capable of one token-aware recovery attempt."""

    async def prepare_auth_recovery_attempt(
        self, invocation: RequestInvocation
    ) -> AuthRecoveryAttempt: ...

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None: ...


@runtime_checkable
class RequestFailureClassifier(Protocol):
    """Injected classifier for transport-neutral resilience decisions."""

    def classify(self, error: BaseException) -> RequestFailure | None: ...
