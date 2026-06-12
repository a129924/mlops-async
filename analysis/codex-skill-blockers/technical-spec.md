# Codex Skill Blockers 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/codex-skill-blockers/requirements.md`

## 目標

建立一份 execution-facing blocker topic baseline，說明兩個 `api-client-porting-*`
skills 為何必須先停在 blocker lane，並把後續 canonicalization prerequisite 鎖成
未來 topic 的前提。

## 允許檔案範圍

此階段只能建立或更新：

- `analysis/codex-skill-blockers/requirements.md`
- `analysis/codex-skill-blockers/technical-spec.md`
- `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
- `plan/codex-skill-blockers/codex-skill-blockers.step.md`
- `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`

此階段不得修改：

- `skills/**`
- `.codex/skills/**`
- `.github/agents/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Blocker evidence capture**
   - topic plan 必須明確記錄兩個 blocker skill 的現況來源路徑：
     - `.github/skills/api-client-porting-implementer/`
     - `.github/skills/api-client-porting-planner/`
   - topic plan 不得把它們寫成 future canonical source

2. **Future prerequisite contract**
   - topic plan 必須明確寫出未來 prerequisite：
     - `skills/api-client-porting-implementer/`
     - `skills/api-client-porting-planner/`
   - 在 prerequisite 未成立前，不得規劃 `.codex/skills` apply

3. **Stop-before-review execution shape**
   - 本 topic 只做到 draft plan commit
   - 因此 plan / step / checklist 必須清楚表達：
     - topic package 已建立
     - independent review 尚未開始
     - final gate 尚未開始

4. **Feasibility / compliance notes**
   - 目前看不到同名 canonical source，因此 blocker 判定成立
   - 若後續 human 要求解 blocker，需另開 canonicalization topic，而不是把 blocker topic
     偷偷擴張成 implementation topic

## Architecture / compliance 自查

- **符合**
  - 保持 blocker lane 與 projection lane 分離
  - 不把 naming similarity 當成 canonical evidence

- **不符合即阻擋**
  - 直接規劃 `.github/skills/api-client-porting-*` -> `.codex/skills/*`
  - 在 blocker topic 內發明替代 canonical source

## 驗證

必要檢查：

1. 五份 topic 工件存在於預期路徑
2. `requirements.md` 與 `technical-spec.md` 都明確寫出 no-direct-projection rule
3. `plan.md` / `step.md` / `checklist.md` 都把 topic 停在 pre-review draft lane

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

- 有人要求在無 canonical source 下直接 projection
- 後續 work 漂移到 `skills/**` 或 `.codex/skills/**`
- human 想把 blocker topic 直接當成 custom-agent 或 projection topic
