"""供 sasctl source 測試使用、較易讀的請求合約案例模型。"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from mlops_async.core.types import JSONValue


@dataclass(frozen=True, slots=True)
class RequestShape:
    """Explicit request contract visible in test code."""

    method: str
    path: str
    query: Mapping[str, JSONValue] = field(default_factory=dict)
    body: JSONValue = None
    required_headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FakeResponse:
    """Mock response configuration consumed by the interception harness."""

    status_code: int = 200
    json_body: JSONValue = None
    text_body: str | None = None
    headers: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def ok_json(cls, body: JSONValue) -> FakeResponse:
        """Return a 200 JSON response spec."""

        return cls(status_code=200, json_body=body)


@dataclass(frozen=True, slots=True)
class SessionSpec:
    """Session configuration for a contract-case invocation."""

    base_url: str = "https://example.test"
    token: str | None = "fake-token"
    verify_ssl: bool = False

    @classmethod
    def default(cls) -> SessionSpec:
        """Return the default session settings used by source request tests."""

        return cls()


@dataclass(frozen=True, slots=True)
class SourceObservedFixture:
    """Reference the source-observed evidence that a case traces back to."""

    request_path: str
    response_path: str | None = None


@dataclass(frozen=True, slots=True)
class EndpointContractCase:
    """Represent a single readable request-contract test case."""

    name: str
    invoke: Callable[[], object]
    expected: RequestShape
    response: FakeResponse
    session: SessionSpec = field(default_factory=SessionSpec.default)
    source_observed: SourceObservedFixture | None = None
