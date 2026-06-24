"""sasctl ModelRepository champion GET 的可讀式請求合約測試。"""

from __future__ import annotations

from uuid import UUID

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
PROJECT_ID = "123e4567-e89b-12d3-a456-426614174001"
CHAMPION_MODEL_ID = "123e4567-e89b-12d3-a456-426614174099"


def _assert_allowed_get_champion_model_project_id(
    blocked_topic_scope_error: type[RuntimeError],
    project_id: object,
) -> str:
    if not isinstance(project_id, str):
        raise blocked_topic_scope_error(
            "Only the direct project identifier branch is allowed in this topic."
        )
    try:
        UUID(project_id)
    except ValueError as error:
        raise blocked_topic_scope_error(
            "Only the direct project identifier branch is allowed in this topic."
        ) from error
    return project_id


def _run_get_champion_model_capture(
    blocked_topic_scope_error: type[RuntimeError],
    project_id: object,
) -> None:
    _assert_allowed_get_champion_model_project_id(blocked_topic_scope_error, project_id)


def test_get_champion_model_path_parameter(sasctl_contract: SasctlContractHarness) -> None:
    case_get_champion_model_path_parameter = EndpointContractCase(
        name="model_repository.get_champion_model.path_parameter",
        invoke=lambda: ModelRepository.get(f"/projects/{PROJECT_ID}/champion"),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{PROJECT_ID}/champion",
            query={},
            body=None,
            required_headers={"Authorization": "Bearer ", "Accept": ""},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={
                "id": CHAMPION_MODEL_ID,
                "name": "demo-champion-model",
                "projectId": PROJECT_ID,
                "links": [],
            },
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/get_champion_model.request-flow.json#direct_project_identifier",
            response_path=f"{FIXTURE_ROOT}/get_champion_model.mock-responses.json#direct_project_identifier",
        ),
    )

    result = sasctl_contract.run(case_get_champion_model_path_parameter)

    assert result.id == CHAMPION_MODEL_ID  # type: ignore[union-attr]
    assert result.projectId == PROJECT_ID  # type: ignore[union-attr]
    assert sasctl_contract.last_request is not None
    assert (
        sasctl_contract.last_request["path"] == f"/modelRepository/projects/{PROJECT_ID}/champion"
    )
    assert sasctl_contract.last_request["query"] == {}


@pytest.mark.parametrize(
    ("project_id", "pattern"),
    [
        ("not-a-uuid", "Only the direct project identifier branch is allowed"),
        (
            {"id": PROJECT_ID, "name": "demo-project"},
            "Only the direct project identifier branch is allowed",
        ),
    ],
)
def test_get_champion_model_blocks_out_of_scope_variants(
    blocked_topic_scope_error: type[RuntimeError],
    project_id: object,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        _run_get_champion_model_capture(blocked_topic_scope_error, project_id)


def test_get_champion_model_interceptor_fails_fast_on_unregistered_request(
    sasctl_contract: SasctlContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="model_repository.get_champion_model.unregistered_request",
        invoke=lambda: ModelRepository.get(f"/projects/{PROJECT_ID}/champion"),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{PROJECT_ID}",
            query={},
            body=None,
            required_headers={"Authorization": "Bearer ", "Accept": ""},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"id": CHAMPION_MODEL_ID, "name": "demo-champion-model", "links": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        sasctl_contract.run(mismatched_case)
