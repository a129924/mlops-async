"""sasctl ModelRepository.get_project 的可讀式請求合約測試。"""

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
DIRECT_IDENTIFIER = "123e4567-e89b-12d3-a456-426614174001"
GetProjectCaptureRunner = Callable[[object, bool, str], list[dict[str, object]]]


def test_get_project_path_parameter(sasctl_contract: SasctlContractHarness) -> None:
    case_get_project_path_parameter = EndpointContractCase(
        name="model_repository.get_project.path_parameter",
        invoke=lambda: ModelRepository.get_project(DIRECT_IDENTIFIER, refresh=False),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{DIRECT_IDENTIFIER}",
            query={},
            body=None,
            required_headers={"Authorization": "Bearer ", "Accept": ""},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={
                "id": DIRECT_IDENTIFIER,
                "name": "demo-project",
                "status": "development",
                "links": [],
            },
            headers={
                "Content-Type": "application/json",
                "ETag": "dummy-etag",
            },
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/get_project_by_id.request-flow.json#direct_identifier",
            response_path=f"{FIXTURE_ROOT}/get_project_by_id.mock-responses.json#direct_identifier",
        ),
    )

    result = sasctl_contract.run(case_get_project_path_parameter)

    assert result.id == DIRECT_IDENTIFIER  # type: ignore[union-attr]
    assert result.name == "demo-project"  # type: ignore[union-attr]
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == f"/modelRepository/projects/{DIRECT_IDENTIFIER}"
    assert sasctl_contract.last_request["query"] == {}


@pytest.mark.parametrize(
    ("item", "refresh", "pattern"),
    [
        ("not-a-uuid", False, "Only the direct identifier branch is allowed"),
        (
            {"id": DIRECT_IDENTIFIER, "name": "demo"},
            False,
            "Only the direct identifier branch is allowed",
        ),
        (DIRECT_IDENTIFIER, True, "refresh=True is out of scope"),
    ],
)
def test_get_project_blocks_out_of_scope_variants(
    blocked_topic_scope_error: type[RuntimeError],
    run_get_project_capture: GetProjectCaptureRunner,
    item: object,
    refresh: bool,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        run_get_project_capture(item, refresh, "direct_identifier")
