# Request Contract Review Readability Implementation Plan

## Goal

把 sasctl source request contract tests 從 JSON-隱性 + fixture-dependent 轉成 inline-explicit + reviewer-first，使得 PR diff 不打開 fixture 即可看懂主要 endpoint contract，同時保留 source-observed evidence artifacts 的獨立性。

## Non-goals

1. Do not introduce new test dependencies such as `requests-mock`, `responses`, or additional pytest plugins.
   This refactor changes test readability and contract expression, not the underlying mocking strategy.

2. Do not replace the existing request interception / capture harness.
   The current `requests.Session.send` interception, PreparedRequest capture, request normalization, and unexpected outbound request fail-fast behavior should be preserved.

3. Do not keep JSON fixtures as the canonical human-readable test specification.
   JSON fixtures may remain as source-observed evidence or large payload fixtures, but endpoint method/path/query/body/header expectations must be visible in the pytest case.

4. Do not implement live authentication or real SAS Viya integration tests.
   Token acquisition, refresh-token behavior, real 401/403 handling, and real endpoint acceptance are out of scope for this refactor.

5. Do not design a multi-request flow DSL in this phase.
   The first version only needs to support single-request endpoint contract cases. Multi-step flows should be added only when an actual endpoint requires them.

6. Do not perform broad test directory migration in the same change.
   The first batch should refactor the existing two endpoint tests in place. Moving tests to a new `tests/contract/sasctl_source/` layout can be handled in a later cleanup if needed.

7. Do not introduce a custom exception hierarchy for test helper failures.
   Use existing pytest/assertion conventions with clear error messages unless current project conventions already require otherwise.

8. Do not expand the scope to target-client/httpx parity tests or response schema validation.
   This phase is limited to making sasctl source request contracts explicit and reviewable.

## Current Context

- `tests/unit/request_contract/models_request_gate/` 存在 2 個 endpoint test cases，測試 sasctl `ModelRepository.list_models()` 和 `ModelRepository.get_model()`
- 現有測試依賴於 conftest 中的 fixture loader 與 helper，主要 contract 語意隱含在 JSON fixtures 中
- `tests/unit/core/` 和 `tests/unit/transport/` 已採用 inline 可讀風格，reviewer 不需打開 helper 即可理解主要功能
- 已凍結 business baseline (`analysis/request-contract-review-readability/requirements.md`) 和 technical-spec (`technical-spec.md`)
- Repo 既有型別策略：imports 使用 `from __future__ import annotations`，全量型別註解

## Requirements

1. Test file 內必須明確暴露每個 case 的 endpoint contract（method/path/query/body/headers），reviewer 在 PR diff 中一眼即知
2. Source-observed JSON fixtures 與 human-readable contract surface 必須分離且一一對應可追蹤
3. Canonical truth 由 source evidence 仲裁；inline case 與 source evidence 漂移時必須升級 human review
4. Implementer 與 maintainer 可視 test file 為 primary readable surface，而不用翻 JSON 猜測 test intent
5. Readability 優先於過度泛化；若某設計要求 reviewer 跳轉 helper 才能理解主要 contract，該設計不得採用
6. 複雜 flow 仍維持可讀性；必要時 split 成多個明確 case 而非藏進 opaque aggregation

## Decisions

- **Async-planning status**: exempt — cite exemption evidence: 本 topic 無 async boundary、pooled resources、background ownership、external I/O concurrency choice、retry/timeout/cancellation policy 或 sync-to-async conversion；純屬既有同步測試的可讀性改寫。

- **Module/package placement**:
  1. 新建 helper / data class 放在 `tests/unit/request_contract/contract_case.py`（新檔案）
  2. First batch 改寫先在原地進行 (`tests/unit/request_contract/models_request_gate/`)
  3. Path migration to `tests/contract/sasctl_source/` 延後到後續 cleanup phase，先驗證可讀性改寫是否成立

- **New public API**: Yes
  - `EndpointContractCase` (dataclass，frozen，slots)
  - `RequestShape` (dataclass，frozen，slots)
  - `FakeResponse` (dataclass，frozen，slots + classmethod helper `ok_json`)
  - `SessionSpec` (dataclass，frozen，slots + classmethod helper `default`)
  - `SourceObservedFixture` (dataclass，frozen，slots)
  - 所有 test-side helper，位置 `tests/unit/request_contract/contract_case.py`

- **Interface changes**: Yes
  - 修改 `tests/unit/request_contract/models_request_gate/conftest.py`，新增 `sasctl_contract` fixture
  - 修改 `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py` 與 `test_get_model_request_contract.py` 簽名，使用新 `EndpointContractCase` API
  - 既有 `requests.Session.send` interception 與 fixture loading logic 保留不變

- **Breaking changes allowed**: Yes
  - 若 secondary actor 依賴既有 conftest fixture 簽名，需更新其 import；但 test harness 層的邏輯不變
  - 新 API 僅用於 test-side，不影響 production code

- **New dependencies**: No
  - 不新增任何 PyPI 套件或 pytest plugin
  - 仍使用既有 `requests` interception 與 conftest harness

