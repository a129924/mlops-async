from __future__ import annotations

import inspect
from typing import get_type_hints

import httpx
import pytest

import mlops_async
import mlops_async.core.client as core_client
import mlops_async.transport.http_client as transport_http_client
from mlops_async.core.client import Client
from mlops_async.core.http_request import HttpRequest
from mlops_async.core.types import JSONValue, RawClientResponse


def _http_client_class() -> type[Client]:
    http_client: type[Client] = transport_http_client.HttpClient
    assert inspect.isclass(http_client)
    return http_client


def test_client_protocol_uses_repo_owned_types_only() -> None:
    request_hints = get_type_hints(Client.request)
    request_json_hints = get_type_hints(Client.request_json)
    request_signature = inspect.signature(Client.request)

    assert request_signature.parameters["options"].name == "options"
    assert request_hints["return"] is RawClientResponse
    assert request_json_hints["return"] == JSONValue
    assert "httpx" not in inspect.getsource(core_client)


@pytest.mark.asyncio
async def test_transport_http_client_satisfies_client_protocol_without_package_root_promotion() -> (
    None
):
    http_client = _http_client_class()
    client = http_client(
        "https://example.com",
        transport=httpx.MockTransport(lambda request: httpx.Response(204, request=request)),
    )

    try:
        assert isinstance(client, Client)
    finally:
        await client.aclose()


def test_transport_http_client_nominally_inherits_client_protocol() -> None:
    http_client = _http_client_class()

    assert http_client.__bases__ == (Client,)
    assert Client in http_client.__mro__


def test_package_root_does_not_reexport_internal_client_symbols() -> None:
    assert not hasattr(mlops_async, "HttpClient")
    assert not hasattr(mlops_async, "Client")
    assert not hasattr(mlops_async, "RequestTimeouts")
    assert not hasattr(mlops_async, "RawClientResponse")
    assert not hasattr(mlops_async, "HttpTransportException")
    assert not hasattr(mlops_async, "HTTPStatusException")
    assert not hasattr(mlops_async, "InvalidJSONResponseException")


def test_client_contract_is_execution_first_with_json_primitive_adapters() -> None:
    execute_signature = inspect.signature(Client.execute)
    execute_hints = get_type_hints(Client.execute)

    assert tuple(execute_signature.parameters) == ("self", "request")
    assert execute_hints["request"] is HttpRequest
    assert execute_hints["return"] is RawClientResponse
    assert hasattr(Client, "request")
    assert hasattr(Client, "request_json")


def test_client_primitive_adapter_and_canonical_execution_have_matching_request_contracts() -> None:
    primitive_signature = inspect.signature(Client.request)
    execute_signature = inspect.signature(Client.execute)

    assert tuple(primitive_signature.parameters) == (
        "self",
        "method",
        "path",
        "headers",
        "params",
        "json_body",
        "content",
        "options",
    )
    assert tuple(execute_signature.parameters) == ("self", "request")
    assert get_type_hints(Client.request)["return"] is RawClientResponse
