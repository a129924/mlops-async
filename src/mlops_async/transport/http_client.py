from __future__ import annotations

from collections.abc import Mapping
from json import JSONDecodeError, loads as json_loads
from math import isfinite
from types import TracebackType
from typing import TypeGuard, cast

import httpx

from mlops_async.core.client import Client
from mlops_async.core.headers import merge_headers
from mlops_async.core.request_options import ClientRequestOptions, RequestTimeouts
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse, ResponseHeaders
from mlops_async.transport.exceptions import (
    HTTPStatusException,
    HttpErrorContext,
    HttpTransportException,
    InvalidJSONResponseException,
)

__all__ = ["HttpClient"]

_DEFAULT_TIMEOUTS = RequestTimeouts()
_REQUEST_ID_HEADER = "X-Request-ID"
_FORBIDDEN_HTTPX_DEFAULT_HEADER_NAMES = frozenset({"accept-encoding", "connection", "user-agent"})
_FORBIDDEN_DEFAULT_HEADER_NAMES = frozenset(
    {
        "authorization",
        "cookie",
        "proxy-authorization",
        "set-cookie",
        "traceparent",
        "tracestate",
        "baggage",
        "user-agent",
        "x-request-id",
        "x-correlation-id",
        "b3",
        "x-b3-traceid",
        "x-b3-spanid",
        "x-amzn-trace-id",
    }
)
_FORBIDDEN_DEFAULT_HEADER_NAME_FRAGMENTS = frozenset({"session", "trace", "correlation"})


class _CallerOwnedAsyncTransport(httpx.AsyncBaseTransport):
    """Proxy transport that keeps caller-owned transports open."""

    def __init__(self, transport: httpx.AsyncBaseTransport) -> None:
        self._transport = transport

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await self._transport.handle_async_request(request)

    async def aclose(self) -> None:
        """Leave the wrapped transport open for the caller to manage."""


def _timeouts_to_httpx(timeouts: RequestTimeouts) -> httpx.Timeout | None:
    if (
        timeouts.total is None
        and timeouts.connect is None
        and timeouts.read is None
        and timeouts.write is None
    ):
        return None

    return httpx.Timeout(
        timeout=timeouts.total,
        connect=timeouts.connect,
        read=timeouts.read,
        write=timeouts.write,
        pool=None,
    )


def _is_forbidden_default_header_name(header_name: str) -> bool:
    normalized_name = header_name.lower()
    return normalized_name in _FORBIDDEN_DEFAULT_HEADER_NAMES or any(
        fragment in normalized_name for fragment in _FORBIDDEN_DEFAULT_HEADER_NAME_FRAGMENTS
    )


def _validate_default_headers(default_headers: Mapping[str, str] | None) -> dict[str, str]:
    if default_headers is None:
        return {}

    resolved_headers = dict(default_headers)
    forbidden_headers = tuple(
        header_name
        for header_name in resolved_headers
        if _is_forbidden_default_header_name(header_name)
    )
    if forbidden_headers:
        forbidden_header_list = ", ".join(forbidden_headers)
        raise ValueError(
            "default_headers cannot include auth/state/observability headers: "
            f"{forbidden_header_list}"
        )
    return resolved_headers


def _is_json_value(value: object) -> TypeGuard[JSONValue]:
    if value is None or isinstance(value, str | bool | int):
        return True

    if isinstance(value, float):
        return isfinite(value)

    if isinstance(value, list):
        list_value = cast(list[object], value)
        return all(_is_json_value(item) for item in list_value)

    if isinstance(value, dict):
        dict_value = cast(dict[object, object], value)
        return all(
            isinstance(key, str) and _is_json_value(item) for key, item in dict_value.items()
        )

    return False