- **Error handling strategy**:
  - 遵循既有慣例：pytest assertion error messages、conftest 中的 exception raise
  - 若 invoke callable 引發 unexpected exception，由既有 conftest 的 fail-fast 邏輯捕捉
  - 新 helper 本身不引入 custom exception type

- **Typing strategy**: Strict typing（full annotations）
  - 所有 `EndpointContractCase` / `RequestShape` / `FakeResponse` / `SessionSpec` 欄位全量型別註解
  - Test function 與 helper 簽名亦全量型別
  - 使用 `from __future__ import annotations` 支援前向參考
  - 允許 `Callable`、`Mapping` 等 ABC 型別，不強制 `dict` / `list` literal

## Public Contract / API Changes

### New test-side data classes (all in `tests/unit/request_contract/contract_case.py`)

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestShape:
    """Explicit endpoint request contract visible in test code."""
    method: str
    path: str
    query: Mapping[str, Any] = field(default_factory=dict)
    body: Any | None = None
    required_headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FakeResponse:
    """Mock response for interception harness."""
    status_code: int = 200
    json_body: Any | None = None
    text_body: str | None = None
    headers: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def ok_json(cls, body: Any) -> FakeResponse:
        """Convenience factory for 200 JSON responses."""
        return cls(status_code=200, json_body=body)


@dataclass(frozen=True, slots=True)
class SessionSpec:
    """Session configuration for test harness."""
    base_url: str = "https://example.test"
    token: str | None = "fake-token"
    verify_ssl: bool = False

    @classmethod
    def default(cls) -> SessionSpec:
        """Default session config."""
        return cls()


@dataclass(frozen=True, slots=True)
class SourceObservedFixture:
    """Reference to source-observed JSON evidence files."""
    request_path: str
    response_path: str | None = None


@dataclass(frozen=True, slots=True)
class EndpointContractCase:
    """Single-request endpoint contract case.

    Attributes:
        name: Human-readable case identifier (format: "<service>.<operation>").
        invoke: Callable that invokes the sasctl endpoint.
        expected: Explicit endpoint contract (method/path/query/body/headers).
        response: Mock response for interception.
        session: Session configuration (defaults to SessionSpec.default()).
        source_observed: Reference to source JSON evidence (optional).
    """
    name: str
    invoke: Callable[[], Any]
    expected: RequestShape
    response: FakeResponse
    session: SessionSpec = field(default_factory=SessionSpec.default)
    source_observed: SourceObservedFixture | None = None
