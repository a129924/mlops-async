"""Semantic response value objects for the Models endpoint family."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn, TypeAlias, TypeGuard

from mlops_async.core.types import JSONValue
from mlops_async.exceptions import MlopsAsyncBaseException

__all__ = [
    "ModelContent",
    "ModelDetail",
    "ModelSummary",
    "ModelsPage",
    "ModelsResponseError",
]

ModelVersion: TypeAlias = int | float | None


class ModelsResponseError(MlopsAsyncBaseException):
    """A successful Models response did not match its semantic contract."""


@dataclass(frozen=True, slots=True)
class ModelContent:
    """Raw model content and optional response metadata from one download."""

    content: bytes
    content_type: str | None
    etag: str | None
    content_range: str | None


@dataclass(frozen=True, slots=True)
class ModelSummary:
    """The supported semantic fields from one Models list item."""

    id: str
    name: str
    project_id: str | None
    model_type: str | None
    score_code_type: str | None
    role: str | None
    version: ModelVersion


@dataclass(frozen=True, slots=True)
class ModelsPage:
    """One server-returned Models page without pagination behavior."""

    count: int
    start: int
    limit: int
    items: tuple[ModelSummary, ...]


@dataclass(frozen=True, slots=True)
class ModelDetail:
    """The supported semantic fields from one Models detail response."""

    id: str
    name: str
    model_type: str | None
    score_code_type: str | None
    project_id: str | None
    role: str | None
    version: ModelVersion


def parse_models_page(value: JSONValue) -> ModelsPage:
    """Parse a validated JSON response into one semantic Models page."""
    response = _require_object(value, "list")
    items_value: JSONValue | None = response.get("items")
    if not _is_json_array(items_value):
        _raise_semantic_error("list", "items must be an array")

    return ModelsPage(
        count=_require_int(response, "count", "list"),
        start=_require_int(response, "start", "list"),
        limit=_require_int(response, "limit", "list"),
        items=tuple(_parse_summary(item) for item in items_value),
    )


def parse_model_detail(value: JSONValue) -> ModelDetail:
    """Parse a validated JSON response into one semantic Model detail."""
    response = _require_object(value, "get")
    return ModelDetail(
        id=_require_string(response, "id", "get"),
        name=_require_string(response, "name", "get"),
        model_type=_optional_string(response, "modelType", "get"),
        score_code_type=_optional_string(response, "scoreCodeType", "get"),
        project_id=_optional_string(response, "projectId", "get"),
        role=_optional_string(response, "role", "get"),
        version=_optional_version(response, "get"),
    )


def _parse_summary(value: JSONValue) -> ModelSummary:
    item = _require_object(value, "list item")
    return ModelSummary(
        id=_require_string(item, "id", "list item"),
        name=_require_string(item, "name", "list item"),
        project_id=_optional_string(item, "projectId", "list item"),
        model_type=_optional_string(item, "modelType", "list item"),
        score_code_type=_optional_string(item, "scoreCodeType", "list item"),
        role=_optional_string(item, "role", "list item"),
        version=_optional_version(item, "list item"),
    )


def _require_object(value: JSONValue, endpoint: str) -> dict[str, JSONValue]:
    if _is_json_object(value):
        return value
    _raise_semantic_error(endpoint, "response must be an object")


def _require_int(response: dict[str, JSONValue], field: str, endpoint: str) -> int:
    value = response.get(field)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    _raise_semantic_error(endpoint, f"{field} must be an integer")


def _require_string(response: dict[str, JSONValue], field: str, endpoint: str) -> str:
    value = response.get(field)
    if isinstance(value, str) and value:
        return value
    _raise_semantic_error(endpoint, f"{field} must be a non-empty string")


def _optional_string(response: dict[str, JSONValue], field: str, endpoint: str) -> str | None:
    if field not in response:
        return None
    value = response[field]
    if isinstance(value, str):
        return value
    _raise_semantic_error(endpoint, f"{field} must be a string when present")


def _optional_version(response: dict[str, JSONValue], endpoint: str) -> ModelVersion:
    if "version" not in response:
        return None
    value = response["version"]
    if isinstance(value, int | float) and not isinstance(value, bool):
        return value
    _raise_semantic_error(endpoint, "version must be a number when present")


def _is_json_object(value: JSONValue) -> TypeGuard[dict[str, JSONValue]]:
    return isinstance(value, dict)


def _is_json_array(value: JSONValue | None) -> TypeGuard[list[JSONValue]]:
    return isinstance(value, list)


def _raise_semantic_error(endpoint: str, detail: str) -> NoReturn:
    raise ModelsResponseError(f"Models {endpoint} response semantic mismatch: {detail}")
