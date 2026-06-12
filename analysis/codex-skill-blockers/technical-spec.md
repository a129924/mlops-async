# Codex Porting Workflow Implementation 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/codex-skill-blockers/requirements.md`

## 目標

建立一份 execution-facing implementation baseline，定義本 topic 會直接創建：

- `.agents/skills/api-client-porting-planner/SKILL.md`
- `.agents/skills/api-client-porting-planner/reference.md`
- `.agents/skills/api-client-porting-planner/examples.md`
- `.agents/skills/api-client-porting-planner/templates/family-map.md`
- `.agents/skills/api-client-porting-implementer/SKILL.md`
- `.agents/skills/api-client-porting-implementer/reference.md`
- `.agents/skills/api-client-porting-implementer/examples.md`
- `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
- `.codex/agents/api-client-porting-workflow.agent.md`

並明確說明 bootstrap input、creator implementation scope、語意保留規則與必要驗證。

## 允許檔案範圍

此階段只能建立或更新：

- `analysis/codex-skill-blockers/requirements.md`
- `analysis/codex-skill-blockers/technical-spec.md`
- `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
- `plan/codex-skill-blockers/codex-skill-blockers.step.md`
- `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`
- `.agents/skills/api-client-porting-planner/SKILL.md`
- `.agents/skills/api-client-porting-planner/reference.md`
- `.agents/skills/api-client-porting-planner/examples.md`
- `.agents/skills/api-client-porting-planner/templates/family-map.md`
- `.agents/skills/api-client-porting-implementer/SKILL.md`
- `.agents/skills/api-client-porting-implementer/reference.md`
- `.agents/skills/api-client-porting-implementer/examples.md`
- `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
- `.codex/agents/api-client-porting-workflow.agent.md`

此階段不得修改：

- 其他 `.github/skills/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Bootstrap input capture**
   - implementation plan 必須明確記錄下列 bootstrap input：
     - `.github/skills/api-client-porting-planner/SKILL.md`
     - `.github/skills/api-client-porting-planner/reference.md`
     - `.github/skills/api-client-porting-planner/examples.md`
     - `.github/skills/api-client-porting-planner/templates/family-map.md`
     - `.github/skills/api-client-porting-implementer/SKILL.md`
     - `.github/skills/api-client-porting-implementer/reference.md`
     - `.github/skills/api-client-porting-implementer/examples.md`
     - `.github/skills/api-client-porting-implementer/templates/porting-result.md`
   - implementation plan 不得把它們寫成 post-bootstrap authority

2. **Creator artifact contract**
   - implementation plan 必須精確寫出 creator 要建立的 exact file paths
   - 不可用 `.agents/skills/api-client-porting-planner/` 這種 directory-level path 取代檔案層級 contract

3. **Skill semantic preservation**
   - planner artifact set 必須保留原 planner 核心語意
   - implementer artifact set 必須保留原 implementer 核心語意
   - workflow agent 必須只承接 orchestration，不得重新吸收 planner / implementer 全部規則

4. **Repo-specific abstraction**
   - `docs/migration-map.md` 與 `docs/porting-ledger.md` 只能作為 default example 或 explicit input
   - `.github/copilot-instructions.md` 不得成為新的 Codex-facing artifact 硬依賴
   - 若 supporting files 內仍出現上述 repo-specific path，必須在新 artifact 中降級處理，而非原封不動視為強制 prerequisite

5. **Review-complete execution shape**
   - 本 rerun 先形成新的 draft plan commit，再依 workflow 完成 independent review 與 planner final gate
   - 因此 plan / step / checklist 必須清楚表達：
     - analysis / plan rerun 已完成
     - implementation scope 已凍結
     - independent review 已完成
     - planner final gate 已完成
     - topic 目前停在 human check 之前，不可直接前進 publish routing

## Architecture / compliance 自查

- **符合**
  - skill / agent 分工清楚
  - creator implementation scope 精確列到檔案
  - repo-specific contract 被降為 optional/default input

- **不符合即阻擋**
  - 只列目錄、不列 exact file paths
  - 將 `.github/skills/api-client-porting-*` 保留為 authority
  - 將 design-only baseline 偽裝成 implementation topic
  - 在 human check 前前進 publish / merge routing

## 驗證

必要檢查：

1. 五份 topic 工件存在於預期路徑
2. `requirements.md` 與 `technical-spec.md` 都明確寫出 implementation topic
3. `plan.md` 必須列出 analysis inputs：
   - `analysis/codex-skill-blockers/requirements.md`
   - `analysis/codex-skill-blockers/technical-spec.md`
4. `plan.md` 的 `Artifact Paths` 必須列出 exact file paths
5. `step.md` / `checklist.md` 都把 topic 停在 human-check-before-publish lane

建議指令：

```bash
test -f analysis/codex-skill-blockers/requirements.md
test -f analysis/codex-skill-blockers/technical-spec.md
test -f plan/codex-skill-blockers/codex-skill-blockers.plan.md
test -f plan/codex-skill-blockers/codex-skill-blockers.step.md
test -f plan/codex-skill-blockers/codex-skill-blockers.checklist.md
```

## 停止條件

若出現以下情況，必須停止並請求人工作審：

- 有人要求跳過 human check 直接進 publish / merge routing
- 後續 work 需要額外建立未列舉的 artifact path
- human 想再次把本 topic 降回 design-only topic