```

### Modified conftest fixture

- Existing `requests.Session.send` interception and PreparedRequest capture logic preserved
- New `sasctl_contract` fixture (in `tests/unit/request_contract/models_request_gate/conftest.py`):
  - accepts `EndpointContractCase` instance
  - returns a harness with `.run(case)` method that validates expected shape and returns mocked response
  - maintains 1:1 linkage between case and source JSON evidence (if present)

### Modified test signatures

- `test_list_models_request_contract.py` and `test_get_model_request_contract.py`
- Replace fixture-driven JSON loading with `EndpointContractCase` instantiation
- Test function bodies become shorter and more explicit

## Affected Files / Modules

Likely affected files:
- `tests/unit/request_contract/contract_case.py` (new)
- `tests/unit/request_contract/models_request_gate/conftest.py` (modified)
- `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py` (modified)
- `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py` (modified)
- `tests/unit/request_contract/models_request_gate/fixtures/` (unchanged, source evidence preserved)

Candidate files to inspect:
- `tests/unit/core/test_client_contract.py` (existing inline test style reference)
- `tests/unit/transport/test_http_transport.py` (existing inline test style reference)
- `tests/conftest.py` (if global fixture setup affects request interception)

## Implementation Steps

1. **Create test-side contract data classes**
   - Open new file `tests/unit/request_contract/contract_case.py`
   - Define `RequestShape`, `FakeResponse`, `SessionSpec`, `SourceObservedFixture`, `EndpointContractCase` as frozen dataclasses with slots
   - All fully typed; use `from __future__ import annotations`
   - Add classmethod helpers: `FakeResponse.ok_json()`, `SessionSpec.default()`
   - Add docstrings to each class explaining its role in the contract model

2. **Inspect existing models_request_gate conftest and tests**
   - Open `tests/unit/request_contract/models_request_gate/conftest.py`
   - Document current `requests.Session.send` interception logic
   - Identify fixture loading and case construction pattern
   - Open `test_list_models_request_contract.py` and `test_get_model_request_contract.py`
   - Document current test structure and JSON fixture references

3. **Design `sasctl_contract` fixture**
   - In `tests/unit/request_contract/models_request_gate/conftest.py`, add `sasctl_contract` fixture
   - Fixture returns a harness object with `.run(case: EndpointContractCase) -> dict` method
   - Harness must:
     - Intercept outbound requests via existing `requests.Session.send` mechanism
     - Validate incoming request matches `case.expected` (method/path/query/body/headers)
     - Return mocked response from `case.response`
     - Preserve 1:1 linkage to `case.source_observed` fixture reference (if present)
   - Harness should raise clear AssertionError if request does not match expected shape

4. **Rewrite test_list_models_request_contract.py**
   - Replace fixture-driven JSON loading with inline `EndpointContractCase` instantiation
   - Case instance names: `case_list_models_default` (for primary case)
   - Invoke `sasctl_contract.run(case)` and validate response
   - Preserve existing source JSON fixture files (`fixtures/model_repository/list_models.request.json`, etc.)
   - Add SourceObservedFixture reference to link test case to evidence

5. **Rewrite test_get_model_request_contract.py**
   - Apply same refactoring pattern as step 4
   - Define case for `ModelRepository.get_model(model_id="test-model")`
   - Preserve existing source JSON fixtures
   - Document inline contract surface for reviewer

6. **Add fixture evidence reference**
   - Confirm existing JSON fixtures in `tests/unit/request_contract/models_request_gate/fixtures/model_repository/` are still discoverable
   - Update `SourceObservedFixture` paths to match current layout (no file move needed in this phase)

7. **Run validation tests**
   - Execute `uv run pytest tests/unit/request_contract/models_request_gate/ -v`
   - Confirm all tests pass
   - Confirm no import errors or missing dependencies

## Test Plan

### Happy path
- `test_list_models_request_contract.py::test_list_models_default_request_shape`
  - Invoke `ModelRepository.list_models()`
  - Verify GET /modelRepository/models outbound request
  - Verify Authorization header present
  - Confirm 200 mocked response returned

### Invalid input
- TBD in later endpoint cases (not in current two-case starter set)

### Edge case
- `test_list_models_request_contract.py::test_list_models_empty_response`
  - Invoke `ModelRepository.list_models()`
  - Verify mocked response with empty `items: []` list
  - Confirm contract still valid with minimal payload

- `test_get_model_request_contract.py::test_get_model_path_parameter`
  - Invoke `ModelRepository.get_model(model_id="test-model-123")`
  - Verify path parameter substitution in `/modelRepository/models/{id}`
  - Confirm exact path in outbound request

### Regression
- Confirm existing `requests.Session.send` interception still works
- Confirm existing PreparedRequest capture logic unchanged
- Confirm existing fixture loading (via conftest helpers) not broken by new `sasctl_contract` fixture

### Backward compatibility
- If any external test imports from `tests/unit/request_contract/models_request_gate/conftest.py`, ensure no signature breakage
- New API is additive; existing helpers remain available

## Validation Commands

```bash
# Run all models_request_gate tests
uv run pytest tests/unit/request_contract/models_request_gate/ -v

# Run type checking (if pyright include list is expanded)
uv run pyright tests/unit/request_contract/

# Run style/lint (existing ruff config)
uv run ruff check tests/unit/request_contract/

# (Optional) coverage check
uv run pytest tests/unit/request_contract/models_request_gate/ --cov=tests/unit/request_contract --cov-report=term-missing
```

## Risks

1. **Hidden coupling in existing conftest**: If global conftest or other test modules depend on internal fixture signatures, changes to conftest.py may break downstream tests. Mitigation: inspect all imports of models_request_gate/conftest before finalizing changes.

2. **Interception harness complexity**: Porting request shape validation from JSON schema to runtime Python assertions may introduce edge cases (e.g., header case sensitivity, query param ordering). Mitigation: validate against existing test runs and compare outbound requests side-by-side with original JSON contracts.

3. **Fixture file layout assumptions**: If existing JSON fixture paths change or are moved, SourceObservedFixture reference may become stale. Mitigation: keep fixture files in place during this phase; deferred to later cleanup.

4. **Early generalization pressure**: Reviewers or follow-on contributors may push to expand `EndpointContractCase` prematurely (e.g., add multi-request support, assertion rules, auto-comparison logic). Mitigation: document non-goals and plan in commit message; defer expansion until real multi-request examples arise.

5. **Type annotation strictness**: If existing test code uses `Any` or loose typing, new dataclass with full type hints may conflict with project's testing conventions. Mitigation: consult existing test module typing style (e.g., `tests/unit/core/`) as reference.

## Rollback Plan

If implementation encounters material conflicts or blocking issues:

1. **Revert files**:
   - `git checkout tests/unit/request_contract/contract_case.py` (if created)
   - `git checkout tests/unit/request_contract/models_request_gate/conftest.py`
   - `git checkout tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
   - `git checkout tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`

2. **Verify rollback**:
   - `uv run pytest tests/unit/request_contract/models_request_gate/ -v` should pass with original code

3. **Return to requirements / technical-spec**:
   - If readability contract proves incompatible with existing harness, escalate to `analysis/request-contract-review-readability/requirements.md` for rebaseline decision
   - If source evidence linkage requires new fixture structure, escalate to technical-spec for architecture conflict resolution

## Open Questions

None. All decision points are resolved as of plan authoring. The 7 Decisions sections above cover module placement, API shape, interface changes, breaking changes, dependencies, error handling, and typing strategy.
