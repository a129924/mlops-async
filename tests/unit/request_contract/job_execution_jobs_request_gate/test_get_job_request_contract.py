"""Non-authoritative shape-only tests for the internal
jobExecution/jobs wrapper request gate."""

from __future__ import annotations

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.job_execution_jobs_request_gate.conftest import (
    JobExecutionContractHarness,
)

FIXTURE_ROOT = "tests/unit/request_contract/job_execution_jobs_request_gate/fixtures"
DIRECT_JOB_ID = "job-id-abc-123"
ACCEPT_HEADER = (
    "application/vnd.sas.job.execution.job+json, "
    "application/vnd.sas.job.execution.job.request+json, "
    "application/vnd.sas.error+json, application/json"
)


@pytest.mark.asyncio
async def test_get_job_direct_identifier_request_shape(
    job_execution_contract: JobExecutionContractHarness,
) -> None:
    case_get_job_direct_identifier = EndpointContractCase(
        name="job_execution_jobs.get_job.direct_identifier",
        invoke=lambda: job_execution_contract.client.get_job(DIRECT_JOB_ID),
        expected=RequestShape(
            method="GET",
            path=f"/jobExecution/jobs/{DIRECT_JOB_ID}",
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": ACCEPT_HEADER,
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={
                "id": DIRECT_JOB_ID,
                "state": "running",
                "creationTimeStamp": "2024-01-15T10:30:00.000Z",
                "elapsedTime": 5.2,
            },
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/get_job.request-flow.json#direct_identifier",
            response_path=f"{FIXTURE_ROOT}/get_job.mock-responses.json#direct_identifier",
        ),
    )

    result = await job_execution_contract.run(case_get_job_direct_identifier)

    assert result.id == DIRECT_JOB_ID  # type: ignore[union-attr]
    assert result.state == "running"  # type: ignore[union-attr]
    assert job_execution_contract.last_request is not None
    assert job_execution_contract.last_request["path"] == f"/jobExecution/jobs/{DIRECT_JOB_ID}"
    assert job_execution_contract.last_request["query"] == {}
    assert job_execution_contract.last_request["body"] is None
    headers = job_execution_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["Accept"] == ACCEPT_HEADER
    assert "Delegate-Domain" not in headers
    assert "Content-Type" not in headers
