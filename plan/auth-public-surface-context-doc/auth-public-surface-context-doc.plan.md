Analysis-layer routing: **incomplete mode** — `analysis/auth-public-surface-context-doc/requirements.md` 與 `analysis/auth-public-surface-context-doc/technical-spec.md` 目前皆不存在。本 plan 直接依據已凍結的人工作業結論 author，且該結論視為本 topic 的 human-approved baseline；若後續新增 analysis artifacts 且與本 plan 衝突，必須停止並先做人工作業對齊，而不是靜默覆寫。

## Goal / Outcome

撰寫一份 repo-visible 的 docs-only topic plan，凍結 `mlops-async` 的 Auth public surface Option B 文件化方向，讓後續 creator 只能在文件層更新下列內容：

- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `docs/migration-map.md`

完成後，repo 應有一份明確的 execution contract，指示 creator 只做文件更新，不碰 `src/`、`tests/`、runtime wiring、或 Python implementation artifacts，同時把下列固定模型正式寫進 docs：

- public surface 採平行 family：`PackageLevelClient`、`client.auth`、`client.projects`、`client.models`、`client.jobs`、`client.tables`
- `AuthClient` 為 public-visible 的 developer entrypoint
- OtherFamilyEndpoint 只持有 `Requester`，不直接依賴 `AuthClient`
- internal auth chain 透過獨立 `TokenEndpointClient` 觸達 `/SASLogon/oauth/token`
- `PackageLevelClient.__init__` 只做 wiring，不預先取得真實 token

## Scope

- **In scope**:
  - `plan/auth-public-surface-context-doc/auth-public-surface-context-doc.plan.md`
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `docs/migration-map.md`
  - 與上述文件直接相關的圖示、class responsibility 說明、async lifecycle 說明、public/internal boundary wording

- **Out of scope**:
  - `analysis/auth-public-surface-context-doc/**`
  - `src/mlops_async/**`
  - `tests/**`
  - `README.md`
  - `VERSION`
  - `uv.lock`
  - request-contract fixtures
  - token endpoint runtime implementation
  - `TokenEndpointClient`、`AuthClient`、`PackageLevelClient` 的 Python class 實作
  - `*.spec.md` / `*.step.md`
  - release / publish / PR routing 以外的實際 git publish 動作

## Locked Decisions

- 本 topic 是 **docs-only implement plan**，不是 Python implement plan。
- 本 topic 的 creator 執行只允許更新 `plan/...` 與 `docs/...` 路徑；不得修改 `src/`、`tests/`、或任何 runtime behavior。
- 本 topic 必須先在 **新的外部 managed worktree** 中執行，不得在 repository root worktree 直接實作。
- 本 topic 採用已凍結的人工作業結論，不再回退成以下被禁止模型：
  - `TokenManager -> AuthClient`
  - `AuthProvider` 自行掌握 token endpoint
  - OtherFamilyEndpoint 直接依賴 `AuthClient`
  - `PackageLevelClient.__init__` 預先取得真實 token
- Public surface 固定為平行 family，而不是 hidden-only auth model：
  - `PackageLevelClient`
  - `AuthClient`
  - `ProjectsClient`
  - `ModelsClient`
  - `JobsClient`
  - `TablesClient`
- OtherFamilyEndpoint 只持有 `Requester`；`Requester` 可依賴 `AuthProvider`，但不理解 `client_id`、`client_secret`、`grant_type` 等 auth config 細節。
- `AuthProvider` 只負責 token-to-header translation；不掌握 token endpoint、不直接打 token API、不兼任 token client。
- `TokenManager` 只負責 token lifecycle decision；不負責 endpoint contract，也不負責 header 組裝。
- internal token endpoint collaborator 名稱以 `TokenEndpointClient` 作為本 topic 的文件基線名稱。
- `AuthClient` 必須 public-visible，但不能成為 internal runtime core；internal auth chain 應獨立透過 `TokenEndpointClient` 運作。
- 本 topic 是 **review-ready-only with no stable-library surfaces**。
- 不需要 `review-log` artifact，因為本 topic 不依賴 reviewer 控制 routing 的 multi-round handoff。
- 不宣告 round cap。

## Boundaries / Exclusions

- Planning actor 只負責產出 repo-visible plan artifact，明確凍結 docs-only scope 與 worktree-first 執行前提。
- Creator 只負責依據本 plan 更新列名 docs，不得趁機補 `TokenEndpointClient`、`AuthClient`、`Requester`、`TokenManager` 的 runtime code。
- Reviewer 只檢查文件是否與本 plan 的固定模型一致，不得把 review scope 擴張成 Python implementation review。
- `docs/migration-map.md` 在本 topic 內只允許做 public-surface alignment 與 naming-conflict note；不得把它擴張回一般 API porting scope。
- 若執行途中發現現有 docs、migration map、或 repo 其他 authority surface 對 Auth public shape 有矛盾，必須停下交人工決策，不得自行平均解讀。
- 本 topic 不產出新 analysis artifacts；若後續需要 business/technical baseline，必須另開 topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; 此 topic 停在 merge，不包含 release。
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

