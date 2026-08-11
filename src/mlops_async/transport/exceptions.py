from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlsplit

from mlops_async.core.request_failure import RequestFailureKind, ResponseFailureMetadata
from mlops_async.exceptions import MlopsAsyncBaseException

_FailureKind = Literal["connection", "timeout", "response"]

__all__ = [  # noqa: RUF022 - export order is locked by the topic contract and tested directly.
    "HttpErrorContext",
    "HttpTransportException",
    "HTTPStatusException",
    "InvalidJSONResponseException",
]


@dataclass(frozen=True, slots=True)
class HttpErrorContext:
    """Structured context captured at the HTTP failure boundary."""

    status_code: int | None
    method: str
    url: str
    body: bytes = b""
    request_id: str | None = None

    @property
    def body_snippet(self) -> str:
        """First 512 bytes of the response body decoded as UTF-8."""
        return self.body[:512].decode("utf-8", errors="replace")


class HttpTransportException(MlopsAsyncBaseException):
    """Transport-level request failure."""

    def __init__(
        self,
        context: HttpErrorContext,
        message: str | None = None,
        *,
        failure_kind: RequestFailureKind | None = None,
        retry_after: str | None = None,
    ) -> None:
        """Capture structured context and build a normalized error message."""
        self._context = context
        self._failure_metadata = ResponseFailureMetadata(
            status_code=context.status_code,
            retry_after=retry_after,
        )
        self._failure_kind: _FailureKind | None = (
            failure_kind
            if failure_kind is not None
            else "response"
            if context.status_code
            else None
        )
        super().__init__(message or self._build_message(context))

    @property
    def context(self) -> HttpErrorContext:
        """Structured failure context."""
        return self._context

    @property
    def status_code(self) -> int | None:
        """HTTP status code from the failing response, if present."""
        return self._context.status_code

    @property
    def method(self) -> str:
        """HTTP method used in the failing request."""
        return self._context.method

    @property
    def url(self) -> str:
        """Full URL of the failing request."""
        return self._context.url

    @property
    def body_snippet(self) -> str:
        """First 512 bytes of the response body decoded as UTF-8."""
        return self._context.body_snippet

    @property
    def request_id(self) -> str | None:
        """Request correlation ID from the response headers, if present."""
        return self._context.request_id

    @property
    def failure_metadata(self) -> ResponseFailureMetadata:
        """Private transport-neutral metadata for request failure classification."""
        return self._failure_metadata

    @property
    def failure_kind(self) -> _FailureKind | None:
        """Private transport-neutral failure kind for request classification."""
        return self._failure_kind

    @staticmethod
    def _normalized_path(url: str) -> str:
        path = urlsplit(url).path
        return path or "/"

    @classmethod
    def _build_message(cls, context: HttpErrorContext) -> str:
        path = cls._normalized_path(context.url)
        status_fragment = (
            f"HTTP {context.status_code}" if context.status_code is not None else "request failure"
        )
        message = f"{context.method} {path} -> {status_fragment}"
        if context.request_id:
            message = f"{message} [request_id={context.request_id}]"
        return message


class HTTPStatusException(HttpTransportException):
    """Non-2xx HTTP response returned by the transport layer."""


class InvalidJSONResponseException(HttpTransportException):
    """HTTP success response whose body could not be decoded as JSON."""

    @classmethod
    def _build_message(cls, context: HttpErrorContext) -> str:
        path = cls._normalized_path(context.url)
        status_fragment = (
            f"HTTP {context.status_code}" if context.status_code is not None else "request failure"
        )
        message = f"{context.method} {path} -> invalid JSON response ({status_fragment})"
        if context.request_id:
            message = f"{message} [request_id={context.request_id}]"
        return message
