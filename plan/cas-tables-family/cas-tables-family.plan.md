---
topic: cas-tables-family
phase: implementation-review
status: approved
created: 2026-08-11
d1_verdict: non-trivial
---

# CAS Tables Endpoint Family

> **Analysis-layer routing: semantic warning — optional analysis layer is absent.**
> Neither `analysis/cas-tables-family/requirements.md` nor
> `analysis/cas-tables-family/technical-spec.md` exists. This plan therefore
> records the human-frozen contract as the execution authority; it does not
> infer any additional public API, response behaviour, or release work.

## Goal / Outcome

提供邊界明確的 `mlops_async.clients.cas_tables` endpoint family：由呼叫端持有
`Requester`，以單一非同步請求完成 tables 的 list、detail 與 state 變更，並在
I/O 邊界前執行輸入驗證及在回應邊界執行嚴格語意解析。

## Scope

- 實作 family-local package `mlops_async.clients.cas_tables`、其指定單元測試，及
  CAS Tables-only 的 `tach.toml` 宣告。
- 公開 re-export 僅在 `mlops_async.clients.cas_tables` 提供：
  `CasTablesClient`、`CasTablesResponseError`、`TableDetail`、`TableState`、
  `TablesPage`。不修改 `mlops_async.clients` shortcut export。
- endpoint 範圍固定為：
  - `GET /casManagement/dataSources/{data_source_id}/tables`，keyword-only
    `start` 與 `limit` query；
  - `GET /casManagement/dataSources/{data_source_id}/tables/{table_name}`；
  - `PUT /casManagement/servers/{server}/caslibs/{caslib}/tables/{table_name}/state`
    搭配 `value=<TableState.value>` query 且無 JSON body。

## Locked Decisions

- `TableState` 必須是 `TableState(str, Enum)`，且唯一值為
  `LOADED = "loaded"`。
- `change_table_state(..., state: str) -> TableDetail` 的 public `state` 型別固定
  為 `str`；在任何 requester I/O 前驗證非空字串並以 `TableState(state)` 轉換。
  無效或未知值拋出 `ValueError`，不擴大 public signature 為 `TableState`。
- `list_tables(...) -> TablesPage`；`get_table(...) -> TableDetail`；
  `change_table_state(...) -> TableDetail`。`TablesPage.items` 的型別固定為
  `tuple[TableDetail, ...]`。
- `TableDetail` 為 frozen、slotted dataclass，且 `name: str`、`caslib: str`、
  `state: TableState` 均採嚴格語意解析；缺少、null、型別錯誤、未知 state 或額外
  table-detail 欄位一律為 `CasTablesResponseError`。
- `data_source_id`、`server`、`caslib`、`table_name` 必須為非空字串；`start` 為
  非 bool 的整數且 `>= 0`；`limit` 為非 bool 的整數且 `> 0`。所有這些輸入錯誤
  必須在 I/O 前以 `ValueError` 結束。動態路徑 segment 必須 percent-encode。
- JSON/envelope/item 語意不符為 `CasTablesResponseError`；transport exception 與
  `asyncio.CancelledError` 必須保留原 instance 傳遞。
- 全部 public operations 是單一 `async def` / 一次 await requester 的邊界。
  不新增 session ownership、`close()`、context manager、timeout/retry、polling、
  `gather`、background task 或 CAS memory orchestration。
- request-contract gates 只可作 request-shape 證據；不得將 gate 的預設 data source
  或 state JSON body 推升為 runtime contract。
- 此 topic 為 non-stable、no-release：`README.md`、`VERSION`、release notes、
  `pyproject.toml`、`uv.lock` 均不在變更範圍。

## Boundaries / Exclusions

- 不新增其他 CAS endpoints、header/query/filter/sort 行為、response tolerance 或
  未明示的 pagination 行為。
- 不修改 `Requester`、core、transport、其他 client family、
  `src/mlops_async/clients/__init__.py`、request-contract gates 或 analysis artifacts。
