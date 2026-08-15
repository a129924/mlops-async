"""Read-only Projects endpoint client."""

from __future__ import annotations

from json import JSONDecodeError, loads as json_loads
from math import isfinite
from typing import TypeGuard

from mlops_async.clients.projects.value_objects import (
    ChampionModel,
    ProjectDetail,
    ProjectsPage,
    ProjectsResponseError,
    ProjectSummary,
    parse_champion_model,
    parse_project_detail,
    parse_projects_page,
)
from mlops_async.core.http_request import EndpointPath
from mlops_async.core.request_execution import RequestExecutor
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse
from mlops_async.transport.exceptions import HttpErrorContext, InvalidJSONResponseException


class ProjectsClient:
    """Expose read-only Projects and Champion operations."""

    def __init__(self, requester: RequestExecutor) -> None:
        """Store the caller-owned request boundary."""
        self._requester = requester

    async def list_projects(self, *, start: int = 0, limit: int = 20) -> ProjectsPage:
        """Return one server-provided Projects page without fetching another page."""
        _validate_page_input(start, limit)
        response = await self._requester.request(
            HttpMethod.GET,
            EndpointPath.literal("/modelRepository/projects").value,
            params={"start": str(start), "limit": str(limit)},
        )
        return parse_projects_page(_decode_json_response(response))

    async def get_project(self, project_id: str) -> ProjectDetail:
        """Return supported semantic fields for one Project identifier."""
        _validate_identifier(project_id, "project_id")
        response = await self._requester.request(
            HttpMethod.GET,
            EndpointPath.from_segments("modelRepository", "projects", project_id).value,
            params={},
        )
        return parse_project_detail(_decode_json_response(response))

    async def get_project_by_name(
        self, name: str, *, page_size: int = 1000
    ) -> ProjectSummary | None:
        """Find one exact project name through validated sequential page traversal."""
        _validate_identifier(name, "name")
        _validate_lookup_page_size(page_size)
        start = 0
        expected_count: int | None = None
        while True:
            page = await self.list_projects(start=start, limit=page_size)
            expected_count = _validate_lookup_page(page, start, page_size, expected_count)
            for item in page.items:
                if item.name == name:
                    return item
            next_start = start + len(page.items)
            if next_start == expected_count:
                return None
            if len(page.items) < page_size:
                raise ProjectsResponseError(
                    "Projects list response semantic mismatch: short page before exhaustion"
                )
            start = next_start

    async def get_champion(self, project_id: str) -> ChampionModel:
        """Return supported Champion metadata for one Project identifier."""
        _validate_identifier(project_id, "project_id")
        response = await self._requester.request(
            HttpMethod.GET,
            EndpointPath.from_segments("modelRepository", "projects", project_id, "champion").value,
            params={},
        )
        return parse_champion_model(_decode_json_response(response))


def _validate_page_input(start: object, limit: object) -> None:
    if not isinstance(start, int) or isinstance(start, bool) or start < 0:
        raise ValueError("start must be a non-boolean integer greater than or equal to zero")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ValueError("limit must be a non-boolean integer from 1 through 1000")


def _validate_lookup_page_size(page_size: object) -> None:
    if not isinstance(page_size, int) or isinstance(page_size, bool) or not 1 <= page_size <= 1000:
        raise ValueError("page_size must be a non-boolean integer from 1 through 1000")


def _validate_identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_lookup_page(
    page: ProjectsPage, start: int, page_size: int, expected_count: int | None
) -> int:
    if page.count < 0:
        _raise_lookup_error("count must be greater than or equal to zero")
    if page.start != start:
        _raise_lookup_error("start must match the requested start")
    if page.limit != page_size:
        _raise_lookup_error("limit must match the requested page size")
    if expected_count is not None and page.count != expected_count:
        _raise_lookup_error("count must remain fixed during traversal")
    item_count = len(page.items)
    if item_count > page_size:
        _raise_lookup_error("items length must not exceed limit")
    if start + item_count > page.count:
        _raise_lookup_error("items must not overshoot count")
    return page.count if expected_count is None else expected_count


def _raise_lookup_error(detail: str) -> None:
    raise ProjectsResponseError(f"Projects list response semantic mismatch: {detail}")


def _decode_json_response(response: RawClientResponse) -> JSONValue:
    try:
        decoded: object = json_loads(response.content)
    except (JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise InvalidJSONResponseException(_error_context(response)) from exc
    try:
        is_json_value = _is_json_value(decoded)
    except RecursionError as exc:
        raise InvalidJSONResponseException(_error_context(response)) from exc
    if not is_json_value:
        raise InvalidJSONResponseException(_error_context(response))
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
    """Narrow ``json.loads`` output before recursively validating list members."""
    return isinstance(value, list)


def _is_runtime_dict(value: object) -> TypeGuard[dict[object, object]]:
    """Narrow ``json.loads`` output before validating dictionary keys and values."""
    return isinstance(value, dict)


def _error_context(response: RawClientResponse) -> HttpErrorContext:
    return HttpErrorContext(
        status_code=response.status_code,
        method=response.method.value,
        url=response.url,
        body=response.content,
        request_id=response.headers.get("X-Request-ID"),
    )
