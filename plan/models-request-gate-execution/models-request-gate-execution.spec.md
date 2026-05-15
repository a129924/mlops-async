# models-request-gate-execution Specification

## Acceptance Criteria

1. 後續 execution 只能修改 `analysis/models-request-gate-execution/*.md`、`plan/models-request-gate-execution/*.md`、以及 `tests/unit/request_contract/models_request_gate/**`；`pyproject.toml` 與 `uv.lock` 在本 topic 一律不得修改。
2. execution 必須使用既有 repo dependencies；若 mock/interception 無法以既有 dependencies 實作，workflow 必須回報 `BLOCKED`，不得擴張 bootstrap scope。
3. `list_models` request-only gate 至少產出：
   - `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json`
   - `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json`
   - `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
4. `get_model` direct identifier branch request-only gate 至少產出：
   - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json`
   - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`
   - `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
5. `list_models` 與 `get_model` 的 request tests 只可驗證 semantic request behavior：HTTP method、endpoint path、required header subset、query key/value semantics、request body shape。
6. `list_models` request tests 只允許宣告 bare GET 與 repo-visible evidence 已確認的 query semantics；`filter` example 可納入，其他 query fields 若無新增證據不得自動納入。
7. `get_model` 在本 topic 只允許 direct identifier branch 進入完成宣告；name/object/refresh variants 必須維持 blocked / unresolved。
8. request tests 明確不得比對 query order、host、content-length、connection headers、transport-generated headers。
9. 本 topic 不得修改 `src/mlops_async/**`，不得做 response / error contract，不得更新 `docs/migration-map.md`，不得更新 `docs/porting-ledger.md`。
10. `tests/unit/request_contract/models_request_gate/**` 下的 artifacts 只可被解讀為 Layer 1 source-observed request-shape 證據；不得被解讀為 auth、session/refresh、real transport、或 target runtime behavior proof。

## Behavioral Scenarios

### Scenario 1: `list_models` bare GET request contract
- **Given**: bootstrap boundary 已凍結為「不得修改 `pyproject.toml` / `uv.lock`，且只能使用既有 repo dependencies」，且 execution 只在 `tests/unit/request_contract/models_request_gate/**` 內工作
- **When**: executor 為 `list_models` 建立 mock/interception strategy、request-flow fixture、mock-response answer set、與 request-contract tests
- **Then**: 測試只斷言 `GET /modelRepository/models` 的 semantic request behavior，保留 `Authorization` / `Accept` header subset expectations，不要求 query order、host、或 transport-generated headers

### Scenario 2: `get_model` direct identifier branch request contract
- **Given**: repo-visible evidence 只證實 direct identifier branch 對應 `GET /modelRepository/models/{modelId}`
- **When**: executor 為 direct `get_model` branch 建立 fixtures 與 request tests
- **Then**: 測試必須斷言 path parameter substitution 與 required header subset，但不得把 name/object/refresh variants 混入同一完成宣告

### Scenario 3: existing dependencies are insufficient or evidence is unresolved
- **Given**: execution 發現 mock/interception 需要 repo 既有 dependencies 之外的能力，或 execution 遇到未證實的 `get_model` / `list_models` request semantics
- **When**: workflow 進入 TDD authoring 或 implementation planning
- **Then**: workflow 必須明確回報 `BLOCKED`，指出缺的 existing-dependency 能力或 evidence 項，不得擴張 bootstrap scope，也不得用猜測補齊 request contract

## Error / Edge Cases

- 若 mock/interception strategy 需要新增 dependency，execution 必須停止於 bootstrap gate；不得修改 `pyproject.toml` 或 `uv.lock`。
- 若 `list_models` 出現 bare GET 與 `filter` example 之外的 query semantics 需求，必須先更新 handoff docs 再決定是否納入本 topic。
- 若 `get_model` 需要 name lookup、object refresh、或其他非 direct identifier branch，必須視為超出本 topic 的已確認 request contract。
- 若 capture evidence 包含 auth steps，可保留於 request-flow fixture，但不得因此把 auth implementation 擴進本 topic。
- 若測試開始比對 host、query order、content-length、connection headers、或 transport-generated headers，視為違反 semantic request boundary。
