"""Non-authoritative shape-only tests for the internal
jobExecution/jobs/state wrapper request gate."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.job_execution_jobs_state_request_gate.conftest import (
    GET_JOB_STATE_ACCEPT_HEADER,
    TOPIC_PACKAGE_DIR,
    JobExecutionStateContractHarness,
    _is_topic_scoped_pytest_run,
)

FIXTURE_ROOT = "tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures"
DIRECT_JOB_ID = "job-id-abc-123"


@pytest.mark.asyncio
async def test_get_job_state_direct_identifier_request_shape(
    job_execution_state_contract: JobExecutionStateContractHarness,
) -> None:
    case_get_job_state_direct_identifier = EndpointContractCase(
        name="job_execution_jobs_state.get_job_state.direct_identifier",
        invoke=lambda: job_execution_state_contract.client.get_job_state(DIRECT_JOB_ID),
        expected=RequestShape(
            method="GET",
            path=f"/jobExecution/jobs/{DIRECT_JOB_ID}/state",
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": GET_JOB_STATE_ACCEPT_HEADER,
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "running"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/get_job_state.request-flow.json#direct_identifier",
            response_path=f"{FIXTURE_ROOT}/get_job_state.mock-responses.json#direct_identifier",
        ),
    )

    result = await job_execution_state_contract.run(case_get_job_state_direct_identifier)

    assert getattr(result, "state", None) == "running"
    assert job_execution_state_contract.last_request is not None
    assert (
        job_execution_state_contract.last_request["path"]
        == f"/jobExecution/jobs/{DIRECT_JOB_ID}/state"
    )
    assert job_execution_state_contract.last_request["query"] == {}
    assert job_execution_state_contract.last_request["body"] is None
    headers = job_execution_state_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["authorization"]).startswith("Bearer ")
    assert headers["accept"] == GET_JOB_STATE_ACCEPT_HEADER
    assert "Delegate-Domain" not in headers
    assert "content-type" not in headers


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("job_id", "pattern"),
    [
        (123, "Only a non-empty jobId string is allowed"),
        ({"id": DIRECT_JOB_ID}, "Only a non-empty jobId string is allowed"),
    ],
)
async def test_get_job_state_blocks_non_string_identifier_variants(
    blocked_topic_scope_error: type[RuntimeError],
    job_execution_state_contract: JobExecutionStateContractHarness,
    job_id: object,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        await job_execution_state_contract.client.get_job_state(job_id)


@pytest.mark.asyncio
async def test_get_job_state_blocks_blank_identifier(
    blocked_topic_scope_error: type[RuntimeError],
    job_execution_state_contract: JobExecutionStateContractHarness,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match="Only a non-empty jobId string is allowed"):
        await job_execution_state_contract.client.get_job_state("")


@pytest.mark.asyncio
async def test_get_job_state_interceptor_fails_fast_on_unregistered_request(
    job_execution_state_contract: JobExecutionStateContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="job_execution_jobs_state.get_job_state.unregistered_request",
        invoke=lambda: job_execution_state_contract.client.get_job_state(DIRECT_JOB_ID),
        expected=RequestShape(
            method="GET",
            path=f"/jobExecution/jobs/{DIRECT_JOB_ID}",
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": GET_JOB_STATE_ACCEPT_HEADER,
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "running"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        await job_execution_state_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/job_execution_jobs_state_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False
