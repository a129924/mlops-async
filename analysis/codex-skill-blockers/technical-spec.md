# Codex Porting Workflow 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/codex-skill-blockers/requirements.md`

## 目標

建立一份 execution-facing migration-design baseline，定義如何把：

- `.github/skills/api-client-porting-planner/`
- `.github/skills/api-client-porting-implementer/`

轉譯為：

- `.agents/skills/api-client-porting-planner/`
- `.agents/skills/api-client-porting-implementer/`
- `.codex/agents/api-client-porting-workflow/`

並明確說明哪些語意必須保留、哪些 repo-specific contract 必須抽離。

## 允許檔案範圍

此階段只能建立或更新：

- `analysis/codex-skill-blockers/requirements.md`
- `analysis/codex-skill-blockers/technical-spec.md`
- `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
- `plan/codex-skill-blockers/codex-skill-blockers.step.md`
- `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`

此階段不得修改：

- `.github/skills/**`
- `.agents/skills/**`
- `.codex/agents/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Bootstrap input capture**
   - topic plan 必須明確記錄 bootstrap input：
     - `.github/skills/api-client-porting-planner/`
     - `.github/skills/api-client-porting-implementer/`
   - topic plan 不得把它們寫成 post-bootstrap authority

2. **Target artifact contract**
   - topic plan 必須明確寫出目標 artifact：
     - `.agents/skills/api-client-porting-planner/`
     - `.agents/skills/api-client-porting-implementer/`
     - `.codex/agents/api-client-porting-workflow/`
   - topic plan 必須固定三者分工：
     - planner skill：planning-only
     - implementer skill：implementation-only
     - workflow agent：orchestration-only

3. **Codex-facing skill normalization**
   - planner 與 implementer 的 `SKILL.md` 設計必須假設 Codex-safe frontmatter
   - 額外 routing signal 若目前只存在 extra frontmatter，必須在新設計中轉進 `description`
     或正文 trigger 區塊
   - supporting files 可保留為 local bundled resources，但必須由 `SKILL.md` 明確引用

4. **Repo-specific abstraction**
   - `docs/migration-map.md` 與 `docs/porting-ledger.md` 在新設計中不得仍是 unconditional requirement
   - multi-agent workflow status 可保留為 optional handoff fields，但不得成為所有使用情境下的必填輸出
   - `.github/copilot-instructions.md` 的 repo policy 不得成為 Codex-facing runtime prerequisite

5. **Stop-before-review execution shape**
   - 本 topic 只做到新的 draft plan commit
   - 因此 plan / step / checklist 必須清楚表達：
     - rerun analysis / plan package 已完成
     - 舊 blocker-only baseline 已被取代
     - independent review 尚未開始
     - final gate 尚未開始

## Architecture / compliance 自查

- **符合**
  - skill 與 agent 責任分離
  - planner / implementer 核心語意保留
  - repo-specific contract 被降級為 optional/default behavior

- **不符合即阻擋**
  - 把 `.github/skills/api-client-porting-*` 直接宣稱為新的 authority
  - 在新 skill 設計中仍硬綁 `docs/migration-map.md` 或 `docs/porting-ledger.md`
  - 讓 workflow agent 吸收 planner / implementer 全部語意
  - 未重跑 analysis / plan package 就前進 review

## 驗證

必要檢查：

1. 五份 topic 工件存在於預期路徑
2. `requirements.md` 與 `technical-spec.md` 都明確寫出 `2 skills + 1 custom agent`
3. `plan.md` 必須列出 analysis inputs：
   - `analysis/codex-skill-blockers/requirements.md`
   - `analysis/codex-skill-blockers/technical-spec.md`
4. `plan.md` / `step.md` / `checklist.md` 都把 topic 停在 pre-review rerun draft lane

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

- 有人要求在未重跑 draft baseline 前直接進 reviewer
- 後續 work 漂移到實際建立 `.agents/skills/**` 或 `.codex/agents/**`
- human 想把本 rerun topic 直接當成 artifact implementation topic
