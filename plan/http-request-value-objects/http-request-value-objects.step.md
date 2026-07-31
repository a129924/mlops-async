---
topic: http-request-value-objects
phase: review-ready
created: 2026-07-29
rework: PR-57-selected-six-threads
---

# http-request-value-objects — Step Tracking

> **Executor**: Mark each step `[X]` only after evidence exists.
> The completed initial-pass record below is historical evidence. The pending
> rework ledger is a separate pass and must not be marked complete from the
> prior approval.

## Workflow Stages — Initial Pass (preserved)

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps — Initial Pass (preserved)

- [X] 1. 建立 request value objects、JsonBody、RawBody、single body union 與 readonly compatibility properties。
- [X] 2. 實作 BaseUrl、EndpointPath literal/from-segments、QueryParams exact encoding rules。
- [X] 3. 整合 request Headers 與 header policy：保留 precedence、final lowercase last-wins/no-duplicate output。
- [X] 4. 修改 Client contract，新增 execution-first contract 與 JSON primitive compatibility adapter。
- [X] 5. 修改 Requester，只做 immutable JSON-domain composition。
- [X] 6. 修改 HttpClient，只執行 canonical URL/body，無 library default/override second semantics。
- [X] 7. 建立 value-object/body/query/endpoint contract tests。
- [X] 8. 僅更新 `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py` 與 `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`：body=None 無 Content-Type，authorization/accept 使用 lowercase canonical lookup。
- [X] 9. 更新 token/password-token tests，驗證 raw primitive non-regression 與 Requester exclusion。
- [X] 10. 以 contract/type tests 驗證 future endpoint family 回傳 EndpointPath，且不 port concrete catalog。

## Workflow Stages — PR #57 Selected Rework

- [X] rework-plan-authoring: six selected IDs, HUMAN locks, exact path inventory, review-log intake, corrected reviewer-handoff contract, and Tester-only fixed-schema TDD verdict contract are complete. The independently approved contract is now in `creator-in-progress` for the Tester-owned TDD pass.
- [X] rework-plan-review: independent Plan-Reviewer `approved` verdict is recorded in the review log for the current rework contract.
- [X] rework-tdd-test-authoring: Tester recorded a `non-trivial` D1 verdict and wrote only the two allowed test modules plus `http-request-value-objects.tdd-verdict.yaml`. The fixed-schema verdict maps exactly the six selected IDs across all five required coverage categories, sets `expected_initial_status: red`, records individual RED evidence for every mapped test name, and records `production_code_modified: false` from the HEAD-based guard. Owner WSL validation: `uv run --no-sync pytest --no-header -rN tests/unit/core/test_http_request.py tests/unit/transport/test_http_client.py` exited 1 with `6 failed, 62 passed`; the six failures are the expected RED contract evidence. Targeted-run coverage was 80.97% (below the 90.0% fail-under) and is not a functional blocker for this TDD handoff.
- [X] rework-implementation: R1-R6 implementation is complete. Owner WSL validation recorded 26 passed for the single focused run and 70 passed for the combined focused run, both with functional failures 0; the full suite recorded 383 passed, 10 skipped, and 95.13% coverage. Ruff passed and Pyright exited 0. Focused partial-coverage fail-under and the CRLF-only diff-check output are non-functional, pre-existing noise and do not change the implementation result.
- [X] rework-implementation-review: independent Implementation-Reviewer recorded an `approved` verdict with no blocking issues. Evidence accepted for the selected R1-R6 scope: the six mapped TDD contracts moved from the recorded RED baseline to focused functional passes (26 passed for the single focused run; 70 passed for the combined focused run), the full suite recorded 383 passed and 10 skipped at 95.13% coverage, and Ruff and Pyright passed. This closes only the implementation-review gate; `rework-code-review` remains pending for an independent Code-Reviewer.
- [X] rework-code-review: independent Code-Reviewer recorded `approved` with no blocking issues. R4 confirms raw C0 is rejected before `urlsplit`; R6 confirms both adapters reject parsed scheme/netloc, including mixed-case absolute and network-path inputs, before HTTP-library build/send. R1 (`b"null"`), R2 direct-constructor invariants, R5 explicit-accept preservation, and embedded-query compatibility remain covered. Owner WSL focused validation recorded `80 passed` with functional failures `0`; `81.94%` targeted coverage produced only the known partial fail-under exit `1` and is non-blocking. The missing reasons on test-only `type: ignore` comments are a non-blocking warning; CRLF-only diff noise is not a code defect. This closes only the code-review gate; publication and PR actions remain unauthorized.

