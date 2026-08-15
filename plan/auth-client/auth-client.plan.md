# AuthClient architecture correction plan

分析層 routing：`analysis/auth-client/requirements.md` 與
`analysis/auth-client/technical-spec.md` 均不存在，故此計畫以明確的人類
override（本 topic 的唯一有效 Architecture Correction contract）為準。這是
INCOMPLETE 的 non-blocking semantic warning，不授權擴張 scope；若日後補入
analysis artifacts，必須先與本 override 對齊再修訂計畫。

## Goal / Outcome

- 將 AuthClient 更正為 concrete endpoint-family client，唯一 canonical
  implementation 位於 `src/mlops_async/clients/auth_client.py`，且以 direct
  import 使用。
- 消除 `core -> package root` 反向依賴，令 Tach 的單向方向為
  `core`（token endpoint、`TokenEndpointClientProtocol`、`AccessToken`）→
  `clients`（concrete endpoint-family `AuthClient`）→ 未來 facade。
- 本 topic 完成可獨立 review 的 AuthClient correction contract；不實作未來
  facade，也不授權任何 publication 或 release。

## Scope

- **In scope**:
  - 建立 flat `clients/<endpoint_family>_client.py` layout 中的 AuthClient，
    使其只直接 await 一次 `fetch_access_token()`。`EndpointFamilyClient` 僅是
    架構分類，不建立或繼承 concrete base、Protocol 或 module。
  - 刪除舊 root AuthClient source/test，移除 package-root `AuthClient` export，
    並以 `mlops_async.clients.auth_client` 直接 import 做為唯一使用方式。
  - 更正 `core/auth.py` 的 root exception inheritance/import，保留
    `TokenEndpointClientProtocol` 與 `AccessToken` 在 core，且不遷移 transport
    或 exception hierarchy。
  - 以靜態 graph 檢查與 Tester validation 的 `uv run tach check` 驗證 Tach
    方向；不得執行 `tach sync`。
  - 在 `tests/unit/clients/test_auth_client.py` 撰寫 replacement RED tests，並
    更新 core contract test 以保護 root 未 export AuthClient 的邊界。

- **Out of scope**:
  - `src/mlops_async/mlops_async_client.py`、`MLOpsAsyncClient`、`.auth` wiring
    或任何 facade implementation。
  - grant selection、refresh、cache、lifecycle/close、transport ownership、
    exception translation、retry、timeout 或 TokenManager policy alteration。
  - transport/exceptions 模組遷移或重設其現有 hierarchy。
  - `tach sync`、release metadata、tag、push、PR、merge、release、live E2E。

## Locked Decisions

### Decisions

- **Async triggered**：AuthClient 的唯一 operation 為 async，且直接 await
  collaborator token-endpoint I/O；它的 cancellation、failure 與 ownership
  boundary 因此必須在計畫、RED tests 與 review 中明確驗證。
- AuthClient 是 concrete endpoint-family client；`EndpointFamilyClient` 僅是
  architectural classification，不是 concrete base class、Protocol 或 module。
  AuthClient 的唯一 canonical path 為
  `src/mlops_async/clients/auth_client.py`；`clients/` 採 flat
  `<endpoint_family>_client.py` layout。
- AuthClient constructor 接受 core 的 `TokenEndpointClientProtocol`；其
  `get_access_token()` 只直接 await `fetch_access_token()`，不挑 grant、不
  refresh、不 cache、不建立或管理 lifecycle、也不轉譯 exception。
- `TokenEndpointClientProtocol` 與 `AccessToken` 留在 core。實作必須移除
  `src/mlops_async/core/auth.py` 對 `mlops_async` package root 的 import 與
  root-exception inheritance；不得以新增 `mlops_async -> mlops_async.core`
  Tach permission 掩蓋 cycle。只有無法維持此單向 graph 時，才停止並請人類
  決定 shared contracts module。
- Tach target：`mlops_async.core` 的 `depends_on` 為空；新增
  `mlops_async.clients` 且它只依賴 `mlops_async.core`；`mlops_async` 不新增
  對 `mlops_async.core` 的依賴。transport 與 exceptions 的既有 hierarchy
  不在本 topic 遷移範圍。
- 未來且僅未來的 composition contract：
  `MLOpsAsyncClient(token_endpoint_client: TokenEndpointClientProtocol)` 位於
  `src/mlops_async/mlops_async_client.py`，由 `from mlops_async import
  MLOpsAsyncClient` 公開，建立 `.auth` 且不擁有或 close transport。本 topic
  絕不實作它。
