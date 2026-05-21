Analysis-layer routing: **incomplete mode** — `analysis/http-client-auth-boundary-context-doc/requirements.md` exists, but companion `analysis/http-client-auth-boundary-context-doc/technical-spec.md` is absent. This plan uses the requirements baseline as the business guardrail and the explicitly approved session baseline as supplemental context. If a future `technical-spec.md` is created and conflicts with this plan, stop and realign instead of silently overriding it.

## Goal / Outcome

建立一個 repo-visible 的 auth-boundary context-document topic plan，讓後續 creator 可以在不改動 runtime behavior 的前提下，新增可被 Agent 優先閱讀的細部文件，並補上 `docs/ARCHITECTURE.md` 的 discoverability 入口。

Topic 完成時，repo 內應有一份可被後續 Agent 穩定引用的 auth-boundary context doc，以及一個清楚的 architecture 入口。最小 guardrail 補強已明確延後至未來 topic，不屬於本 topic 交付物。

## Scope

- **In scope**:
  - `analysis/http-client-auth-boundary-context-doc/requirements.md`
  - `plan/http-client-auth-boundary-context-doc/http-client-auth-boundary-context-doc.plan.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `docs/ARCHITECTURE.md`

- **Out of scope**:
  - `analysis/http-client-auth-boundary-context-doc/technical-spec.md`
  - auth/request boundary runtime behavior changes
  - `src/mlops_async/**`
  - `tests/**`
  - `README.md`、`VERSION`、release-note 或其他 stable-library surfaces
  - `tach.toml`
  - 與 auth/request boundary 無關的廣泛模組重整

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**.
- This topic is a **docs / diagram topic**, not a Python implementation topic; it does **not** use `python-implementation-workflow`, and it does not require `*.spec.md` / `*.step.md` to proceed.
- 細部 context doc 的固定路徑為 `docs/standards/http-client-auth-boundary.md`；`docs/ARCHITECTURE.md` 只做總覽與導向，不承載全部細節。
- 細部 context doc 必須包含：依賴圖、元件職責與非職責、邊界與禁止事項、`Authorization` collision policy、refresh / expiry / lock contract、以及 future `MlopsAsyncClient` facade 定位。
- 細部 context doc 檔頭必須帶有 **Agent first-read marker**，明確說明處理 auth/request boundary 相關 topic 前先讀此文件。
- `docs/ARCHITECTURE.md` 是總覽；`docs/standards/http-client-auth-boundary.md` 是細節。細部 context doc 必須明確寫出：若其內容未來與 code 或 `tach.toml` 衝突，Agent 必須停下來交給人工決策。
- `tach.toml` 在需求 baseline 中屬於可選的同-topic guardrail 補強，但 **本 plan 明確延後該變更**；此 topic 只建立文件與 discoverability 入口，不修改 guardrail。
- 若未來另開 guardrail topic，`tach.toml` 只允許表達：
  - `mlops_async.transport` 可依賴 `mlops_async.core`
  - `mlops_async.core` 不可反向依賴 `mlops_async.transport`
- No correction/delta artifact path is used in this topic.
- No `review-log` artifact is required because routing does not depend on reviewer-controlled multi-round rework.
- No round cap is declared for this topic.

## Boundaries / Exclusions

- Planning actor 只建立 repo-visible requirements 與 topic plan；不進入文件實作或 guardrail 實作。
- Creator 後續若執行此 topic，不得把文件 topic 擴張成 auth implementation 變更、public facade 設計、或與 auth/request boundary 無關的 tach 重構。
- Reviewer 只能依據這份 plan、requirements baseline、與 exact artifact paths 審查，不得在 review 時把 scope 擴張到 `src/**`、`tests/**`、README、VERSION 或 release workflow。
- Executor scope ends at local file changes plus validation summary; `git commit / push / PR` remain Main Agent operations under the canonical repo lifecycle and are not part of creator execution for this topic.
- 若未來需要 `technical-spec.md`、step tracker、或 broader module-boundary governance，必須另行對齊，不可假設它們已被此 plan 隱含涵蓋。

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops before release and does not declare stable-library promotion.
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

- Analysis-layer incomplete mode applies for this topic because `technical-spec.md` is absent.
- Shared-file coordination warning: `docs/ARCHITECTURE.md` is a shared governance/boundary surface; if parallel worktrees touch it, treat any drift as a human-coordination issue before implementation continues.
- Executor handoff boundary for this topic: implementation stops at review-ready local changes; publish routing starts only when Main Agent later resumes canonical `publish-in-progress`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/http-client-auth-boundary-context-doc/requirements.md` | Planning actor | Business baseline and business guardrail for this topic |
| Topic plan | `plan/http-client-auth-boundary-context-doc/http-client-auth-boundary-context-doc.plan.md` | Planning actor | Repo-visible execution contract for creator/reviewer workflow |
| Auth-boundary context document | `docs/standards/http-client-auth-boundary.md` | Creator | Agent-first-read detailed context document for auth/request boundary topics |
| Architecture overview link | `docs/ARCHITECTURE.md` | Creator | Human/Agent discoverability entry point that links to the detailed auth-boundary context doc |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or `.github/copilot-instructions.md`.
- Listed paths are an executable contract; if later work drifts outside them, stop and realign the plan before implementation continues.
- This topic also does **not** modify `tach.toml`; the optional guardrail work is explicitly deferred and is not part of this artifact contract.
- No correction or delta artifact family is used here.
- No `review-log` path is listed because reviewer feedback does not control routing across mandatory multi-round rework in this topic.

## Implementation Steps

1. Create `docs/standards/http-client-auth-boundary.md` with an Agent first-read marker that explicitly tells future auth/request boundary topics to read this file before design or implementation work; the marker should be a prominent top-of-file callout rather than a buried note.
2. In `docs/standards/http-client-auth-boundary.md`, document the fixed dependency diagrams for the main request path and the auth-side collaborator path.
3. In `docs/standards/http-client-auth-boundary.md`, document the responsibilities and non-responsibilities of `HttpClient`, `Requester`, and `AuthProvider`.
4. In `docs/standards/http-client-auth-boundary.md`, document the responsibilities and non-responsibilities of `TokenManager`, `TokenStorage`, `TokenFetcher`, and the future `MlopsAsyncClient` facade/composition-root role.
5. In `docs/standards/http-client-auth-boundary.md`, record the source-of-truth rule, the requirement to stop on doc/code/guardrail mismatch, and the bounded role of `tach.toml` when present even though guardrail changes are deferred for this topic.
6. Update `docs/ARCHITECTURE.md` so the existing internal client-contract section points readers to `docs/standards/http-client-auth-boundary.md` for the detailed auth/request boundary context.

## Validation / Acceptance Checks

- `analysis/http-client-auth-boundary-context-doc/requirements.md` exists and this plan stays inside its actor, success-signal, and scope decisions.
- `docs/standards/http-client-auth-boundary.md` includes:
  - Agent first-read marker
  - main request-path dependency diagram
  - auth-side collaborator dependency diagram
  - component responsibilities and non-responsibilities
  - future `MlopsAsyncClient` facade guidance
  - source-of-truth / conflict-stop rule
- `docs/ARCHITECTURE.md` contains a clear pointer to the detailed auth-boundary context doc.
- Manual inspection: `rg -n "http-client-auth-boundary|auth-boundary" docs/ARCHITECTURE.md` confirms the new document is referenced from the internal client-contract section.
- `tach.toml` remains unchanged in this topic; any future guardrail topic must align to the documented dependency direction instead of redefining it.
- No runtime behavior files under `src/` or tests under `tests/` are modified by this topic.
- Validation commands remain bounded to this topic's scope:
  - `rg -n "http-client-auth-boundary|auth-boundary" docs/ARCHITECTURE.md docs/standards/http-client-auth-boundary.md`

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

- After merge, no repository release action is required for this topic.
- No README row, VERSION bump, or release-note action is expected.

## Open Questions / Unresolved Items

- None.
