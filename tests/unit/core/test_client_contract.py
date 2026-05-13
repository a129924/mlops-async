import inspect
import json
from collections.abc import Mapping
from types import TracebackType
from typing import get_type_hints

import pytest

import mlops_async
import mlops_async.core.client as client_module
from mlops_async.core.client import Client
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse, ResponseHeaders
from mlops_async.exceptions import CustomException, HttpErrorContext


class FakeClient:
    def __init__(self, response: RawClientResponse) -> None:
        self._response = response
        self.closed = False

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
        del method, path, headers, params, json_body, content, options
        return self._response

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
        response = await self.request(
            method,
            path,
            headers=headers,
            params=params,
            json_body=json_body,
            content=content,
            options=options,
        )
        request_id = response.headers.get("x-request-id")
        method_name = (
            response.method.value
            if isinstance(response.method, HttpMethod)
            else str(response.method)
        )
        if response.status_code == 204:
            raise CustomException(
                HttpErrorContext(
                    status_code=response.status_code,
                    method=method_name,
                    url=response.url,
                    body=response.content,
                    request_id=request_id,
                )
            )

        try:
            return json.loads(response.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise CustomException(
                HttpErrorContext(
                    status_code=response.status_code,
                    method=method_name,
                    url=response.url,
                    body=response.content,
                    request_id=request_id,
                )
            ) from error

    async def aclose(self) -> None:
        self.closed = True

    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc, traceback
        await self.aclose()


def _build_response(
    *,
    status_code: int = 200,
    content: bytes = b'{"ok": true}',
    url: str = "https://example.com/base/items/?page=1",
) -> RawClientResponse:
    return RawClientResponse(
        status_code=status_code,
        headers=ResponseHeaders((("X-Request-ID", "req-1"), ("Content-Type", "application/json"))),
        content=content,
        method=HttpMethod.GET,
        url=url,
    )


def test_client_protocol_uses_repo_owned_types_only() -> None:
    request_hints = get_type_hints(Client.request)
    request_json_hints = get_type_hints(Client.request_json)
    request_signature = inspect.signature(Client.request)

    assert request_signature.parameters["options"].name == "options"
    assert request_hints["return"] is RawClientResponse
    assert request_json_hints["return"] == JSONValue
    assert "httpx" not in inspect.getsource(client_module)
    assert isinstance(FakeClient(_build_response()), Client)


@pytest.mark.asyncio
async def test_request_preserves_raw_response() -> None:
    response = _build_response(content=b'{"name": "demo"}')
    client = FakeClient(response)

    result = await client.request(HttpMethod.GET, "/items")

    assert result is response
    assert result.headers.get("x-request-id") == "req-1"
    assert result.content == b'{"name": "demo"}'


@pytest.mark.asyncio
async def test_request_json_returns_json_value() -> None:
    client = FakeClient(_build_response(content=b'{"name": "demo"}'))

    result = await client.request_json(HttpMethod.GET, "/items")

    assert result == {"name": "demo"}


@pytest.mark.asyncio
async def test_request_json_rejects_non_json_success_body() -> None:
    client = FakeClient(_build_response(content=b"not-json"))

    with pytest.raises(CustomException, match="/base/items/"):
        await client.request_json(HttpMethod.GET, "/items")


@pytest.mark.asyncio
async def test_no_content_response_stays_on_raw_path() -> None:
    client = FakeClient(_build_response(status_code=204, content=b""))

    response = await client.request(HttpMethod.GET, "/items")

    assert response.status_code == 204

    with pytest.raises(CustomException, match="HTTP 204"):
        await client.request_json(HttpMethod.GET, "/items")


def test_package_root_does_not_reexport_core_contracts() -> None:
    assert not hasattr(mlops_async, "Client")
    assert not hasattr(mlops_async, "RequestTimeouts")
    assert not hasattr(mlops_async, "ResponseHeaders")
    assert not hasattr(mlops_async, "RawClientResponse")