### Async contradiction log

- 舊 root import、舊 root implementation，及其
  已記錄的 release-prep/evidence 與更正後的 clients direct import、future
  facade only contract 互相衝突。此衝突判為 blocking，並由本 correction
  contract 取代舊契約；未被更正後 plan 與獨立 gate 驗證前，不得作為實作、
  TDD、review 或 release 授權。
- `src/mlops_async/auth_client.py`、`src/mlops_async/__init__.py`、
  `tests/unit/core/test_auth_client.py` 與
  `tests/unit/core/test_auth_contract.py` 中的舊 root-import/old supporting
  assertions/evidence，以及 TDD/reviewer/release-prep evidence 一律為
  **superseded**。這是舊語意/evidence 的分類，不把四個 filesystem paths
  標為 ReadOnly。parent revision 不存在兩個 standalone root paths，故不宣稱
  delete；僅 `__init__.py` 的 root export 需要移除。TDD
  YAML 必須由 Tester 在 plan approval 後重寫；Plan-Creator 不可改寫該 YAML。
- 此 topic 有 stable-library-impact history，但更正後的 promotion 時間完全
  **未授權**；`0.14.0` 的既有授權完全失效。Planning actor 只改寫本 plan/spec/
  step；Creator、Tester、Reviewer 與 Main Agent 的職責不可混合。

## Boundaries / Exclusions

- `clients` 只可向下依賴 core token implementation 或 lower contracts；core
  不得向上依賴 clients、future facade 或 package root。
- package root 不 export `AuthClient`；`from mlops_async import AuthClient`
  必須不存在。保留既有 `hello()` 的行為不屬於 AuthClient public API。
- AuthClient 不 import TokenManager、Requester、grant-specific client、
  transport implementation、asyncio 或 root exceptions。
- TDD YAML、tests、source、metadata/docs 與 Tach config 均非 Planning actor
  可寫範圍；實作前須通過獨立 Plan-Reviewer。
- 如果實作需觸及未列 Artifact Paths，或 core 保留單向依賴不可能，停止並
  回報 human decision，不得自行擴張。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: Planning actor 已完成更正後 plan/spec/step，下一關為
  independent Plan-Reviewer。只有 `approved` 才可依序進入 Tester RED tests、
  Implementer、Tester validation、implementation review 與 code review；
  publish/release 均不在目前授權中。
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

Routing notes:

- 標準 Phase 4.5 獨立 review 適用；Plan-Reviewer 不得被 Planner、
  Plan-Creator 或 Implementer 自我取代。
- `approved` 只開啟後續受限實作工作，不是 release metadata、tag、push、PR、
  merge 或 release 的授權。每一 publication action 必須由更正後 plan 與
  獨立 human gate 重新授權。
