"""Readable request-contract tests for sasctl ModelRepository.list_models."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sasctl._services.model_repository import ModelRepository  # pyright: ignore[reportMissingTypeStubs]

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.models_request_gate.conftest import SasctlContractHarness

FIXTURE_ROOT = "tests/unit/request_contract/models_request_gate/fixtures"
PROJECT_FILTER = 'in(projectId,"proj-uuid")'
ListModelsCaptureRunner = Callable[[str | None, str], list[dict[str, object]]]
EMPTY_LIST_RESPONSE = {
    "items": [],
    "count": 0,
    "start": 0,
    "limit": 20,
    "links": [],
}

case_list_models_default = EndpointContractCase(
    name="model_repository.list_models.default_request_shape",
    invoke=lambda: ModelRepository.list_models(),
    expected=RequestShape(
        method="GET",
        path="/modelRepository/models",
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
        request_path=f"{FIXTURE_ROOT}/list_models.request-flow.json#bare_get",
        response_path=f"{FIXTURE_ROOT}/list_models.mock-responses.json#bare_get",
    ),
)

case_list_models_filter_project_id = EndpointContractCase(
    name="model_repository.list_models.filter_project_id",
    invoke=lambda: ModelRepository.list_models(filter=PROJECT_FILTER),
    expected=RequestShape(
        method="GET",
        path="/modelRepository/models",
        query={"filter": PROJECT_FILTER},
        body=None,
        required_headers={"Authorization": "Bearer ", "Accept": ""},
    ),
    response=FakeResponse(
        status_code=200,
        json_body=EMPTY_LIST_RESPONSE,
        headers={"Content-Type": "application/json"},
    ),
    source_observed=SourceObservedFixture(
        request_path=f"{FIXTURE_ROOT}/list_models.request-flow.json#filter_project_id",
        response_path=f"{FIXTURE_ROOT}/list_models.mock-responses.json#filter_project_id",
    ),
)


def test_list_models_default_request_shape(sasctl_contract: SasctlContractHarness) -> None:
    result = sasctl_contract.run(case_list_models_default)

    assert result == []
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == "/modelRepository/models"
    assert sasctl_contract.last_request["query"] == {}
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert "Accept" in headers


def test_list_models_empty_response(sasctl_contract: SasctlContractHarness) -> None:
    result = sasctl_contract.run(case_list_models_default)

    assert result == []
    assert case_list_models_default.response.json_body == EMPTY_LIST_RESPONSE
    assert EMPTY_LIST_RESPONSE["items"] == []


def test_list_models_filter_project_id_request_shape(
    sasctl_contract: SasctlContractHarness,
) -> None:
    result = sasctl_contract.run(case_list_models_filter_project_id)

    assert result == []
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["query"] == {"filter": PROJECT_FILTER}


def test_list_models_blocks_unsupported_filter_semantics(
    blocked_topic_scope_error: type[RuntimeError],
    run_list_models_capture: ListModelsCaptureRunner,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r'Only bare GET and filter=in\(projectId,"proj-uuid"\) are allowed',
    ):
        run_list_models_capture('eq(name,"m1")', "filter_project_id")


def test_list_models_interceptor_fails_fast_on_unregistered_request(
    sasctl_contract: SasctlContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="model_repository.list_models.unregistered_request",
        invoke=lambda: ModelRepository.list_models(filter=PROJECT_FILTER),
        expected=case_list_models_default.expected,
        response=case_list_models_default.response,
        source_observed=case_list_models_default.source_observed,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        sasctl_contract.run(mismatched_case)
