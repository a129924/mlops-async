"""Semantic response value objects for the Job Execution endpoint family."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import NoReturn, TypeAlias, TypeGuard

from mlops_async.core.types import JSONValue
from mlops_async.exceptions import MlopsAsyncBaseException

__all__ = ["Job", "JobExecutionResponseError", "JobState"]

_JSONContainer: TypeAlias = dict[str, JSONValue] | list[JSONValue]


class JobExecutionResponseError(MlopsAsyncBaseException):
    """A successful Job Execution response did not match its semantic contract."""


class JobState(str, Enum):
    """The six Job Execution states accepted from the service."""

    PENDING = "pending"
    RUNNING = "running"
    CANCELED = "canceled"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timedOut"


@dataclass(frozen=True, slots=True)
class Job:
    """The supported semantic fields from one Job Execution response."""

    id: str | None
    state: JobState | None
    state_details: str | None
    results: Mapping[str, str] | None
    error: Mapping[str, JSONValue] | None
    job_request: Mapping[str, JSONValue] | None
    heartbeat_interval: int | None
    heartbeat_timestamp: str | None
    creation_timestamp: str | None
    modified_timestamp: str | None
    end_timestamp: str | None
    elapsed_time: int | float | None
    log_location: str | None
    expiration_timestamp: str | None
    created_by: str | None
    modified_by: str | None
    submitted_by_application: str | None
    links: tuple[Mapping[str, JSONValue], ...] | None
    version: int | None


def parse_job(value: JSONValue) -> Job:
    """Parse a JSON Job document into the family-local semantic value object."""
    response = _require_object(value, "job")
    state = _optional_state(response)
    state_details = _optional_string(response, "stateDetails")
    if state_details is not None and state is None:
        _raise_semantic_error("job", "stateDetails requires a valid state")
    return Job(
        id=_optional_string(response, "id"),
        state=state,
        state_details=state_details,
        results=_optional_results(response),
        error=_optional_object(response, "error"),
        job_request=_optional_object(response, "jobRequest"),
        heartbeat_interval=_optional_int(response, "heartbeatInterval"),
        heartbeat_timestamp=_optional_string(response, "heartbeatTimeStamp"),
        creation_timestamp=_optional_string(response, "creationTimeStamp"),
        modified_timestamp=_optional_string(response, "modifiedTimeStamp"),
        end_timestamp=_optional_string(response, "endTimeStamp"),
        elapsed_time=_optional_number(response, "elapsedTime"),
        log_location=_optional_string(response, "logLocation"),
        expiration_timestamp=_optional_string(response, "expirationTimeStamp"),
        created_by=_optional_string(response, "createdBy"),
        modified_by=_optional_string(response, "modifiedBy"),
        submitted_by_application=_optional_string(response, "submittedByApplication"),
        links=_optional_links(response),
        version=_optional_int(response, "version"),
    )


def parse_job_state(content: bytes) -> JobState:
    """Parse one exact UTF-8 plain-text Job state without normalization."""
    try:
        return JobState(content.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise JobExecutionResponseError("Job state response semantic mismatch") from exc


def _require_object(value: JSONValue, context: str) -> dict[str, JSONValue]:
    if _is_json_object(value):
        return value
    _raise_semantic_error(context, "response must be an object")


def _optional_string(response: dict[str, JSONValue], field: str) -> str | None:
    value = response.get(field)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    _raise_semantic_error("job", f"{field} must be a string when present")


def _optional_state(response: dict[str, JSONValue]) -> JobState | None:
    value = response.get("state")
    if value is None:
        return None
    if not isinstance(value, str):
        _raise_semantic_error("job", "state must be a string when present")
    try:
        return JobState(value)
    except ValueError as exc:
        raise JobExecutionResponseError("Job response semantic mismatch: unknown state") from exc


def _optional_results(response: dict[str, JSONValue]) -> Mapping[str, str] | None:
    value = response.get("results")
    if value is None:
        return None
    if not _is_json_object(value):
        _raise_semantic_error("job", "results must be an object with string values when present")
    results: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(item, str):
            _raise_semantic_error(
                "job", "results must be an object with string values when present"
            )
        results[key] = item
    return deepcopy(results)


def _optional_object(response: dict[str, JSONValue], field: str) -> Mapping[str, JSONValue] | None:
    value = response.get(field)
    if value is None:
        return None
    if not _is_json_object(value):
        _raise_semantic_error("job", f"{field} must be an object when present")
    return _copy_json_object(value)


def _optional_int(response: dict[str, JSONValue], field: str) -> int | None:
    value = response.get(field)
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    _raise_semantic_error("job", f"{field} must be an integer when present")


def _optional_number(response: dict[str, JSONValue], field: str) -> int | float | None:
    value = response.get(field)
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float) and isfinite(value):
        return value
    _raise_semantic_error("job", f"{field} must be a number when present")


def _optional_links(
    response: dict[str, JSONValue],
) -> tuple[Mapping[str, JSONValue], ...] | None:
    value = response.get("links")
    if value is None:
        return None
    if not _is_json_array(value):
        _raise_semantic_error("job", "links must be an array of objects when present")
    links: list[Mapping[str, JSONValue]] = []
    for item in value:
        if not _is_json_object(item):
            _raise_semantic_error("job", "links must be an array of objects when present")
        links.append(_copy_json_object(item))
    return tuple(links)


def _copy_json_object(value: dict[str, JSONValue]) -> dict[str, JSONValue]:
    copied = _copy_json_value(value)
    if _is_json_object(copied):
        return copied
    raise AssertionError("JSON object copy produced a non-object")


def _copy_json_value(value: JSONValue) -> JSONValue:
    """Copy raw JSON containers iteratively without adding nested validation."""
    if not isinstance(value, dict | list):
        return value

    copied_root: _JSONContainer = {} if isinstance(value, dict) else []
    pending: list[tuple[_JSONContainer, _JSONContainer]] = [(value, copied_root)]
    while pending:
        source, destination = pending.pop()
        if isinstance(source, dict):
            if not isinstance(destination, dict):
                raise AssertionError("JSON container type changed during copy")
            for key, item in source.items():
                if isinstance(item, dict):
                    copied_item: _JSONContainer = {}
                    destination[key] = copied_item
                    pending.append((item, copied_item))
                elif isinstance(item, list):
                    copied_item = []
                    destination[key] = copied_item
                    pending.append((item, copied_item))
                else:
                    destination[key] = item
        else:
            if not isinstance(destination, list):
                raise AssertionError("JSON container type changed during copy")
            for item in source:
                if isinstance(item, dict):
                    copied_item = {}
                    destination.append(copied_item)
                    pending.append((item, copied_item))
                elif isinstance(item, list):
                    copied_item = []
                    destination.append(copied_item)
                    pending.append((item, copied_item))
                else:
                    destination.append(item)
    return copied_root


def _is_json_object(value: JSONValue) -> TypeGuard[dict[str, JSONValue]]:
    return isinstance(value, dict)


def _is_json_array(value: JSONValue) -> TypeGuard[list[JSONValue]]:
    return isinstance(value, list)


def _raise_semantic_error(context: str, detail: str) -> NoReturn:
    raise JobExecutionResponseError(f"Job Execution {context} response semantic mismatch: {detail}")