- Tester validation 完成後，獨立 implementation reviewer 再獨立 code reviewer
  依序給出 verdict；此 routing 不屬於 Creator Implementation Steps。只有兩個
  review verdict 均完成後，Main Agent 才可向人類請求 publication human gate；
  請求本身不構成 tag、push、PR、merge 或 release 授權。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/auth-client/auth-client.plan.md` | Planning actor | 更正後的 workflow 與 execution contract |
| Topic specification | `plan/auth-client/auth-client.spec.md` | Planning actor | AuthClient acceptance、async 與 graph contract |
| Step tracker | `plan/auth-client/auth-client.step.md` | Planning actor | 更正後 phase/implementation completion gate |
| Superseded TDD verdict | `plan/auth-client/auth-client.tdd-test-authoring.yaml` | Tester | 只在 plan approval 後重寫；目前不可作為 gate/evidence |
| Canonical AuthClient | `src/mlops_async/clients/auth_client.py` | Implementer | 唯一 direct-import concrete endpoint-family client；不建立或繼承 EndpointFamilyClient base |
| Legacy root AuthClient | `src/mlops_async/auth_client.py` | N/A | parent revision 不存在；無 delete mutation，僅其舊 root semantic 為 superseded |
| Core auth boundary | `src/mlops_async/core/auth.py` | Implementer | 移除 root import/root-exception inheritance，保留 token contracts |
| Package root | `src/mlops_async/__init__.py` | Implementer | approval 後 update target：移除 AuthClient export，不新增 root-to-core dependency |
| Tach graph | `tach.toml` | Implementer | core no-root dependency、clients only-to-core module declarations |
| Canonical AuthClient tests | `tests/unit/clients/test_auth_client.py` | Tester then Implementer | RED/validation tests for clients direct import and delegation contract |
| Legacy root AuthClient tests | `tests/unit/core/test_auth_client.py` | N/A | parent revision 不存在；無 delete mutation，僅其舊 root-import assertions 為 superseded |
| Root non-export contract | `tests/unit/core/test_auth_contract.py` | Tester then Implementer | approval 後 update target；驗證 `mlops_async` 不存在 AuthClient，core surfaces保持 internal |

Artifact path notes:

- 本 topic 不修改 `.github/copilot-instructions.md`；下列逐一路徑的 evidence
  需區分舊語意/evidence 的 superseded 狀態與 approval 後的 filesystem
  disposition。parent revision 中兩個 standalone root source/test paths 不存在，
  因此不是 delete targets；`__init__.py` 和 supporting contract test 是 update
  targets。只有 TDD YAML（approval 前）與 release-prep
  metadata/docs 維持 ReadOnly。
- 未來 facade canonical path 與下列 evidence 是讀取/分類脈絡，並非此 topic
  的 Creator 寫入 targets。
- 任一未列路徑均為 plan-alignment problem，須先修訂並重新 review 本計畫。

### Superseded evidence inventory

| Evidence | Exact repository-relative path | Exists | Classification |
| --- | --- | --- | --- |
| Old root implementation | `src/mlops_async/auth_client.py` | No | parent revision does not contain this path; no delete mutation; any old root semantic is superseded and not a gate/authorization source |
| Old package-root export | `src/mlops_async/__init__.py` | Yes | old root-export semantic is superseded and not a gate/authorization source; Implementer update target after approval |
| Old root-import tests | `tests/unit/core/test_auth_client.py` | No | parent revision does not contain this path; no delete mutation; any old root-import assertions are superseded and not a gate/authorization source |
| Old supporting contract-test change | `tests/unit/core/test_auth_contract.py` | Yes | old supporting assertions/evidence are superseded and not a gate/authorization source; Implementer update target after approval |
| Old TDD/reviewer-phase evidence | `plan/auth-client/auth-client.tdd-test-authoring.yaml` | Yes | superseded; ReadOnly; Tester rewrites only after new plan approval; not a gate or authorization source |
| Old release-prep README text | `README.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep version file | `VERSION` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep project metadata | `pyproject.toml` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep lock metadata | `uv.lock` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep architecture text | `docs/ARCHITECTURE.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep auth-boundary text | `docs/standards/http-client-auth-boundary.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Separate reviewer verdict/evidence artifact | None under `plan/auth-client/` | No | no materialized reviewer verdict, implementation-review evidence, code-review evidence, or review-log exists; it cannot be used as a gate or authorization source |

The `0.14.0` authorization recorded by the listed release-prep artifacts is
superseded and cannot be reused.

### Filesystem dispositions

- **ReadOnly before approval**: `plan/auth-client/auth-client.tdd-test-authoring.yaml`
  is Tester-only until plan approval; `README.md`, `VERSION`, `pyproject.toml`,
  `uv.lock`, `docs/ARCHITECTURE.md`, and
  `docs/standards/http-client-auth-boundary.md` have no write target in this
  topic.
- **Written or updated after approval**: Tester rewrites
  `plan/auth-client/auth-client.tdd-test-authoring.yaml` and
  `tests/unit/clients/test_auth_client.py`; Implementer writes
  `src/mlops_async/clients/auth_client.py`, updates
  `src/mlops_async/core/auth.py`, `src/mlops_async/__init__.py`,
  `tests/unit/core/test_auth_contract.py`, and `tach.toml`.
- **Deleted after approval**: None. The parent revision does not contain
  `src/mlops_async/auth_client.py` or `tests/unit/core/test_auth_client.py`, so
  this correction has no delete mutation for those paths.

## Stable library metadata

- `README row`: 明確 no-change；更正後 topic 未獲授權變更 README。
- `VERSION bump`: 明確 no-bump；既有 `0.14.0` authorization 已失效。
- `timing`: 未授權且 deferred；只有更正後計畫完整通過所需 reviews，並取得
  獨立 human gate，才可另行規劃 promotion。
- `rationale`: AuthClient public-surface correction 不能延用舊 root API 的
  release intent，否則會將 superseded contract 誤作 stable publication。
