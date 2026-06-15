# Codex Porting Workflow Implementation Requirements

## Purpose

本文件重跑並凍結 `codex-skill-blockers` topic 的 implementation baseline：

- 本 topic 是 **implementation topic**
- 本 topic 會直接創建兩個 Codex-facing agent skills 與一個 Codex custom agent
- 本 topic 不再停在 design-only migration baseline，而是把 creator implementation
  scope 鎖定為本次要建立的實際 artifact

## Scope

本需求只涵蓋下列 bootstrap input 與 creator implementation target：

- Bootstrap input
  - `.github/skills/api-client-porting-planner/SKILL.md`
  - `.github/skills/api-client-porting-planner/reference.md`
  - `.github/skills/api-client-porting-planner/examples.md`
  - `.github/skills/api-client-porting-planner/templates/family-map.md`
  - `.github/skills/api-client-porting-implementer/SKILL.md`
  - `.github/skills/api-client-porting-implementer/reference.md`
  - `.github/skills/api-client-porting-implementer/examples.md`
  - `.github/skills/api-client-porting-implementer/templates/porting-result.md`

- Creator implementation target
  - `.agents/skills/api-client-porting-planner/SKILL.md`
  - `.agents/skills/api-client-porting-planner/reference.md`
  - `.agents/skills/api-client-porting-planner/examples.md`
  - `.agents/skills/api-client-porting-planner/templates/family-map.md`
  - `.agents/skills/api-client-porting-implementer/SKILL.md`
  - `.agents/skills/api-client-porting-implementer/reference.md`
  - `.agents/skills/api-client-porting-implementer/examples.md`
  - `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
  - `.codex/agents/api-client-porting-workflow.toml`

- Topic package
  - `analysis/codex-skill-blockers/requirements.md`
  - `analysis/codex-skill-blockers/technical-spec.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.step.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`

Out of scope:

- 其他 `.github/skills/*`
- runtime installation / load verification
- `README.md`
- `VERSION`

## Actors and ownership

- Planner agent：重跑 implementation baseline 需求與 scope
- PlanCreator agent：重跑 repo-visible implementation plan / step / checklist
- Creator：後續依此 implementation plan 建立 skill / agent artifacts
- Human reviewer：在新 draft plan commit 後再決定是否允許進 reviewer gate

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Implementation-topic requirement**
   - Condition: 本 topic 重跑 analysis / plan package 時
   - Required outcome: 工件必須明確把本 topic 定義為 implementation topic
   - Acceptance signal: 不可再保留 design-only / blocker-only baseline 語意

2. **Exact creator artifact set**
   - Condition: creator implementation scope 凍結時
   - Required outcome: creator scope 必須精確列出 2 個 skill artifact set 與 1 個 workflow agent artifact
   - Acceptance signal: 不可只列 directory-level path，不可遺漏 required supporting files

3. **Planner semantic preservation**
   - Condition: 建立 `.agents/skills/api-client-porting-planner/*` 時
   - Required outcome: planner skill 核心語意必須保留
   - Acceptance signal: 新 artifact 必須保留
     - source evidence
     - request contract
     - risk
     - stop flags
     - handoff

4. **Implementer semantic preservation**
   - Condition: 建立 `.agents/skills/api-client-porting-implementer/*` 時
   - Required outcome: implementer skill 核心語意必須保留
   - Acceptance signal: 新 artifact 必須保留
     - request-test-first
     - minimal implementation
     - response / error contract
     - compatibility
     - final decision

5. **Workflow agent TOML contract**
   - Condition: 建立 `.codex/agents/api-client-porting-workflow.toml` 時
   - Required outcome: workflow agent 必須維持 orchestration-only，並以 Codex TOML artifact 表達
   - Acceptance signal:
     - 不得把 orchestration agent 降格改寫成 skill
     - `developer_instructions` 必須承載主要 orchestration contract
     - 不得吸收 planner / implementer 的完整內文責任

6. **Repo-specific contract downgrade**
   - Condition: 建立 Codex-facing artifacts 時
   - Required outcome: `mlops-async` repo-specific contract 必須降為 optional/default input
   - Acceptance signal:
     - `docs/migration-map.md` 不得保留為無條件硬依賴
     - `docs/porting-ledger.md` 不得保留為無條件硬依賴
     - `.github/copilot-instructions.md` 不得保留為 runtime prerequisite

7. **Bootstrap authority rule**
   - Condition: 本 topic 進行實作前
   - Required outcome: `.github/skills/api-client-porting-*` 只能被視為 bootstrap input
   - Acceptance signal: 不可在新的 implementation baseline 中同時宣稱它們仍是 post-bootstrap authority

8. **Repo-visible planning package**
   - Condition: 本 implementation topic draft package 建立時
   - Required outcome: 必須存在 requirements、technical-spec、plan、step、checklist
   - Acceptance signal: 缺任何一份都表示 implementation baseline 尚未可執行

## Contradictions surfaced and resolved

1. design-only migration design vs 直接建立 artifact
   - Resolution: 本 topic 固定轉為 implementation topic，creator 之後真的要建檔

2. 只做 skill translation vs 需要 orchestration agent
   - Resolution: 固定採用 `2 agent skills + 1 custom agent`

3. 保留 repo-specific contract vs 做成較通用 Codex-facing artifact
   - Resolution: 保留 planner / implementer 核心語意，但將 repo-specific contract 降為 optional/default input

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- 把本 topic 再退回 design-only baseline
- 只建立 `SKILL.md` 但漏掉已知需要的 supporting files
- 把 `docs/migration-map.md` 或 `docs/porting-ledger.md` 保留為無條件 prerequisite
- 在新的 draft plan commit 完成前直接進 reviewer gate

## Non-goals

- 本 topic 不建立其他 `.github/skills/*` 的 Codex-facing 版本
- 本 topic 不處理 runtime installation
- 本 topic 不處理 `README.md`
- 本 topic 不處理 `VERSION`

## Blockers

- 舊的 design-only baseline 已由新的 implementation draft baseline 取代，不再構成當前阻擋。
- 後續若要前進 publish / merge routing，前提是先完成 human check。

## Freeze status

Status: `FROZEN`
