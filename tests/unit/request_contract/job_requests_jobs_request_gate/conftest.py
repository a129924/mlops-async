"""Layer 1 source-observed request-shape helpers for the start_job request gate."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from sasctl import Session  # pyright: ignore[reportMissingTypeStubs]  # sasctl 未提供 type stubs

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    RequestShape,
)
from tests.unit.request_contract.header_families import JOB_EXECUTION_JOB_ACCEPT_HEADER

BASE_URL = "https://example.test"
DUMMY_TOKEN = "fake-token"
START_JOB_ACCEPT = JOB_EXECUTION_JOB_ACCEPT_HEADER
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


def _split_fixture_locator(locator: str) -> tuple[Path, str | None]:
    raw_path, _, raw_case_name = locator.partition("#")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise AssertionError(
            "Fixture locator path must be relative to the topic fixture directory."
        )

    resolved_path = (FIXTURE_DIR / candidate).resolve(strict=False)
    fixture_root = FIXTURE_DIR.resolve()
    if not resolved_path.is_relative_to(fixture_root):
        raise AssertionError("Fixture locator path must stay within the topic fixture directory.")

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
                f"Fixture {fixture_path} requires an explicit #case locator "
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


def _build_stub_response(request_url: str) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response.url = request_url
    response.encoding = "utf-8"
    response._content = b"{}"
    return response


@contextmanager
def _intercept_requests(
    expected_request: Mapping[str, object],
) -> Iterator[list[dict[str, object]]]:
    captured: list[dict[str, object]] = []
    request_count = 0

    def fake_send(
        self: requests.sessions.Session,
        request: requests.PreparedRequest,
        **kwargs: object,
    ) -> requests.Response:
        del self, kwargs
        nonlocal request_count

        actual = _capture_semantic_request(request)
        captured.append(actual)
        request_count += 1

        if request_count > 1:
            raise AssertionError(f"Unexpected outbound request: {actual!r}")
        if not _matches_expected_request(actual, expected_request):
            raise AssertionError(f"Unexpected outbound request: {actual!r}")
        return _build_stub_response(request.url or "")

    with patch.object(requests.sessions.Session, "send", new=fake_send):
        yield captured

    if request_count != 1:
        raise AssertionError(f"Expected exactly one outbound request, got {request_count}.")


def _assert_allowed_job_request_id(job_request_id: object) -> str:
    if not isinstance(job_request_id, str) or not job_request_id:
        raise BlockedTopicScopeError(
            "Only a non-empty jobRequestId string is allowed in this topic."
        )
    return job_request_id


def _assert_allowed_start_job_body(body: Mapping[str, object]) -> dict[str, object]:
    normalized = dict(body)
    if normalized != {}:
        raise BlockedTopicScopeError("Only the empty JSON object body is allowed in this topic.")
    return normalized


def invoke_start_job(
    job_request_id: str,
    *,
    body: Mapping[str, object] | None = None,
) -> requests.Response:
    normalized_job_request_id = _assert_allowed_job_request_id(job_request_id)
    normalized_body = _assert_allowed_start_job_body(body or {})

    with Session(BASE_URL, token=DUMMY_TOKEN, verify_ssl=False) as session:
        return session.post(
            f"/jobExecution/jobRequests/{normalized_job_request_id}/jobs",
            json=normalized_body,
            headers={
                "Delegate-Domain": "",
                "Content-Type": "application/json",
                "Accept": START_JOB_ACCEPT,
            },
        )


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
            return _build_stub_response(request.url or "")

        self_harness = self
        with patch.object(requests.sessions.Session, "send", new=fake_send):
            result = case.invoke()

        if request_count != 1:
            raise AssertionError(f"Expected exactly one outbound request, got {request_count}.")
        return result


@pytest.fixture
def blocked_topic_scope_error() -> type[BlockedTopicScopeError]:
    return BlockedTopicScopeError


@pytest.fixture
def run_start_job_capture(
    blocked_topic_scope_error: type[BlockedTopicScopeError],
) -> Callable[[str, Mapping[str, object], str], list[dict[str, object]]]:
    del blocked_topic_scope_error

    def _run(
        job_request_id: str,
        body: Mapping[str, object],
        case_name: str,
    ) -> list[dict[str, object]]:
        normalized_job_request_id = _assert_allowed_job_request_id(job_request_id)
        normalized_body = _assert_allowed_start_job_body(body)
        expected_request = _expected_request_from_case(
            _load_case("start_job.request-flow.json", case_name)
        )

        def invocation() -> object:
            return invoke_start_job(
                normalized_job_request_id,
                body=normalized_body,
            )

        with _intercept_requests(expected_request) as captured:
            invocation()
        return captured

    return _run


@pytest.fixture
def sasctl_contract() -> SasctlContractHarness:
    return SasctlContractHarness()
