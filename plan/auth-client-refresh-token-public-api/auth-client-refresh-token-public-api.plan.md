# AuthClient refresh-token public API Plan

本 plan 在 analysis layer strict mode 下執行：
`analysis/auth-client-refresh-token-public-api/technical-spec.md` 是 execution-facing source
of truth，`analysis/auth-client-refresh-token-public-api/requirements.md` 是 business-intent
guardrail；兩者均依已凍結的人類合約 materialize，後續角色不得另行擴張。

## Goal / Outcome

新增 `AuthClient.refresh_access_token(token: AccessToken) -> AccessToken` 與同 module 的
`AuthClientRefreshTokenError`，讓 callers 能明確 refresh 有 refresh token 的 token，並在
缺 token 時保留既有 fetch 行為。完成時既有 constructor 與 `get_access_token()` 不變，且
無 core、dependency、root-export、版本或 release 變更；`README.md` 的 public `AuthClient`
說明則與此 API 契約同步。

## Scope

- **In-Scope**:
  - `src/mlops_async/clients/auth_client.py` 的公開 async refresh method 與
    `AuthClientRefreshTokenError`。
  - `tests/unit/clients/test_auth_client.py` 的 unit coverage。
  - `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落。
  - 本 topic 的五個 planning artifacts。
- **Out-Of-Scope**:
  - core protocols、TokenManager、token endpoint、transport、依賴或 package-root export。
  - constructor/get method 的行為或簽名、快取、lifecycle、retry、timeout、concurrency。
  - VERSION、`pyproject.toml`、`uv.lock`、release、tag、commit、push、PR、merge、live E2E
    與 credentials。
- **Goal**: 以上公開 API 的最小可驗證實作。
- **Non-Goal**: 不將 AuthClient 轉變為 token lifecycle manager，亦不進行任何 release
  promotion。

## Locked Decisions

- D1 verdict: **non-trivial**；此 topic 新增 public async API、例外契約與五個可獨立驗證的
  行為分支，必須有 plan/step/spec 三件套。
- Async-planning status: **triggered — cite trigger evidence:**
  `src/mlops_async/clients/auth_client.py` 已有 `async def`/`await` collaborator I/O；本 topic
  增加另一 public async boundary，並凍結 cancellation 與 failure translation。
- Module/package placement: 新 method 與 `AuthClientRefreshTokenError` 僅在
  `mlops_async.clients.auth_client`。
- New public API: yes —
  `async def AuthClient.refresh_access_token(self, token: AccessToken) -> AccessToken`；
  `AuthClientRefreshTokenError` 可由同 module 匯入，無 root export。
- Interface changes: no；constructor 繼續接受 `TokenEndpointFetchClientProtocol`，
  `get_access_token()` 完全不變。完整 protocol 僅為 present-refresh-token branch 的 optional
  runtime capability。
- Breaking changes allowed: no；既有 fetch-only collaborator 仍可建構並可取得 token。
- New dependencies: no。
- Error handling strategy: absent refresh token 直接 fetch；present token + fetch-only
  collaborator 直接 raise `AuthClientRefreshTokenError`；full collaborator 的
  `CancelledError` 原樣 raise；其他 `Exception` 以
  `AuthClientRefreshTokenError` 並 `from exc` 鏈結。
- Typing strategy: 完全型別化；沿用既有 `AccessToken`、runtime-checkable
  `TokenEndpointFetchClientProtocol` 與 `TokenEndpointClientProtocol`，不引入 `Any`。
- 此 topic 影響 stable-library public documentation：`README.md` 會在已核准的 topic
  implementation/publish-in-progress 路徑中與 public API 同步；VERSION 不 bump。release
  不是本 topic 的 action，僅能在 merge 後由人類另行授權。

### Async boundary decision

`AuthClient` 保持 thin async delegation client。新 method 僅 await 一個已注入 collaborator；
不建立新的 sync-to-async seam 或 background task。

### Resource lifecycle decision

`AuthClient` 不建立、擁有、共享或關閉 collaborator 資源。constructor 與既有 lifecycle
surface 保持不變。

### Concurrency model

每一次 method invocation 僅 direct-await 一次選定分支；不加入 lock、fan-out、batch、stream
或 shared refresh coordination。

### Failure model

absent-token fetch 的既有例外傳播語意不改。present-token refresh branch 將一般
`Exception` 轉成 `AuthClientRefreshTokenError` 並保留 `__cause__`；缺少 full capability
同樣明確 raise，不可 fallback。

### Cancellation / timeout policy

`asyncio.CancelledError` 不包裝、不清理、不重試並立即向上傳播。此 topic 不新增 timeout
或 retry boundary。

### Validation plan

以 async pytest 驗證每個 branch 的 call count、傳入 token identity、returned token identity、
cancellation identity 與 chained cause；再透過 WSL route 跑 format、lint、typing、Tach 與
diff check。

### Handoff notes for the implementer

不得為了型別方便而把 constructor 升級成 full protocol 或修改 core。判斷 full capability
只可在 token 有 `refresh_token` 的分支中進行；exception message wording 可維持最小，但
例外型別、no-fallback、cancellation 與 chaining 不可偏離。

## Boundaries / Exclusions

- Planning actor 只建立這五個 artifacts；Plan-Reviewer 獨立審核計畫；independent
  Implementer 僅在核准後修改 `Modify` paths；independent Reviewer 獨立審核實作。
- Main Agent 擁有 worktree、topic commit、push、draft PR 與 human review 的 routing；本 plan
  不授權任何一項外部動作。
- `AuthClientRefreshTokenError` 不得移至 core 或 package root，且不得修改任何 ReadOnly path。
- 任何不在 Artifact Paths 的工作均為 plan-alignment 問題，必須停止並交回人類決定。

## Status / Allowed Transitions

- **Current**: `review-ready`。
- **Execution model**: `worktree -> Plan-Creator -> Plan-Reviewer -> independent Implementer
  -> independent Reviewer -> topic commit -> push -> draft PR -> human review`；此 topic 在
  human review 停止，沒有 merge/release 授權。
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

- `approved` 是獨立 Plan-Reviewer 對 plan 的 verdict；之後由 independent Implementer 執行，
  再由 independent Reviewer 審核 implementation，不得把任一審核角色併入 creator。
- `publish-in-progress` 前必須取得 topic commit/push/draft PR 的人類授權；`pr-open` 代表
  draft PR 已建立，human review 是下一個明確的人類邊界。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business requirements | `analysis/auth-client-refresh-token-public-api/requirements.md` | Plan-Creator | Business guardrail |
| Technical specification | `analysis/auth-client-refresh-token-public-api/technical-spec.md` | Plan-Creator | Strict-mode execution truth |
| Topic plan | `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.plan.md` | Plan-Creator | Repo-visible execution contract |
| Step tracker | `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.step.md` | Plan-Creator, then executor | Workflow and completion tracker |
| Topic spec | `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.spec.md` | Plan-Creator | Non-trivial acceptance contract |
| AuthClient implementation | `src/mlops_async/clients/auth_client.py` | independent Implementer | Public API and error translation |
| AuthClient unit tests | `tests/unit/clients/test_auth_client.py` | independent Implementer | Behavioral and regression coverage |
| Public AuthClient documentation | `README.md` | independent Implementer | Update the English and Traditional Chinese public-surface paragraphs for the refresh API without adding a package-root export |

Artifact path notes:

- **ReadOnly**: `src/mlops_async/core/auth.py`, `src/mlops_async/core/token_storage.py`,
  `src/mlops_async/__init__.py`, `src/mlops_async/clients/__init__.py`, `VERSION`,
  `pyproject.toml`, `uv.lock`, `tests/integration/**`, `config/.env.test`.
- **Written**: 僅本 topic 的五個 planning artifact paths。
- **Deleted**: None。
- **Modify**: `src/mlops_async/clients/auth_client.py` 與
  `tests/unit/clients/test_auth_client.py`、`README.md`，且只在 Plan-Reviewer `approved` 後由
  independent Implementer 修改。
- `README.md` 僅更新 English 與繁體中文 `AuthClient` public-surface 段落；`VERSION`、
  `pyproject.toml`、`uv.lock` 與 `.github/copilot-instructions.md` 均不修改。任何額外路徑需要
  重新做 plan-alignment decision。

## Stable library metadata

- `README row`: 修改 `README.md` 開頭的 English 與繁體中文 `AuthClient` public-surface
  段落（目前的 `get_access_token()`／「no refresh」敘述），改為記錄
  `refresh_access_token()`、absent-token fetch、present-token full-protocol requirement、
  `AuthClientRefreshTokenError`，並保留 direct module import 及無 package-root export 的界線。
- `VERSION bump`: none；`VERSION`、`pyproject.toml` 與 `uv.lock` 明確不在本 topic 修改範圍。
- `timing`: `publish-in-progress`；README 變更作為此 topic 已核准 implementation 的一部分，
  在未來取得人類授權的 topic publication 前完成並接受 reviewer 驗證。
- `rationale`: 新增 module-public async API 需要同步修正既有宣稱 `AuthClient` 沒有 refresh
  行為的穩定 public documentation，避免使用者取得錯誤能力界線。
- `release`: release 與 release notes 不由本 topic 執行；若 topic 日後 merge，任何 release
  仍是 merge 後、獨立的人類授權 gate。

## Implementation Steps

1. 在 `src/mlops_async/clients/auth_client.py` 定義 `AuthClientRefreshTokenError`，並在
   `AuthClient` 增加完全型別化 `refresh_access_token(self, token: AccessToken) -> AccessToken`：
   absent token 直接 await fetch；present token 要求 full protocol 並 await refresh。
2. 在相同方法的 present-token branch 保留 cancellation，將其他 collaborator `Exception`
   `raise AuthClientRefreshTokenError(...) from exc`；fetch-only collaborator 的 present-token
   branch 直接 raise error 且不呼叫 fetch。不得變更 `__init__` 或 `get_access_token()`。
3. 在 `tests/unit/clients/test_auth_client.py` 更新 test doubles，新增 async tests 驗證 absent
   fallback、full refresh、fetch-only rejection、cancellation identity、ordinary-error cause，並
   保留 constructor/get-method regression assertions。
4. 更新 `README.md` 開頭的 English 與繁體中文 `AuthClient` public-surface 段落，依
   Stable library metadata 的精確內容記錄 refresh API；不得加入 package-root export、version
   或 release 宣告。
5. 透過 Windows-to-WSL route 依 technical spec 依序執行 scoped pytest、Ruff format/check、
   Pyright、Tach 與 `git diff --check`；若 WSL/Linux Python 不可用，記錄 blocked evidence，
   不改用 Windows project-local executable。

## Validation / Acceptance Checks

- **TestCase T1**: absent refresh token 只呼叫一次 fetch，且 fetch-only collaborator 可用。
- **TestCase T2**: present refresh token 只呼叫一次 full collaborator refresh，收到同一個
  token，沒有 fetch fallback。
- **TestCase T3**: present refresh token + fetch-only collaborator raises
  `AuthClientRefreshTokenError`，且沒有 collaborator fetch call。
- **TestCase T4**: `asyncio.CancelledError` 保持同一 instance、未被包裝。
- **TestCase T5**: 一般 collaborator error 被 `AuthClientRefreshTokenError` 包裝且
  `__cause__` 是原 error。
- **TestCase T6**: constructor fetch-only compatibility 與既有 `get_access_token()` call count
  不變。
- **TestCase T7**: `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落正確
  記錄 refresh API、兩個 capability branches、error 邊界、direct module import 與無
  package-root export，且不宣稱 version 或 release 已變更。
- Plan-Reviewer 必須檢查 scope/path labels、async baseline、reviewer handoff JSON 與
  README stable-library metadata、no-core/no-root-export/no-release boundary。Independent Reviewer
  必須檢查 implementation、documentation 與每個 TestCase 的實際 evidence。

## Reviewer Handoff

Plan-Reviewer has independently approved this plan before implementation. The
review verdict applies to this topic plan only; implementation review and code
review remain pending.

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

本 topic 的 `README.md` public documentation 在 `publish-in-progress` 路徑隨已核准的
implementation 完成，但 `VERSION`、tag 與 release notes 皆維持不變。merge 不授權 release；
任何 release 都是 merge 後的獨立人類授權 gate，且此 plan 在 draft PR 後的 human review gate
停止。

## Open Questions / Unresolved Items

None。已凍結的合約足以供 Plan-Reviewer 判定，實作者不得重新決定 API、fallback、取消或
error translation 語意。

## Workflow State Contract

- `current_step`: implementation complete; independent implementation review handoff
- `next_step`: implementation-review
- `status`: COMPLETE
