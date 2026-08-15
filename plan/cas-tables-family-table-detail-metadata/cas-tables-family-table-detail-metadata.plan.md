---
topic: cas-tables-family-table-detail-metadata
phase: publish-in-progress
status: publish-in-progress
created: 2026-08-12
d1_verdict: non-trivial
---

# CAS Tables Table Detail Metadata follow-up plan

> **Analysis-layer routing: semantic warning — optional analysis layer is absent.**
> `analysis/cas-tables-family-table-detail-metadata/` 不存在，故
> `requirements.md` 與 `technical-spec.md` 都不存在。本 plan 不建立 analysis
> artifacts；本次由 Human 鎖定的 contract 作為唯一 planning input，並不把既有
> `plan/cas-tables-family/` 的批准狀態沿用到本 follow-up topic。

## Goal / Outcome

- 在既有 `mlops_async.clients.cas_tables` 的 `TableDetail` public response
  contract 中，新增且只新增四個日期 metadata：`created`、`last_modified`、
  `last_accessed`、`source_last_modified`。
- 以嚴格且可驗證的 wire parser 完成四個日期欄位的 mapping、required/optional
  failure semantics 與 exact allowlist；完成後既有 list/get/state 三個 endpoint
  仍維持原 request 行為與既有 transport/error/cancellation semantics。
- 本 topic 完成定義為：在 canonical `review-ready -> reviewer-in-progress`
  transition 中，由獨立 Plan-Reviewer 審查；只有後續 `approved` 才能由 Creator
  實作；實作完成後依序通過 implementation-review 與 code-review。Plan-Creator 本次只建立
  下列 planning artifacts，不實作 source 或 tests。

## Scope

- **In scope**:
  - `src/mlops_async/clients/cas_tables/value_objects.py`：擴充 frozen/slotted
    `TableDetail` 與其 detail parser 的四個日期 metadata contract。
  - `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`：新增
    response mapping、null/missing/type、unknown-field 與 metadata preservation
    測試。
  - `tests/unit/clients/cas_tables/test_cas_tables_client.py`：更新既有三個
    endpoint response fixtures 以符合新增 required metadata，並保留 request
    shape、one-request、failure propagation regression coverage。
  - 本 topic 的 plan、spec、step 三份 repo-visible planning artifacts。

