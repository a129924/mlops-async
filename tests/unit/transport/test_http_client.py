from __future__ import annotations

import inspect
import ssl
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from types import ModuleType
from typing import NoReturn, get_type_hints
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

import mlops_async.core.headers as headers_mod
import mlops_async.transport.exceptions as transport_exceptions
import mlops_async.transport.http_client as transport_http_client
from mlops_async.core.client import Client
from mlops_async.core.http_request import (
    BaseUrl,
    EndpointPath,
    Headers,
    HttpRequest,
    JsonBody,
    QueryParams,
    RawBody,
)
from mlops_async.core.request_options import ClientRequestOptions, RequestTimeouts
from mlops_async.core.types import HttpMethod, RawClientResponse


def _http_client_class() -> type[Client]:
    http_client = getattr(transport_http_client, "HttpClient", None)
    assert inspect.isclass(http_client)
    return http_client


def _transport_exceptions() -> ModuleType:
    return transport_exceptions


def _exception_type(name: str) -> type[BaseException]:
    module = _transport_exceptions()
    exception_type = getattr(module, name, None)
    assert inspect.isclass(exception_type)
    return exception_type


class TrackingTransport(httpx.AsyncBaseTransport):
    def __init__(
        self,
        handler: Callable[[httpx.Request], Awaitable[httpx.Response]],
    ) -> None:
        self._handler = handler
        self.closed = False
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return await self._handler(request)

    async def aclose(self) -> None:
        self.closed = True


def _json_response(
    request: httpx.Request,
    *,
    status_code: int = 200,
    content: bytes = b'{"ok": true}',
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        headers=headers
        or {
            "Content-Type": "application/json",
            "X-Request-ID": "req-1",
        },
        content=content,
        request=request,
    )


def test_constructor_surface_is_locked_to_minimal_transport_parameters() -> None:
    http_client = _http_client_class()
    parameters = inspect.signature(http_client).parameters

    assert tuple(parameters) == (
        "base_url",
        "timeout",
        "verify",
        "transport",
        "default_headers",
    )
    assert parameters["base_url"].default is inspect.Signature.empty
    assert parameters["timeout"].default == RequestTimeouts()
    assert "client" not in parameters
    assert "params" not in parameters
    assert "options" not in parameters


def test_constructor_verify_annotation_accepts_bool_or_ssl_context() -> None:
    hints = get_type_hints(transport_http_client.HttpClient.__init__)

    assert hints["verify"] == bool | ssl.SSLContext


def test_constructor_passes_default_verify_true_to_async_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, object] = {}

    def capture_async_client(**kwargs: object) -> object:
        captured_kwargs.update(kwargs)
        return object()

    monkeypatch.setattr(transport_http_client.httpx, "AsyncClient", capture_async_client)

    _http_client_class()("https://example.com")

    assert captured_kwargs["verify"] is True


@pytest.mark.parametrize("verify", [True, False])
def test_constructor_passes_explicit_bool_verify_to_async_client(
    monkeypatch: pytest.MonkeyPatch,
    verify: bool,
) -> None:
    captured_kwargs: dict[str, object] = {}

    def capture_async_client(**kwargs: object) -> object:
        captured_kwargs.update(kwargs)
        return object()

    monkeypatch.setattr(transport_http_client.httpx, "AsyncClient", capture_async_client)

    _http_client_class()("https://example.com", verify=verify)

    assert captured_kwargs["verify"] is verify


