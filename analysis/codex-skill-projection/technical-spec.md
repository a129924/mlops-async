# Codex Skill Projection 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/codex-skill-projection/requirements.md`

## 目標

把「同名 skill canonicalization -> `.codex/skills` projection」落成一個可被後續
creator 執行的 repo-visible topic plan，並明確保留 skills / agents 分流。

## 允許檔案範圍

此 planning 階段只能建立或更新：

- `analysis/codex-skill-projection/requirements.md`
- `analysis/codex-skill-projection/technical-spec.md`
- `plan/codex-skill-projection/codex-skill-projection.plan.md`
- `plan/codex-skill-projection/codex-skill-projection.step.md`
- `plan/codex-skill-projection/codex-skill-projection.checklist.md`

此階段不得修改：

- `skills/**`
- `.codex/skills/**`
- `.github/skills/**`
- `.github/agents/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Candidate inventory freeze**
   - Topic plan 必須固定 32 個可轉移 skill 名稱
   - 必須明確記錄排除：
     - `copilot-instructions-init`
     - `api-client-porting-implementer`
     - `api-client-porting-planner`
     - `.github/agents/*`

2. **Source-of-truth mapping**
   - Topic plan 必須把 future canonical source 鎖定為
     `agent-skills/skills/<name>/`
   - `mlops-async/.github/skills/<name>/` 僅能被描述為現況 compatibility surface

3. **Future implementation target model**
   - Topic plan 必須把未來目標拆成兩層：
     - canonical `mlops-async/skills/<name>/`
     - projected `mlops-async/.codex/skills/<name>/`
   - 必須明確說明 `.codex/skills` 是 projection / compatibility surface，
     不是 canonical source

4. **Projection execution contract**
   - future creator work 必須先引入 `platform-projection-adapter`
   - projection 只能走：
     - dry-run
     - `--apply` with explicit write intent
     - `--force` only with explicit human overwrite authorization
   - 不允許第二套 projection algorithm

5. **Agent split contract**
   - topic plan 必須把 `.github/agents/python-implementation-workflow.agent.md`
     明確排除到 `custom-agent-codex-compat`
   - 不得把任何 `.github/agents/*` 路徑列為本 topic creator artifact

6. **Feasibility / compliance notes**
   - 目前 repo 缺少 canonical `skills/` tree 與 `.codex/` surface，因此此 topic
     是 future-migration planning，不是 immediate projection execution
   - 若後續 implementation 發現 `.codex/skills` 還需要 README、provenance、
     或其他 support files 才能符合 consumer expectation，必須 stop and amend
     plan，而不是在 creator 階段擴張

## Architecture / compliance 自查

- **符合**
  - planning / governance topic 與 repo `project-goal`、`project-guidelines`
    一致
  - 明確維持 skills / agents 分流
  - 不把 compatibility surface 誤當 canonical source

- **不符合即阻擋**
  - 在無 canonical `skills/` 的前提下直接規劃 `.github/skills` -> `.codex`
  - 在無 human authorization 下規劃 `--force`
  - 在 projection topic 內處理 agent compatibility

- **需豁免才可前進**
  - 若後續需要超出 topic plan 列出的 artifact paths

## 驗證

此階段僅限分析與計畫產物。

必要檢查：

1. 五份 topic 工件都存在於預期路徑
2. `requirements.md` 明確列出 32 個 candidates 與排除集合
3. `technical-spec.md`、`plan.md` 都明確記錄 canonical source 與 projection
   surface 差異
4. `plan.md` 不得列入 `.github/agents/*`

建議指令：

```bash
test -f analysis/codex-skill-projection/requirements.md
test -f analysis/codex-skill-projection/technical-spec.md
test -f plan/codex-skill-projection/codex-skill-projection.plan.md
test -f plan/codex-skill-projection/codex-skill-projection.step.md
test -f plan/codex-skill-projection/codex-skill-projection.checklist.md
```

## 停止條件

若出現以下情況，必須停止並請求人工作審：

- candidate set 與 `agent-skills/skills/` 真實內容不一致
- future implementation 需要處理 `.github/agents/*`
- projection 需要額外 governance support files，但 plan 尚未列入
- 後續執行者想繞過 `platform-projection-adapter`
