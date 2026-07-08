from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError, loads as json_loads
from math import isfinite
from typing import TypeGuard, cast
from urllib.parse import quote

from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, JSONValue

__all__ = ["TablesClient", "TablesListResponse"]


@dataclass(frozen=True, slots=True)
class TablesListResponse:
    """Minimal response boundary for the tables runtime MVP."""

    items: tuple[JSONValue, ...]    


class TablesClient:
    """Authenticated tables-link endpoint client backed only by Requester."""

    def __init__(self, requester: Requester) -> None:
        """Store the managed requester used for authenticated table requests."""
        self._requester = requester

    async def list_tables(self, project_id: str) -> TablesListResponse:
        """List tables for one project using the fixed-path MVP baseline."""
        normalized_project_id = _require_non_empty_project_id(project_id)
        encoded_project_id = quote(normalized_project_id, safe="")
        response = await self._requester.request(
            HttpMethod.GET,
            f"/modelRepository/projects/{encoded_project_id}/tables",
        )
        return _parse_list_tables_response(response.content)


def _require_non_empty_project_id(project_id: str) -> str:
    if not project_id.strip():
        raise ValueError("project_id must be a non-empty string")
    return project_id


def _parse_list_tables_response(content: bytes) -> TablesListResponse:
    try:
        payload = json_loads(content)
    except (JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise ValueError("list_tables response must decode to a JSON object") from exc

    if not _is_json_object(payload):
        raise ValueError("list_tables response must decode to a JSON object")

    items = payload.get("items")
    if not _is_json_array(items):
        raise ValueError("list_tables response field 'items' must be a JSON array")

    return TablesListResponse(items=tuple(items))


def _is_json_value(value: object) -> TypeGuard[JSONValue]:
    if value is None or isinstance(value, (str, bool, int)):
        return True

    if isinstance(value, float):
        return isfinite(value)

    if isinstance(value, list):
        return _is_json_array(cast(list[object], value))

    if isinstance(value, dict):
        return _is_json_object(cast(dict[object, object], value))

    return False


def _is_json_object(value: object) -> TypeGuard[dict[str, JSONValue]]:
    if not isinstance(value, dict):
        return False

    mapping_value = cast(dict[object, object], value)
    for key, item in mapping_value.items():
        if not isinstance(key, str) or not _is_json_value(item):
            return False
    return True


def _is_json_array(value: object) -> TypeGuard[list[JSONValue]]:
    if not isinstance(value, list):
        return False

    array_value = cast(list[object], value)
    for item in array_value:
        if not _is_json_value(item):
            return False
    return True
