Analysis-layer routing: **incomplete mode** — `analysis/http-client-auth-boundary-tach-guard/requirements.md` exists, but companion `analysis/http-client-auth-boundary-tach-guard/technical-spec.md` is absent. This plan uses the requirements baseline as the business guardrail. If a future `technical-spec.md` is created and conflicts with this plan, stop and realign instead of silently overriding it.

## Goal / Outcome

建立一個 repo-visible 的 auth-boundary tach-guard topic plan，讓後續 creator 可以在不改動
runtime behavior 的前提下，補上 `mlops_async.core` / `mlops_async.transport` 的最小
`tach.toml` guardrail，並在需要時同步修正直接描述該 guardrail current state 的文件。

Topic 完成時，repo 應同時具備：

1. 可執行的最小 `tach.toml` boundary guardrail
2. 與 guardrail 不矛盾的 current-state 文件描述

## Scope

- **In scope**:
  - `analysis/http-client-auth-boundary-tach-guard/requirements.md`
  - `plan/http-client-auth-boundary-tach-guard/http-client-auth-boundary-tach-guard.plan.md`
  - `tach.toml`
  - `README.md`
  - `.github/CONTRIBUTING.md`

- **Out of scope**:
  - `analysis/http-client-auth-boundary-tach-guard/technical-spec.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `docs/ARCHITECTURE.md`
  - `src/mlops_async/**`
  - `tests/**`
  - `VERSION`、git tag、release-note 或其他 release workflow
  - 與 auth/request boundary 無關的廣泛模組重整

## Locked Decisions

- This topic affects repository governance and documentation surfaces, but it does **not** change runtime behavior or public API semantics.
- This topic is a **minimal tach guardrail topic**; it must not expand into general module-governance cleanup.
- Analysis-first ordering is mandatory: creator must read the requirements baseline and current import graph before changing `tach.toml`.
- `tach.toml` only allows the bounded auth-boundary rule:
  - `mlops_async.core` may depend on package root `mlops_async` only for existing root-level entry contracts such as base exceptions
  - `mlops_async.transport` may depend on `mlops_async.core`
  - `mlops_async.transport` may depend on package root `mlops_async` only for existing root-level entry contracts such as base exceptions
  - `mlops_async.core` may not depend on `mlops_async.transport`
- If expressing that minimal rule requires broader package/module restatement, creator must stop and hand the conflict back for human review instead of widening scope.
- `README.md` and `.github/CONTRIBUTING.md` may be updated only to keep their current-state `tach` descriptions accurate after the guardrail change; they are not open-ended documentation refresh surfaces.
- No correction/delta artifact path is used in this topic.
- No `review-log` artifact is required because routing does not depend on reviewer-controlled multi-round rework.
- No round cap is declared for this topic.

## Boundaries / Exclusions

- Planning actor 只建立 repo-visible requirements 與 topic plan；不進入 `tach.toml` 或文件實作。
- Creator 不得修改 `src/**`、`tests/**`、`docs/standards/http-client-auth-boundary.md` 或 `docs/ARCHITECTURE.md` 來「配合」guardrail；若 guardrail 與既有 boundary baseline 衝突，必須停止。
- Reviewer 只能依據 requirements baseline、topic plan、`tach.toml` 與列出的 current-state 文件檢查 scope；不得把 review 擴張成一般模組架構審查。
- Main Agent 的 publish/merge/release 工作不屬於 creator scope；本 topic 不預設需要版本更新或 release 動作。

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic does not declare a repository release action.
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

- Analysis-layer incomplete mode applies because `technical-spec.md` is absent.
- Shared-file coordination warning: `README.md` 與 `.github/CONTRIBUTING.md` 是 shared governance / contributor surfaces；若平行 worktree 也在修改它們，必須先做人類協調再繼續。
- Creator 若在實作過程中發現最小 guardrail 會被 `tach` 語法限制逼成 broader governance change，必須回報 blocker，不得自行超出已列 artifact paths。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/http-client-auth-boundary-tach-guard/requirements.md` | Planning actor | Business baseline and scope guardrail for this topic |
| Topic plan | `plan/http-client-auth-boundary-tach-guard/http-client-auth-boundary-tach-guard.plan.md` | Planning actor | Repo-visible execution contract for creator/reviewer workflow |
| Tach guardrail config | `tach.toml` | Creator | Minimal structural guardrail for the auth/request boundary direction |
| README structural-guardrail wording | `README.md` | Creator | Current-state user-facing description of `tach` governance when wording drift would otherwise occur |
| Contributor governance wording | `.github/CONTRIBUTING.md` | Creator | Contributor-facing current-state description of `tach` governance when wording drift would otherwise occur |

Artifact path notes:

- This topic may modify `README.md`, but it does **not** modify `VERSION` or `.github/copilot-instructions.md`.
- Listed paths are an executable contract; if later work drifts outside them, stop and realign the plan before implementation continues.
- `README.md` and `.github/CONTRIBUTING.md` are conditional-sync surfaces: if current wording remains accurate after the guardrail change, keep them unchanged; if wording becomes false, they must be updated in this topic.
- No correction or delta artifact family is used here.
- No `review-log` path is listed because reviewer feedback does not control routing across mandatory multi-round rework in this topic.

## Stable library metadata

- `README row`: update only the `## Structural guardrails` wording if the new `tach.toml` guardrail would otherwise leave a false current-state description
- `VERSION bump`: no bump
- `timing`: `publish-in-progress`
- `rationale`: README may need current-state sync because the topic changes repository governance documentation, but the topic does not change shipped runtime behavior or require a release action
- release-note expectation: none

## Implementation Steps

1. Re-read `analysis/http-client-auth-boundary-tach-guard/requirements.md`, `docs/standards/http-client-auth-boundary.md`, and the current `tach.toml` plus import graph evidence so the creator confirms the desired guardrail still matches the repo state before editing anything.
2. Update `tach.toml` to represent the minimal auth-boundary dependency direction between `mlops_async.transport` and `mlops_async.core`, while preserving the existing `_repo_hooks` governance and avoiding unrelated new module rules.
3. Inspect `README.md` and `.github/CONTRIBUTING.md`; if their current-state `tach` wording becomes inaccurate because of step 2, update only the directly affected structural-governance text.
4. Keep all runtime code and tests unchanged; do not "fix" imports or refactor modules inside this topic.

## Validation / Acceptance Checks

- `analysis/http-client-auth-boundary-tach-guard/requirements.md` exists and this plan stays inside its scope, blocker, and documentation-sync rules.
- `tach.toml` expresses the minimal auth-boundary rule without broadening governance to unrelated package families.
- Manual import check confirms no direct `mlops_async.transport` imports exist under `src/mlops_async/core/**` before creator claims the minimal rule is valid.
- `uv run tach check` passes on the topic branch after the `tach.toml` change.
- If `README.md` or `.github/CONTRIBUTING.md` changed, their `tach` wording no longer claims the old coarse-grained scope.
- No files under `src/` or `tests/` are modified by this topic.

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
- No VERSION bump, tag, or release-note action is expected.

## Open Questions / Unresolved Items

- None.
