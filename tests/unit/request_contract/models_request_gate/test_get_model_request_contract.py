"""Layer 1 source-observed request-shape tests for sasctl ModelRepository.get_model.

These assertions document the current harness-observed direct-identifier branch only.
They do not prove target runtime behavior, refresh handling, or session semantics.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest


DIRECT_IDENTIFIER = "123e4567-e89b-12d3-a456-426614174000"


def _expected_request(case: Mapping[str, object]) -> Mapping[str, object]:
    flow = case.get("full_observed_flow")
    if not isinstance(flow, list) or len(flow) != 1:
        raise AssertionError("Each request-flow case must define exactly one observed step.")
    step = flow[0]
    if not isinstance(step, dict):
        raise AssertionError("Observed flow step must be an object.")
    request = step.get("request")
    if not isinstance(request, dict):
        raise AssertionError("Observed flow step must define a request object.")
    return request


def test_get_model_direct_identifier_matches_request_flow_fixture(
    load_request_flow_case: Callable[[str, str], Mapping[str, object]],
    run_get_model_capture: Callable[[object, bool, str], list[dict[str, object]]],
    assert_semantic_request_matches_fixture: Callable[
        [Mapping[str, object], Mapping[str, object]], None
    ],
) -> None:
    case = load_request_flow_case("get_model_by_id.request-flow.json", "direct_identifier")
    captured = run_get_model_capture(DIRECT_IDENTIFIER, False, "direct_identifier")

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], _expected_request(case))


def test_get_model_direct_identifier_emits_single_target_request(
    run_get_model_capture: Callable[[object, bool, str], list[dict[str, object]]],
) -> None:
    captured = run_get_model_capture(DIRECT_IDENTIFIER, False, "direct_identifier")

    assert [entry["path"] for entry in captured] == [f"/modelRepository/models/{DIRECT_IDENTIFIER}"]
    assert captured[0]["query"] == {}
    assert captured[0]["body"] is None


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
    run_get_model_capture: Callable[[object, bool, str], list[dict[str, object]]],
    item: object,
    refresh: bool,
    pattern: str,
) -> None:
    with pytest.raises(RuntimeError, match=pattern):
        run_get_model_capture(item, refresh, "direct_identifier")
