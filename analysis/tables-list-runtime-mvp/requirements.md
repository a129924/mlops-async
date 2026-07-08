# tables-list-runtime-mvp Requirements

## 狀態

- Topic: `tables-list-runtime-mvp`
- Date: `2026-07-07`
- 狀態：frozen draft baseline
- 本文件為 runtime MVP 的 business / boundary baseline，不是 implementation 輸出。

## 目標

在不擴張 auth UX、也不跨到其他 endpoint family 的前提下，補上第一個真正消費既有 internal auth spine 的 business runtime slice，讓 `client.tables.list_tables(project_id)` 能透過既有 `Requester` 完成最小可用的 authenticated `list_tables` 呼叫。

## Actors

- 套件使用者：呼叫 `client.tables.list_tables(project_id)` 的 API consumer
- repo runtime author：需要在不污染 auth boundary 的前提下落地 tables family runtime
- reviewer：需要驗證 family-endpoint boundary、lazy token lifecycle、與 request-baseline 一致性

## Requirements

### R1. 單一 runtime slice

- Condition: 本 topic 啟動 implementation 時
- Required outcome: 僅實作 `modelRepository/projects -> tables-link surface / list_tables`
- Evidence signal: 只有 `client.tables.list_tables(project_id)` 被納入 public/runtime scope
- Failure meaning: 若擴到 `get_table`、`change_table_state`、或其他 family，topic scope 漂移

### R2. 既有 auth spine 消費，不重做 auth UX

- Condition: `client.tables.list_tables(project_id)` 發出 authenticated request
- Required outcome: request 必須走既有 `Requester -> AuthProvider -> TokenManager -> TokenEndpointClient -> HttpClient`
- Evidence signal: `TablesClient` 不直接持有 `AuthClient`、`TokenManager`、`TokenStorage`、或 token endpoint collaborator
- Failure meaning: 若 family client 自行接觸 auth internals，boundary 被污染

### R3. Lazy token resolve

- Condition: 第一次 authenticated business request 發生時
- Required outcome: 第一次 request 才觸發 token resolve；`PackageLevelClient.__init__` 與 `__aenter__` 不得預先拿真實 token
- Evidence signal: runtime tests 可觀察 first-request obtain / second-request reuse
- Failure meaning: 若 constructor 或 wiring phase 預取 token，違反 docs baseline

### R4. Request baseline 不漂移

- Condition: `list_tables(project_id)` 送出 request
- Required outcome: path 維持 `GET /modelRepository/projects/{project_id}/tables`，並與既有 request-contract baseline 一致
- Evidence signal: runtime topic 的 request truth 能對照 `tests/unit/request_contract/projects_tables_link_request_gate/**`
- Failure meaning: 若回頭改成 HATEOAS rediscovery、CAS tables remap、或其他 path 變體，fixed-path MVP baseline 被破壞

### R5. Tables family 不自行處理 Authorization header

- Condition: `TablesClient` 建立 outbound request
- Required outcome: `TablesClient` 不自行組 `Authorization` header，也不自行處理 token refresh
- Evidence signal: Authorization injection 僅由 `Requester` + `AuthProvider` 完成
- Failure meaning: 若 family client 直接處理 bearer header，會繞過既有 collision guard 與 auth policy

### R6. 最小 response boundary

- Condition: `list_tables` 成功回傳 JSON body
- Required outcome: 提供最小穩定 response boundary，只承接本 endpoint MVP 所需欄位
- Evidence signal: runtime tests 可在不引入通用 response model framework 的前提下驗證必要欄位
- Failure meaning: 若 topic 擴成大規模 response-model 系統化設計，scope 失控

## Non-goals

- 不實作 `get_table`
- 不實作 `change_table_state`
- 不擴張 `AuthClient` public UX / method naming
- 不一次引入 `projects` / `models` / `jobs` runtime family
- 不新增 retry / backoff / metrics / observability
- 不建立通用 tables response framework

## Read-only Evidence

- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `docs/migration-map.md`
- `plan/internal-auth-spine-mvp/**`
- `tests/unit/request_contract/projects_tables_link_request_gate/**`
- `src/mlops_async/core/**`

## Human Override

- 使用者已明示 module placement：
  - `PackageLevelClient` wiring 保留在 `src/mlops_async/client.py`
  - `TablesClient` 放在 `src/mlops_async/endpoints/tables.py`
  - 由 `client.tables` 對外暴露
- 因此「target file 目前尚不存在」在本 topic 不構成 authority blocker；它們是 planned new files。

## Freeze Status

- frozen for topic plan authoring
- 若後續 authority evidence 要求改動 `client.py` / `endpoints/tables.py` placement，必須先回到 planning / review gate，不得在 implementation 中靜默改寫
