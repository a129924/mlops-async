# models-request-gate-execution

## Goal

建立可交給 `python-implementation-workflow` 的 execution contract，讓後續工作只在 `tests/unit/request_contract/models_request_gate/**` 與既有 repo dependencies 內完成 `list_models` 與 `get_model` 的 request-only gate，並在依賴或 request-contract evidence 不足時主動 BLOCKED。

## Non-goals

- 本變更不會修改 `src/mlops_async/**` production code。
- 本變更不會建立 response / error contract。
- 本變更不會更新 `docs/migration-map.md` 或 `docs/porting-ledger.md`。
- 本變更不會把 `sasctl.ModelRepository.get_model` 的非 direct-request variants 自動納入同一個 execution topic。
- 本變更不會修改 `pyproject.toml` 或 `uv.lock`。
- 本變更不會新增 dependency。

## Current Context

`models-request-gate-proof` 已凍結第一個 read-only `model-repository/models` family 的 planning baseline，並明確要求 follow-up execution topic 承接 request-only mock/interception、fixtures、與 request tests。現有 repo-visible evidence 位於 `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`、`docs/api-endpoints/markdown-reference/SASCTL_MLOPS_OPERATIONS.md`、`docs/api-endpoints/swagger-spec/models-spec.yaml` 與 `docs/api-endpoints/swagger-spec/openapi-complete.yaml`。目前可以確認 `legacy get_all_models` 與 `legacy get_one_model` 的 direct request path；`sasctl.ModelRepository.get_model` 的非 direct-request branch 仍屬 out-of-scope stop area。本 topic 的 bootstrap boundary 已凍結為：不得修改 `pyproject.toml`、不得修改 `uv.lock`、只能使用既有 repo dependencies。

## Requirements

1. 後續 execution 只能修改本 topic 文件與 `tests/unit/request_contract/models_request_gate/**`；不得修改 `pyproject.toml` 或 `uv.lock`，且只能使用既有 repo dependencies；若既有依賴不足，必須回報 `BLOCKED`。
2. `list_models` 與 `get_model` 都必須進入 request-only gate，且完成物必須同時包含 request-flow fixture、mock-response answer set、與 request-contract tests。
3. request-contract tests 只可比對 semantic request behavior：method、path、required header subset、query key/value semantics、body shape。
4. request-contract tests 不得比對 query order、host、content-length、connection headers、transport-generated headers。
5. `get_model` 在本 topic 只允許 direct identifier branch 進入完成宣告；非 direct-request variants 必須保持 blocked。
6. `list_models` 在本 topic 只允許 bare GET 與 repo-visible evidence 已確認的 query semantics；未證實 query fields 不得自動納入測試 contract。
7. 本 topic 必須保留 request-only boundary：不得修改 `src/mlops_async/**`、不得建立 response/error contract、不得更新 migration map / ledger。
8. `plan/models-request-gate-execution/models-request-gate-execution.spec.md` 必須作為非 trivial execution 的 primary behavior contract。

## Decisions

- Module/package placement: 新增測試與 fixtures 只允許放在 `tests/unit/request_contract/models_request_gate/`；topic context 文件只允許更新 `analysis/models-request-gate-execution/*.md` 與 `plan/models-request-gate-execution/*.md`。
- New public API: no — 本 topic 不新增或修改任何 public Python API。
- Interface changes: no — 本 topic 只建立 tests-side request-contract artifacts，不變更現有 `src/mlops_async/**` 介面。
- Breaking changes allowed: no — 不允許破壞既有 library surface。
- New dependencies: no — 本 topic 只能使用既有 repo dependencies；若 mock/interception 需要額外 dependency，直接 `BLOCKED`，不得修改 `pyproject.toml` 或 `uv.lock`。
- Error handling strategy: 規劃階段以 active gate 為主；若既有依賴不足、allowed file scope 不足、或 request contract evidence 不足，workflow 必須回報 `BLOCKED`，不得以 fallback 行為繼續。
- Typing strategy: 所有新增 Python tests / helpers 維持完整 type hints，遵守 repo 既有 strict typing 基線；不使用 `Any` 來掩蓋 request artifact shape。

## Public Contract / API Changes

No public API changes. 本 topic 只建立 request-only 測試與 fixture artifacts，並不新增 `src/mlops_async` 的對外函式、類別、或方法。

## Affected Files / Modules

