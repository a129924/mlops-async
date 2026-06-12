> **Analysis layer — strict mode**
>
> `analysis/codex-skill-projection/requirements.md` and
> `analysis/codex-skill-projection/technical-spec.md` exist. This plan maps to
> that technical spec as the execution-facing baseline.

## Goal / Outcome

- 將 32 個 frozen same-name skills 從 `source repo/.codex/skills/<name>/`
  對齊到 `target repo/.agents/skills/<name>/`。
- 建立 `AGENTS.md`，明確宣告 `.agents/skills/` 是此 repo 的 discoverable
  skill surface。
- 產出一份 repo-visible audit ledger，對每個 skill 明確記錄：
  - 是否已搬過去
  - 是否有 diff
  - 若有 diff，是否已以 source 覆蓋 target

## Scope

- **In scope**:
  - `AGENTS.md`
  - `analysis/codex-skill-projection/requirements.md`
  - `analysis/codex-skill-projection/technical-spec.md`
  - `plan/codex-skill-projection/codex-skill-projection.plan.md`
  - `plan/codex-skill-projection/codex-skill-projection.step.md`
  - `plan/codex-skill-projection/codex-skill-projection.checklist.md`
  - `plan/codex-skill-projection/codex-skill-projection.audit.md`
  - `plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md`
  - `.agents/skills/<name>/` for the frozen 32 names only

- **Out of scope**:
  - `copilot-instructions-init`
  - `api-client-porting-implementer`
  - `api-client-porting-planner`
  - `.github/agents/*`
  - 非同名 skill
  - `.github/skills/* -> .agents/skills/*` 直接搬移
  - `skills/*` canonicalization
  - `platform-projection-adapter`
  - `.codex/skills/*` active target maintenance
  - `README.md`
  - `VERSION`
  - release / publish routing

## Locked Decisions

- 本次唯一 source of truth 是 `source repo/.codex/skills/<name>/`。
- 本次唯一 discovery target 是 `target repo/.agents/skills/<name>/`。
- `AGENTS.md` 是本次唯一新增的 repo-level discovery contract file。
- frozen scope 只限這 32 個同名 skills：
  - `business-intent-alignment`
  - `business-to-technical-translation`
  - `git-branch-naming`
  - `git-commit-convention`
  - `git-post-merge-workflow`
  - `git-release-management`
  - `plan-creator`
  - `plan-reviewer`
  - `plan-step-tracker`
  - `python-api-signature`
  - `python-async-await`
  - `python-async-planning`
  - `python-class-design`
  - `python-code-review`
  - `python-context-management`
  - `python-data-model-methods`
  - `python-docstrings`
  - `python-error-handling`
  - `python-implementation-review`
  - `python-library-architecture`
  - `python-model-selection`
  - `python-module-boundaries`
  - `python-naming`
  - `python-package-layout`
  - `python-plan-authoring`
  - `python-plan-review`
  - `python-serialization-boundaries`
  - `python-tdd-test-authoring`
  - `python-testing-pytest`
  - `python-type-hints-strict`
  - `sense-env-scaffold`
  - `worktree-manager`
- 本次不使用 `platform-projection-adapter`。
- 本次不讀 `mlops-async/.github/skills/*` 當 source。
- 本次不建立或修改 `mlops-async/skills/*`。
- 若 target 已存在且與 source 有 diff，先記錄 audit，再用 source 整棵覆蓋
  target，並移除 target-only 檔案。
- recursive diff audit 比的是整棵 skill root，不只 `SKILL.md`。
- branch 內若已有本 topic 先前建立的 `.codex/skills/<name>` 副本，必須移除。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只維護 analysis / plan / audit / corrective-prompt contract。
- Creator / Implementer 可建立 `AGENTS.md`，並且只可在 target
  `.agents/skills/<name>/` 下建立或覆蓋 frozen 32 個 names。
- Reviewer 只審查 `AGENTS.md` discovery contract、audit ledger、target 對齊結果、
  corrective prompt、與 `step.md` 勾選一致性。
