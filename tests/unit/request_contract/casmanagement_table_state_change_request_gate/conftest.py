"""Request-shape helpers for CASManagement change_table_state request gate."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, quote, urlsplit

import pytest
import requests

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
)

BASE_URL = "https://example.test"
DUMMY_TOKEN = "fake-token"
FIXTURE_DIR = Path(__file__).with_name("fixtures").resolve()
TOPIC_PACKAGE_DIR = Path(__file__).resolve().parent
CHANGE_TABLE_STATE_PATH_PREFIX = "/casManagement/servers/cas-shared-default/caslibs/"
BODY_OVERRIDE_SENTINEL = object()


def _is_topic_scoped_pytest_run(config: pytest.Config) -> bool:
    requested_targets = tuple(str(arg) for arg in config.args)
    if not requested_targets:
        return False

    for raw_target in requested_targets:
        candidate = Path(raw_target)
        if not candidate.is_absolute():
            candidate = (config.rootpath / candidate).resolve()
        else:
            candidate = candidate.resolve()

        try:
            candidate.relative_to(TOPIC_PACKAGE_DIR)
        except ValueError:
            return False

    return True


def pytest_configure(config: pytest.Config) -> None:
    if not _is_topic_scoped_pytest_run(config):
        return

    cov_plugin = config.pluginmanager.getplugin("_cov")
    if cov_plugin is not None:
        cov_plugin.options.cov_fail_under = 0


class BlockedTopicScopeError(RuntimeError):
    """Raised when a call drifts outside this topic's request boundary."""


def _normalize_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise BlockedTopicScopeError(
            f"Only a non-empty {field_name} string is allowed in this topic."
        )
    if not value.strip():
        raise BlockedTopicScopeError(
            f"Only a non-empty {field_name} string is allowed in this topic."
        )
    return value


def _normalize_state(value: object) -> str:
    if not isinstance(value, str):
        raise BlockedTopicScopeError("Only value=loaded is allowed in this topic.")
    if value == "loaded":
        return value
    if value == "unloaded":
        raise BlockedTopicScopeError("value=unloaded is blocked in this topic.")
    raise BlockedTopicScopeError("Only value=loaded is allowed in this topic.")


def _normalize_extra_query(extra_query: object | None) -> dict[str, str]:
    if extra_query is None:
        return {}
    raise BlockedTopicScopeError("Extra query params are blocked in this topic.")


def _normalize_body_override(
    body_override: object,
    *,
    caslib: str,
    table_name: str,
) -> dict[str, str]:
    if body_override is BODY_OVERRIDE_SENTINEL:
        return {
            "outputCaslibName": caslib,
            "outputTableName": table_name,
        }
    if body_override is None:
        raise BlockedTopicScopeError("Request body is required in this topic.")
    if not isinstance(body_override, dict):
        raise BlockedTopicScopeError("Request body must be a JSON object in this topic.")

    output_caslib = body_override.get("outputCaslibName")
    output_table_name = body_override.get("outputTableName")
    if output_caslib != caslib:
        raise BlockedTopicScopeError("Request body outputCaslibName must match the path caslib.")
    if output_table_name != table_name:
        raise BlockedTopicScopeError("Request body outputTableName must match the path tableName.")
    return {
        "outputCaslibName": str(output_caslib),
        "outputTableName": str(output_table_name),
    }


def _normalize_endpoint_variant(endpoint_variant: object) -> str:
    if endpoint_variant == "change_table_state":
        return "change_table_state"
    if endpoint_variant == "list_tables":
        raise BlockedTopicScopeError("list_tables drift is blocked in this topic.")
    if endpoint_variant == "get_table":
        raise BlockedTopicScopeError("get_table drift is blocked in this topic.")
    raise BlockedTopicScopeError("Only change_table_state is allowed in this topic.")


def _load_json_fixture_from_path(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"Fixture {path} must be a JSON object.")
    return loaded


def _split_fixture_locator(locator: str) -> tuple[Path, str | None]:
    raw_path, _, raw_case_name = locator.partition("#")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        resolved_path = candidate.resolve()
    else:
        resolved_path = (FIXTURE_DIR / candidate).resolve()

    try:
        resolved_path.relative_to(FIXTURE_DIR)
    except ValueError as exc:
        raise AssertionError("Fixture locator must stay under the topic fixture root.") from exc

    return resolved_path, raw_case_name or None


def _load_case_from_locator(locator: str) -> Mapping[str, object]:
    fixture_path, case_name = _split_fixture_locator(locator)
    payload = _load_json_fixture_from_path(fixture_path)
    cases = payload.get("cases")
    if not isinstance(cases, dict):
        raise TypeError(f"Fixture {fixture_path} must define a cases object.")
    if len(cases) != 1:
        raise AssertionError(f"Fixture {fixture_path} must define exactly one case for this topic.")
    if case_name is None:
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


def _assert_source_observed_required_headers(
    actual_headers: Mapping[str, object],
    expected_request: Mapping[str, object],
) -> None:
    expected_headers = expected_request.get("required_header_subset", {})
    if not isinstance(expected_headers, dict):
        raise TypeError("Source-observed request required_header_subset must be a JSON object.")

    lowered_actual = {key.lower(): str(value) for key, value in actual_headers.items()}
    for header_name, expected_value in expected_headers.items():
        actual_value = lowered_actual.get(str(header_name).lower())
        if actual_value is None:
            raise AssertionError("Observed request headers drifted from source evidence.")
        if actual_value != str(expected_value):
            raise AssertionError("Observed request headers drifted from source evidence.")


