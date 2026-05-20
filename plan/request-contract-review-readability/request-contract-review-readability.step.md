# Implementation Step Tracker: request-contract-review-readability

**Topic**: request-contract-review-readability

**Phase**: code-review

**Created**: 2026-05-19

**Executor Notes**:

This is a structured-concurrency step tracker for the implementation plan in `request-contract-review-readability.plan.md`. Each step below mirrors the numbered Implementation Steps section. Mark items `[X]` (uppercase X) as completed. Do not use lowercase `[x]`.

All step metadata (topic, phase, created) must remain in the header and be updated only at phase transitions.

---

## Implementation Steps

1. [X] Create test-side contract data classes in `tests/unit/request_contract/contract_case.py`
2. [X] Inspect existing models_request_gate conftest and tests
3. [X] Design `sasctl_contract` fixture in `tests/unit/request_contract/models_request_gate/conftest.py`
4. [X] Rewrite `test_list_models_request_contract.py` with inline `EndpointContractCase`
5. [X] Rewrite `test_get_model_request_contract.py` with inline `EndpointContractCase`
6. [X] Add fixture evidence reference and verify paths
7. [X] Run validation tests and confirm all pass

---

## Workflow Stages

### Stage 1: Pre-flight Checks

- [X] Confirm worktree branch is `docs/andrew/test-contract-rewrite` (base: dev)
- [X] Confirm git status is clean or changes are intentional
- [X] Inspect `tests/unit/request_contract/models_request_gate/conftest.py` for existing fixture patterns
- [X] Inspect `tests/unit/core/test_client_contract.py` and `tests/unit/transport/test_http_client.py` for inline test style reference
- [X] Verify no global conftest imports or dependencies on `models_request_gate/conftest.py` from outside its directory

### Stage 2: Implementation

- [X] **Step 1: Create test-side contract data classes**
  - [X] Create file `tests/unit/request_contract/contract_case.py`
  - [X] Define `RequestShape` dataclass with `method`, `path`, `query`, `body`, `required_headers`
  - [X] Define `FakeResponse` dataclass with `status_code`, `json_body`, `text_body`, `headers`, and `ok_json()` classmethod
  - [X] Define `SessionSpec` dataclass with `base_url`, `token`, `verify_ssl`, and `default()` classmethod
  - [X] Define `SourceObservedFixture` dataclass with `request_path` and `response_path`
  - [X] Define `EndpointContractCase` dataclass with `name`, `invoke`, `expected`, `response`, `session`, `source_observed`
  - [X] All dataclasses: frozen=True, slots=True, full type hints, `from __future__ import annotations`
  - [X] Add docstrings to each class

- [X] **Step 2: Inspect existing models_request_gate conftest and tests**
  - [X] Review `tests/unit/request_contract/models_request_gate/conftest.py` current implementation
  - [X] Document existing `requests.Session.send` interception and fixture loading logic
  - [X] Review `test_list_models_request_contract.py` structure and JSON fixture references
  - [X] Review `test_get_model_request_contract.py` structure and JSON fixture references

- [X] **Step 3: Design `sasctl_contract` fixture**
  - [X] Add `sasctl_contract` fixture to `tests/unit/request_contract/models_request_gate/conftest.py`
  - [X] Implement `.run(case: EndpointContractCase)` method on harness object
  - [X] Harness must intercept requests via existing `requests.Session.send` mechanism
  - [X] Harness must validate request matches `case.expected` (method/path/query/body/headers)
  - [X] Harness must return mocked response from `case.response`
  - [X] Harness must preserve 1:1 linkage to `case.source_observed` (if present)
  - [X] Harness must raise clear AssertionError on mismatch

- [X] **Step 4: Rewrite test_list_models_request_contract.py**
  - [X] Replace fixture-driven JSON loading with inline `EndpointContractCase` instantiation
  - [X] Define case instance(s) for `ModelRepository.list_models()`
  - [X] Use `sasctl_contract.run(case)` pattern
  - [X] Add `SourceObservedFixture` reference to existing JSON fixtures
  - [X] Preserve existing source JSON files in `fixtures/model_repository/list_models.*`
  - [X] Verify test function bodies are shorter and contract is visible in test code

- [X] **Step 5: Rewrite test_get_model_request_contract.py**
  - [X] Replace fixture-driven JSON loading with inline `EndpointContractCase` instantiation
  - [X] Define case instance(s) for `ModelRepository.get_model(model_id=...)`
  - [X] Use `sasctl_contract.run(case)` pattern
  - [X] Add `SourceObservedFixture` reference to existing JSON fixtures
  - [X] Preserve existing source JSON files in `fixtures/model_repository/get_model.*`
  - [X] Verify test function bodies are shorter and contract is visible in test code

- [X] **Step 6: Add fixture evidence reference**
  - [X] Confirm JSON fixtures in `tests/unit/request_contract/models_request_gate/fixtures/model_repository/` are accessible
  - [X] Update `SourceObservedFixture` paths in test cases to reference correct fixture locations
  - [X] Verify no file moves needed in this phase

- [X] **Step 7: Run validation tests**
  - [X] Execute `uv run pytest tests/unit/request_contract/models_request_gate/ -v`
  - [X] Confirm all tests pass
  - [X] Confirm no import errors or missing dependencies
  - [X] (Optional) Execute `uv run ruff check tests/unit/request_contract/`
  - [X] (Optional) Expand pyright include to check `tests/unit/request_contract/` if needed

### Stage 3: Verification

- [X] All 7 Implementation Steps complete and passing
- [X] No unexpected test failures or import errors
- [X] Code review checklist passed (if applicable in workflow)

### Stage 4: Merge Readiness

- [ ] Worktree branch ready for commit
- [ ] Commit message includes Co-authored-by trailer
- [ ] Plan is review-ready and ready for handoff to executor

### Stage 5: Post-Merge (If applicable)

- [ ] TBD (merge workflow handled separately)

### Stage 6: Archive

- [ ] Plan execution complete; worktree and branch can be archived per workflow rules

---

## Notes

- Keep this file in sync with Implementation Steps in `request-contract-review-readability.plan.md`
- Mark steps complete (`[X]`) only when the corresponding Implementation Step is fully executed
- If a step is blocked or encounters issues, note the blocker and do not advance to next stage
- Do not modify topic, phase, or created fields except at explicit phase transitions
