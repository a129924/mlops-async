"""`start_job` 的可讀式請求合約測試。"""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.job_requests_jobs_request_gate.conftest import (
    START_JOB_ACCEPT,
    SasctlContractHarness,
    invoke_start_job,
)

RunStartJobCapture = Callable[[str, Mapping[str, object], str], list[dict[str, object]]]

case_start_job_empty_json_body = EndpointContractCase(
    name="job_execution.start_job.empty_json_body",
    invoke=lambda: invoke_start_job("job-request-abc-123"),
    expected=RequestShape(
        method="POST",
        path="/jobExecution/jobRequests/job-request-abc-123/jobs",
        query={},
        body="{}",
        required_headers={
            "Authorization": "Bearer ",
            "Accept": START_JOB_ACCEPT,
            "Content-Type": "application/json",
            "Delegate-Domain": "",
        },
    ),
    response=FakeResponse(),
    source_observed=SourceObservedFixture(
        request_path="start_job.request-flow.json#empty_json_body",
    ),
)


def test_start_job_empty_json_body_request_shape(sasctl_contract: SasctlContractHarness) -> None:
    sasctl_contract.run(case_start_job_empty_json_body)

    assert sasctl_contract.last_request is not None
    assert (
        sasctl_contract.last_request["path"] == "/jobExecution/jobRequests/job-request-abc-123/jobs"
    )
    assert sasctl_contract.last_request["query"] == {}
    assert sasctl_contract.last_request["body"] == "{}"
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["Accept"] == START_JOB_ACCEPT
    assert headers["Content-Type"] == "application/json"
    assert headers["Delegate-Domain"] == ""


def test_start_job_blocks_non_empty_json_body(
    blocked_topic_scope_error: type[RuntimeError],
    run_start_job_capture: RunStartJobCapture,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r"Only the empty JSON object body is allowed",
    ):
        run_start_job_capture(
            "job-request-abc-123", {"runtimeOverrides": {"threads": 2}}, "empty_json_body"
        )
