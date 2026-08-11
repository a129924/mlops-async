from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping

import pytest

import mlops_async.clients.cas_tables.client as cas_tables_client_module
from mlops_async.clients.cas_tables import (
    CasTablesClient,
    CasTablesResponseError,
    TableDetail,
    TablesPage,
    TableState,
)
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from mlops_async.transport.exceptions import HttpErrorContext, HttpTransportException


class _FakeRequester:
    def __init__(self, outcomes: list[RawClientResponse | BaseException]) -> None:
        self._outcomes = outcomes
        self.requests: list[tuple[HttpMethod, str, dict[str, str], dict[str, str], object]] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object = None,
    ) -> RawClientResponse:
        self.requests.append((method, path, dict(headers or {}), dict(params or {}), json_body))
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _response(payload: bytes) -> RawClientResponse:
    return RawClientResponse(
        status_code=200,
        headers=ResponseHeaders(),
        content=payload,
        method=HttpMethod.GET,
        url="https://viya.example.test/casManagement",
    )


@pytest.mark.asyncio
async def test_list_tables_sends_one_request_with_explicit_page_query() -> None:
    requester = _FakeRequester(
        [_response(b'{"items":[{"name":"INPUT","caslib":"CASUSER","state":"loaded"}]}')]
    )
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    page = await client.list_tables("source id/with slash", start=0, limit=20)

    assert page == TablesPage((TableDetail("INPUT", "CASUSER", TableState.LOADED),))
    assert requester.requests == [
        (
            HttpMethod.GET,
            "/casManagement/dataSources/source%20id%2Fwith%20slash/tables",
            {},
            {"start": "0", "limit": "20"},
            None,
        )
    ]


@pytest.mark.asyncio
async def test_get_table_sends_one_request_and_parses_a_strict_detail() -> None:
    requester = _FakeRequester([_response(b'{"name":"INPUT","caslib":"CASUSER","state":"loaded"}')])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    detail = await client.get_table("source", "INPUT/TABLE")

    assert detail == TableDetail("INPUT", "CASUSER", TableState.LOADED)
    assert requester.requests == [
        (
            HttpMethod.GET,
            "/casManagement/dataSources/source/tables/INPUT%2FTABLE",
            {},
            {},
            None,
        )
    ]


@pytest.mark.asyncio
async def test_change_table_state_validates_string_then_sends_empty_body_put() -> None:
    requester = _FakeRequester([_response(b'{"name":"INPUT","caslib":"CASUSER","state":"loaded"}')])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    detail = await client.change_table_state("server", "CAS/USER", "INPUT", "loaded")

    assert detail == TableDetail("INPUT", "CASUSER", TableState.LOADED)
    assert requester.requests == [
        (
            HttpMethod.PUT,
            "/casManagement/servers/server/caslibs/CAS%2FUSER/tables/INPUT/state",
            {},
            {"value": "loaded"},
            None,
        )
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "args", "kwargs"),
    (
        ("list_tables", ("  ",), {}),
        ("list_tables", (1,), {}),
        ("list_tables", ("source",), {"start": "0"}),
        ("list_tables", ("source",), {"start": True}),
        ("list_tables", ("source",), {"start": -1}),
        ("list_tables", ("source",), {"limit": "20"}),
        ("list_tables", ("source",), {"limit": True}),
        ("list_tables", ("source",), {"limit": 0}),
        ("list_tables", ("source",), {"limit": -1}),
        ("get_table", ("  ", "table"), {}),
        ("get_table", (1, "table"), {}),
        ("get_table", ("source", "  "), {}),
        ("get_table", ("source", 1), {}),
        ("change_table_state", ("  ", "caslib", "table", "loaded"), {}),
        ("change_table_state", (1, "caslib", "table", "loaded"), {}),
        ("change_table_state", ("server", "  ", "table", "loaded"), {}),
        ("change_table_state", ("server", 1, "table", "loaded"), {}),
        ("change_table_state", ("server", "caslib", "  ", "loaded"), {}),
        ("change_table_state", ("server", "caslib", 1, "loaded"), {}),
        ("change_table_state", ("server", "caslib", "table", "  "), {}),
        ("change_table_state", ("server", "caslib", "table", 1), {}),
        ("change_table_state", ("server", "caslib", "table", "unsupported"), {}),
    ),
)
async def test_invalid_public_input_fails_before_requester_io(
    method: str, args: tuple[object, ...], kwargs: dict[str, object]
) -> None:
    requester = _FakeRequester([])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        await getattr(client, method)(*args, **kwargs)

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception",
    (
        HttpTransportException(HttpErrorContext(status_code=503, method="GET", url="https://test")),
        asyncio.CancelledError(),
    ),
)
async def test_requester_exceptions_propagate_as_exact_instances(exception: BaseException) -> None:
    requester = _FakeRequester([exception])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    with pytest.raises(type(exception)) as error_info:
        await client.list_tables("source")

    assert error_info.value is exception
    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_invalid_json_and_semantic_response_raise_family_error() -> None:
    requester = _FakeRequester([_response(b"not-json"), _response(b'{"items":[]}')])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    with pytest.raises(CasTablesResponseError):
        await client.list_tables("source")
    with pytest.raises(CasTablesResponseError):
        await client.get_table("source", "table")


@pytest.mark.asyncio
async def test_recursive_decoded_json_response_raises_family_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    decoded: list[object] = []
    decoded.append(decoded)
    monkeypatch.setattr(cas_tables_client_module, "json_loads", lambda _content: decoded)
    requester = _FakeRequester([_response(b"[]")])
    client = CasTablesClient(requester)  # type: ignore[arg-type]

    with pytest.raises(
        CasTablesResponseError,
        match="CAS Tables response semantic mismatch: invalid JSON",
    ) as error_info:
        await client.list_tables("source")

    assert isinstance(error_info.value.__cause__, RecursionError)


def test_public_surface_is_frozen_and_has_no_lifecycle_helpers() -> None:
    assert list(inspect.signature(CasTablesClient).parameters) == ["requester"]
    assert list(inspect.signature(CasTablesClient.list_tables).parameters) == [
        "self",
        "data_source_id",
        "start",
        "limit",
    ]
    list_parameters = inspect.signature(CasTablesClient.list_tables).parameters
    assert list_parameters["start"].kind is inspect.Parameter.KEYWORD_ONLY
    assert list(inspect.signature(CasTablesClient.change_table_state).parameters) == [
        "self",
        "server",
        "caslib",
        "table_name",
        "state",
    ]
    state_parameter = inspect.signature(CasTablesClient.change_table_state).parameters["state"]
    assert state_parameter.annotation == "str"
    assert not hasattr(CasTablesClient, "close")
    assert not hasattr(CasTablesClient, "__aenter__")
    assert Requester.__name__ == "Requester"