Likely affected files:
- `analysis/models-request-gate-execution/requirements.md`
- `analysis/models-request-gate-execution/technical-spec.md`
- `plan/models-request-gate-execution/models-request-gate-execution.plan.md`
- `plan/models-request-gate-execution/models-request-gate-execution.spec.md`
- `plan/models-request-gate-execution/models-request-gate-execution.step.md`
- `tests/unit/request_contract/models_request_gate/conftest.py`
- `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
- `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
- `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json`
- `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json`
- `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json`
- `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`

Candidate files to inspect:
- `docs/standards/request-contract-testing.md`
- `analysis/models-request-gate-proof/requirements.md`
- `analysis/models-request-gate-proof/technical-spec.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
- `docs/api-endpoints/markdown-reference/SASCTL_MLOPS_OPERATIONS.md`
- `docs/api-endpoints/swagger-spec/models-spec.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `pyproject.toml`
- `uv.lock`

## Implementation Steps

1. Open `plan/models-request-gate-execution/models-request-gate-execution.plan.md`, `plan/models-request-gate-execution/models-request-gate-execution.spec.md`, and `analysis/models-request-gate-execution/technical-spec.md`. Confirm the fixed bootstrap rule: `pyproject.toml` and `uv.lock` are forbidden, and execution must use existing repo dependencies only; if that is insufficient, stop the workflow with `BLOCKED` before writing tests.
2. Create tests-side support files only under `tests/unit/request_contract/models_request_gate/` (for example `conftest.py` or helper modules) to host the approved mock/interception strategy without touching `src/mlops_async/**`.
3. Add `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json` and `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json` so the `list_models` request-only gate has traceable raw flow and answer-set evidence.
4. Add `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json` and `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json` so the direct-request `get_model` branch has traceable raw flow and answer-set evidence.
5. Create `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py` and assert only semantic request behavior for the allowed `list_models` scenarios: method, path, required header subset, confirmed query key/value semantics, and body shape.
6. Create `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py` and assert only semantic request behavior for the direct identifier `get_model` branch: method, path parameter substitution, required header subset, absent/confirmed query semantics, and body shape.
7. If execution evidence reveals non-direct `get_model` request construction, additional `list_models` query fields, or any need for a new dependency / `pyproject.toml` / `uv.lock` change, stop with `BLOCKED` instead of widening scope or guessing.

## Test Plan

Test file: `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`, `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`

Test cases:
- Happy path: `list_models` bare GET and direct `get_model` by identifier both emit the expected method/path/header subset/body-shape contract.
- Invalid input: unsupported `get_model` variants, unsupported `list_models` query fields, or any mock/interception design that requires a new dependency produce `BLOCKED` setup instead of silent fallback.
- Edge case: semantic query assertions ignore query ordering while still verifying confirmed key/value meaning; absent body remains an explicit assertion.
- Regression: tests preserve the rule that host, content-length, connection headers, and transport-generated headers are not asserted.
- Backward compatibility: request-only artifacts do not modify `src/mlops_async/**`, public API exports, or migration evidence files.

## Validation Commands

```
uv run --python 3.10.0 pytest tests/unit/request_contract/models_request_gate -q
uv run --python 3.10.0 ruff check tests/unit/request_contract/models_request_gate
uv run --python 3.10.0 pyright
python .github/skills/plan-step-tracker/scripts/step_tracker.py check_impl_steps_succeeded models-request-gate-execution
```

## Risks

- 若既有 repo dependencies 無法支撐 mock/interception strategy，execution 會被正確阻擋，topic 需另開新 topic 承接 bootstrap enablement。
- `sasctl.ModelRepository.get_model` 的非 direct-request variants 若被誤納入本 topic，會讓 request-contract tests 從 confirmed branch 漂移到推測行為。
- 若測試比對 transport noise 而非 semantic request behavior，request gate 會變成脆弱快照測試。

## Rollback Plan

- Revert via git: `analysis/models-request-gate-execution/requirements.md`, `analysis/models-request-gate-execution/technical-spec.md`, `plan/models-request-gate-execution/models-request-gate-execution.plan.md`, `plan/models-request-gate-execution/models-request-gate-execution.spec.md`, `plan/models-request-gate-execution/models-request-gate-execution.step.md`, and any files created under `tests/unit/request_contract/models_request_gate/`.
- Any attempted edit to `pyproject.toml` or `uv.lock` in this topic is out of scope and should be reverted immediately with the rest of the topic-local changes.

## Open Questions

- **Non-blocking once direct branch is accepted — Human reviewer:** Should a later follow-up topic cover `sasctl.ModelRepository.get_model` name/object/refresh variants, or should they remain permanently outside the first request-only gate?
- **Non-blocking once bare GET is accepted — Human reviewer:** Which additional `list_models` query keys, if any, should be promoted from unresolved to confirmed semantics for this family?