- **Out of scope**:
  - 任何 request drift：不改三個既有 endpoint 的 method、path、query、body、
    auth、`Requester` 呼叫或 one-request 行為。
  - `caslibName` compatibility、`createdBy`、`lastModifiedBy`、`label`、
    `rowCount`、`columnCount` 或任何其他 response 欄位。
  - 其他 endpoint、pagination、requester/core/transport/auth/serialization
    shared policy、live Viya E2E、legacy package。
  - `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、release notes、
    release/tag、commit、push、PR 或 cleanup。
  - `analysis/cas-tables-family-table-detail-metadata/`；analysis-layer 缺失只
    在 plan 中記錄 semantic warning，不建立補充分析文件。
  - 既有 `plan/cas-tables-family/` 的任何重寫或狀態變更，以及目前 unrelated
    untracked `analysis/mlops-async-client-facade/`、
    `plan/mlops-async-client-facade/` 的任何變更。

## Locked Decisions

- 這是一個 bounded follow-up topic，不能把已完成的
  `plan/cas-tables-family/` 視為本 topic 已批准。當 topic 位於
  `reviewer-in-progress` 時，由獨立 Plan-Reviewer 產生 verdict；只有該 verdict
  為 `approved` 後，才可依 canonical `approved -> creator-in-progress`
  transition 進入 Creator implementation。`independent-plan-review` 不是額外
  status、stage 或 transition。
- `TableDetail` 的 public fields 保留既有 `name: str`、`caslib: str`、
  `state: TableState`，並只新增：
  - `created: str`
  - `last_modified: str`
  - `last_accessed: str | None`
  - `source_last_modified: str | None`
- Wire mapping 固定為：`created -> created`、`lastModified -> last_modified`、
  `lastAccessed -> last_accessed`、`sourceLastModified -> source_last_modified`。
- 只接受 wire key `caslib`；`caslibName` 不具相容性意義。既有 public
  `caslib: str` 名稱與語意維持不變。
- Parser 的 exact allowlist 固定為既有三欄加四個日期 wire keys：
  `name`、`caslib`、`state`、`created`、`lastModified`、`lastAccessed`、
  `sourceLastModified`。任何未知或額外欄位（包含 `caslibName`）仍以
  `CasTablesResponseError` 拒絕。
- `created` 與 `lastModified` 是 required：missing、explicit JSON `null`、
  非字串都必須 raise `CasTablesResponseError`。兩者只驗證為字串，不新增
  timestamp format、parse、timezone 或空白內容 validation，並保留原始字串。
- `lastAccessed` 與 `sourceLastModified` 是 optional：missing 或 explicit JSON
  `null` 都映射為 `None`；若 key 存在且非 null，必須是字串，否則以
  `CasTablesResponseError` 拒絕。字串保持原值，不做 timestamp format validation。
- `TableDetail` 繼續是 frozen/slotted dataclass；`name`、`caslib`、`state` 的
  既有 validation 與 `TableState` semantics 不放寬。
- 三個既有 endpoint（list、get、state change）共用的 detail response parsing
  必須套用上述新 response contract，但其 method/path/query/body/auth、
  `Requester` ownership、single request 與原有 error/transport/cancellation
  propagation 均不得改變。
- 本 topic 是 **non-stable / release-excluded**。不修改 README、VERSION 或
  任何 release surface；不產生 release intent。
- Creator、implementation-reviewer、code-reviewer 與 Main Agent 的角色分離：
  Creator 只在批准後依本 plan 實作；reviewer 不補做 Creator 工作；Main Agent
  負責後續 gate routing。Plan-Creator 不在本次執行 source/test 修改。

## Boundaries / Exclusions

- **Planning actor 可寫**：產生並維護本 topic 的三個 paths：
  `cas-tables-family-table-detail-metadata.plan.md`、`.spec.md`、`.step.md`。
- **Creator future write boundary**：只可修改
  `src/mlops_async/clients/cas_tables/value_objects.py`、
  `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py` 與
  `tests/unit/clients/cas_tables/test_cas_tables_client.py`，以及只用來記錄
  implementation step/status evidence 的
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.step.md`。
  Creator 不得改寫或重產
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.plan.md`
  或 `.spec.md`；任何其他 path 都是 plan drift，必須停止並重新規劃。
- **Read-only regression boundary**：
  `src/mlops_async/clients/cas_tables/client.py`、
  `src/mlops_async/clients/cas_tables/__init__.py`、
  `src/mlops_async/core/requester.py`、
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`、
  `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py`、
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`
  只用來確認 request/public boundary，不得因本 topic 改寫。
- **Preserve**：`name/caslib/state`、frozen/slotted `TableDetail`、三個既有
  endpoint 的 method/path/query/body/auth/Requester/one-request 行為，以及
  既有 semantic error、transport exception 與 `asyncio.CancelledError` 原樣
  propagation。
- **禁止接觸**：`reference/legacy_code/**`、任何 legacy package、
  `analysis/mlops-async-client-facade/`、`plan/mlops-async-client-facade/`、
  `plan/cas-tables-family/`、production code/tests outside the listed future
  write boundary、README/VERSION/release surfaces。

## Status / Allowed Transitions

- **Completion evidence**: `python-implementation-review` verdict 為 `approved`；
  `python-code-review` verdict 為 `approved`、zero findings。Focused pytest 74 passed，
  Ruff、Tach 與 Pyright 皆 passed。
- **Current publication state**: 已依 canonical `approved -> publish-in-progress`
  transition 推進；commit、push、PR 與 merge 仍為 pending，未由本 evidence 宣告完成。
- **Next routing**: Main Agent 在取得所需授權後執行 commit-and-push；後續只可依
  `publish-in-progress -> pr-open` 或 `publish-in-progress -> merged` 推進。

- **Review evidence**: 獨立 Plan-Reviewer、`python-implementation-review` 與
  `python-code-review` 均已 `approved`；code review 為 zero findings，focused pytest
  74 passed，Ruff、Tach、Pyright passed。
- **Current**: `publish-in-progress`。已完成 canonical `approved ->
  publish-in-progress` transition；commit、push、PR 與 merge 仍為 pending。
- **Execution model**: Main Agent 後續在取得所需授權後執行 commit-and-push；只可依
  `publish-in-progress -> pr-open` 或 `publish-in-progress -> merged` 推進。
- **Allowed transitions**:
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
- **Topic-specific routing**:
  - 獨立 Plan-Reviewer、implementation-reviewer 與 code-reviewer 均已完成其各自
    gate；implementation-review 為 `approved`，code-review 為 `approved`、zero
    findings，且 validation 為 74 pytest、Ruff、Tach、Pyright passed。
  - 現在僅進入 publish-in-progress；commit、push、PR、merge 與本 topic 的 non-release
    boundary 維持原 contract，不得由本次 state alignment 執行或預先完成。
  - 本 topic 不宣告 release action，因此 `merged` 為 terminal；不新增
    `merged -> released`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.plan.md` | Plan-Creator | 本 topic 的 canonical workflow、scope、contract 與 handoff |
| Topic specification | `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.spec.md` | Plan-Creator | 四個 metadata、failure semantics 與 testable acceptance contract |
| Step tracker | `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.step.md` | Plan-Creator；Creator 僅限 step/status evidence | workflow stages 與 Creator implementation completion evidence |
| Table detail value objects | `src/mlops_async/clients/cas_tables/value_objects.py` | Creator | 未來唯一 production response-model/parser change target |
| Table detail value-object tests | `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py` | Creator | mapping、allowlist、type/null 與 immutable public contract tests |
| CAS client regression tests | `tests/unit/clients/cas_tables/test_cas_tables_client.py` | Creator | 三個 endpoint 的既有 request/failure behavior regression tests |
| Existing CAS client boundary | `src/mlops_async/clients/cas_tables/client.py` | Creator / Reviewer | read-only proof that request construction and one-request behavior remain unchanged |
| Existing CAS public exports | `src/mlops_async/clients/cas_tables/__init__.py` | Reviewer | read-only proof that no new public export is required |
| List request-shape evidence | `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py` | Reviewer | read-only existing list request-shape evidence |
| Get request-shape evidence | `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py` | Reviewer | read-only existing get request-shape evidence |
| State-change request-shape evidence | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py` | Reviewer | read-only existing state-change request-shape evidence |
| Repository governance | `AGENTS.md` | Plan-Creator / Reviewer | language、active surface 與 legacy boundary evidence |
| Workflow contract | `plan/agent-handoff-workflow.md` | Plan-Creator / Reviewer | canonical lifecycle and routing evidence |
| Shared plan contract | `plan/topic-plan-contract.md` | Plan-Creator / Reviewer | required sections and contract-blocking evidence |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`pyproject.toml`、`uv.lock` 或
  `.github/copilot-instructions.md`；它們不是本 topic 的 artifact paths。
- 不建立 `analysis/cas-tables-family-table-detail-metadata/`；缺少 optional
  analysis layer 已在 plan 開頭以 semantic warning 記錄。
- 既有 `plan/cas-tables-family/`、目前 unrelated untracked facade paths 與
  其他未列出的檔案保持原狀。若後續工作漂移到未列 paths，必須停止並重新
  對齊 plan，不能視為 harmless detail。

## Implementation Steps

1. 在 `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py` 先建立
   response contract tests：完整四欄 mapping、optional missing/null -> `None`、
   required missing/null/non-string errors、optional non-null wrong-type error、
   原始字串 preservation、`caslibName`/unknown field rejection，以及
   frozen/slotted dataclass fields。
2. 在 `src/mlops_async/clients/cas_tables/value_objects.py` 將 `TableDetail`
   擴充為既有三欄加四個日期 public fields；更新 detail parser 的 exact
   allowlist、required/optional type handling 與 wire-to-public mapping，且保留
   `CasTablesResponseError` boundary、existing name/caslib/state semantics。
3. 在 `tests/unit/clients/cas_tables/test_cas_tables_client.py` 只更新既有
   response payloads/expected `TableDetail` 以提供 required `created` 與
   `lastModified`，並補足三個 endpoint 都能回傳新 detail metadata 的 regression
   assertions；不得改變 request assertions。
4. 由 Creator 在其 feature worktree 執行本 plan 的 targeted pytest、Ruff、
   Pyright、Tach 與 diff checks，確認變更沒有觸及 request/client/core、legacy
   或 release boundaries；完成後將 step tracker 對應 implementation steps
   記錄為完成並 hand off `review-ready`。

## Validation / Acceptance Checks

- **Public response contract**：`TableDetail` 仍是 frozen/slotted dataclass，
  保留 `name: str`、`caslib: str`、`state: TableState`，並精確包含四個新增
  fields；沒有 `caslibName` 或任何排除欄位。
- **Mapping**：完整合法 object 的四個 wire keys 分別正確映射至四個 public
  fields；日期字串逐字保留，不做 format/parse/normalization。
- **Optional behavior**：`lastAccessed`、`sourceLastModified` 缺少或 JSON
  `null` 均得到 `None`；存在的非-null 值必須是字串。
- **Required behavior**：`created`、`lastModified` 缺少、JSON `null` 或非字串
  均 raise `CasTablesResponseError`；字串（包含不符合任何 timestamp 格式者）
  不因格式被拒絕。
- **Exact parser boundary**：allowlist 僅為
  `name/caslib/state/created/lastModified/lastAccessed/sourceLastModified`；
  unknown key、extra key 與 `caslibName` 均 raise `CasTablesResponseError`。
- **Endpoint regression**：list/get/state 三個既有 operation 的 method、path、
  query、body、auth/Requester boundary、single request 與 return/error behavior
  維持不變；所有既有 request assertions 仍通過。
- **Failure semantics**：semantic response mismatch 仍為
  `CasTablesResponseError`；transport exceptions 與
  `asyncio.CancelledError` 仍以相同 instance 原樣傳出，不新增 retry、cleanup
  或 background work。
- **Scope validation**：只修改 Artifact Paths 中列出的 future write targets；
  `plan/cas-tables-family/`、facade untracked paths、legacy package、README、
  VERSION 與 release surfaces 均無 diff；analysis directory 仍不存在。
- **Required validation commands**（由後續 Creator 執行；本次 Plan-Creator
  不執行 production/test mutation）：

  ```powershell
  & "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pytest --override-ini addopts="" tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py -q'
  & "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 ruff check src/mlops_async/clients/cas_tables/value_objects.py tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py'
  & "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pyright'
  & "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 tach check'
  git diff --check
  ```

- Targeted test success 不代表 full coverage、release readiness、commit/push/PR
  或 merge completion；這些均不在本 topic 的 current gate。

## Reviewer Handoff

本 JSON 是 reviewer handoff contract，不是預先填寫的 approval。Plan-Reviewer
必須獨立確認本 plan 的 canonical sections、exact paths、locked response
contract、request unchanged boundary、analysis warning、non-stable intent，以及
後續 implementation-review/code-review sequence，再填寫 verdict。

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- 本 topic 沒有 post-merge release action；`merged` 後不修改 `VERSION`、
  `pyproject.toml`、`uv.lock`、`README.md`，不建立 tag、release notes 或
  GitHub Release。
- commit、push、PR、merge 與任何 post-merge cleanup 都不是本次 Plan-Creator
  執行內容，且須遵循獨立的人工作業授權與 workflow gate；不因本 topic 自動
  推導 release intent。

## Open Questions / Unresolved Items

None。Human 已鎖定 public fields、wire mapping、strict allowlist、failure
semantics、request-preservation boundary、exclusions、independent review
sequence 與 no-release intent；optional analysis layer 缺失是已記錄的 semantic
warning，不是待重新決策事項。

## In-Scope

- 補齊 `TableDetail` 的四個日期 metadata：`created`、`lastModified ->
  last_modified`、`lastAccessed -> last_accessed`、
  `sourceLastModified -> source_last_modified`。
- 只接受 wire `caslib`；optional `lastAccessed` / `sourceLastModified` 缺少或
  explicit null 映射為 `None`；required `created` / `lastModified` 的 missing、
  null、wrong type 產生 `CasTablesResponseError`。
- 維持 strict allowlist，並規劃對應 value object/parser 與既有 CAS client
  response assertions 的測試更新。

## Out-Of-Scope

- `caslibName` compatibility、`createdBy`、`lastModifiedBy`、`label`、
  `rowCount`、`columnCount` 或其他 metadata。
- 新 endpoint、live E2E、release/README/VERSION，以及既有
  `plan/cas-tables-family/` 的任何修改。

## ReadOnly

- `docs/api-endpoints/swagger-spec/upstream/casManagement-openapi.yml`。
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`。
- `tests/unit/request_contract/casmanagement_table_get_request_gate/test_get_table_request_contract.py`。
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`。
- `plan/cas-tables-family/cas-tables-family.plan.md`、
  `plan/cas-tables-family/cas-tables-family.spec.md`、
  `plan/cas-tables-family/cas-tables-family.step.md`。
- 上述 evidence 僅供 contract/reference verification，均不得改動。

## Written

- 實作階段預計寫入的 production path：
  `src/mlops_async/clients/cas_tables/value_objects.py`。
- 實作階段預計寫入的 test paths：
  `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`、
  `tests/unit/clients/cas_tables/test_cas_tables_client.py`。
- 本 follow-up planning artifacts：
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.plan.md`、
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.spec.md`、
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.step.md`。
- 本次 Plan-Creator 只更新本 plan artifact；上述 production/test paths 不在本次
  mutation 中，且不得把 unrelated paths 納入 Written scope。

## Deleted

- None；本 follow-up 不刪除任何檔案、module、public symbol 或其他 filesystem
  artifact。

## Modify

- `TableDetail` frozen/slotted dataclass 的四個日期 metadata fields。
- strict response parser 的 allowlist 與 wire-to-public mapping。
- 既有 list/get/state response assertions，以覆蓋完整 metadata、optional 與
  required response semantics。
- request behavior 不變：endpoint、method/path/query/body/auth、`Requester` 與
  one-request semantics 均維持既有 contract。

## Goal

- 補齊 CAS `TableDetail` 的四個日期 metadata，讓既有 response parser 與測試
  contract 能嚴格表達 mapping、optional nullability、required errors 與未知欄位
  rejection。

## Non-Goal

- 不改 endpoint、request、auth、`Requester`、one-request behavior、pagination、
  release/version、legacy package 或其他 metadata。

## TestCase

- Happy path：完整四個日期 metadata response 正確 mapping 並由 list/get/state
  回傳 `TableDetail`。
- Optional missing/null：`lastAccessed` 與 `sourceLastModified` 各自缺少或為
  explicit null 時映射為 `None`。
- Required missing/null/wrong type：`created` 與 `lastModified` 各自缺少、null
  或非字串時產生 `CasTablesResponseError`。
- Unknown field rejection：strict allowlist 拒絕未知欄位及 `caslibName`。
- List/get/state return mapping：三個既有 operation 的 response mapping 與
  existing return behavior 維持正確。
- Request contract unchanged：method/path/query/body/auth/Requester/one-request
  assertions 維持既有結果。

Workflow state:

- `current_step`: `publish-in-progress`
- `next_step`: `commit-and-push`
- `status`: `publish-in-progress`
