"""Semantic response value objects for the CAS Tables endpoint family."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NoReturn, TypeGuard

from mlops_async.core.types import JSONValue
from mlops_async.exceptions import MlopsAsyncBaseException

__all__ = [
    "CasTablesResponseError",
    "TableDetail",
    "TableState",
    "TablesPage",
]


class CasTablesResponseError(MlopsAsyncBaseException):
    """A successful CAS Tables response did not match its semantic contract."""


class TableState(str, Enum):
    """The one CAS Table state supported by this bounded endpoint family."""

    LOADED = "loaded"


@dataclass(frozen=True, slots=True)
class TableDetail:
    """The exact semantic fields returned for one CAS table."""

    name: str
    caslib: str
    state: TableState
    created: str
    last_modified: str
    last_accessed: str | None
    source_last_modified: str | None


@dataclass(frozen=True, slots=True)
class TablesPage:
    """One server-provided CAS Tables page without pagination behavior."""

    items: tuple[TableDetail, ...]


def parse_tables_page(value: JSONValue) -> TablesPage:
    """Parse a JSON list envelope into one immutable page of table details."""
    response = _require_object(value, "list")
    items = response.get("items")
    if not _is_json_array(items):
        _raise_semantic_error("list", "items must be an array")
    return TablesPage(items=tuple(_parse_table_detail(item, "list item") for item in items))


def parse_table_detail(value: JSONValue) -> TableDetail:
    """Parse a JSON table detail document into its exact semantic fields."""
    return _parse_table_detail(value, "get")


def _parse_table_detail(value: JSONValue, context: str) -> TableDetail:
    response = _require_object(value, context)
    _require_exact_fields(response, context)
    return TableDetail(
        name=_require_string(response, "name", context),
        caslib=_require_string(response, "caslib", context),
        state=_require_state(response, context),
        created=_require_metadata_string(response, "created", context),
        last_modified=_require_metadata_string(response, "lastModified", context),
        last_accessed=_require_optional_metadata_string(response, "lastAccessed", context),
        source_last_modified=_require_optional_metadata_string(
            response, "sourceLastModified", context
        ),
    )


def _require_object(value: JSONValue, context: str) -> dict[str, JSONValue]:
    if _is_json_object(value):
        return value
    _raise_semantic_error(context, "response must be an object")


def _require_exact_fields(response: dict[str, JSONValue], context: str) -> None:
    allowed_fields = {
        "name",
        "caslib",
        "state",
        "created",
        "lastModified",
        "lastAccessed",
        "sourceLastModified",
    }
    if not set(response) <= allowed_fields:
        _raise_semantic_error(
            context,
            "response must contain only name, caslib, state, created, lastModified, "
            "lastAccessed, and sourceLastModified",
        )


def _require_string(response: dict[str, JSONValue], field: str, context: str) -> str:
    value = response.get(field)
    if isinstance(value, str) and value:
        return value
    _raise_semantic_error(context, f"{field} must be a non-empty string")


def _require_metadata_string(response: dict[str, JSONValue], field: str, context: str) -> str:
    value = response.get(field)
    if isinstance(value, str):
        return value
    _raise_semantic_error(context, f"{field} must be a string")


def _require_optional_metadata_string(
    response: dict[str, JSONValue], field: str, context: str
) -> str | None:
    value = response.get(field)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    _raise_semantic_error(context, f"{field} must be a string when present")


def _require_state(response: dict[str, JSONValue], context: str) -> TableState:
    value = response.get("state")
    if not isinstance(value, str):
        _raise_semantic_error(context, "state must be a string")
    try:
        return TableState(value)
    except ValueError as exc:
        raise CasTablesResponseError(
            f"CAS Tables {context} response semantic mismatch: unknown state"
        ) from exc


def _is_json_object(value: JSONValue) -> TypeGuard[dict[str, JSONValue]]:
    return isinstance(value, dict)


def _is_json_array(value: JSONValue | None) -> TypeGuard[list[JSONValue]]:
    return isinstance(value, list)


def _raise_semantic_error(context: str, detail: str) -> NoReturn:
    raise CasTablesResponseError(f"CAS Tables {context} response semantic mismatch: {detail}")
