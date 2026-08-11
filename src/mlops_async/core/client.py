from __future__ import annotations

from types import TracebackType
from typing import Protocol, TypeVar, runtime_checkable
from collections.abc import Mapping

from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.request_failure import RequestFailure, ResponseFailureMetadata
from mlops_async.core.http_request import HttpRequest
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = ["Client"]

_ClientT = TypeVar("_ClientT", bound="Client")


@runtime_checkable
class Client(Protocol):
    """Internal-only contract for the async HTTP client boundary."""

    async def execute(self, request: HttpRequest) -> RawClientResponse: ...

    def failure_for(self, exception: BaseException) -> RequestFailure | None:
        """Classify a private transport failure without importing its implementation."""
        kind = getattr(exception, "failure_kind", None)
        metadata = getattr(exception, "failure_metadata", None)
        if kind not in ("connection", "timeout", "response"):
            return None
        if metadata is not None and not isinstance(metadata, ResponseFailureMetadata):
            return None
        return RequestFailure(kind=kind, metadata=metadata)

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

    async def request_json(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> JSONValue: ...

    async def aclose(self) -> None: ...

    async def __aenter__(self: _ClientT) -> _ClientT: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
