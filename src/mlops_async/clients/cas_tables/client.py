"""One-request client for the CAS Tables endpoint family."""

from __future__ import annotations

from json import JSONDecodeError, loads as json_loads
from math import isfinite
from typing import TypeGuard

from mlops_async.clients.cas_tables.value_objects import (
    CasTablesResponseError,
    TableDetail,
    TablesPage,
    TableState,
    parse_table_detail,
    parse_tables_page,
)
from mlops_async.core.http_request import EndpointPath
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse


class CasTablesClient:
    """Expose bounded one-request CAS Tables operations."""

    def __init__(self, requester: Requester) -> None:
        """Store the caller-owned request composition boundary."""
        self._requester = requester

    async def list_tables(
        self, data_source_id: str, *, start: int = 0, limit: int = 20
    ) -> TablesPage:
        """Return one explicit CAS Tables page without pagination expansion."""
        _validate_identifier(data_source_id, "data_source_id")
        _validate_page_input(start, limit)
        endpoint_path = EndpointPath.from_segments(
            "casManagement", "dataSources", data_source_id, "tables"
        )
        response = await self._requester.request(
            HttpMethod.GET,
            endpoint_path.value,
            params={"start": str(start), "limit": str(limit)},
        )
        return parse_tables_page(_decode_json_response(response))

    async def get_table(self, data_source_id: str, table_name: str) -> TableDetail:
        """Return one strict CAS table detail from its data-source endpoint."""
        _validate_identifier(data_source_id, "data_source_id")
        _validate_identifier(table_name, "table_name")
        endpoint_path = EndpointPath.from_segments(
            "casManagement", "dataSources", data_source_id, "tables", table_name
        )
        response = await self._requester.request(HttpMethod.GET, endpoint_path.value, params={})
        return parse_table_detail(_decode_json_response(response))

    async def change_table_state(
        self, server: str, caslib: str, table_name: str, state: str
    ) -> TableDetail:
        """Set one table state with an empty PUT body and no follow-up work."""
        _validate_identifier(server, "server")
        _validate_identifier(caslib, "caslib")
        _validate_identifier(table_name, "table_name")
        table_state = _validate_state_input(state)

        endpoint_path = EndpointPath.from_segments(
            "casManagement", "servers", server, "caslibs", caslib, "tables", table_name, "state"
        )
        response = await self._requester.request(
            HttpMethod.PUT,
            endpoint_path.value,
            params={"value": table_state.value},
            json_body=None,
        )
        return parse_table_detail(_decode_json_response(response))


def _validate_identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_page_input(start: object, limit: object) -> None:
    if not isinstance(start, int) or isinstance(start, bool) or start < 0:
        raise ValueError("start must be a non-boolean integer greater than or equal to zero")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("limit must be a non-boolean positive integer")


def _validate_state_input(value: object) -> TableState:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("state must be a non-empty string")
    try:
        return TableState(value)
    except ValueError:
        raise ValueError("state must be a supported table state") from None


def _decode_json_response(response: RawClientResponse) -> JSONValue:
    try:
        decoded: object = json_loads(response.content)
    except (JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise CasTablesResponseError("CAS Tables response semantic mismatch: invalid JSON") from exc
    if not _is_json_value(decoded):
        raise CasTablesResponseError("CAS Tables response semantic mismatch: invalid JSON value")
    return decoded


def _is_json_value(value: object) -> TypeGuard[JSONValue]:
    if value is None or isinstance(value, str | bool | int):
        return True
    if isinstance(value, float):
        return isfinite(value)
    if _is_runtime_list(value):
        return all(_is_json_value(item) for item in value)
    if _is_runtime_dict(value):
        return all(isinstance(key, str) and _is_json_value(item) for key, item in value.items())
    return False


def _is_runtime_list(value: object) -> TypeGuard[list[object]]:
    """Narrow decoded JSON before recursively validating list members."""
    return isinstance(value, list)


def _is_runtime_dict(value: object) -> TypeGuard[dict[object, object]]:
    """Narrow decoded JSON before recursively validating dictionary members."""
    return isinstance(value, dict)
