"""sasctl ModelRepository.list_models 的可讀式請求合約測試。"""

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
from tests.unit.request_contract.models_request_gate.conftest import SasctlContractHarness

FIXTURE_ROOT = "tests/unit/request_contract/models_request_gate/fixtures"
PROJECT_FILTER = 'in(projectId,"proj-uuid")'
ListModelsCaptureRunner = Callable[[str | None, str], list[dict[str, object]]]
MINIMAL_LIST_RESPONSE = {"items": []}

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
        json_body=MINIMAL_LIST_RESPONSE,
        headers={"Content-Type": "application/json"},
    ),
    source_observed=SourceObservedFixture(
        request_path=f"{FIXTURE_ROOT}/list_models.request-flow.json#bare_get",
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
        json_body=MINIMAL_LIST_RESPONSE,
        headers={"Content-Type": "application/json"},
    ),
    source_observed=SourceObservedFixture(
        request_path=f"{FIXTURE_ROOT}/list_models.request-flow.json#filter_project_id",
    ),
)


def test_list_models_default_request_shape(sasctl_contract: SasctlContractHarness) -> None:
    sasctl_contract.run(case_list_models_default)

    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == "/modelRepository/models"
    assert sasctl_contract.last_request["query"] == {}
    assert sasctl_contract.last_request["body"] is None
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert "Accept" in headers


def test_list_models_filter_project_id_request_shape(
    sasctl_contract: SasctlContractHarness,
) -> None:
    sasctl_contract.run(case_list_models_filter_project_id)

    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == "/modelRepository/models"
    assert sasctl_contract.last_request["query"] == {"filter": PROJECT_FILTER}
    assert sasctl_contract.last_request["body"] is None
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert "Accept" in headers


def test_list_models_blocks_unsupported_filter_semantics(
    blocked_topic_scope_error: type[RuntimeError],
    run_list_models_capture: ListModelsCaptureRunner,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r'Only bare GET and filter=in\(projectId,"proj-uuid"\) are allowed',
    ):
        run_list_models_capture('eq(name,"m1")', "filter_project_id")