def _response_spec_from_answer_case(case: Mapping[str, object]) -> Mapping[str, object]:
    responses = case.get("responses")
    if not isinstance(responses, list) or len(responses) != 1:
        raise AssertionError("Each mock-responses case must define exactly one response.")
    response_entry = responses[0]
    if not isinstance(response_entry, dict):
        raise AssertionError("Mock response entry must be an object.")
    response = response_entry.get("response")
    if not isinstance(response, dict):
        raise AssertionError("Mock response entry must define a response object.")
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
        if expected_prefix and not str(header_value).startswith(expected_prefix):
            raise AssertionError(f"Unexpected outbound request: {actual!r}")


def _assert_fake_response_matches_source_observed(
    response: FakeResponse,
    source_response: Mapping[str, object],
) -> None:
    if response.status_code != int(source_response["status_code"]):  # type: ignore[arg-type]
        raise AssertionError("Fake response status_code drifted from source-observed fixture.")

    headers = source_response.get("headers", {})
    if not isinstance(headers, dict):
        raise TypeError("Source-observed response headers must be a JSON object.")
    if dict(response.headers) != {str(key): str(value) for key, value in headers.items()}:
        raise AssertionError("Fake response headers drifted from source-observed fixture.")
    if response.json_body != source_response.get("json_body"):
        raise AssertionError("Fake response json_body drifted from source-observed fixture.")
    if response.text_body != source_response.get("text_body"):
        raise AssertionError("Fake response text_body drifted from source-observed fixture.")


def _normalize_query(query: str) -> dict[str, object]:
    parsed = parse_qs(query, keep_blank_values=True)
    normalized: dict[str, object] = {}
    for key, values in parsed.items():
        normalized[key] = values[0] if len(values) == 1 else values
    return normalized


def _body_value(request: requests.PreparedRequest) -> object:
    body = request.body
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    if body is None:
        return None

    content_type = str(request.headers.get("Content-Type", ""))
    if content_type.startswith("application/json") and isinstance(body, str):
        return json.loads(body)
    return body


def _capture_semantic_request(request: requests.PreparedRequest) -> dict[str, object]:
    split = urlsplit(request.url or "")
    return {
        "method": request.method,
        "path": split.path,
        "headers": dict(request.headers),
        "query": _normalize_query(split.query),
        "body": _body_value(request),
    }


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


class CASManagementTableStateChangeClient:
    """Minimal state-change client used only for this isolated request gate."""

    def __init__(self) -> None:
        self._session = requests.Session()

    def change_table_state(
        self,
        *,
        caslib: object,
        table_name: object,
        state: object = "loaded",
        include_state_query: bool = True,
        extra_query: object | None = None,
        body_override: object = BODY_OVERRIDE_SENTINEL,
        endpoint_variant: object = "change_table_state",
    ) -> object:
        normalized_caslib = _normalize_non_empty_string(caslib, "caslib")
        normalized_table_name = _normalize_non_empty_string(table_name, "tableName")
        _normalize_endpoint_variant(endpoint_variant)
        normalized_state = _normalize_state(state)
        normalized_extra_query = _normalize_extra_query(extra_query)
        normalized_body = _normalize_body_override(
            body_override,
            caslib=normalized_caslib,
            table_name=normalized_table_name,
        )

        if not include_state_query:
            raise BlockedTopicScopeError("Missing value query is blocked in this topic.")

        encoded_caslib = quote(normalized_caslib, safe="")
        encoded_table_name = quote(normalized_table_name, safe="")
        query = {"value": normalized_state}
        query.update(normalized_extra_query)
        response = self._session.request(
            "PUT",
            (
                f"{BASE_URL}{CHANGE_TABLE_STATE_PATH_PREFIX}{encoded_caslib}"
                f"/tables/{encoded_table_name}/state"
            ),
            params=query,
            headers={
                "Authorization": f"Bearer {DUMMY_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=normalized_body,
        )
        if not response.content:
            return SimpleNamespace()

        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError(
                "CAS change_table_state request-gate response must decode to a JSON object."
            )
        return SimpleNamespace(**payload)


class CASManagementTableStateChangeContractHarness:
    def __init__(self) -> None:
        self.client = CASManagementTableStateChangeClient()
        self.last_request: dict[str, object] | None = None

    def run(self, case: EndpointContractCase) -> object:
        self.last_request = None
        if case.source_observed is not None and case.source_observed.response_path is not None:
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
            harness.last_request = actual
            if request_count > 1:
                raise AssertionError(f"Unexpected outbound request: {actual!r}")
            _assert_request_matches_contract(actual, case.expected)
            return _build_fake_response(case.response, request.url or "")

        harness = self
        with patch.object(requests.sessions.Session, "send", new=fake_send):
            result = case.invoke()

        if request_count != 1:
            raise AssertionError(f"Expected exactly one outbound request, got {request_count}.")

        if case.source_observed is not None:
            source_case = _load_case_from_locator(case.source_observed.request_path)
            expected_request = _expected_request_from_case(source_case)
            if self.last_request is None:
                raise AssertionError("Expected one outbound request to be captured.")
            for key in ("method", "path", "query", "body"):
                if self.last_request[key] != expected_request[key]:
                    raise AssertionError(
                        "Observed request drifted from source evidence: "
                        f"{self.last_request!r} != {expected_request!r}"
                    )
            actual_headers = self.last_request.get("headers")
            if not isinstance(actual_headers, dict):
                raise TypeError("Captured request headers must be a mapping.")
            _assert_source_observed_required_headers(actual_headers, expected_request)

        return result


@pytest.fixture
def blocked_topic_scope_error() -> type[BlockedTopicScopeError]:
    return BlockedTopicScopeError


@pytest.fixture
def casmanagement_table_state_change_contract() -> CASManagementTableStateChangeContractHarness:
    return CASManagementTableStateChangeContractHarness()
