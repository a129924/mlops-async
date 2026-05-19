"""Readable request-contract tests for sasctl ModelRepository.get_model."""

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
DIRECT_IDENTIFIER = "123e4567-e89b-12d3-a456-426614174000"
GetModelCaptureRunner = Callable[[object, bool, str], list[dict[str, object]]]


def test_get_model_path_parameter(sasctl_contract: SasctlContractHarness) -> None:
    case_get_model_path_parameter = EndpointContractCase(
        name="model_repository.get_model.path_parameter",
        invoke=lambda: ModelRepository.get_model(DIRECT_IDENTIFIER, refresh=False),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/models/{DIRECT_IDENTIFIER}",
            query={},
            body=None,
            required_headers={"Authorization": "Bearer ", "Accept": ""},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"id": DIRECT_IDENTIFIER, "name": "demo-model", "links": []},
            headers={
                "Content-Type": "application/json",
                "ETag": "dummy-etag",
            },
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/get_model_by_id.request-flow.json#direct_identifier",
            response_path=f"{FIXTURE_ROOT}/get_model_by_id.mock-responses.json#direct_identifier",
        ),
    )

    result = sasctl_contract.run(case_get_model_path_parameter)

    assert result.id == DIRECT_IDENTIFIER
    assert result.name == "demo-model"
    assert sasctl_contract.last_request is not None
    assert sasctl_contract.last_request["path"] == f"/modelRepository/models/{DIRECT_IDENTIFIER}"
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
def test_get_model_blocks_out_of_scope_variants(
    blocked_topic_scope_error: type[RuntimeError],
    run_get_model_capture: GetModelCaptureRunner,
    item: object,
    refresh: bool,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        run_get_model_capture(item, refresh, "direct_identifier")
