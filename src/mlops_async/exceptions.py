from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

__all__ = ["CustomException", "HttpErrorContext"]


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


class CustomException(Exception):  # noqa: N818 - name frozen by the contract
    """Base exception for all HTTP failures in the internal client contract."""

    def __init__(self, context: HttpErrorContext, message: str | None = None) -> None:
        """Capture the structured context and build the normalized error message."""
        self._context = context
        super().__init__(message or self._build_message(context))

    @property
    def context(self) -> HttpErrorContext:
        """Structured failure context."""
        return self._context

    @property
    def status_code(self) -> int | None:
        """HTTP status code from the failing response."""
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
