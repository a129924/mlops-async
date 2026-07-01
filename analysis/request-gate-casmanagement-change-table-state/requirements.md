# request-gate-casmanagement-change-table-state requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結
  `PUT /casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
  對應 `change_table_state` 的最小 request contract。
- creator phase 只建立 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/**` request-gate artifacts。
- 本 topic 不碰 `src/**`，也不在 creator / publish-in-progress 觸發 release。

## Goal

- 凍結 `change_table_state` 的單一正向 request baseline，作為後續 CAS mutation
  implementation 的 request-side baseline。
- 明確把 `change_table_state` 與既有
  `list_tables` / `get_table` surface 分開治理，避免混成同一個 CAS topic。
- 本輪只覆蓋：
  - method: `PUT`
  - path:
    `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
  - query: `value=loaded`
  - body:
    `{"outputCaslibName": "<caslib>", "outputTableName": "<tableName>"}`

## In-Scope

- `analysis/request-gate-casmanagement-change-table-state/requirements.md`
- `analysis/request-gate-casmanagement-change-table-state/technical-spec.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.plan.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.step.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.spec.md`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`

## Out-of-scope

- `src/**`
- `list_tables`
- `get_table`
- `value=unloaded`
- response schema semantics beyond minimal mock scaffold
- CAS load / unload business rules
- CAS memory lifecycle orchestration
- auth runtime wiring
- `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION` /
  `pyproject.toml` / `uv.lock` / `docs/request-shape-priority-workflow/**`
  在 creator / publish-in-progress 的任何修改

## Non-goal

- 不在本 topic 建立可運行的 CAS state-change client。
- 不在本 topic 決定 broader load/unload transition semantics。
- 不在本 topic 擴成 `value=unloaded` 的第二個正向 baseline。
- 不在本 topic 修改 transport、core CAS modules、或 public runtime API。
- 不在本 topic 提前做 VERSION bump、release tag、或 release note。

## ReadOnly

- `tests/unit/request_contract/contract_case.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py`
- `docs/api-endpoints/swagger-spec/tables-spec.yaml`
- `docs/api-endpoints/markdown-reference/README.md`
- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Written

- `analysis/request-gate-casmanagement-change-table-state/requirements.md`
- `analysis/request-gate-casmanagement-change-table-state/technical-spec.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.plan.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.step.md`
- `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.spec.md`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/__init__.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`

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

- topic name 固定為 `request-gate-casmanagement-change-table-state`
- branch 名稱固定為 `feat/andrew/request-gate-casmanagement-change-table-state`
- 唯一正向 state baseline 固定為 `value=loaded`
- `cas-shared-default` 視為固定 path segment，不在本 topic 參數化
- body 必須保留 `outputCaslibName` / `outputTableName`
- body values 必須與 path identifiers 一致
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- docs / workflow-doc / version alignment 延後到 final `release`
- `publish-in-progress` 不做 `README.md` / endpoint docs / `VERSION` /
  `docs/request-shape-priority-workflow/**` 變更

## Blocked Variants

- blank `caslib`
- non-string `caslib`
- blank `tableName`
- non-string `tableName`
- missing `value`
- `value=unloaded`
- any non-string `value`
- any `value` other than `loaded`
- extra query params
- missing body
- non-object body
- body `outputCaslibName` mismatch
- body `outputTableName` mismatch
- any drift to `list_tables`
- any drift to `get_table`

## Release-stage Alignment Intent

- `README.md`: final release 時補上
  `casManagement/caslibs/tables/state -> change_table_state` 的 request-gate status
- `docs/api-endpoints/markdown-reference/README.md`: final release 時補上 endpoint inventory / status
- `docs/request-shape-priority-workflow/**`: final release 時同步 current truth，
  說明 `change_table_state` 已落地但仍屬 queue 外 boundary topic
- `VERSION` / `pyproject.toml` / `uv.lock`: only at final `release`

## Acceptance Baseline

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/**`
  是唯一 implementation surface
- 正向 case 只存在一個：`loaded_direct_identifiers`
- fixture path 固定為
  `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
- blocked variants 明確覆蓋 invalid identifiers、state drift、body drift、query drift、
  endpoint drift
- 沒有任何 `src/**` 或 runtime CAS module 被納入修改集合
