"""Stable internal contracts for request execution and recovery policies."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, TypeAlias, cast, runtime_checkable

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

_FrozenJSONValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | tuple["_FrozenJSONValue", ...]
    | Mapping[str, "_FrozenJSONValue"]
)


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

    def __post_init__(self) -> None:
        """Snapshot caller-owned collections before policies can observe them."""
        if self.headers is not None:
            object.__setattr__(self, "headers", MappingProxyType(dict(self.headers)))
        if self.params is not None:
            object.__setattr__(self, "params", MappingProxyType(dict(self.params)))
        object.__setattr__(self, "json_body", _freeze_json(self.json_body))


def thaw_json_body(value: JSONValue | None) -> JSONValue | None:
    """Return a mutable JSON value for the transport boundary from an invocation snapshot."""
    return _thaw_json(cast(_FrozenJSONValue | None, value))


def _freeze_json(value: JSONValue | None) -> _FrozenJSONValue | None:
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    return value


def _thaw_json(value: _FrozenJSONValue | None) -> JSONValue | None:
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    return value


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
