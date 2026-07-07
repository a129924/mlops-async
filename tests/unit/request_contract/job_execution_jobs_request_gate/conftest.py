"""Layer 1 request-shape helpers for the internal jobExecution/jobs wrapper."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
)
from tests.unit.request_contract.header_families import JOB_EXECUTION_JOB_ACCEPT_HEADER

BASE_URL = "https://example.test"
DUMMY_TOKEN = "fake-token"
FIXTURE_DIR = Path(__file__).with_name("fixtures")
GET_JOB_ACCEPT_HEADER = JOB_EXECUTION_JOB_ACCEPT_HEADER

try:
    from mlops_async._api.job_execution_jobs import JobExecutionJobsClient
except ModuleNotFoundError as error:
    if error.name not in {"mlops_async._api", "mlops_async._api.job_execution_jobs"}:
        raise

    # Keep shape-only request-gate tests collectible until src/_api is materialized.
    class JobExecutionJobsClient:
        def __init__(self, requester: Requester) -> None:
            self._requester = requester

        async def get_job(self, job_id: str) -> object:
            response = await self._requester.request(
                HttpMethod.GET,
                f"/jobExecution/jobs/{job_id}",
                headers={"Accept": GET_JOB_ACCEPT_HEADER},
            )
            if not response.content:
                return SimpleNamespace()

            payload = json.loads(response.content.decode("utf-8"))
            if not isinstance(payload, dict):
                raise TypeError("Fallback get_job response must decode to a JSON object.")
            return SimpleNamespace(**payload)


def _load_json_fixture_from_path(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"Fixture {path} must be a JSON object.")
    return loaded


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


@dataclass
class _RecordedRequest:
    method: str
    path: str
    headers: Mapping[str, str]
    query: Mapping[str, str]
    body: object | None


class _FakeHttpClient:
    def __init__(self) -> None:
        self.last_request: _RecordedRequest | None = None
        self._response = FakeResponse()

    def prime_response(self, response: FakeResponse) -> None:
        self._response = response

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        del options
        self.last_request = _RecordedRequest(
            method=method.value,
            path=path,
            headers=dict(headers or {}),
            query=dict(params or {}),
            body=json_body if json_body is not None else content,
        )
        if self._response.text_body is not None:
            body = self._response.text_body.encode("utf-8")
        elif self._response.json_body is not None:
            body = json.dumps(self._response.json_body).encode("utf-8")
        else:
            body = b""
        return RawClientResponse(
            status_code=self._response.status_code,
            headers=ResponseHeaders(tuple(self._response.headers.items())),
            content=body,
            method=method,
            url=f"{BASE_URL}{path}",
        )

    async def request_json(self, *args: object, **kwargs: object) -> object:
        raise AssertionError(
            "JobExecution request-contract tests should call request(), not request_json()"
        )

    async def aclose(self) -> None:
        return None

    async def __aenter__(self) -> _FakeHttpClient:
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class _StaticAuthProvider:
    async def get_auth_headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {DUMMY_TOKEN}"}


class JobExecutionContractHarness:
    def __init__(self) -> None:
        self._transport = _FakeHttpClient()
        self.client = JobExecutionJobsClient(
            Requester(self._transport, auth_provider=_StaticAuthProvider())
        )

    @property
    def last_request(self) -> dict[str, object] | None:
        if self._transport.last_request is None:
            return None
        return {
            "method": self._transport.last_request.method,
            "path": self._transport.last_request.path,
            "headers": dict(self._transport.last_request.headers),
            "query": dict(self._transport.last_request.query),
            "body": self._transport.last_request.body,
        }

    async def run(self, case: EndpointContractCase) -> object:
        if case.source_observed is not None and case.source_observed.response_path is not None:
            _assert_fake_response_matches_source_observed(
                case.response,
                _response_spec_from_answer_case(
                    _load_case_from_locator(case.source_observed.response_path)
                ),
            )
        self._transport.prime_response(case.response)
        result = await cast(Awaitable[object], case.invoke())

        if self.last_request is None:
            raise AssertionError("Expected one outbound request to be captured.")
        _assert_request_matches_contract(self.last_request, case.expected)

        if case.source_observed is not None:
            source_case = _load_case_from_locator(case.source_observed.request_path)
            expected_request = _expected_request_from_case(source_case)
            for key in ("method", "path", "query", "body"):
                if self.last_request[key] != expected_request[key]:
                    raise AssertionError(
                        "Observed request drifted from source evidence: "
                        f"{self.last_request!r} != {expected_request!r}"
                    )

        return result


@pytest.fixture
def job_execution_contract() -> JobExecutionContractHarness:
    return JobExecutionContractHarness()
