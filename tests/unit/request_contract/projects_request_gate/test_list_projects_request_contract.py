"""sasctl ModelRepository.list_projects 的可讀式請求合約測試。"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sasctl._services.model_repository import ModelRepository  # pyright: ignore[reportMissingTypeStubs]  # sasctl 未提供 type stubs

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.projects_request_gate.conftest import SasctlContractHarness

FIXTURE_ROOT = "tests/unit/request_contract/projects_request_gate/fixtures"
ListProjectsCaptureRunner = Callable[[int | None, str], list[dict[str, object]]]
EMPTY_LIST_RESPONSE = {
    "items": [],
    "count": 0,
    "start": 0,
    "limit": 20,
    "links": [],
}

case_list_projects_default = EndpointContractCase(
    name="model_repository.list_projects.default_request_shape",
    invoke=lambda: ModelRepository.list_projects(),
    expected=RequestShape(
        method="GET",
        path="/modelRepository/projects",
        query={},
        body=None,
        required_headers={"Authorization": "Bearer ", "Accept": ""},
    ),
    response=FakeResponse(
        status_code=200,
        json_body=EMPTY_LIST_RESPONSE,
        headers={"Content-Type": "application/json"},
    ),
    source_observed=SourceObservedFixture(
        request_path=f"{FIXTURE_ROOT}/list_projects.request-flow.json#bare_get",
        response_path=f"{FIXTURE_ROOT}/list_projects.mock-responses.json#bare_get",
    ),
)

case_list_projects_limit_1000 = EndpointContractCase(
    name="model_repository.list_projects.limit_1000",
    invoke=lambda: ModelRepository.list_projects(limit=1000),
    expected=RequestShape(
        method="GET",
        path="/modelRepository/projects",
        query={"limit": "1000"},
        body=None,
        required_headers={"Authorization": "Bearer ", "Accept": ""},
    ),
    response=FakeResponse(
        status_code=200,
        json_body={**EMPTY_LIST_RESPONSE, "limit": 1000},
        headers={"Content-Type": "application/json"},
    ),
    source_observed=SourceObservedFixture(
        request_path=f"{FIXTURE_ROOT}/list_projects.request-flow.json#limit_1000",
        response_path=f"{FIXTURE_ROOT}/list_projects.mock-responses.json#limit_1000",
    ),
)


def test_list_projects_default_request_shape(sasctl_contract: SasctlContractHarness) -> None:
    result = sasctl_contract.run(case_list_projects_default)

    assert result == []
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == "/modelRepository/projects"
    assert sasctl_contract.last_request["query"] == {}
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert "Accept" in headers


def test_list_projects_empty_response(sasctl_contract: SasctlContractHarness) -> None:
    result = sasctl_contract.run(case_list_projects_default)

    assert result == []
    assert case_list_projects_default.response.json_body == EMPTY_LIST_RESPONSE
    assert EMPTY_LIST_RESPONSE["items"] == []


def test_list_projects_limit_1000_request_shape(
    sasctl_contract: SasctlContractHarness,
) -> None:
    result = sasctl_contract.run(case_list_projects_limit_1000)

    assert result == []
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["query"] == {"limit": "1000"}


def test_list_projects_blocks_unsupported_limit(
    blocked_topic_scope_error: type[RuntimeError],
    run_list_projects_capture: ListProjectsCaptureRunner,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r"Only bare GET and limit=1000 are allowed",
    ):
        run_list_projects_capture(500, "bare_get")


def test_list_projects_interceptor_fails_fast_on_unregistered_request(
    sasctl_contract: SasctlContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="model_repository.list_projects.unregistered_request",
        invoke=lambda: ModelRepository.list_projects(limit=1000),
        expected=case_list_projects_default.expected,
        response=case_list_projects_default.response,
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        sasctl_contract.run(mismatched_case)
