"""Layer 1 source-observed request-shape tests for sasctl ModelRepository.list_models.

These assertions document the current harness-observed request shape only.
They do not prove target runtime behavior or stricter target header intent.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest


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


def test_list_models_bare_get_matches_request_flow_fixture(
    load_request_flow_case: Callable[[str, str], Mapping[str, object]],
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
    assert_semantic_request_matches_fixture: Callable[
        [Mapping[str, object], Mapping[str, object]], None
    ],
) -> None:
    case = load_request_flow_case("list_models.request-flow.json", "bare_get")
    captured = run_list_models_capture(None, "bare_get")

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], _expected_request(case))


def test_list_models_filter_semantics_match_request_flow_fixture(
    load_request_flow_case: Callable[[str, str], Mapping[str, object]],
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
    assert_semantic_request_matches_fixture: Callable[
        [Mapping[str, object], Mapping[str, object]], None
    ],
) -> None:
    case = load_request_flow_case("list_models.request-flow.json", "filter_project_id")
    captured = run_list_models_capture('in(projectId,"proj-uuid")', "filter_project_id")

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], _expected_request(case))


def test_list_models_emits_single_target_request(
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    captured = run_list_models_capture(None, "bare_get")

    assert [entry["path"] for entry in captured] == ["/modelRepository/models"]
    assert captured[0]["query"] == {}
    assert captured[0]["body"] is None


def test_list_models_blocks_unsupported_filter_semantics(
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    with pytest.raises(
        RuntimeError,
        match=r'Only bare GET and filter=in\(projectId,"proj-uuid"\) are allowed',
    ):
        run_list_models_capture('eq(name,"m1")', "filter_project_id")


def test_list_models_interceptor_fails_fast_on_unregistered_request(
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        run_list_models_capture('in(projectId,"proj-uuid")', "bare_get")