@pytest.mark.parametrize(
    ("with_timeout", "with_transport"),
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_constructor_preserves_ssl_context_identity_in_every_client_branch(
    monkeypatch: pytest.MonkeyPatch,
    with_timeout: bool,
    with_transport: bool,
) -> None:
    captured_kwargs: dict[str, object] = {}
    verify = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    constructor_kwargs: dict[str, object] = {"verify": verify}
    if with_timeout:
        constructor_kwargs["timeout"] = RequestTimeouts(total=1.0)
    if with_transport:
        constructor_kwargs["transport"] = httpx.MockTransport(
            lambda request: httpx.Response(204, request=request)
        )

    def capture_async_client(**kwargs: object) -> object:
        captured_kwargs.update(kwargs)
        return object()

    monkeypatch.setattr(transport_http_client.httpx, "AsyncClient", capture_async_client)

    _http_client_class()("https://example.com", **constructor_kwargs)

    assert captured_kwargs["verify"] is verify


@pytest.mark.parametrize(
    "invalid_verify",
    ["company-ca.pem", Path("company-ca.pem"), None, object()],
    ids=["str", "path", "none", "object"],
)
def test_constructor_rejects_unsupported_verify_before_creating_async_client(
    monkeypatch: pytest.MonkeyPatch,
    invalid_verify: object,
) -> None:
    async_client_created = False

    def fail_if_async_client_is_created(**_kwargs: object) -> NoReturn:
        nonlocal async_client_created
        async_client_created = True
        raise AssertionError("AsyncClient must not be created for invalid verify")

    monkeypatch.setattr(
        transport_http_client.httpx,
        "AsyncClient",
        fail_if_async_client_is_created,
    )

    with pytest.raises(TypeError, match=r"^verify must be bool or ssl\.SSLContext$"):
        _http_client_class()(
            "https://example.com",
            **{"verify": invalid_verify},
        )

    assert async_client_created is False


def test_http_client_nominally_inherits_client_protocol() -> None:
    http_client = _http_client_class()

    assert http_client.__bases__ == (Client,)
    assert Client in http_client.__mro__


@pytest.mark.asyncio
async def test_constructor_rejects_complete_async_client_injection() -> None:
    http_client = _http_client_class()

    async with httpx.AsyncClient() as injected_client:
        with pytest.raises(TypeError, match="client"):
            http_client("https://example.com", **{"client": injected_client})


@pytest.mark.asyncio
async def test_transport_http_client_accepts_httpx_url_base_and_satisfies_client_protocol() -> None:
    http_client = _http_client_class()
    client = http_client(
        httpx.URL("https://example.com"),
        transport=httpx.MockTransport(lambda request: httpx.Response(204, request=request)),
    )

    try:
        assert isinstance(client, Client)
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_returns_raw_response_and_applies_minimal_json_headers() -> None:
    http_client = _http_client_class()

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"name": "demo"}')

    transport = TrackingTransport(handler)
    client = http_client(
        "https://example.com",
        transport=transport,
        default_headers={"X-Default": "kept"},
    )

    try:
        response = await client.request(
            HttpMethod.POST,
            "/base/items",
            headers={"X-Request-Level": "present"},
            params={"page": "1"},
            json_body={"name": "demo"},
        )
    finally:
        await client.aclose()

    assert isinstance(response, RawClientResponse)
    assert response.status_code == 200
    assert response.content == b'{"name": "demo"}'
    assert response.method is HttpMethod.POST
    assert response.url == "https://example.com/base/items?page=1"

    sent_request = transport.requests[0]
    expected_headers = headers_mod.json_request_headers(
        {"X-Default": "kept"},
        {"X-Request-Level": "present"},
        json_body={"name": "demo"},
    )
    for header_name, header_value in expected_headers.items():
        assert sent_request.headers[header_name.lower()] == header_value
    assert parse_qs(urlsplit(str(sent_request.url)).query) == {"page": ["1"]}


@pytest.mark.asyncio
async def test_request_preserves_per_request_header_override_without_non_json_content_type() -> (
    None
):
    http_client = _http_client_class()

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204, content=b"")

    transport = TrackingTransport(handler)
    client = http_client(
        "https://example.com",
        transport=transport,
        default_headers={"X-Mode": "default", "X-Kept": "yes"},
    )

    try:
        response = await client.request(
            HttpMethod.GET,
            "/base/items",
            headers={"X-Mode": "request"},
            params={"limit": "5"},
        )
    finally:
        await client.aclose()

    assert response.status_code == 204

    sent_request = transport.requests[0]
    assert sent_request.headers["accept"] == "application/json"
    assert sent_request.headers["x-mode"] == "request"
    assert sent_request.headers["x-kept"] == "yes"
    assert "content-type" not in sent_request.headers
    assert parse_qs(urlsplit(str(sent_request.url)).query) == {"limit": ["5"]}


