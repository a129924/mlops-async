"""One-request client for the Job Execution endpoint family."""

from __future__ import annotations

from json import JSONDecodeError, loads as json_loads
from math import isfinite
from typing import TypeGuard

from mlops_async.clients.job_execution.value_objects import (
    Job,
    JobExecutionResponseError,
    JobState,
    parse_job,
    parse_job_state,
)
from mlops_async.core.http_request import EndpointPath
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

_JOB_ACCEPT = (
    "application/vnd.sas.job.execution.job+json, "
    "application/vnd.sas.job.execution.job.request+json, "
    "application/vnd.sas.error+json, application/json"
)
_COMMON_HEADERS = {"Delegate-Domain": "", "Content-Type": "application/json"}
_JOB_HEADERS = {**_COMMON_HEADERS, "Accept": _JOB_ACCEPT}


class JobExecutionClient:
    """Expose single-request Job Execution operations with caller-owned transport."""

    def __init__(self, requester: Requester) -> None:
        """Store the caller-owned request composition boundary."""
        self._requester = requester

    async def start_job(self, job_request_id: str) -> Job:
        """Start one job from an existing Job Request without sending a body."""
        _validate_identifier(job_request_id, "job_request_id")
        endpoint_path = EndpointPath.from_segments(
            "jobExecution", "jobRequests", job_request_id, "jobs"
        )
        response = await self._requester.request(
            HttpMethod.POST, endpoint_path.value, headers=_JOB_HEADERS, params={}
        )
        return parse_job(_decode_json_response(response))

    async def get_job(self, job_id: str) -> Job:
        """Return the supported semantic fields for one Job identifier."""
        _validate_identifier(job_id, "job_id")
        endpoint_path = EndpointPath.from_segments("jobExecution", "jobs", job_id)
        response = await self._requester.request(
            HttpMethod.GET, endpoint_path.value, headers=_JOB_HEADERS, params={}
        )
        return parse_job(_decode_json_response(response))

    async def get_job_state(self, job_id: str) -> JobState:
        """Return one exact plain-text Job state without polling or normalization."""
        _validate_identifier(job_id, "job_id")
        endpoint_path = EndpointPath.from_segments("jobExecution", "jobs", job_id, "state")
        response = await self._requester.request(
            HttpMethod.GET, endpoint_path.value, headers=_COMMON_HEADERS, params={}
        )
        return parse_job_state(response.content)


def _validate_identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _decode_json_response(response: RawClientResponse) -> JSONValue:
    try:
        decoded: object = json_loads(response.content)
    except (JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise JobExecutionResponseError("Job response semantic mismatch: invalid JSON") from exc
    if not _is_json_value(decoded):
        raise JobExecutionResponseError("Job response semantic mismatch: invalid JSON value")
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
