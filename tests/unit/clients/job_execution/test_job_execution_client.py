from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

import mlops_async
from mlops_async.clients.job_execution import (
    Job,
    JobExecutionClient,
    JobExecutionResponseError,
    JobState,
)
from mlops_async.core.request_execution import RequestExecutor
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from mlops_async.resilience import PolicyRequestExecutor

_JOB_ACCEPT = (
    "application/vnd.sas.job.execution.job+json, "
    "application/vnd.sas.job.execution.job.request+json, "
    "application/vnd.sas.error+json, application/json"
)
_STATE_HEADERS = {
    "Delegate-Domain": "",
    "Content-Type": "application/json",
    "Accept": "text/plain",
}


@dataclass(frozen=True)
class _RecordedRequest:
    method: HttpMethod
    path: str
    headers: dict[str, str]
    params: dict[str, str]
    json_body: object | None


class _FakeRequester:
    def __init__(self, outcomes: list[RawClientResponse | BaseException]) -> None:
        self._outcomes = outcomes
        self.requests: list[_RecordedRequest] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object | None = None,
    ) -> RawClientResponse:
        self.requests.append(
            _RecordedRequest(method, path, dict(headers or {}), dict(params or {}), json_body)
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _response(content: bytes, *, method: HttpMethod = HttpMethod.GET) -> RawClientResponse:
    return RawClientResponse(
        200,
        ResponseHeaders(),
        content,
        method,
        "https://viya.example.test/jobExecution/jobs/job-1",
    )


@pytest.mark.asyncio
async def test_start_job_makes_one_bodyless_post_with_locked_headers_and_encoded_identifier() -> (
    None
):
    requester = _FakeRequester(
        [_response(b'{"id":"job-1","state":"pending"}', method=HttpMethod.POST)]
    )

    client = JobExecutionClient(requester)  # type: ignore[arg-type]
    job = await client.start_job("request id/slash")

    assert job.id == "job-1"
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.POST,
            "/jobExecution/jobRequests/request%20id%2Fslash/jobs",
            {"Delegate-Domain": "", "Content-Type": "application/json", "Accept": _JOB_ACCEPT},
            {},
            None,
        )
    ]


@pytest.mark.asyncio
async def test_get_job_makes_one_request_with_locked_headers_and_no_body() -> None:
    requester = _FakeRequester([_response(b'{"id":"job-1","state":"running"}')])

    job = await JobExecutionClient(requester).get_job("job id/slash")  # type: ignore[arg-type]

    assert job.state is JobState.RUNNING
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/jobExecution/jobs/job%20id%2Fslash",
            {"Delegate-Domain": "", "Content-Type": "application/json", "Accept": _JOB_ACCEPT},
            {},
            None,
        )
    ]


@pytest.mark.asyncio
async def test_job_execution_client_accepts_a_decorated_executor_without_shape_drift() -> None:
    raw = _FakeRequester([_response(b'{"id":"job-1","state":"running"}')])
    client = JobExecutionClient(PolicyRequestExecutor(raw, []))

    job = await client.get_job("job-1")

    assert job.id == "job-1"
    assert raw.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/jobExecution/jobs/job-1",
            {"Delegate-Domain": "", "Content-Type": "application/json", "Accept": _JOB_ACCEPT},
            {},
            None,
        )
    ]


@pytest.mark.asyncio
async def test_get_job_state_makes_one_plain_text_request_without_json_decoding_or_normalization():
    requester = _FakeRequester([_response(b"timedOut")])

    client = JobExecutionClient(requester)  # type: ignore[arg-type]
    state = await client.get_job_state("job id/slash")

    assert state is JobState.TIMED_OUT
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/jobExecution/jobs/job%20id%2Fslash/state",
            _STATE_HEADERS,
            {},
            None,
        )
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", ("start_job", "get_job", "get_job_state"))
async def test_requester_exceptions_and_cancellation_propagate_unchanged(method_name: str) -> None:
    for exception in (RuntimeError("transport failed"), asyncio.CancelledError()):
        requester = _FakeRequester([exception])
        client = JobExecutionClient(requester)  # type: ignore[arg-type]

        with pytest.raises(type(exception)) as error_info:
            await getattr(client, method_name)("identifier")

        assert error_info.value is exception
        assert len(requester.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", ("start_job", "get_job", "get_job_state"))
async def test_invalid_identifiers_fail_before_requester_io(method_name: str) -> None:
    requester = _FakeRequester([])
    client = JobExecutionClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        await getattr(client, method_name)(" ")

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "content"),
    (("start_job", b"not-json"), ("get_job", b"[]"), ("get_job_state", b"running\n")),
)
async def test_semantic_response_failures_raise_the_family_error(
    method_name: str, content: bytes
) -> None:
    requester = _FakeRequester([_response(content)])
    client = JobExecutionClient(requester)  # type: ignore[arg-type]

    with pytest.raises(JobExecutionResponseError):
        await getattr(client, method_name)("job-1")

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_start_job_translates_non_utf8_json_success_response_to_family_error() -> None:
    requester = _FakeRequester([_response(b"\xff", method=HttpMethod.POST)])

    with pytest.raises(JobExecutionResponseError):
        await JobExecutionClient(requester).start_job("job-1")  # type: ignore[arg-type]

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_job_rejects_non_finite_elapsed_time_decoded_from_json() -> None:
    requester = _FakeRequester([_response(b'{"elapsedTime":1e400}')])

    with pytest.raises(JobExecutionResponseError):
        await JobExecutionClient(requester).get_job("job-1")  # type: ignore[arg-type]

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_json_response_allows_a_deeply_nested_unmodeled_container() -> None:
    nested_container = "[" * 400 + "null" + "]" * 400
    content = ('{"id":"job-1","state":"running","unmodeled":' + nested_container + "}").encode()
    requester = _FakeRequester([_response(content)])

    job = await JobExecutionClient(requester).get_job("job-1")  # type: ignore[arg-type]

    assert job.id == "job-1"
    assert job.state is JobState.RUNNING


def test_job_execution_client_has_the_frozen_caller_owned_public_surface() -> None:
    signature = inspect.signature(JobExecutionClient)

    assert list(signature.parameters) == ["requester"]
    for method_name, return_type in (
        ("start_job", Job),
        ("get_job", Job),
        ("get_job_state", JobState),
    ):
        method_signature = inspect.signature(getattr(JobExecutionClient, method_name))
        expected_name = "job_request_id" if method_name == "start_job" else "job_id"
        assert list(method_signature.parameters) == ["self", expected_name]
        assert method_signature.return_annotation == return_type.__name__
    assert signature.parameters["requester"].annotation == RequestExecutor.__name__
    assert not hasattr(JobExecutionClient, "close")
    assert not hasattr(JobExecutionClient, "__aenter__")
    assert not hasattr(mlops_async, "JobExecutionClient")
