# Codex Skill Projection Requirements

## Purpose

本文件凍結 `mlops-async` 將既有可對應 skill 規劃為 Codex-compatible skill
surface 的業務基線：

- 先凍結哪些 `.github/skills/*` 屬於同名可轉移候選
- 明確宣告 canonical source 將以 `agent-skills/skills/<name>/` 為準
- 再規劃未來如何建立 `mlops-async/skills/<name>/` 與
  `mlops-async/.codex/skills/<name>/`

本 topic 是 planning / governance work，不是 runtime implementation。

## Scope

本需求只涵蓋 `codex-skill-projection` topic 的 planning baseline，不直接執行
skill migration。

In scope candidate set:

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

Out of scope:

- `copilot-instructions-init`
- `api-client-porting-implementer`
- `api-client-porting-planner`
- `.github/agents/*`
- runtime execution semantics
- public release / version promotion

## Actors and ownership

- Planner agent：凍結 candidate set、治理邊界與 acceptance rules
- PlanCreator agent：建立 repo-visible topic plan / step / checklist
- PlanReviewer agent：針對 topic plan 做獨立 contract review
- Human reviewer：決定是否接受 future implementation 與任何 force overwrite

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Exact candidate inventory**
   - Condition: topic baseline 凍結時
   - Required outcome: candidate set 必須明確列出 32 個同名 skill
   - Acceptance signal: inventory 中不得混入 `copilot-instructions-init`、
     blockers、或 agents

2. **Canonical-source rule**
   - Condition: future migration planning
   - Required outcome: 同名 skill 的 canonical source 一律指向
     `agent-skills/skills/<name>/`
   - Acceptance signal: requirements、technical-spec、plan 三者都不得把
     `mlops-async/.github/skills/<name>/` 視為新 canonical truth

3. **Two-surface target rule**
   - Condition: candidate set 被規劃為 Codex-compatible migration
   - Required outcome: future implementation 必須同時考慮 canonical
     `skills/<name>/` 與 projected `.codex/skills/<name>/`
   - Acceptance signal: topic plan 必須明確寫出兩層 surface 與其角色差異

4. **Projection gate safety**
   - Condition: future implementation 準備 materialize `.codex/skills`
   - Required outcome: 只能使用 `platform-projection-adapter` 的 dry-run ->
     `--apply` -> optional `--force` gate
   - Acceptance signal: 不允許 ad-hoc copy / rewrite path，也不允許跳過 dry-run

5. **Agent exclusion**
   - Condition: planning 範圍確認
   - Required outcome: `.github/agents/*` 不得被當成這個 topic 的 projection
     目標
   - Acceptance signal: agent compatibility 必須獨立留在
     `custom-agent-codex-compat`

6. **Repo-visible planning package**
   - Condition: 本 topic 進入 reviewer gate 前
   - Required outcome: 必須存在 requirements、technical-spec、plan、step、
     checklist 五份工件
   - Acceptance signal: 缺一不可；少任何一份即 topic package 不完整

## Contradictions surfaced and resolved

1. `mlops-async` 目前只有 `.github/skills/` vs 未來要有 canonical `skills/`
   - Resolution: 本 topic 只規劃 canonicalization 與 projection contract，不直接把
     `.github/skills/` 升格為 canonical source

2. 想要 Codex-compatible surface vs `platform-projection-adapter` 只接受 canonical
   `skills/`
   - Resolution: 先建立 canonical `skills/` 再談 `.codex/skills/` projection；
     不反向把 adapter 用在 `.github/skills/`

3. 想要處理 skills 與 agents vs adapter 不支援 agents
   - Resolution: agents 完全分流到 `custom-agent-codex-compat`

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- candidate set 混入未在 `agent-skills/skills/` 存在的 skill
- candidate set 混入 `copilot-instructions-init`
- 直接把 `.github/skills/*` 當 projection source
- 未建立 canonical `skills/` 就規劃 `platform-projection-adapter --apply`
- 嘗試把 `.github/agents/*` 併入此 topic
- 未經人工明示就規劃 `--force`

## Non-goals

- 本 topic 不直接搬移或寫入 32 個 skill 目錄
- 本 topic 不建立 `.codex/agents/`
- 本 topic 不修改 `README.md`、`VERSION`、release timing
- 本 topic 不處理 blockers 或 custom-agent 的需求澄清

## Blockers

本需求目前無內容層 blocker，可進入 technical translation。

## Freeze status

Status: `FROZEN`
