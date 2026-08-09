"""Read-only Models endpoint client."""

from __future__ import annotations

from json import JSONDecodeError, loads as json_loads
from math import isfinite
from typing import TypeGuard

from mlops_async.clients.models.value_objects import (
    ModelContent,
    ModelDetail,
    ModelsPage,
    parse_model_detail,
    parse_models_page,
)
from mlops_async.core.http_request import EndpointPath
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse
from mlops_async.transport.exceptions import HttpErrorContext, InvalidJSONResponseException


class ModelsClient:
    """Expose one-request Models list and detail operations."""

    def __init__(self, requester: Requester) -> None:
        """Store the caller-owned request composition boundary."""
        self._requester = requester

    async def list_models(
        self,
        *,
        start: int = 0,
        limit: int = 20,
        project_id: str | None = None,
    ) -> ModelsPage:
        """Return one server-provided Models page without fetching another page."""
        _validate_page_input(start, limit, project_id)
        params = {"start": str(start), "limit": str(limit)}
        if project_id is not None:
            params["filter"] = f'in(projectId,"{project_id}")'

        endpoint_path = EndpointPath.literal("/modelRepository/models")
        response = await self._requester.request(
            HttpMethod.GET,
            endpoint_path.value,
            params=params,
        )
        return parse_models_page(_decode_json_response(response))

    async def get_model(self, model_id: str) -> ModelDetail:
        """Return the supported semantic fields for one model identifier."""
        _validate_identifier(model_id, "model_id")
        endpoint_path = EndpointPath.from_segments("modelRepository", "models", model_id)
        response = await self._requester.request(
            HttpMethod.GET,
            endpoint_path.value,
            params={},
        )
        return parse_model_detail(_decode_json_response(response))

    async def get_model_content(
        self,
        model_id: str,
        content_id: str,
        *,
        range_header: str | None = None,
        if_range: str | None = None,
    ) -> ModelContent:
        """Download raw content for one model content identifier."""
        _validate_identifier(model_id, "model_id")
        _validate_identifier(content_id, "content_id")
        _validate_optional_header(range_header, "range_header")
        _validate_optional_header(if_range, "if_range")
        if if_range is not None and range_header is None:
            raise ValueError("if_range requires range_header")

        headers: dict[str, str] = {}
        if range_header is not None:
            headers["Range"] = range_header
        if if_range is not None:
            headers["If-Range"] = if_range

        endpoint_path = EndpointPath.from_segments(
            "modelRepository",
            "models",
            model_id,
            "contents",
            content_id,
            "content",
        )
        response = await self._requester.request(
            HttpMethod.GET,
            endpoint_path.value,
            headers=headers,
            params={},
        )
        return ModelContent(
            content=response.content,
            content_type=response.headers.get("Content-Type"),
            etag=response.headers.get("ETag"),
            content_range=response.headers.get("Content-Range"),
        )


def _validate_page_input(start: object, limit: object, project_id: object) -> None:
    if not isinstance(start, int) or isinstance(start, bool) or start < 0:
        raise ValueError("start must be a non-boolean integer greater than or equal to zero")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("limit must be a non-boolean positive integer")
    if project_id is not None:
        _validate_identifier(project_id, "project_id")


def _validate_identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_optional_header(value: object, name: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"{name} must be a non-empty string when provided")


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
