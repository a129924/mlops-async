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
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders

_JOB_ACCEPT = (
    "application/vnd.sas.job.execution.job+json, "
    "application/vnd.sas.job.execution.job.request+json, "
    "application/vnd.sas.error+json, application/json"
)


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
async def test_start_job_makes_one_bodyless_post_with_locked_headers_and_encoded_identifier(
) -> None:
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
async def test_get_job_state_makes_one_plain_text_request_without_json_decoding_or_normalization(
) -> None:
    requester = _FakeRequester([_response(b"timedOut")])

    client = JobExecutionClient(requester)  # type: ignore[arg-type]
    state = await client.get_job_state("job id/slash")

    assert state is JobState.TIMED_OUT
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/jobExecution/jobs/job%20id%2Fslash/state",
            {"Delegate-Domain": "", "Content-Type": "application/json"},
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
    assert signature.parameters["requester"].annotation == Requester.__name__
    assert not hasattr(JobExecutionClient, "close")
    assert not hasattr(JobExecutionClient, "__aenter__")
    assert not hasattr(mlops_async, "JobExecutionClient")