- Analysis-layer incomplete mode applies because no topic-local analysis artifact exists。
- Shared-file coordination warning: `docs/ARCHITECTURE.md`、`docs/standards/http-client-auth-boundary.md`、`docs/migration-map.md` 都是 shared doc surfaces；若其他 worktrees 同步修改，必須先做人工作業協調。
- Creator execution for this topic must happen inside the managed worktree `../mlops-async.worktrees/agent-20260702-auth-public-surface-context-doc` or its direct successor if the human later explicitly relocates the topic。
- This topic does not use `python-implementation-workflow`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/auth-public-surface-context-doc/auth-public-surface-context-doc.plan.md` | Planning actor | Repo-visible execution contract for this docs-only topic |
| Architecture wording update | `docs/ARCHITECTURE.md` | Creator | 說明 public family surface、Requester ownership、lazy auth lifecycle、與 internal boundary |
| Auth boundary standard update | `docs/standards/http-client-auth-boundary.md` | Creator | 固定 Option B 的詳細 dependency diagram、component responsibilities、與禁止模型 |
| Migration-map alignment note | `docs/migration-map.md` | Creator | 對齊 `AuthClient` public surface 與 auth target naming / status note，避免與文件新基線衝突 |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`、`src/**`、或 `tests/**`。
- 上列 path 視為 executable contract；若 creator 需要新增其他文件或修改其他路徑，必須先回到 planning 重新對齊，而不是直接擴 scope。
- `plan/...` 與 `docs/...` 以外的變更一律視為 drift。

## Implementation Steps

1. 在 `docs/ARCHITECTURE.md` 補上或改寫 public/internal architecture 段落，明確記錄平行 family public surface 與 internal runtime chain 的分工。
2. 在 `docs/ARCHITECTURE.md` 補上 `PackageLevelClient.__init__` 只做 wiring、first authenticated request 才 lazy resolve token 的 async lifecycle 說明。
3. 在 `docs/standards/http-client-auth-boundary.md` 更新 dependency diagram，將 internal token endpoint collaborator 固定為 `TokenEndpointClient`，並寫出：
   - `AuthClient -> TokenEndpointClient`
   - `TokenManager -> TokenEndpointClient`
   - OtherFamilyEndpoint -> `Requester`
4. 在 `docs/standards/http-client-auth-boundary.md` 補上各 component responsibilities / non-responsibilities：
   - `AuthClient`
   - `Requester`
   - `AuthProvider`
   - `TokenManager`
   - `TokenStorage`
   - `TokenEndpointClient`
   - `HttpClient`
   - `PackageLevelClient`
5. 在 `docs/standards/http-client-auth-boundary.md` 明文列出本 topic 禁止模型，避免後續 reader 再回推成 `TokenManager -> AuthClient` 或 `AuthProvider` 持有 token endpoint。
6. 在 `docs/migration-map.md` 對 auth family row 加入必要的 wording alignment，避免現有 `AuthClient.login` 草案與新的 public-surface baseline 發生未標記衝突；若 method naming 尚未定案，文件必須明示 pending / draft，而不是假裝已定案。
7. 保持所有變更為 docs-only；完成後用 bounded grep 驗證新 wording 已落在指定文件，且沒有誤改到 runtime 路徑。

## Validation / Acceptance Checks

- `plan/auth-public-surface-context-doc/auth-public-surface-context-doc.plan.md` 存在且 canonical sections 完整。
- `docs/ARCHITECTURE.md` 明確包含：
  - 平行 family public surface
  - family client 只持有 `Requester`
  - `PackageLevelClient.__init__` 只做 wiring
  - lazy token resolve lifecycle
- `docs/standards/http-client-auth-boundary.md` 明確包含：
  - `TokenEndpointClient` 作為 internal token endpoint collaborator
  - `AuthClient` 為 public-visible entrypoint 但不是 runtime core
  - `AuthProvider` 不掌握 token endpoint
  - `TokenManager` 不依賴 `AuthClient`
  - OtherFamilyEndpoint 不直接依賴 `AuthClient`
- `docs/migration-map.md` 不再與新的 docs baseline 形成未標記衝突；若 naming 未凍結，必須顯式標記 draft / pending。
- `src/**` 與 `tests/**` 無變更。
- 驗證命令應保持 bounded：
  - `rg -n "AuthClient|TokenEndpointClient|Requester|lazy|__init__" docs/ARCHITECTURE.md docs/standards/http-client-auth-boundary.md docs/migration-map.md`
  - `git diff --name-only -- plan/auth-public-surface-context-doc docs`

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

- After merge, no repository release action is required for this topic。
- No README row, VERSION bump, release-note, or tag action is expected。

## Open Questions / Unresolved Items

- `AuthClient` 的 public method naming 是否最終採 `login`、`obtain_token`、`refresh_token`，本 topic 只要求文件與 migration-map 不可未標記衝突；若要正式凍結 method names，需另開後續 topic。