class HttpClient(Client):
    """Internal concrete `Client` implementation backed by `httpx.AsyncClient`."""

    def __init__(
        self,
        base_url: str | httpx.URL,
        timeout: RequestTimeouts = _DEFAULT_TIMEOUTS,
        verify: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Create a minimal internal HTTP client."""
        self._default_headers = _validate_default_headers(default_headers)

        wrapped_transport = _CallerOwnedAsyncTransport(transport) if transport is not None else None
        resolved_timeout = _timeouts_to_httpx(timeout)

        if resolved_timeout is None and wrapped_transport is None:
            self._client = httpx.AsyncClient(base_url=base_url, verify=verify)
        elif resolved_timeout is None:
            self._client = httpx.AsyncClient(
                base_url=base_url,
                verify=verify,
                transport=wrapped_transport,
            )
        elif wrapped_transport is None:
            self._client = httpx.AsyncClient(
                base_url=base_url,
                verify=verify,
                timeout=resolved_timeout,
            )
        else:
            self._client = httpx.AsyncClient(
                base_url=base_url,
                verify=verify,
                timeout=resolved_timeout,
                transport=wrapped_transport,
            )

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
    ) -> RawClientResponse:
        """Execute an HTTP request and return a raw response only for 2xx outcomes."""
        request_headers = merge_headers(
            {"Accept": "application/json"},
            self._default_headers,
            headers,
        )
        if json_body is not None and "content-type" not in {
            name.lower() for name in request_headers
        }:
            request_headers["Content-Type"] = "application/json"

        resolved_timeout = self._resolve_timeout(options)
        try:
            if resolved_timeout is None:
                request = self._client.build_request(
                    method.value,
                    path,
                    headers=request_headers,
                    params=params,
                    json=json_body,
                    content=content,
                )
            else:
                request = self._client.build_request(
                    method.value,
                    path,
                    headers=request_headers,
                    params=params,
                    json=json_body,
                    content=content,
                    timeout=resolved_timeout,
                )
            self._strip_hidden_default_headers(request, request_headers)
            response = await self._client.send(request)
        except (httpx.HTTPError, httpx.InvalidURL) as exc:
            context = self._context_from_transport_failure(method, path, exc)
            raise HttpTransportException(context) from exc

        if 200 <= response.status_code < 300:
            return RawClientResponse(
                status_code=response.status_code,
                headers=ResponseHeaders(response.headers.multi_items()),
                content=response.content,
                method=method,
                url=str(response.url),
            )

        raise HTTPStatusException(self._context_from_response(response))

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
    ) -> JSONValue:
        """Execute an HTTP request and decode a successful JSON response."""
        response = await self.request(
            method,
            path,
            headers=headers,
            params=params,
            json_body=json_body,
            content=content,
            options=options,
        )

        try:
            decoded = json_loads(response.content)
        except (JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
            raise InvalidJSONResponseException(self._context_from_raw_response(response)) from exc

        try:
            valid = _is_json_value(decoded)
        except RecursionError as exc:
            raise InvalidJSONResponseException(self._context_from_raw_response(response)) from exc

        if not valid:
            raise InvalidJSONResponseException(self._context_from_raw_response(response))

        return decoded

    async def aclose(self) -> None:
        """Close resources owned by the concrete client."""
        await self._client.aclose()

    async def __aenter__(self) -> HttpClient:
        """Return the client instance for async context manager usage."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the client when leaving an async context manager."""
        del exc_type, exc, traceback
        await self.aclose()

    def _resolve_timeout(self, options: ClientRequestOptions | None) -> httpx.Timeout | None:
        if options is None:
            return None

        return _timeouts_to_httpx(options.timeout)

    def _strip_hidden_default_headers(
        self,
        request: httpx.Request,
        request_headers: Mapping[str, str],
    ) -> None:
        explicit_header_names = {name.lower() for name in request_headers}
        for header_name in _FORBIDDEN_HTTPX_DEFAULT_HEADER_NAMES - explicit_header_names:
            if header_name in request.headers:
                del request.headers[header_name]

    def _context_from_response(self, response: httpx.Response) -> HttpErrorContext:
        return HttpErrorContext(
            status_code=response.status_code,
            method=response.request.method,
            url=str(response.request.url),
            body=response.content,
            request_id=response.headers.get(_REQUEST_ID_HEADER),
        )

    def _context_from_raw_response(self, response: RawClientResponse) -> HttpErrorContext:
        return HttpErrorContext(
            status_code=response.status_code,
            method=response.method.value,
            url=response.url,
            body=response.content,
            request_id=response.headers.get(_REQUEST_ID_HEADER),
        )

    def _context_from_transport_failure(
        self,
        method: HttpMethod,
        path: str,
        error: httpx.HTTPError | httpx.InvalidURL,
    ) -> HttpErrorContext:
        request = error.request if isinstance(error, httpx.RequestError) else None
        if request is not None:
            return HttpErrorContext(
                status_code=None,
                method=request.method,
                url=str(request.url),
                request_id=None,
            )

        return HttpErrorContext(
            status_code=None,
            method=method.value,
            url=self._safe_transport_failure_url(path),
            request_id=None,
        )

    def _safe_transport_failure_url(self, path: str) -> str:
        base_url = str(self._client.base_url).rstrip("/")
        safe_path = path if path.startswith("/") else f"/{path}" if path else "/"
        return f"{base_url}{safe_path}"
