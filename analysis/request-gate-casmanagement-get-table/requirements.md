# request-gate-casmanagement-get-table requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結
  `GET /casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}`
  對應 `get_table` 的最小 request contract。
- creator phase 只建立 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/**` request-gate artifacts。
- 本 topic 不修改 `src/**`，也不在 creator / publish-in-progress 階段執行 release。

## Goal

- 建立 `get_table` 的最小 request baseline，延續已完成的 `list_tables` 同 surface 治理。
- 與 `list_tables`、`change_table_state` 分開治理，避免 CAS table surfaces 被誤視為同一批 endpoint。
- 凍結最小可行 request shape：
  - method: `GET`
  - path:
    `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}`
  - query: `{}`
  - body: `null`

## In-Scope

- `analysis/request-gate-casmanagement-get-table/requirements.md`
- `analysis/request-gate-casmanagement-get-table/technical-spec.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.plan.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.step.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.spec.md`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.mock-responses.json`

## Out-of-scope

- `src/**`
- `list_tables`
- `change_table_state`
- response schema semantics beyond minimal mock scaffold
- pagination semantics
- filter / sort / search
- CAS load-state business semantics
- auth runtime wiring
- `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION` /
  `pyproject.toml` / `uv.lock` / `docs/request-shape-priority-workflow/**`
  在 creator / publish-in-progress 階段的任何變更

## Non-goal

- 不在本 topic 建立可運行的 CAS table detail client。
- 不在本 topic 決定可變 server routing。
- 不在本 topic 擴成 response schema、table state behavior、或 broader CAS lifecycle。
- 不在本 topic 修改 transport 或 core auth modules。
- 不在本 topic 提前做 VERSION bump、release tag、或 release note 落地。

## ReadOnly

- `tests/unit/request_contract/contract_case.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/swagger-spec/tables-spec.json`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Written

- `analysis/request-gate-casmanagement-get-table/requirements.md`
- `analysis/request-gate-casmanagement-get-table/technical-spec.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.plan.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.step.md`
- `plan/request-gate-casmanagement-get-table/request-gate-casmanagement-get-table.spec.md`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.mock-responses.json`

## Modified

- creator phase: none outside the new topic-local artifacts and new request-contract package
- release phase only:
  - `README.md`
  - `docs/api-endpoints/markdown-reference/README.md`
  - `VERSION`
  - `pyproject.toml`
  - `uv.lock`
  - `docs/request-shape-priority-workflow/README.md`
  - `docs/request-shape-priority-workflow/standards.md`
  - `docs/request-shape-priority-workflow/checklist.md`

## Locked Decisions

- topic name 固定為 `request-gate-casmanagement-get-table`
- direct `caslib + tableName` path identifiers 是唯一正向 shape
- `cas-shared-default` 是固定 path segment，不在本 topic 參數化
- query 不屬於正向 baseline
- body 不屬於正向 baseline
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- docs / version alignment 延後到 final `release`
- `publish-in-progress` 不做 `README.md` / endpoint docs / `VERSION` /
  `docs/request-shape-priority-workflow/**` 變更

## Blocked Variants

- blank `caslib`
- non-string `caslib`
- blank `tableName`
- non-string `tableName`
- any query params
- request body present
- any drift to `list_tables`
- any drift to `change_table_state`

## Release-stage Alignment Intent

- `README.md`：final release 時補上或更新
  `casManagement/dataSources/tables -> get_table` 的 request-gate status 描述。
- `docs/api-endpoints/markdown-reference/README.md`：final release 時同步更新 endpoint inventory / status。
- `docs/request-shape-priority-workflow/**`：final release 時同步補上 queue 外 current truth，
  但不得把 `get_table` 誤改成 queue 內 `[X]`。
- `VERSION`、`pyproject.toml`、`uv.lock`：only at final `release`。

## Acceptance Baseline

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/casmanagement_table_get_request_gate/**` 是唯一 implementation surface
- 正向 case 只存在一個：`direct_identifiers`
- fixture path 固定為
  `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}`
- blocked variants 明確覆蓋 invalid identifiers、query drift、body drift、與 endpoint drift
- 沒有任何 `src/**` 或 CAS runtime module 納入修改集合
