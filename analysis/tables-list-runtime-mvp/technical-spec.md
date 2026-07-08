# tables-list-runtime-mvp Technical Spec

## 狀態

- Topic: `tables-list-runtime-mvp`
- Source baseline: `analysis/tables-list-runtime-mvp/requirements.md`
- 狀態：execution-facing technical baseline

## Source Baseline Summary

本 topic 只承接單一 endpoint、單一 family、單一 authenticated business request 的 runtime MVP：

1. public access point 為 `client.tables.list_tables(project_id)`
2. auth path 只能消費既有 internal auth spine
3. 第一次 authenticated business request 才 lazy resolve token
4. `TablesClient` 只持有 `Requester`
5. request path 必須延續 fixed-path MVP baseline
6. response boundary 只做最小必要承接

## Technical Realization

| Requirement | Technical realization | Dependencies | Risk | Status |
| --- | --- | --- | --- | --- |
| R1 單一 runtime slice | 新增 `PackageLevelClient` wiring 與 `TablesClient.list_tables(project_id)` | `client.py`, `endpoints/tables.py` | 中 | feasible |
| R2 既有 auth spine 消費 | `TablesClient` 委派 `Requester`，不接觸 auth internals | `core/requester.py`, `core/auth.py` | 中 | feasible |
| R3 lazy token resolve | 以 runtime tests 驗證 first business request obtain / second request reuse | `TokenManager`, `AuthProvider`, `Requester` | 中 | feasible |
| R4 request baseline 不漂移 | runtime path 對齊既有 request-contract baseline | `projects_tables_link_request_gate` | 低到中 | feasible |
| R5 header boundary | Authorization 完全由 `Requester` 注入，family client 不組 header | existing requester boundary tests | 低 | feasible |
| R6 最小 response boundary | 在 `endpoints/tables.py` 建立最小 repo-owned response shape | no framework expansion | 中 | feasible |

## Workstream 1: Public wiring and endpoint placement

### Goal

- 以最小 public wiring 落地 `client.tables`
- 維持 family-endpoint boundary，避免把 auth lifecycle 拉進 family module

### Technical tasks

- 新增 `src/mlops_async/client.py` 作為 `PackageLevelClient` composition root
- 新增 `src/mlops_async/endpoints/__init__.py`
- 新增 `src/mlops_async/endpoints/tables.py` 承載 `TablesClient`
- `PackageLevelClient` 只做 wiring，不在 constructor 預取 token

## Workstream 2: Runtime request path

### Goal

- 讓 `TablesClient.list_tables(project_id)` 以既有 `Requester` 發出 authenticated request

### Technical tasks

- `TablesClient` 建構子只接收 `Requester`
- `list_tables(project_id)` 做最小 input validation
- path 使用 `/modelRepository/projects/{project_id}/tables`
- 保留 `Requester` 現有 auth merge / collision / content-type policy

## Workstream 3: Response boundary

### Goal

- 最小承接 `list_tables` 回傳所需欄位，不引入新的通用 response framework

### Technical tasks

- 在 `endpoints/tables.py` 定義最小 repo-owned response shape
- 只翻譯本 topic 真正需要的欄位
- JSON parse / transport / auth failures 維持既有 runtime exception boundary

## Async Baseline

- Async-planning status: triggered
- Trigger evidence:
  - business request 直接走 async `Requester`
  - 會消費 `AuthProvider` / `TokenManager` 的 async token lifecycle
  - 需要凍結 failure propagation、resource ownership、與 cancellation 行為

### Async boundary decision

- `PackageLevelClient` 的 sync `__init__` 只做 wiring
- `TablesClient.list_tables` 維持 async method
- 不做 sync facade、不做 background worker、不做 fan-out

### Resource lifecycle decision

- `PackageLevelClient` 擁有 shared `HttpClient`、`TokenEndpointClient`、`TokenManager`、`AuthProvider`、`Requester`
- `TablesClient` 不擁有額外 async resource

### Concurrency model

- 單一 direct await request
- 無 batching、無 fan-out、無 background task

### Failure model

- input validation failure 在 family boundary fast-fail
- auth / transport / HTTP / parse failures 沿既有 boundary 傳播
- 不新增 retry / backoff / grouped failure policy

### Cancellation / timeout policy

- 沿用既有 `Requester` / `HttpClient` timeout 與 cancellation 行為
- 本 topic 不新增 family-specific timeout 或 cancellation owner

### Validation plan

- runtime unit tests 驗證 first-request obtain / second-request reuse
- runtime unit tests 驗證 `TablesClient` delegation 與 header boundary
- request truth 對照既有 request-contract baseline
- `ruff`, `pyright`, bounded `pytest`

### Handoff notes for the implementer

- 不得讓 `TablesClient` 直接持有 `AuthClient`
- 不得在 `client.py` constructor 預取 token
- 若需要修改 `Requester` / `AuthProvider` public contract，先停下回到 planning gate

## Candidate Implementation Artifacts

- `src/mlops_async/client.py`
- `src/mlops_async/endpoints/__init__.py`
- `src/mlops_async/endpoints/tables.py`
- `tests/unit/endpoints/test_tables_client.py`
- `tests/unit/test_client_tables_runtime.py`
- 可能的 bounded regression 更新：`tests/unit/core/test_requester_auth_boundary.py`

## Architecture Compliance

| Dimension | Result | Notes |
| --- | --- | --- |
| Family client 只持有 `Requester` | fits | 對齊 auth boundary docs |
| `PackageLevelClient.__init__` 只做 wiring | fits | 對齊 architecture docs |
| Internal auth chain 不反向依賴 `AuthClient` | fits | `TablesClient -> AuthClient` 明確禁止 |
| Fixed-path `list_tables` baseline 延續 | fits | 對齊 request gate evidence |
| No stable-library release work in this topic | fits with prerequisites | 以 non-stable intent author |

## Risks and Rollback Triggers

1. 若 `client.py` public wiring scope 意外擴成 broader facade，topic 需回到 planning gate。
2. 若 response boundary 開始承接過多欄位，topic 會漂移成 response-model topic。
3. 若 implementation 需要讓 family client 直接碰 auth internals，代表 baseline 與 reality 衝突，必須停止對齊。
