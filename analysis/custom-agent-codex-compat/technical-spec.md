# Custom Agent Codex Compat 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/custom-agent-codex-compat/requirements.md`

## 目標

建立一份 execution-facing custom-agent planning baseline，說明為何
`.github/agents/python-implementation-workflow.agent.md` 目前只能停在 governance /
compatibility planning lane，而不能直接被當成 `.codex/agents` implementation topic。

## 允許檔案範圍

此階段只能建立或更新：

- `analysis/custom-agent-codex-compat/requirements.md`
- `analysis/custom-agent-codex-compat/technical-spec.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md`

此階段不得修改：

- `.github/agents/python-implementation-workflow.agent.md`
- `.codex/agents/**`
- `.github/skills/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Current-source evidence**
   - topic plan 必須明確記錄現況 source path：
     `.github/agents/python-implementation-workflow.agent.md`

2. **Governance-gap capture**
   - topic plan 必須明確寫出至少三個 future prerequisite：
     - `.codex/agents` path / folder contract
     - runtime / execution semantics contract
     - validation / acceptance contract

3. **No-direct-implementation shape**
   - 本 topic 只做到 draft plan commit
   - topic 工件不得假裝 `.codex/agents` 已存在可落地目標

4. **Tooling boundary**
   - topic plan 必須明確排除 `platform-projection-adapter` 作為 agent solution
   - topic plan 不得把 skill projection workflow 直接套用到 agent surface

## Architecture / compliance 自查

- **符合**
  - skills / agents 分流
  - 不發明現成治理契約
  - 不誤用 skill adapter

- **不符合即阻擋**
  - 把 `.codex/agents` 寫成既成 canonical / projection surface
  - 在無治理契約下前進到 implementation planning

## 驗證

必要檢查：

1. 五份 topic 工件存在於預期路徑
2. `requirements.md` 與 `technical-spec.md` 都明確列出 governance gap
3. `plan.md` / `step.md` / `checklist.md` 都把 topic 停在 draft-plan lane

建議指令：

```bash
test -f analysis/custom-agent-codex-compat/requirements.md
test -f analysis/custom-agent-codex-compat/technical-spec.md
test -f plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md
test -f plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md
test -f plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md
```

## 停止條件

若出現以下情況，必須停止並請求人工作審：

- 有人要求直接建立 `.codex/agents/*`
- 有人要求把 skill projection tooling 當成 agent solution
- 後續 work 漂移到 `.github/agents/python-implementation-workflow.agent.md` 的實質改寫