- 不執行 live Viya E2E、worktree lifecycle、commit、push、PR、merge、tag、release 或
  cleanup。
- 若 frozen contract 外的 public API、解析規則或 release 行為需要改變，停止並交由
  human-check，而非自行擴張範圍。

## Status / Allowed Transitions

- **Current:** `approved`。獨立 Plan-Reviewer 已完成審查，並回傳 approved 的
  machine-consumable verdict；沒有 blocking issues，且沒有待 ADDRESS、DISCUSS 或 SKIP
  的 Copilot feedback。
- **Allowed transitions:**
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal
- **Routing / stop condition:** 下一個必經 gate 是獨立 implementation review。
  This approved plan does not authorize publish, PR, merge, or release.

## Artifact Paths

| Artifact | Path | Owner | Responsibility |
| --- | --- | --- | --- |
| Topic plan | `plan/cas-tables-family/cas-tables-family.plan.md` | Planning actor | Contract and workflow routing |
| Step tracker | `plan/cas-tables-family/cas-tables-family.step.md` | Planning actor / creator | Implementation completion evidence |
| Topic specification | `plan/cas-tables-family/cas-tables-family.spec.md` | Planning actor | Acceptance contract |
| Governance evidence | `AGENTS.md` | Planning actor / reviewer | Repo governance and language boundary |
| Workflow evidence | `plan/topic-plan-contract.md` | Planning actor / reviewer | Required plan sections and blocking semantics |
| Workflow evidence | `plan/agent-handoff-workflow.md` | Planning actor / reviewer | Canonical transitions and handoff routing |
| Core evidence | `src/mlops_async/core/requester.py` | Creator / reviewer | Caller-owned requester contract |
| Core evidence | `src/mlops_async/core/http_request.py` | Creator / reviewer | Dynamic path construction contract |
| Core evidence | `src/mlops_async/core/types.py` | Creator / reviewer | HTTP and JSON types |
| Request-shape evidence | `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py` | Creator / reviewer | Non-authoritative list shape evidence |
| Request-shape evidence | `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py` | Creator / reviewer | Non-authoritative detail shape evidence |
| Request-shape evidence | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py` | Creator / reviewer | Non-authoritative state shape evidence |
| Source | `src/mlops_async/clients/cas_tables/__init__.py` | Creator | Family-local public re-exports |
| Source | `src/mlops_async/clients/cas_tables/client.py` | Creator | Client, pre-I/O validation and request construction |
| Source | `src/mlops_async/clients/cas_tables/value_objects.py` | Creator | Value objects, parsers and family response error |
| Test | `tests/unit/clients/cas_tables/test_cas_tables_client.py` | Creator | Client request, validation and propagation tests |
| Test | `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py` | Creator | Value-object and parser tests |
| Module declaration | `tach.toml` | Creator | CAS Tables module dependency declarations |

## Implementation Steps

1. 將 value-object CAS unit-test module 置於 collision-free unique canonical path
   `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`，並維持
   `TableState`、frozen/slotted `TableDetail`、
   `TablesPage.items: tuple[TableDetail, ...]` 與 strict detail/list parser 的 acceptance tests。
2. 在 `src/mlops_async/clients/cas_tables/value_objects.py` 實作
   `CasTablesResponseError`、`TableState`、`TableDetail`、`TablesPage` 與 strict
   semantic parsers。
3. 在 `src/mlops_async/clients/cas_tables/client.py` 與 `__init__.py` 實作 caller-owned
   `CasTablesClient`、frozen public signatures、pre-I/O validation、three fixed endpoint
   paths、query/no-body PUT、正確回傳型別與 family-local re-exports。
4. 將 client CAS unit-test module 置於 collision-free unique canonical path
   `tests/unit/clients/cas_tables/test_cas_tables_client.py`，並維持 list/get/state
   request shape、return types、I/O 前驗證、JSON/semantic failure、
   transport/cancellation identity、percent encoding 及不含 lifecycle helpers 的 public surface。
5. 在 `tach.toml` 宣告 `mlops_async.clients.cas_tables`、`.client`、`.value_objects`
   與實際 imports 相符的 bounded dependencies。
6. 透過 Windows-to-WSL routing 執行指定 pytest、Ruff、Pyright、Tach，另執行
   `git diff --check`；僅在全部實作與驗證證據成立後更新 completion routing 為
   `review-ready`。

## Validation / Acceptance Checks

- `TableState` 是 `str, Enum` 且只有 `LOADED = "loaded"`；`TableDetail` 與
  `TablesPage` 都是 frozen/slotted，`TablesPage.items` 是 `tuple[TableDetail, ...]`。
- `list_tables` 回傳 `TablesPage`；`get_table` 與 `change_table_state` 回傳
  `TableDetail`。所有動態 identifiers 都是 percent-encoded path segments。
- `change_table_state(..., state: str)` 在 requester I/O 前轉為 `TableState`，並送出
  `PUT`、`value=loaded` query、`json_body is None`。
- identifier/page/state 的無效輸入在 I/O 前為 `ValueError`；response semantic mismatch
  為 `CasTablesResponseError`；transport exception 和 cancellation instance 原樣傳遞。
- 驗證命令（由實作者在 WSL 執行；本 planning alignment 不執行 tests）：

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pytest --override-ini addopts="" tests/unit/clients/cas_tables/test_cas_tables_client.py tests/unit/clients/cas_tables/test_cas_tables_value_objects.py -q'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 ruff check src/mlops_async/clients/cas_tables/__init__.py src/mlops_async/clients/cas_tables/client.py src/mlops_async/clients/cas_tables/value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py tests/unit/clients/cas_tables/test_cas_tables_value_objects.py'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pyright'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 tach check'
git diff --check
```

