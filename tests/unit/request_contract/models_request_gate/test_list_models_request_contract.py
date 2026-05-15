"""Layer 1 source-observed request-shape tests for sasctl ModelRepository.list_models.

These assertions document the current harness-observed request shape only.
They do not prove target runtime behavior or stricter target header intent.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest


def test_list_models_bare_get_matches_request_flow_fixture(
    expected_request_from_case: Callable[[Mapping[str, object]], Mapping[str, object]],
    load_request_flow_case: Callable[[str, str], Mapping[str, object]],
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
    assert_semantic_request_matches_fixture: Callable[
        [Mapping[str, object], Mapping[str, object]], None
    ],
) -> None:
    case = load_request_flow_case("list_models.request-flow.json", "bare_get")
    captured = run_list_models_capture(None, "bare_get")

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], expected_request_from_case(case))


def test_list_models_filter_semantics_match_request_flow_fixture(
    expected_request_from_case: Callable[[Mapping[str, object]], Mapping[str, object]],
    load_request_flow_case: Callable[[str, str], Mapping[str, object]],
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
    assert_semantic_request_matches_fixture: Callable[
        [Mapping[str, object], Mapping[str, object]], None
    ],
) -> None:
    case = load_request_flow_case("list_models.request-flow.json", "filter_project_id")
    captured = run_list_models_capture('in(projectId,"proj-uuid")', "filter_project_id")

    assert len(captured) == 1
    assert_semantic_request_matches_fixture(captured[0], expected_request_from_case(case))


def test_list_models_emits_single_target_request(
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    captured = run_list_models_capture(None, "bare_get")

    assert [entry["path"] for entry in captured] == ["/modelRepository/models"]
    assert captured[0]["query"] == {}
    assert captured[0]["body"] is None


def test_list_models_blocks_unsupported_filter_semantics(
    blocked_topic_scope_error: type[RuntimeError],
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match=r'Only bare GET and filter=in\(projectId,"proj-uuid"\) are allowed',
    ):
        run_list_models_capture('eq(name,"m1")', "filter_project_id")


def test_list_models_interceptor_fails_fast_on_unregistered_request(
    run_list_models_capture: Callable[[str | None, str], list[dict[str, object]]],
) -> None:
    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        run_list_models_capture('in(projectId,"proj-uuid")', "bare_get")
