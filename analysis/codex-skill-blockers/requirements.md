# Codex Porting Workflow Requirements

## Purpose

本文件重跑並凍結 `codex-skill-blockers` topic 的新需求 baseline：

- 將既有 `.github/skills/api-client-porting-*` 視為 bootstrap input
- 規劃其遷移為兩個 Codex-facing agent skills 與一個 Codex custom agent
- 保留核心 planner / implementer 語意，同時抽離 `mlops-async` 專屬 workflow 假設

## Scope

本需求只涵蓋下列 migration-design 目標：

- `.github/skills/api-client-porting-planner/`
- `.github/skills/api-client-porting-implementer/`
- `.agents/skills/api-client-porting-planner/SKILL.md`
- `.agents/skills/api-client-porting-implementer/SKILL.md`
- `.codex/agents/api-client-porting-workflow.agent.md`
- `analysis/codex-skill-blockers/requirements.md`
- `analysis/codex-skill-blockers/technical-spec.md`
- `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
- `plan/codex-skill-blockers/codex-skill-blockers.step.md`
- `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`

Out of scope:

- 其他 `.github/skills/*`
- 實際建立 `.agents/skills/*` 或 `.codex/agents/*`
- runtime installation / load verification
- git review / final gate execution
- `README.md`
- `VERSION`

## Actors and ownership

- Planner agent：重跑需求 baseline 與 migration decisions
- PlanCreator agent：重跑 repo-visible plan / step / checklist
- Human reviewer：檢查 migration design 是否足以進入下一個 review topic

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Exact migration target set**
   - Condition: 本 topic 重跑 analysis / plan package 時
   - Required outcome: target set 必須只包含兩個 agent skills 與一個 custom agent
   - Acceptance signal: 不可混入其他 skill migration 或 broader agent taxonomy

2. **Three-part architecture**
   - Condition: 本 topic 定義 Codex-facing artifact shape 時
   - Required outcome: 必須固定為
     - 一個 planning skill
     - 一個 implementation skill
     - 一個 orchestration agent
   - Acceptance signal: 不可退化成單一 mega-skill，也不可把 planner / implementer 語意全部塞回 workflow agent

3. **Semantic preservation**
   - Condition: `.github/skills/api-client-porting-*` 轉譯為 Codex-facing skill design 時
   - Required outcome: planner 與 implementer 的核心語意必須保留
   - Acceptance signal:
     - planner 仍保留 source evidence、request contract、risk、stop flags、handoff
     - implementer 仍保留 request-test-first、minimal implementation、response/error contract、compatibility、final decision

4. **Repo-specific contract abstraction**
   - Condition: Codex-facing skills 與 workflow agent 設計時
   - Required outcome: `mlops-async` 專屬路徑與 workflow 假設不得再作為無條件 prerequisite
   - Acceptance signal:
     - `docs/migration-map.md` 與 `docs/porting-ledger.md` 只能作為 default example 或 explicit input
     - `.github/copilot-instructions.md` 不得作為 Codex-facing runtime dependency

5. **Bootstrap authority rule**
   - Condition: 新 migration design baseline 建立時
   - Required outcome: `.github/skills/api-client-porting-*` 只能被定義為 bootstrap input
   - Acceptance signal: 不可在同一份 baseline 中同時宣稱 `.github/skills/*` 仍是 post-bootstrap authority

6. **Repo-visible planning package**
   - Condition: 本 rerun draft package 建立時
   - Required outcome: 必須存在 requirements、technical-spec、plan、step、checklist
   - Acceptance signal: 缺任何一份都表示此 topic 尚未完成 rerun baseline

## Contradictions surfaced and resolved

1. 直接保留 repo-specific skill vs 轉成較通用的 Codex-facing skill
   - Resolution: skill 核心語意保留，但 repo-specific contract 降級為 optional / default behavior

2. 只做 skills vs 要不要有 custom agent
   - Resolution: 固定採用 `2 agent skills + 1 custom agent` 分工

3. `.github/skills/*` 繼續當 authority vs 只當 bootstrap input
   - Resolution: 本 topic 中 `.github/skills/*` 只作為 bootstrap input；新的設計 authority 轉向 `.agents/skills/*` 與 `.codex/agents/*`

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- 把其他 `.github/skills/*` 一起納入 migration
- 把 planner / implementer skill 合併成單一 skill
- 把 orchestration agent 擴張成 repo-wide generic workflow registry
- 保留 `docs/migration-map.md` 或 `docs/porting-ledger.md` 為無條件硬依賴
- 在未重跑 analysis / plan package 前直接進入 review

## Non-goals

- 本 topic 不直接建立 `.agents/skills/api-client-porting-planner/SKILL.md`
- 本 topic 不直接建立 `.agents/skills/api-client-porting-implementer/SKILL.md`
- 本 topic 不直接建立 `.codex/agents/api-client-porting-workflow.agent.md`
- 本 topic 不定義其他 Codex custom agent 路徑或 registry
- 本 topic 不處理 runtime installation

## Blockers

- 舊的 blocker-only baseline 已不符合目前 intent；因此必須先重跑 analysis / plan package，
  才能進入 reviewer / fix / final gate。

## Freeze status

Status: `FROZEN`
