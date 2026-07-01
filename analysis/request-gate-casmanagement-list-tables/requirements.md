# request-gate-casmanagement-list-tables requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結 `GET /casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables`
  對應 `list_tables` 的最小 request contract。
- creator phase 只建立 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/**` request-gate artifacts。
- 本 topic 不修改 `src/**`，也不在 creator / publish-in-progress 階段執行 release。

## Goal

- 以 strict `limit=1000&start=0` 建立 `list_tables` 的最小 request baseline。
- 與後續 `get_table`、`change_table_state` 分開治理，避免 CAS table surfaces 被誤視為同一批 endpoint。
- 凍結最小可行 request shape：
  - method: `GET`
  - path:
    `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables`
  - query:
    - `limit=1000`
    - `start=0`
  - body: `null`

## In-Scope

- `analysis/request-gate-casmanagement-list-tables/requirements.md`
- `analysis/request-gate-casmanagement-list-tables/technical-spec.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.plan.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.step.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.spec.md`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`

## Out-of-scope

- `src/**`
- `get_table`
- `change_table_state`
- bare `GET` baseline without `limit/start`
- pagination semantics beyond `limit=1000&start=0`
- filter / sort / search query support
- CAS load-state business semantics
- auth runtime wiring
- `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION` /
  `pyproject.toml` / `uv.lock` 在 creator / publish-in-progress 階段的任何變更

## Non-goal

- 不在本 topic 建立可運行的 CAS table client。
- 不在本 topic 決定可變 server routing。
- 不在本 topic 擴成 response schema、pagination behavior、或 broader CAS lifecycle。
- 不在本 topic 修改 transport 或 core auth modules。
- 不在本 topic 提前做 VERSION bump、release tag、或 release note 落地。

## ReadOnly

- `tests/unit/request_contract/contract_case.py`
- `tests/unit/request_contract/projects_request_gate/conftest.py`
- `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/swagger-spec/tables-spec.json`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Written

- `analysis/request-gate-casmanagement-list-tables/requirements.md`
- `analysis/request-gate-casmanagement-list-tables/technical-spec.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.plan.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.step.md`
- `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.spec.md`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`

## Modified

- creator phase: none outside the new topic-local artifacts and new request-contract package
- release phase only:
  - `README.md`
  - `docs/api-endpoints/markdown-reference/README.md`
  - `VERSION`
  - `pyproject.toml`
  - `uv.lock`

## Locked Decisions

- topic name 固定為 `request-gate-casmanagement-list-tables`
- strict `limit=1000&start=0` 是唯一正向 query shape
- bare `GET` 不屬於正向 baseline
- `cas-shared-default` 是固定 path segment，不在本 topic 參數化
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- docs / version alignment 延後到 final `release`
- `publish-in-progress` 不做 `README.md` / endpoint docs / `VERSION` 變更

## Blocked Variants

- blank `caslib`
- non-string `caslib`
- bare `GET` without `limit/start`
- `limit != 1000`
- `start != 0`
- extra query params
- request body present
- any drift to `get_table`
- any drift to `change_table_state`

## Release-stage Alignment Intent

- `README.md`：final release 時補上或更新
  `casManagement/dataSources/tables -> list_tables` 的 request-gate status 描述。
- `docs/api-endpoints/markdown-reference/README.md`：final release 時同步更新 endpoint inventory / status。
- `VERSION`、`pyproject.toml`、`uv.lock`：only at final `release`。

## Acceptance Baseline

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/**` 是唯一 implementation surface
- 正向 case 只存在一個：`limit_1000_start_0`
- fixture query 固定為 `limit=1000&start=0`
- blocked variants 明確覆蓋 invalid `caslib`、query drift、body drift、與 endpoint drift
- 沒有任何 `src/**` 或 CAS runtime module 納入修改集合