## Rework Implementation Steps — Pending

- [X] TDD. The pre-write `git diff --quiet HEAD -- src/` guard exited 0 and is recorded as `production_code_modified: false`; no reset, clean, or checkout was used. Tester wrote only `tests/unit/core/test_http_request.py`, `tests/unit/transport/test_http_client.py`, and `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml`. The YAML retains only the six required top-level keys, records non-trivial D1 and `expected_initial_status: red`, and contains individual RED evidence for `test_execute_serializes_json_null_as_json_literal`, `test_direct_construction_matches_named_invariants`, `test_endpoint_path_literal_rejects_noncanonical_static_paths`, `test_base_url_rejects_invalid_authority_characters`, `test_execute_removes_implicit_accept_but_preserves_explicit_accept`, and `test_primitive_request_adapters_preserve_embedded_query`. The exact-six mapping uses `happy path`, `error/exception`, `boundary/edge`, `state/side effects`, and `integration points`, collectively covering all five categories. Owner WSL command `uv run --no-sync pytest --no-header -rN tests/unit/core/test_http_request.py tests/unit/transport/test_http_client.py`: 6 failed, 62 passed; coverage 80.97% is a targeted-run non-functional fail-under result, not a functional blocker.
- [X] R1. `PRRT_kwDOSTt_386VAaWm`: preserve `JsonBody(None)` as wire `b"null"` through body-variant transport handling; do not serialize in the value object.
- [X] R2. `PRRT_kwDOSTt_386VAaWr`: enforce equivalent direct and named construction invariants for `BaseUrl`, `EndpointPath`, `QueryParams`, and `Headers`; the mapping follow-up is complete.
- [X] R3. `PRRT_kwDOSTt_386VAaWs`: reject non-canonical static `EndpointPath.literal()` inputs before transport normalization.
- [X] R4. `PRRT_kwDOSTt_386VAaWw`: reject BaseUrl authorities/hostnames containing parser-permitted invalid characters at construction.
- [X] R5. `PRRT_kwDOSTt_386VAaWx`: remove implicit httpx `accept: */*` on canonical direct execute while preserving explicit `accept`.
- [X] R6. `PRRT_kwDOSTt_386VAaW2`: preserve embedded primitive path query behavior in both `request()` and `request_json()` through canonical construction.

## Rework Exclusions

- [ ] No work may be added for the three HUMAN-excluded active threads or the
  HUMAN-excluded outdated unresolved thread documented in the review log.
- [ ] No origin-only BaseUrl, body-union, lowercase-Headers, endpoint-family,
  token/form, or primitive-adapter-role lock may be reopened.

## R4/R6 Hardening Implementation-Reviewer Evidence (appended)

- [X] `rework-implementation-review` remains complete: the independent
  Implementation-Reviewer recorded `approved` for the R4/R6 hardening
  evidence. R4 validates C0 before `urlsplit` and rejects invalid authority
  through both scheme and netloc validation; R6 remains within the primitive
  compatibility-adapter lock.
- [X] The selected-module functional validation recorded `80 passed`.
  Targeted coverage was `81.94%`, a partial fail-under result classified as
  non-functional and not a blocker for this implementation-review closure.
- [X] `rework-code-review` is complete under the independent `approved`
  verdict. No publication, PR action, or scope expansion is authorized by this
  evidence.