- Targeted validation does not prove full coverage, release readiness, or final Git publication gates.

- 2026-08-11 validation evidence rework：已確認可執行的 main-worktree Linux
  `.venv/bin/python` 在 feature `PYTHONPATH` 下 import 的是
  `agent-20260811-cas-tables-family/src/mlops_async/__init__.py`，且 feature
  `GIT_DIR` 與 `GIT_WORK_TREE` 均已驗證。approved paired target command 將兩個
  renamed test files 與 `--override-ini addopts=""` 一併執行，結果為
  `49 passed in 7.05s`。它在 `--no-sync` 下使用既有 main-worktree 環境；uv 因該
  環境為 Python 3.10.20、命令要求 Python 3.10.0 而輸出
  incompatible-environment warning。沒有下載、安裝或修改 dependency。保留的較早
  scoped Ruff、Pyright、Tach evidence 均為 exit 0。以 feature `GIT_DIR` 與
  `GIT_WORK_TREE` 執行的 retained latest default full pytest evidence 精確為
  `603 passed, 10 skipped`、95.54% coverage。八個 untracked topic paths 均以
  `git diff --no-index --check -- /dev/null <path>` 逐檔檢查且未輸出 whitespace
  diagnostic；exit 1 是預期的 no-index content-difference status。這是
  untracked-content evidence，普通 `git diff --check` 不會檢查 untracked files。
  這些結果不證明 full coverage、release readiness 或 final Git publication gates。

## Reviewer Handoff

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

此 topic 為 non-stable、no-release；沒有 post-merge release action。若日後改變此決定，
必須由新的 human decision 建立含 stable-library metadata 的計畫，不能由本 topic 推定
`merged` -> `released`。

## Open Questions / Unresolved Items

- 無。Human-frozen contract 已鎖定本次 public contract、endpoint scope、async boundary 與
  no-release intent。
- 分析層兩份 optional artifact 缺失已在文件開頭明示；它們不授權擴張此 locked contract。