- `release notes`: 明確 no-change；本 topic 不建立或修改 release note。

## Implementation Steps

1. Tester 在 Plan-Reviewer `approved` 後，僅重寫
   `plan/auth-client/auth-client.tdd-test-authoring.yaml` 與
   `tests/unit/clients/test_auth_client.py` 的 RED evidence；舊 YAML/test 不可
   視為完成證據。
2. Implementer 建立 canonical AuthClient，使其作為 concrete endpoint-family
   client 接受 core protocol，並只 await 一次 `fetch_access_token()`；不得
   建立或繼承 EndpointFamilyClient base、Protocol 或 module。
3. Implementer 移除 `__init__.py` 的 root AuthClient export，並更新 core
   contract test，確保 package root 不存在 AuthClient。parent revision 並無
   root AuthClient source/test，因此不執行或宣稱其 delete mutation。
4. Implementer 修改 `core/auth.py` 以消除對 package root 的 import/root
   exception inheritance，同時不遷移 transport/exceptions，也不改變
   TokenManager 的 fetch/refresh policy。
5. Implementer 修改 `tach.toml` 至 locked target，並以靜態 graph 檢查確認
   core 無 root dependency、clients 僅依賴 core、root 未新增 direct core
   permission；禁止 `tach sync`。
6. Tester 執行 plan 指定 validation，將 `uv run tach check` 的真實結果納入
   evidence；若 WDAC 阻擋，記錄 validation blocker，不能 skip 或假稱成功。

## Validation / Acceptance Checks

- `AuthClient` 可由 `mlops_async.clients.auth_client` canonical direct import，
  且是 concrete endpoint-family client；`mlops_async` 不存在 `AuthClient`。
  不存在 EndpointFamilyClient base、Protocol 或 module。
- 每次 `get_access_token()` exactly once await collaborator
  `fetch_access_token()` 並回傳同一 `AccessToken`；errors 與 cancellation
  原樣傳播。
- tests 明確證明無 refresh、grant selection、cache、lifecycle/close、context
  entry/exit、exception translation、retry 或 timeout。
- static Tach graph 符合 locked target；Tester 階段執行 `uv run tach check`。
  若 native extension 被 WDAC 阻擋，evidence 必須標為 blocker，不能以
  `tach sync`、skip 或 fake success 取代。
- `TokenEndpointClientProtocol` 與 `AccessToken` 留在 core，且
  `core/auth.py` 不再 import package root 或繼承 root exception。
- `MLOpsAsyncClient` 僅以 future-only composition note 存在，無 source、
  `.auth` wiring、transport ownership 或 close implementation。
- Plan/Spec/Step 全部將舊 root-import/release-prep assertions、TDD/reviewer
  evidence 標為 superseded；parent revision 中兩個 standalone root paths 不存在，
  所以沒有虛構的 delete mutation；只更新 root export／contract-test 邊界，且沒有
  舊 `0.14.0` 授權被重用。

## Reviewer Handoff

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

- 無已授權的 post-merge 或 release action。release metadata、tag、push、PR、
  merge、release 全部 pending，且必須由更正後 plan 及各自的獨立 human gate
  重新授權。
- 不得把舊 root-AuthClient 的 `0.14.0` release-prep evidence、approval 或
  metadata 視為本 correction 的 merge/release 依據。

## PR review correction contract

- `mlops_async.exceptions` 是既有的零依賴 shared-error leaf。Tach 中
  `mlops_async.core` 只可向下依賴此 leaf；package root 不得新增對 core 的直接依賴。
- `AuthException` 保持既有具體 class name，並繼承
  `MlopsAsyncBaseException`，讓呼叫端可捕捉既有 library base，且不轉譯 transport exception。
- `TokenEndpointFetchClientProtocol` 只含
  `fetch_access_token() -> AccessToken`。AuthClient 接受此窄 collaborator；完整的
  `TokenEndpointClientProtocol` 繼承它並保留 refresh，供 TokenManager 與 future-only
  `MLOpsAsyncClient` contract 使用。

## Open Questions / Unresolved Items

- 無阻礙 Plan-Reviewer 的 runtime contract question；Planner preflight 判定
  shared contracts module 目前不需要。
- 若實作無法在不新增 root-to-core dependency 的情況下保留單向 graph，這是
  blocking human decision：是否另建 shared contracts module。不得自行建立。