@pytest.mark.asyncio
async def test_request_json_raises_invalid_json_response_exception_for_deeply_nested_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RecursionError from _is_json_value on deeply nested decoded JSON must map to
    InvalidJSONResponseException, not leak as RecursionError."""
    module = transport_http_client
    http_client = module.HttpClient
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"x": 1}')

    def _raise_recursion(_value: object) -> NoReturn:
        raise RecursionError("max recursion depth exceeded")

    client = http_client("https://example.com", transport=TrackingTransport(handler))
    monkeypatch.setattr(module, "_is_json_value", _raise_recursion)

    try:
        with pytest.raises(
            invalid_json_exception,
            match=r"GET /base/items -> invalid JSON response \(HTTP 200\) \[request_id=req-1\]",
        ) as exc_info:
            await client.request_json(HttpMethod.GET, "/base/items")

        assert isinstance(exc_info.value.__cause__, RecursionError)
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_json_raises_invalid_json_response_exception_for_decoder_recursion_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = transport_http_client
    http_client = module.HttpClient
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"x": 1}')

    def _raise_recursion(_content: bytes) -> NoReturn:
        raise RecursionError("max recursion depth exceeded")

    client = http_client("https://example.com", transport=TrackingTransport(handler))
    monkeypatch.setattr(module, "json_loads", _raise_recursion)

    try:
        with pytest.raises(
            invalid_json_exception,
            match=r"GET /base/items -> invalid JSON response \(HTTP 200\) \[request_id=req-1\]",
        ) as exc_info:
            await client.request_json(HttpMethod.GET, "/base/items")

        assert isinstance(exc_info.value.__cause__, RecursionError)
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_raises_http_status_exception_for_non_2xx_response() -> None:
    http_client = _http_client_class()
    http_status_exception = _exception_type("HTTPStatusException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            request,
            status_code=404,
            content=b'{"error": "not found"}',
            headers={"X-Request-ID": "req-404"},
        )

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        with pytest.raises(
            http_status_exception,
            match=r"GET /base/items -> HTTP 404 \[request_id=req-404\]",
        ) as exc_info:
            await client.request(HttpMethod.GET, "/base/items")

        error = exc_info.value
        assert error.status_code == 404
        assert error.method == "GET"
        assert error.url == "https://example.com/base/items"
        assert error.request_id == "req-404"
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_json_returns_decoded_python_value() -> None:
    http_client = _http_client_class()

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"items": [1, 2, 3]}')

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        response = await client.request_json(HttpMethod.GET, "/base/items")
    finally:
        await client.aclose()

    assert response == {"items": [1, 2, 3]}


@pytest.mark.asyncio
async def test_request_json_raises_invalid_json_response_exception_for_non_json_runtime_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = transport_http_client
    http_client = module.HttpClient
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"items": [1, 2, 3]}')

    client = http_client("https://example.com", transport=TrackingTransport(handler))
    monkeypatch.setattr(module, "json_loads", lambda _content: object())

    try:
        with pytest.raises(
            invalid_json_exception,
            match=r"GET /base/items -> invalid JSON response \(HTTP 200\) \[request_id=req-1\]",
        ):
            await client.request_json(HttpMethod.GET, "/base/items")
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_json_raises_invalid_json_response_exception_for_non_json_success_body() -> (
    None
):
    http_client = _http_client_class()
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            request,
            status_code=200,
            content=b"not-json",
            headers={"Content-Type": "text/plain", "X-Request-ID": "req-invalid"},
        )

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        with pytest.raises(
            invalid_json_exception,
            match=(
                r"GET /base/items -> invalid JSON response \(HTTP 200\) "
                r"\[request_id=req-invalid\]"
            ),
        ) as exc_info:
            await client.request_json(HttpMethod.GET, "/base/items")

        error = exc_info.value
        assert error.status_code == 200
        assert error.request_id == "req-invalid"
        assert "not-json" in error.body_snippet
    finally:
        await client.aclose()


@pytest.mark.parametrize(
    ("content", "request_id"),
    [
        (b"NaN", "req-nan"),
        (b"Infinity", "req-pos-inf"),
        (b"-Infinity", "req-neg-inf"),
    ],
)
@pytest.mark.asyncio
async def test_request_json_rejects_non_finite_json_constants(
    content: bytes,
    request_id: str,
) -> None:
    http_client = _http_client_class()
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            request,
            status_code=200,
            content=content,
            headers={"Content-Type": "application/json", "X-Request-ID": request_id},
        )

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        with pytest.raises(
            invalid_json_exception,
            match=(
                rf"GET /base/items -> invalid JSON response \(HTTP 200\) "
                rf"\[request_id={request_id}\]"
            ),
        ) as exc_info:
            await client.request_json(HttpMethod.GET, "/base/items")

        error = exc_info.value
        assert error.status_code == 200
        assert error.request_id == request_id
        assert error.body_snippet == content.decode("utf-8")
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_json_raises_invalid_json_response_exception_for_empty_success_body() -> None:
    http_client = _http_client_class()
    invalid_json_exception = _exception_type("InvalidJSONResponseException")

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            request,
            status_code=200,
            content=b"",
            headers={"Content-Type": "application/json", "X-Request-ID": "req-empty"},
        )

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        with pytest.raises(
            invalid_json_exception,
            match=r"GET /base/items -> invalid JSON response \(HTTP 200\) \[request_id=req-empty\]",
        ) as exc_info:
            await client.request_json(HttpMethod.GET, "/base/items")

        error = exc_info.value
        assert error.status_code == 200
        assert error.request_id == "req-empty"
        assert error.body_snippet == ""
    finally:
        await client.aclose()


@pytest.mark.parametrize(
    "header_name",
    ["Authorization", "X-Request-ID", "traceparent", "X-Correlation-ID"],
)
def test_constructor_rejects_forbidden_default_headers(header_name: str) -> None:
    http_client = _http_client_class()

    with pytest.raises(
        ValueError,
        match="default_headers cannot include auth/state/observability headers",
    ):
        http_client("https://example.com", default_headers={header_name: "forbidden"})


@pytest.mark.asyncio
async def test_request_wraps_transport_failures_in_http_transport_exception() -> None:
    http_client = _http_client_class()
    transport_exception = _exception_type("HttpTransportException")

    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = http_client("https://example.com", transport=TrackingTransport(handler))

    try:
        with pytest.raises(transport_exception) as exc_info:
            await client.request(HttpMethod.GET, "/base/items")

        error = exc_info.value
        assert error.status_code is None
        assert error.__cause__ is not None
        assert isinstance(error.__cause__, httpx.ConnectError)
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_wraps_invalid_absolute_url_without_request_in_http_transport_exception() -> (
    None
):
    http_client = _http_client_class()
    transport_exception = _exception_type("HttpTransportException")
    client = http_client("https://example.com")

    try:
        with pytest.raises(transport_exception) as exc_info:
            await client.request(HttpMethod.GET, "http://example.com:bad")

        error = exc_info.value
        assert error.status_code is None
        assert error.url == "https://example.com/http://example.com:bad"
        assert str(error) == "GET /http://example.com:bad -> request failure"
        assert isinstance(error.__cause__, httpx.InvalidURL)
        assert str(error.__cause__) == "Invalid port: 'bad'"
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_request_timeout_options_do_not_merge_with_constructor_defaults() -> None:
    http_client = _http_client_class()

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request)

    transport = TrackingTransport(handler)
    client = http_client(
        "https://example.com",
        transport=transport,
        timeout=RequestTimeouts(total=30.0, connect=5.0, read=10.0, write=15.0),
    )

    try:
        await client.request(
            HttpMethod.GET,
            "/base/items",
            options=ClientRequestOptions(timeout=RequestTimeouts(connect=2.5, read=1.5)),
        )
    finally:
        await client.aclose()

    assert transport.requests[0].extensions["timeout"] == {
        "connect": 2.5,
        "read": 1.5,
        "write": None,
        "pool": None,
    }


@pytest.mark.asyncio
async def test_aclose_does_not_close_injected_transport() -> None:
    http_client = _http_client_class()

    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request)

    transport = TrackingTransport(handler)
    client = http_client("https://example.com", transport=transport)

    await client.aclose()

    assert transport.closed is False


def test_execute_surface_accepts_only_a_canonical_http_request() -> None:
    parameters = inspect.signature(transport_http_client.HttpClient.execute).parameters

    assert tuple(parameters) == ("self", "request")
    assert "path" not in parameters
    assert "params" not in parameters
    assert "json_body" not in parameters
    assert "content" not in parameters


@pytest.mark.asyncio
async def test_execute_uses_http_request_url_and_raw_body_without_second_url_semantics() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204)

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://must-not-be-used.example", transport=transport)
    request = HttpRequest(
        method=HttpMethod.POST,
        base_url=BaseUrl.create("https://api.example.test"),
        endpoint_path=EndpointPath.literal("/api/v1/imports"),
        query=QueryParams.create((("tag", "first"), ("tag", "second"))),
        headers=Headers.create((("X-Trace", "canonical"),)),
        body=RawBody(b"raw body"),
        options=None,
    )

    try:
        response = await client.execute(request)
    finally:
        await client.aclose()

    assert response.url == request.url
    assert str(transport.requests[0].url) == request.url
    assert transport.requests[0].content == b"raw body"
    assert transport.requests[0].headers["x-trace"] == "canonical"
    assert "content-type" not in transport.requests[0].headers


@pytest.mark.asyncio
async def test_execute_serializes_json_null_as_json_literal() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204, content=b"")

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://api.example.test", transport=transport)
    request = HttpRequest(
        method=HttpMethod.POST,
        base_url=BaseUrl.create("https://api.example.test"),
        endpoint_path=EndpointPath.literal("/api/v1/items"),
        query=QueryParams.create({}),
        headers=Headers.create({}),
        body=JsonBody(None),
        options=None,
    )

    try:
        await client.execute(request)
    finally:
        await client.aclose()

    assert transport.requests[0].content == b"null"


@pytest.mark.asyncio
async def test_execute_removes_implicit_accept_but_preserves_explicit_accept() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204, content=b"")

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://api.example.test", transport=transport)
    without_accept = HttpRequest(
        method=HttpMethod.GET,
        base_url=BaseUrl.create("https://api.example.test"),
        endpoint_path=EndpointPath.literal("/api/v1/items"),
        query=QueryParams.create({}),
        headers=Headers.create({}),
        body=None,
        options=None,
    )
    with_accept = HttpRequest(
        method=HttpMethod.GET,
        base_url=BaseUrl.create("https://api.example.test"),
        endpoint_path=EndpointPath.literal("/api/v1/items"),
        query=QueryParams.create({}),
        headers=Headers.create({"Accept": "application/vnd.example+json"}),
        body=None,
        options=None,
    )

    try:
        await client.execute(without_accept)
        await client.execute(with_accept)
    finally:
        await client.aclose()

    assert "accept" not in transport.requests[0].headers
    assert transport.requests[1].headers["accept"] == "application/vnd.example+json"


@pytest.mark.asyncio
async def test_primitive_request_adapter_matches_direct_canonical_execution() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204)

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://api.example.test", transport=transport)

    try:
        primitive_response = await client.request(
            HttpMethod.POST,
            "/api/v1/items",
            headers={"X-Trace": "parity"},
            params={"tag": "one"},
            json_body={"name": "demo"},
        )
        canonical_response = await client.execute(
            HttpRequest(
                method=HttpMethod.POST,
                base_url=BaseUrl.create("https://api.example.test"),
                endpoint_path=EndpointPath.literal("/api/v1/items"),
                query=QueryParams.create({"tag": "one"}),
                headers=Headers.create(
                    {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Trace": "parity",
                    }
                ),
                body=JsonBody({"name": "demo"}),
                options=None,
            )
        )
    finally:
        await client.aclose()

    primitive_request, canonical_request = transport.requests
    assert primitive_response.url == canonical_response.url
    assert str(primitive_request.url) == str(canonical_request.url)
    assert primitive_request.content == canonical_request.content
    assert dict(primitive_request.headers) == dict(canonical_request.headers)


@pytest.mark.asyncio
async def test_primitive_request_adapters_preserve_embedded_query() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, content=b'{"ok": true}')

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://api.example.test", transport=transport)

    try:
        primitive_response = await client.request(HttpMethod.GET, "/items?tag=a")
        json_response = await client.request_json(HttpMethod.GET, "/items?tag=a")
    finally:
        await client.aclose()

    assert primitive_response.status_code == 200
    assert json_response == {"ok": True}
    assert [str(request.url) for request in transport.requests] == [
        "https://api.example.test/items?tag=a",
        "https://api.example.test/items?tag=a",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "absolute_path", ("https://legacy.example.test/items", "http://legacy.example.test/items")
)
async def test_primitive_absolute_http_paths_fail_before_http_library_execution(
    monkeypatch: pytest.MonkeyPatch,
    absolute_path: str,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204)

    http_client = _http_client_class()
    transport = TrackingTransport(handler)
    client = http_client("https://api.example.test", transport=transport)
    build_calls = 0
    send_calls = 0

    def fail_build_request(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal build_calls
        build_calls += 1
        raise AssertionError("legacy absolute paths must not reach build_request")

    async def fail_send(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal send_calls
        send_calls += 1
        raise AssertionError("legacy absolute paths must not reach send")

    monkeypatch.setattr(client._client, "build_request", fail_build_request)
    monkeypatch.setattr(client._client, "send", fail_send)

    try:
        transport_exception = _exception_type("HttpTransportException")
        with pytest.raises(transport_exception) as exc_info:
            await client.request(HttpMethod.GET, absolute_path)
    finally:
        await client.aclose()

    assert exc_info.value.status_code is None
    assert exc_info.value.url == absolute_path
    assert build_calls == 0
    assert send_calls == 0
    assert transport.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize("request_adapter", ("request", "request_json"))
@pytest.mark.parametrize(
    "rejected_path",
    (
        "HTTP://legacy.example.test/items",
        "HtTpS://legacy.example.test/items",
        "//legacy.example.test/items",
    ),
)
async def test_primitive_request_adapters_reject_case_varied_absolute_and_network_paths_before_http_library_execution(
    monkeypatch: pytest.MonkeyPatch,
    request_adapter: str,
    rejected_path: str,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(request, status_code=204)

    transport = TrackingTransport(handler)
    client = _http_client_class()("https://api.example.test", transport=transport)
    build_calls = 0
    send_calls = 0

    def fail_build_request(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal build_calls
        build_calls += 1
        raise AssertionError("rejected primitive paths must not reach build_request")

    async def fail_send(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal send_calls
        send_calls += 1
        raise AssertionError("rejected primitive paths must not reach send")

    monkeypatch.setattr(client._client, "build_request", fail_build_request)
    monkeypatch.setattr(client._client, "send", fail_send)

    try:
        transport_exception = _exception_type("HttpTransportException")
        request_method = (
            client.request if request_adapter == "request" else client.request_json
        )
        with pytest.raises(transport_exception) as exc_info:
            await request_method(HttpMethod.GET, rejected_path)
    finally:
        await client.aclose()

    assert exc_info.value.status_code is None
    assert exc_info.value.url == rejected_path
    assert build_calls == 0
    assert send_calls == 0
    assert transport.requests == []
