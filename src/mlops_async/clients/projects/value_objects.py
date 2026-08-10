"""Semantic response value objects for the Projects endpoint family."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn, TypeGuard

from mlops_async.core.types import JSONValue
from mlops_async.exceptions import MlopsAsyncBaseException

__all__ = [
    "ChampionFile",
    "ChampionModel",
    "ProjectDetail",
    "ProjectSummary",
    "ProjectsPage",
    "ProjectsResponseError",
]


class ProjectsResponseError(MlopsAsyncBaseException):
    """A successful Projects response did not match its semantic contract."""


@dataclass(frozen=True, slots=True)
class ProjectSummary:
    """The supported semantic fields from one Projects list item."""

    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ProjectsPage:
    """One server-returned Projects page without pagination behavior."""

    count: int
    start: int
    limit: int
    items: tuple[ProjectSummary, ...]


@dataclass(frozen=True, slots=True)
class ProjectDetail:
    """The supported semantic fields from one Project detail response."""

    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ChampionFile:
    """One raw Champion file reference, before content download validation."""

    id: str | None
    name: str | None


@dataclass(frozen=True, slots=True)
class ChampionModel:
    """The supported Champion metadata and its raw file references."""

    id: str
    name: str
    score_code_type: str
    files: tuple[ChampionFile, ...]


def parse_projects_page(value: JSONValue) -> ProjectsPage:
    """Parse a validated JSON response into one semantic Projects page."""
    response = _require_object(value, "list")
    items_value = response.get("items")
    if not _is_json_array(items_value):
        _raise_semantic_error("list", "items must be an array")
    return ProjectsPage(
        count=_require_int(response, "count", "list"),
        start=_require_int(response, "start", "list"),
        limit=_require_int(response, "limit", "list"),
        items=tuple(_parse_project_summary(item) for item in items_value),
    )


def parse_project_detail(value: JSONValue) -> ProjectDetail:
    """Parse a validated JSON response into one semantic Project detail."""
    response = _require_object(value, "get")
    return ProjectDetail(
        id=_require_string(response, "id", "get"),
        name=_require_string(response, "name", "get"),
    )


def parse_champion_model(value: JSONValue) -> ChampionModel:
    """Parse a validated JSON response into supported Champion metadata."""
    response = _require_object(value, "champion")
    if "files" not in response:
        files: tuple[ChampionFile, ...] = ()
    else:
        files_value = response["files"]
        if not _is_json_array(files_value):
            _raise_semantic_error("champion", "files must be an array when present")
        files = tuple(_parse_champion_file(item) for item in files_value)
    return ChampionModel(
        id=_require_string(response, "id", "champion"),
        name=_require_string(response, "name", "champion"),
        score_code_type=_require_string(response, "scoreCodeType", "champion"),
        files=files,
    )


def _parse_project_summary(value: JSONValue) -> ProjectSummary:
    item = _require_object(value, "list item")
    return ProjectSummary(
        id=_require_string(item, "id", "list item"),
        name=_require_string(item, "name", "list item"),
    )


def _parse_champion_file(value: JSONValue) -> ChampionFile:
    item = _require_object(value, "champion file")
    return ChampionFile(
        id=_optional_string(item, "id", "champion file"),
        name=_optional_string(item, "name", "champion file"),
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


def _is_json_object(value: JSONValue) -> TypeGuard[dict[str, JSONValue]]:
    return isinstance(value, dict)


def _is_json_array(value: JSONValue | None) -> TypeGuard[list[JSONValue]]:
    return isinstance(value, list)


def _raise_semantic_error(endpoint: str, detail: str) -> NoReturn:
    raise ProjectsResponseError(f"Projects {endpoint} response semantic mismatch: {detail}")
