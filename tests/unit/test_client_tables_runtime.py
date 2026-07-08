from __future__ import annotations

import json

import httpx
import pytest

from mlops_async.client import PackageLevelClient
from mlops_async.endpoints.tables import TablesClient

_TABLES_PATH = "/modelRepository/projects/project-id-abc-123/tables"


@pytest.mark.asyncio
async def test_package_level_client_wires_tables_without_prefetching_token_on_enter() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/SASLogon/oauth/token":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"access_token": "managed-token", "expires_in": 3600},
                request=request,
            )
        if request.method == "GET" and request.url.path == _TABLES_PATH:
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"items": []},
                request=request,
            )
        raise AssertionError(f"Unexpected outbound request: {request.method} {request.url}")

    client = PackageLevelClient(
        "https://example.test",
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
        transport=httpx.MockTransport(handler),
    )

    async with client as managed_client:
        assert managed_client is client
        assert isinstance(client.tables, TablesClient)
        assert requests == []

        response = await client.tables.list_tables("project-id-abc-123")

    assert response.items == ()
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/SASLogon/oauth/token"),
        ("GET", "/modelRepository/projects/project-id-abc-123/tables"),
    ]
    assert requests[1].headers["authorization"] == "Bearer managed-token"


@pytest.mark.asyncio
async def test_package_level_client_reuses_cached_token_on_second_tables_request() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/SASLogon/oauth/token":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"access_token": "managed-token", "expires_in": 3600},
                request=request,
            )
        if request.method == "GET" and request.url.path == _TABLES_PATH:
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"items": []},
                request=request,
            )
        raise AssertionError(f"Unexpected outbound request: {request.method} {request.url}")

    client = PackageLevelClient(
        "https://example.test",
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
        transport=httpx.MockTransport(handler),
    )

    try:
        await client.tables.list_tables("project-id-abc-123")
        await client.tables.list_tables("project-id-abc-123")
    finally:
        await client.aclose()

    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/SASLogon/oauth/token"),
        ("GET", "/modelRepository/projects/project-id-abc-123/tables"),
        ("GET", "/modelRepository/projects/project-id-abc-123/tables"),
    ]


@pytest.mark.asyncio
async def test_package_level_client_forwards_default_headers_to_tables_requests() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/SASLogon/oauth/token":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"access_token": "managed-token", "expires_in": 3600},
                request=request,
            )
        if request.method == "GET" and request.url.path == _TABLES_PATH:
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                content=json.dumps({"items": []}).encode("utf-8"),
                request=request,
            )
        raise AssertionError(f"Unexpected outbound request: {request.method} {request.url}")

    client = PackageLevelClient(
        "https://example.test",
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
        transport=httpx.MockTransport(handler),
        default_headers={"X-Mode": "runtime"},
    )

    try:
        await client.tables.list_tables("project-id-abc-123")
    finally:
        await client.aclose()

    assert requests[1].headers["x-mode"] == "runtime"