- Main Agent 不得把 scope 擴張到 blockers、agents、release files。
- 若執行中發現需要讀 `.github/skills/*`、寫 `skills/*`、或處理 `.github/agents/*`，
  必須停止並回報。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: creator implementation for the corrected repo-local
  `.agents/skills/` direction is complete; the topic is ready for reviewer
  verification of the discovery contract, audit ledger, and materialized target.
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

- This topic does not enter release / publish routing in the current round.
- Reviewer must verify repo-visible artifacts plus materialized `.agents/skills/`
  content, not `.codex/skills/`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Repo-local discovery contract | `AGENTS.md` | Implementer | Declares `.agents/skills/` as this repo's discoverable skill surface |
| Topic requirements baseline | `analysis/codex-skill-projection/requirements.md` | Planning actor | Frozen business baseline for same-name migration |
| Topic technical spec baseline | `analysis/codex-skill-projection/technical-spec.md` | Planning actor | Frozen execution-facing migration baseline |
| Topic plan | `plan/codex-skill-projection/codex-skill-projection.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/codex-skill-projection/codex-skill-projection.step.md` | Planning actor, then Implementer | Workflow-step evidence for this topic |
| Topic checklist | `plan/codex-skill-projection/codex-skill-projection.checklist.md` | Planning actor, then Reviewer | Author / review / final-gate checks |
| Topic audit ledger | `plan/codex-skill-projection/codex-skill-projection.audit.md` | Implementer | Per-skill migration and diff ledger |
| Corrective handoff prompt | `plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md` | Planning actor | Re-runnable prompt for the corrected discovery-path workflow |
| Source path model | `source repo/.codex/skills/<name>/` | External read-only source | Frozen source-of-truth for the 32 names |
| Target path model | `.agents/skills/<name>/` | Implementer | Discovery target for the 32 names only |

Artifact path notes:

- Target path model is executable only for the frozen 32 names in `Locked Decisions`.
- This topic does **not** modify `.github/agents/*`, `.github/skills/*`,
  `skills/*`, `README.md`, or `VERSION`.
- Existing `.codex/skills/*` content is not counted as completion evidence for
  this topic and must be removed if it was previously created by this topic.

## Implementation Steps

1. Freeze the 32-skill same-name scope and exclusion set in the analysis layer.
2. Rewrite the analysis, plan, step, checklist, and audit artifacts from
   `.codex/skills/` target language to `.agents/skills/` target language.
3. Create or update `AGENTS.md` to declare `.agents/skills/` as the repo-local
   discovery surface.
4. Create `plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md`.
5. Audit source existence for all 32 names under `source repo/.codex/skills/`.
6. Audit target existence for all 32 names under `.agents/skills/`.
7. Record a repo-visible per-skill ledger in
   `plan/codex-skill-projection/codex-skill-projection.audit.md`.
8. Create missing target skill roots by copying the full source skill root into
   `.agents/skills/`.
9. If any existing target differs, overwrite it from source and remove
   target-only drift.
10. Remove any topic-managed `.codex/skills/<name>` copies from the branch.
11. Re-run recursive verification and confirm all 32 target skill roots align
    with source.
12. Update `plan/codex-skill-projection/codex-skill-projection.step.md` and
    `plan/codex-skill-projection/codex-skill-projection.checklist.md` to reflect
    completed creator work.

## Validation / Acceptance Checks

- All eight topic / governance artifacts exist at their exact paths.
- `.agents/skills/` exists in `mlops-async`.
- The audit ledger contains exactly 32 rows for the frozen names only.
- Every frozen name has:
  - `source_exists = yes`
  - `post_verify = aligned`
- No artifact in this topic modifies or depends on `.github/agents/*`,
  `.github/skills/*`, blockers, or `skills/*`.
- `AGENTS.md` explicitly declares `.agents/skills/` as the discovery surface.
- The plan does not use `platform-projection-adapter`.
- Stable-library intent is explicit as absent.

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

- No repository release action is required for this topic.
- This topic stops after reviewer verification and planner final gate, before any
  optional publish routing.

## Open Questions / Unresolved Items

- None.
