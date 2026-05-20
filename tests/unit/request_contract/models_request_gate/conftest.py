"""Layer 1 source-observed request-shape helpers for models request gate.

This harness captures prepared requests from sasctl with existing repo dependencies only.
It does not prove auth/session/refresh, real transport, or target runtime behavior.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import pytest
import requests
from sasctl import Session  # pyright: ignore[reportMissingTypeStubs]  # sasctl 未提供 type stubs
from sasctl._services.model_repository import ModelRepository  # pyright: ignore[reportMissingTypeStubs]  # sasctl 未提供 type stubs
from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
)

BASE_URL = "https://example.test"
DUMMY_TOKEN = "fake-token"
ALLOWED_LIST_MODELS_FILTER = 'in(projectId,"proj-uuid")'
FIXTURE_DIR = Path(__file__).with_name("fixtures")


class BlockedTopicScopeError(RuntimeError):
    pass


def _load_json_fixture(filename: str) -> dict[str, object]:
    loaded = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"Fixture {filename} must be a JSON object.")
    return loaded


def _load_case(filename: str, case_name: str) -> Mapping[str, object]:
    cases = _load_json_fixture(filename).get("cases")
    if not isinstance(cases, dict):
        raise TypeError(f"Fixture {filename} must define a cases object.")
    case = cases.get(case_name)
    if not isinstance(case, dict):
        raise KeyError(f"Case {case_name} was not found in {filename}.")
    return case


def _expected_request_from_case(case: Mapping[str, object]) -> Mapping[str, object]:
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


def _normalize_query(query: str) -> dict[str, object]:
    parsed = parse_qs(query, keep_blank_values=True)
    normalized: dict[str, object] = {}
    for key, values in parsed.items():
        normalized[key] = values[0] if len(values) == 1 else values
    return normalized


def _body_value(body: object) -> object:
    if isinstance(body, bytes):
        return body.decode("utf-8")
    return body


def _capture_semantic_request(request: requests.PreparedRequest) -> dict[str, object]:
    split = urlsplit(request.url or "")
    return {
        "method": request.method,
        "path": split.path,
        "headers": dict(request.headers),
        "query": _normalize_query(split.query),
        "body": _body_value(request.body),
    }


def _matches_expected_request(actual: Mapping[str, object], expected: Mapping[str, object]) -> bool:
    return (
        actual.get("method") == expected.get("method")
        and actual.get("path") == expected.get("path")
        and actual.get("query") == expected.get("query")
        and actual.get("body") == expected.get("body")
    )


def _build_response(response_spec: Mapping[str, object], request_url: str) -> requests.Response:
    response = requests.Response()
    response.status_code = int(response_spec["status_code"])
    response.url = request_url
    response.encoding = "utf-8"

    headers = response_spec.get("headers", {})
    if not isinstance(headers, dict):
        raise TypeError("Response headers must be a JSON object.")
    response.headers.update({str(key): str(value) for key, value in headers.items()})

    json_body = response_spec.get("json_body")
    response._content = b"" if json_body is None else json.dumps(json_body).encode("utf-8")
    return response


def _build_fake_response(response_spec: FakeResponse, request_url: str) -> requests.Response:
    response = requests.Response()
    response.status_code = response_spec.status_code
    response.url = request_url
    response.encoding = "utf-8"
    response.headers.update(dict(response_spec.headers))
    if response_spec.text_body is not None:
        response._content = response_spec.text_body.encode("utf-8")
    elif response_spec.json_body is not None:
        response._content = json.dumps(response_spec.json_body).encode("utf-8")
    else:
        response._content = b""
    return response


@contextmanager
def _intercept_requests(answer_set_case: Mapping[str, object]) -> Iterator[list[dict[str, object]]]:
    responses = answer_set_case.get("responses")
    if not isinstance(responses, list):
        raise TypeError("Answer set case must provide a responses list.")

    captured: list[dict[str, object]] = []
    response_index = 0

    def fake_send(
        self: requests.sessions.Session,
        request: requests.PreparedRequest,
        **kwargs: object,
    ) -> requests.Response:
        del self, kwargs
        nonlocal response_index

        actual = _capture_semantic_request(request)
        captured.append(actual)

        if response_index >= len(responses):
            raise AssertionError(f"Unexpected outbound request: {actual!r}")

        response_entry = responses[response_index]
        response_index += 1
        if not isinstance(response_entry, dict):
            raise TypeError("Each response entry must be a JSON object.")

        expected_match = response_entry.get("match")
        if not isinstance(expected_match, dict):
            raise TypeError("Each response entry must define a match object.")
        if not _matches_expected_request(actual, expected_match):
            raise AssertionError(f"Unexpected outbound request: {actual!r}")

        response_spec = response_entry.get("response")
        if not isinstance(response_spec, dict):
            raise TypeError("Each response entry must define a response object.")
        return _build_response(response_spec, request.url or "")

    with patch.object(requests.sessions.Session, "send", new=fake_send):
        yield captured

    if response_index != len(responses):
        raise AssertionError(
            f"Registered responses were not exhausted: used {response_index} of {len(responses)}"
        )


def _assert_allowed_list_models_filter(filter_value: str | None) -> str | None:
    if filter_value is None:
        return None
    if filter_value != ALLOWED_LIST_MODELS_FILTER:
        raise BlockedTopicScopeError(
            'Only bare GET and filter=in(projectId,"proj-uuid") are allowed in this topic.'
        )
    return filter_value


def _assert_allowed_get_model_input(item: object, *, refresh: bool) -> str:
    if refresh:
        raise BlockedTopicScopeError("refresh=True is out of scope for this topic.")
    if not isinstance(item, str):
        raise BlockedTopicScopeError("Only the direct identifier branch is allowed in this topic.")
    try:
        UUID(item)
    except ValueError as error:
        raise BlockedTopicScopeError(
            "Only the direct identifier branch is allowed in this topic."
        ) from error
    return item


def _run_with_session(
    invocation: Callable[[], object],
    answer_set_case: Mapping[str, object],
) -> list[dict[str, object]]:
    with _intercept_requests(answer_set_case) as captured:
        with Session(BASE_URL, token=DUMMY_TOKEN, verify_ssl=False):
            invocation()
    return captured


def _split_fixture_locator(locator: str) -> tuple[Path, str | None]:
    raw_path, _, raw_case_name = locator.partition("#")
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        if candidate.exists():
            resolved_path = candidate
        else:
            resolved_path = FIXTURE_DIR / candidate
    else:
        resolved_path = candidate
    return resolved_path, raw_case_name or None


def _load_json_fixture_from_path(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"Fixture {path} must be a JSON object.")
    return loaded


def _load_case_from_locator(locator: str) -> Mapping[str, object]:
    fixture_path, case_name = _split_fixture_locator(locator)
    payload = _load_json_fixture_from_path(fixture_path)
    cases = payload.get("cases")
    if not isinstance(cases, dict):
        raise TypeError(f"Fixture {fixture_path} must define a cases object.")
    if case_name is None:
        if len(cases) != 1:
            raise AssertionError(
                "Fixture "
                f"{fixture_path} requires an explicit #case locator "
                "when multiple cases exist."
            )
        only_case = next(iter(cases.values()))
        if not isinstance(only_case, dict):
            raise TypeError(f"Fixture {fixture_path} case must be a JSON object.")
        return only_case
    case = cases.get(case_name)
    if not isinstance(case, dict):
        raise KeyError(f"Case {case_name} was not found in {fixture_path}.")
    return case


def _response_spec_from_answer_case(case: Mapping[str, object]) -> Mapping[str, object]:
    responses = case.get("responses")
    if not isinstance(responses, list) or len(responses) != 1:
        raise AssertionError("Each answer-set case must define exactly one response entry.")
    entry = responses[0]
    if not isinstance(entry, dict):
        raise TypeError("Each response entry must be a JSON object.")
    response = entry.get("response")
    if not isinstance(response, dict):
        raise TypeError("Each response entry must define a response object.")
    return response


def _assert_request_matches_contract(actual: Mapping[str, object], expected: RequestShape) -> None:
    if actual.get("method") != expected.method:
        raise AssertionError(f"Unexpected outbound request: {actual!r}")
    if actual.get("path") != expected.path:
        raise AssertionError(f"Unexpected outbound request: {actual!r}")
    if actual.get("query") != dict(expected.query):
        raise AssertionError(f"Unexpected outbound request: {actual!r}")
    if actual.get("body") != expected.body:
        raise AssertionError(f"Unexpected outbound request: {actual!r}")

    actual_headers = actual.get("headers")
    if not isinstance(actual_headers, dict):
        raise TypeError("Actual headers must be a mapping.")

    lowered_actual = {key.lower(): value for key, value in actual_headers.items()}
    for header_name, expected_prefix in expected.required_headers.items():
        header_value = lowered_actual.get(header_name.lower())
        if header_value is None:
            raise AssertionError(f"Unexpected outbound request: {actual!r}")
        if expected_prefix:
            if not str(header_value).startswith(expected_prefix):
                raise AssertionError(f"Unexpected outbound request: {actual!r}")


def _assert_request_shape_matches_source_observed(
    request_shape: RequestShape,
    source_request: Mapping[str, object],
) -> None:
    assert request_shape.method == source_request.get("method")
    assert request_shape.path == source_request.get("path")
    assert dict(request_shape.query) == source_request.get("query")
    assert request_shape.body == source_request.get("body")

    expected_headers = source_request.get("required_header_subset")
    if not isinstance(expected_headers, dict):
        raise TypeError("Source-observed request must define required_header_subset.")

    for header_name, raw_rule in expected_headers.items():
        if not isinstance(raw_rule, dict):
            raise TypeError("Each header rule must be a mapping.")
        actual_rule = request_shape.required_headers.get(header_name)
        assert actual_rule is not None, f"Missing required header in contract case: {header_name}"
        scheme = raw_rule.get("scheme")
        if scheme is not None:
            assert actual_rule.startswith(str(scheme))
        equals = raw_rule.get("equals")
        if equals is not None:
            assert actual_rule == equals


def _assert_fake_response_matches_source_observed(
    response: FakeResponse,
    source_response: Mapping[str, object],
) -> None:
    assert response.status_code == int(source_response["status_code"])
    headers = source_response.get("headers", {})
    if not isinstance(headers, dict):
        raise TypeError("Source-observed response headers must be a JSON object.")
    assert dict(response.headers) == {str(key): str(value) for key, value in headers.items()}
    assert response.json_body == source_response.get("json_body")
    assert response.text_body == source_response.get("text_body")


class SasctlContractHarness:
    """Run a readable contract case through the existing requests interception hook."""

    def __init__(self) -> None:
        self.last_request: dict[str, object] | None = None

    def run(self, case: EndpointContractCase) -> object:
        self.last_request = None
        if case.source_observed is not None:
            _assert_request_shape_matches_source_observed(
                case.expected,
                _expected_request_from_case(
                    _load_case_from_locator(case.source_observed.request_path)
                ),
            )
            if case.source_observed.response_path is not None:
                _assert_fake_response_matches_source_observed(
                    case.response,
                    _response_spec_from_answer_case(
                        _load_case_from_locator(case.source_observed.response_path)
                    ),
                )

        request_count = 0

        def fake_send(
            self: requests.sessions.Session,
            request: requests.PreparedRequest,
            **kwargs: object,
        ) -> requests.Response:
            del self, kwargs
            nonlocal request_count
            request_count += 1
            actual = _capture_semantic_request(request)
            self_harness.last_request = actual
            if request_count > 1:
                raise AssertionError(f"Unexpected outbound request: {actual!r}")
            _assert_request_matches_contract(actual, case.expected)
            return _build_fake_response(case.response, request.url or "")

        self_harness = self
        with patch.object(requests.sessions.Session, "send", new=fake_send):
            with Session(
                case.session.base_url,
                token=case.session.token,
                verify_ssl=case.session.verify_ssl,
            ):
                result = case.invoke()

        if request_count != 1:
            raise AssertionError(f"Expected exactly one outbound request, got {request_count}.")
        return result


@pytest.fixture
def load_request_flow_case() -> Callable[[str, str], Mapping[str, object]]:
    return lambda filename, case_name: _load_case(filename, case_name)


@pytest.fixture
def load_answer_set_case() -> Callable[[str, str], Mapping[str, object]]:
    return lambda filename, case_name: _load_case(filename, case_name)


@pytest.fixture
def expected_request_from_case() -> Callable[[Mapping[str, object]], Mapping[str, object]]:
    return _expected_request_from_case


@pytest.fixture
def blocked_topic_scope_error() -> type[BlockedTopicScopeError]:
    return BlockedTopicScopeError


@pytest.fixture
def run_list_models_capture(
    load_answer_set_case: Callable[[str, str], Mapping[str, object]],
) -> Callable[[str | None, str], list[dict[str, object]]]:
    def _run(filter_value: str | None, case_name: str) -> list[dict[str, object]]:
        allowed_filter = _assert_allowed_list_models_filter(filter_value)
        answer_set_case = load_answer_set_case("list_models.mock-responses.json", case_name)
        if allowed_filter is None:

            def invocation() -> object:
                return ModelRepository.list_models()
        else:

            def invocation() -> object:
                return ModelRepository.list_models(filter=allowed_filter)

        return _run_with_session(invocation, answer_set_case)

    return _run


@pytest.fixture
def run_get_model_capture(
    load_answer_set_case: Callable[[str, str], Mapping[str, object]],
) -> Callable[[object, bool, str], list[dict[str, object]]]:
    def _run(item: object, refresh: bool, case_name: str) -> list[dict[str, object]]:
        identifier = _assert_allowed_get_model_input(item, refresh=refresh)
        answer_set_case = load_answer_set_case("get_model_by_id.mock-responses.json", case_name)

        def invocation() -> object:
            return ModelRepository.get_model(identifier, refresh=refresh)

        return _run_with_session(invocation, answer_set_case)

    return _run


@pytest.fixture
def assert_semantic_request_matches_fixture() -> Callable[
    [Mapping[str, object], Mapping[str, object]], None
]:
    def _assert(actual: Mapping[str, object], expected: Mapping[str, object]) -> None:
        assert actual.get("method") == expected.get("method")
        assert actual.get("path") == expected.get("path")
        assert actual.get("query") == expected.get("query")
        assert actual.get("body") == expected.get("body")

        actual_headers = actual.get("headers")
        expected_headers = expected.get("required_header_subset")
        if not isinstance(actual_headers, dict):
            raise TypeError("Actual headers must be a mapping.")
        if not isinstance(expected_headers, dict):
            raise TypeError("Expected required_header_subset must be a mapping.")

        lowered_actual = {key.lower(): value for key, value in actual_headers.items()}
        for header_name, raw_rule in expected_headers.items():
            if not isinstance(raw_rule, dict):
                raise TypeError("Each header rule must be a mapping.")
            header_value = lowered_actual.get(header_name.lower())
            assert header_value is not None, f"Missing required header: {header_name}"
            if raw_rule.get("present") is False:
                raise AssertionError(f"Header rule for {header_name} cannot require absence.")
            scheme = raw_rule.get("scheme")
            if scheme is not None:
                assert str(header_value).startswith(f"{scheme} ")
            exact_value = raw_rule.get("equals")
            if exact_value is not None:
                assert header_value == exact_value

    return _assert


@pytest.fixture
def sasctl_contract() -> SasctlContractHarness:
    return SasctlContractHarness()
