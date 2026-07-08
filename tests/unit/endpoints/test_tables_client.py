from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse, ResponseHeaders
from mlops_async.endpoints.tables import TablesClient, TablesListResponse


@dataclass
class _RecordedRequest:
    method: HttpMethod
    path: str
    headers: Mapping[str, str] | None
    params: Mapping[str, str] | None
    json_body: JSONValue | None
    content: bytes | None
    options: ClientRequestOptions | None


class _FakeRequester:
    def __init__(self, response: RawClientResponse) -> None:
        self._response = response
        self.requests: list[_RecordedRequest] = []

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
        self.requests.append(
            _RecordedRequest(
                method=method,
                path=path,
                headers=headers,
                params=params,
                json_body=json_body,
                content=content,
                options=options,
            )
        )
        return self._response


class _CancelledRequester:
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
        raise asyncio.CancelledError


def _raw_json_response(content: bytes) -> RawClientResponse:
    return RawClientResponse(
        status_code=200,
        headers=ResponseHeaders((("Content-Type", "application/json"),)),
        content=content,
        method=HttpMethod.GET,
        url="https://example.test/modelRepository/projects/project-id-abc-123/tables",
    )


@pytest.mark.asyncio
async def test_list_tables_delegates_fixed_path_request_and_returns_minimal_response_boundary() -> (
    None
):
    requester = _FakeRequester(
        _raw_json_response(b'{"items": [{"id": "tbl-1"}, {"name": "tbl-2"}]}')
    )
    client = TablesClient(requester)

    result = await client.list_tables("project-id-abc-123")

    assert result == TablesListResponse(items=({"id": "tbl-1"}, {"name": "tbl-2"}))
    assert requester.requests == [
        _RecordedRequest(
            method=HttpMethod.GET,
            path="/modelRepository/projects/project-id-abc-123/tables",
            headers=None,
            params=None,
            json_body=None,
            content=None,
            options=None,
        )
    ]


@pytest.mark.asyncio
async def test_list_tables_percent_encodes_reserved_project_id_characters() -> None:
    requester = _FakeRequester(_raw_json_response(b'{"items": []}'))
    client = TablesClient(requester)

    await client.list_tables("project/id?draft=yes")

    assert (
        requester.requests[0].path
        == "/modelRepository/projects/project%2Fid%3Fdraft%3Dyes/tables"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("project_id", ["", "   "])
async def test_list_tables_rejects_blank_project_id(project_id: str) -> None:
    requester = _FakeRequester(_raw_json_response(b'{"items": []}'))
    client = TablesClient(requester)

    with pytest.raises(ValueError, match="project_id must be a non-empty string"):
        await client.list_tables(project_id)

    assert requester.requests == []


@pytest.mark.asyncio
async def test_list_tables_does_not_build_authorization_headers_in_family_client() -> None:
    requester = _FakeRequester(_raw_json_response(b'{"items": []}'))
    client = TablesClient(requester)

    await client.list_tables("project-id-abc-123")

    assert requester.requests[0].headers is None


def test_tables_client_keeps_only_requester_dependency() -> None:
    requester = _FakeRequester(_raw_json_response(b'{"items": []}'))
    client = TablesClient(requester)

    assert vars(client) == {"_requester": requester}
    assert not hasattr(client, "_auth_client")
    assert not hasattr(client, "_token_manager")
    assert not hasattr(client, "_token_storage")
    assert not hasattr(client, "_token_endpoint_client")


@pytest.mark.asyncio
async def test_list_tables_re_raises_request_cancellation_without_translation() -> None:
    client = TablesClient(_CancelledRequester())

    with pytest.raises(asyncio.CancelledError):
        await client.list_tables("project-id-abc-123")


@pytest.mark.asyncio
async def test_list_tables_rejects_non_object_json_payload() -> None:
    requester = _FakeRequester(_raw_json_response(b'["not-an-object"]'))
    client = TablesClient(requester)

    with pytest.raises(ValueError, match="list_tables response must decode to a JSON object"):
        await client.list_tables("project-id-abc-123")


@pytest.mark.asyncio
async def test_list_tables_rejects_non_list_items_field() -> None:
    requester = _FakeRequester(_raw_json_response(b'{"items": {"id": "tbl-1"}}'))
    client = TablesClient(requester)

    with pytest.raises(ValueError, match="list_tables response field 'items' must be a JSON array"):
        await client.list_tables("project-id-abc-123")
