# Codex Skill Projection Requirements

## Purpose

本文件凍結 `codex-skill-projection` topic 的修正方向：

- 主任務是把 32 個同名 agent skills 更新到 target repo
- source 一律讀取 `source repo/.codex/skills/<name>/`
- target 一律寫入 `target repo/.agents/skills/<name>/`
- repo 必須新增最小 discovery 契約，明確讓 `.agents/skills/` 成為此 repo 的
  discoverable skill surface
- repo-visible audit ledger 只回答：
  - 是否已搬過去
  - 是否有 diff
  - 若有 diff，是否已由 source 覆蓋 target

本 topic 不再以 `.codex/skills/` 為 active target，也不做 whole-library
projection 或 `mlops-async/skills/` canonicalization。

## Scope

本需求涵蓋：

- 32 個 in-scope same-name skills 的 source/target existence audit
- 32 個 in-scope same-name skills 的 recursive diff audit
- `mlops-async/.agents/skills/<name>/` 的實際 materialization
- `mlops-async/AGENTS.md` 的 repo-local discovery contract
- repo-visible planning artifacts 與 audit ledger 更新

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
- 非同名 skill
- whole-library projection
- `.github/skills/* -> .agents/skills/*` 直接搬移
- `mlops-async/skills/*` canonicalization
- `.codex/skills/*` active target maintenance
- `README.md`
- `VERSION`
- release / publish routing

## Actors and ownership

- Planner agent: 凍結 scope、source/target model、discovery contract、overwrite
  policy
- Implementer agent: 建立 `AGENTS.md`、盤點、比對、搬移、覆蓋、更新 audit ledger 與
  step evidence
- Reviewer agent: 審查 `AGENTS.md` discovery contract、target 對齊結果、audit
  ledger、與 step 勾選一致性
- Human reviewer: 決定是否接受本輪 repo-local `.agents/skills` 更新結果

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Frozen 32-skill scope**
   - Condition: topic 執行
   - Required outcome: 只處理 32 個列名 skills
   - Acceptance signal: audit ledger 不得出現非同名 skill、blockers、或 agents

2. **Source-of-truth rule**
   - Condition: source 比對或搬移
   - Required outcome: source 一律來自
     `source repo/.codex/skills/<name>/`
   - Acceptance signal: 不得改讀 `mlops-async/.github/skills/<name>/`、
     `agent-skills/skills/<name>/`、或其他 surface

3. **Repo-local discovery contract**
   - Condition: target repo 啟用本 topic skill surface
   - Required outcome: `mlops-async/AGENTS.md` 必須明確宣告 `.agents/skills/`
     是 repo-local discoverable skill root
   - Acceptance signal: reviewer 可從 `AGENTS.md` 直接辨識 `.agents/skills/`
     是此 topic 的 active target surface

4. **Target-only rule**
   - Condition: 實際搬移或覆蓋
   - Required outcome: target 一律寫到 `mlops-async/.agents/skills/<name>/`
   - Acceptance signal: 不得建立或修改 `mlops-async/skills/<name>/`

5. **Diff-audit rule**
   - Condition: source 與 target 同名 skill 都存在
   - Required outcome: 必須做整棵 skill root 的 recursive diff audit
   - Acceptance signal: diff 不得只比 `SKILL.md`

6. **Materialization rule**
   - Condition: source 存在但 target 不存在
   - Required outcome: 必須建立 target skill root
  - Acceptance signal: `target repo/.agents/skills/<name>/` 實際存在且內容與
     source 對齊

7. **Overwrite rule**
   - Condition: source 與 target 都存在且有 diff
   - Required outcome: 先記錄 diff audit，再用 source 整棵覆蓋 target
   - Acceptance signal: 覆蓋後 target 與 source recursive compare 一致，且不殘留
     target-only 檔案

8. **Legacy target cleanup**
   - Condition: branch 內已有本 topic 管理的 `.codex/skills/<name>`
   - Required outcome: 這些錯誤落點不再作為 active target surface
   - Acceptance signal: 本 topic success evidence 不再依賴 `.codex/skills/*`；
     若 branch 內已有 32 個 topic-managed `.codex/skills` 副本，應移除

9. **Repo-visible execution package**
   - Condition: topic 進入 reviewer gate 前
   - Required outcome: 必須存在 `AGENTS.md`、requirements、technical-spec、plan、
     step、checklist、audit 七份工件
   - Acceptance signal: 缺任一即 package 不完整

## Contradictions surfaced and resolved

1. `.codex/skills/` 合法但不是這次要的 discovery 路徑
   - Resolution: active target 改為 repo-local `.agents/skills/`

2. 想要更新上去的 skill vs repo 內原本沒有 `.agents/skills/` discovery 契約
   - Resolution: 以 `AGENTS.md` 補最小 repo-level discovery contract

3. 先前 branch 已有 `.codex/skills/` 材料化結果
   - Resolution: 視為錯誤落點；topic success 改以 `.agents/skills/` 為準，並清除
     topic-managed `.codex/skills` 副本

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- source skill 缺失卻仍建立 target
- target 已存在且不同，但未記錄 diff 就直接覆蓋
- target 覆蓋後仍保留 target-only drift
- 任何 `.github/agents/*` 被納入本 topic
- 任何 blocker 被納入本 topic
- 任何 `mlops-async/skills/*` 被建立或修改
- 任何 `.codex/skills/*` 被保留作 active target success evidence

## Non-goals

- 不處理非同名 skills
- 不處理 `.github/agents/*`
- 不處理 blockers
- 不建立 canonical `skills/`
- 不維護 `.codex/skills/*` 作為本 topic 的 discoverable surface
- 不修改 `README.md`、`VERSION`
- 不處理 release / publish routing

## Blockers

目前無內容層 blocker，可進入實作。

## Freeze status

Status: `FROZEN`
