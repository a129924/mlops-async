from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import get_type_hints

import httpx
import pytest

import mlops_async
import mlops_async.core.client as client_module
from mlops_async.core.client import Client
from mlops_async.core.types import JSONValue, RawClientResponse


def _http_client_class() -> type[Client]:
    try:
        module = importlib.import_module("mlops_async.transport.http_client")
    except ModuleNotFoundError as exc:
        pytest.fail(
            "Concrete HttpClient must live at mlops_async.transport.http_client; "
            f"import failed: {exc}"
        )
    http_client: type[Client] = module.HttpClient
    assert inspect.isclass(http_client)
    return http_client


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_client_protocol_uses_repo_owned_types_only() -> None:
    request_hints = get_type_hints(Client.request)
    request_json_hints = get_type_hints(Client.request_json)
    request_signature = inspect.signature(Client.request)

    assert request_signature.parameters["options"].name == "options"
    assert request_hints["return"] is RawClientResponse
    assert request_json_hints["return"] == JSONValue
    assert "httpx" not in inspect.getsource(client_module)


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


def test_transport_http_client_is_only_supported_concrete_client_module_path() -> None:
    assert importlib.util.find_spec("mlops_async.transport.http_client") is not None
    assert importlib.util.find_spec("mlops_async.core.http_client") is None
    assert not (_repo_root() / "src/mlops_async/core/http_client.py").exists()


def test_package_root_does_not_reexport_internal_client_symbols() -> None:
    assert not hasattr(mlops_async, "HttpClient")
    assert not hasattr(mlops_async, "Client")
    assert not hasattr(mlops_async, "RequestTimeouts")
    assert not hasattr(mlops_async, "RawClientResponse")
    assert not hasattr(mlops_async, "HttpTransportException")
    assert not hasattr(mlops_async, "HTTPStatusException")
    assert not hasattr(mlops_async, "InvalidJSONResponseException")
