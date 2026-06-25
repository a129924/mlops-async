"""`get_model_content` 的可讀式請求合約測試。"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.models_content_request_gate.conftest import (
    SasctlContractHarness,
    invoke_get_model_content,
)

MODEL_ID = "model-id-abc-123"
FILE_ID = "file-001"
RunGetModelContentCapture = Callable[[object, object, str], list[dict[str, object]]]

case_get_model_content_direct_identifiers = EndpointContractCase(
    name="model_repository.get_model_content.direct_identifiers",
    invoke=lambda: invoke_get_model_content(MODEL_ID, FILE_ID),
    expected=RequestShape(
        method="GET",
        path=f"/modelRepository/models/{MODEL_ID}/contents/{FILE_ID}/content",
        query={},
        body=None,
        required_headers={
            "Authorization": "Bearer ",
            "If-Range": "",
            "Range": "",
            "Access-Quarantine": "",
        },
    ),
    response=FakeResponse(
        status_code=200,
        text_body="",
        headers={"Content-Type": "application/octet-stream"},
    ),
    source_observed=SourceObservedFixture(
        request_path="get_model_content.request-flow.json#direct_identifiers",
    ),
)


def test_get_model_content_direct_identifiers_request_shape(
    sasctl_contract: SasctlContractHarness,
) -> None:
    sasctl_contract.run(case_get_model_content_direct_identifiers)

    assert sasctl_contract.last_request is not None
    assert (
        sasctl_contract.last_request["path"]
        == f"/modelRepository/models/{MODEL_ID}/contents/{FILE_ID}/content"
    )
    assert sasctl_contract.last_request["query"] == {}
    assert sasctl_contract.last_request["body"] is None
    headers = sasctl_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["If-Range"] == ""
    assert headers["Range"] == ""
    assert headers["Access-Quarantine"] == ""


def test_get_model_content_capture_matches_source_observed_fixture(
    run_get_model_content_capture: RunGetModelContentCapture,
    load_request_flow_case: Callable[[str, str], dict[str, object]],
    expected_request_from_case: Callable[[dict[str, object]], dict[str, object]],
    assert_semantic_request_matches_fixture: Callable[[dict[str, object], dict[str, object]], None],
) -> None:
    captured = run_get_model_content_capture(MODEL_ID, FILE_ID, "direct_identifiers")
    expected_case = load_request_flow_case(
        "get_model_content.request-flow.json", "direct_identifiers"
    )
    expected_request = expected_request_from_case(expected_case)

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], expected_request)


@pytest.mark.parametrize(
    ("model_id", "file_id"),
    [
        ("", FILE_ID),
        ("   ", FILE_ID),
        (MODEL_ID, ""),
        (MODEL_ID, None),
    ],
)
def test_get_model_content_blocks_invalid_identifiers(
    blocked_topic_scope_error: type[RuntimeError],
    run_get_model_content_capture: RunGetModelContentCapture,
    model_id: object,
    file_id: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r"Only non-empty (modelId|fileId) strings are allowed in this topic.",
    ):
        run_get_model_content_capture(model_id, file_id, "direct_identifiers")
