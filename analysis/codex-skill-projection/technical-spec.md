# Codex Skill Projection 技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/codex-skill-projection/requirements.md`

## 目標

把 32 個 in-scope same-name skills 從
`source repo/.codex/skills/<name>/` 對齊到
`target repo/.agents/skills/<name>/`，並讓 `AGENTS.md` 明確宣告
`.agents/skills/` 是此 repo 的 discoverable skill surface。

## 允許檔案範圍

本 topic 允許建立或更新：

- `AGENTS.md`
- `analysis/codex-skill-projection/requirements.md`
- `analysis/codex-skill-projection/technical-spec.md`
- `plan/codex-skill-projection/codex-skill-projection.plan.md`
- `plan/codex-skill-projection/codex-skill-projection.step.md`
- `plan/codex-skill-projection/codex-skill-projection.checklist.md`
- `plan/codex-skill-projection/codex-skill-projection.audit.md`
- `plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md`
- `.agents/skills/<name>/` for the frozen 32 names only

本 topic 不得修改：

- `.github/agents/**`
- `.github/skills/**`
- `skills/**`
- `README.md`
- `VERSION`

## 技術需求對照

1. **Discovery contract**
   - `AGENTS.md` 必須宣告 `.agents/skills/` 是 repo-local discoverable skill
     root
   - 內容需明確區分：
     - `.agents/skills/` = active target / discovery surface for this repo
     - `.codex/skills/` = non-active / superseded surface for this topic

2. **Source inventory**
   - 對 frozen 32 names 逐一檢查 source skill root 是否存在
   - source path 固定為
     `source repo/.codex/skills/<name>/`

3. **Target inventory**
   - 對 frozen 32 names 逐一檢查 target skill root 是否存在
   - target path 固定為
     `target repo/.agents/skills/<name>/`

4. **Recursive diff audit**
   - 若 source 與 target 都存在，必須做整棵目錄的 recursive compare
   - compare scope 包含 skill root 內所有 repo-visible files and subdirectories

5. **Migration rule**
   - 若 source 存在且 target 不存在，建立 target 並複製整棵 source root

6. **Overwrite rule**
   - 若 source 存在、target 存在且 recursive compare 不一致：
     - 先記錄 diff audit
     - 再用 source 整棵覆蓋 target
     - 移除 target-only 檔案

7. **Legacy `.codex/skills` cleanup**
   - 若 branch 內已有本 topic 建出的 `.codex/skills/<name>`：
     - 視為錯誤落點
     - 從 topic branch 移除
   - reviewer 不以 `.codex/skills/*` 作成功依據

8. **No-op rule**
   - 若 source 與 target 已一致，只記錄 `identical`，不重寫 target

9. **Audit ledger contract**
   - `codex-skill-projection.audit.md` 必須為 32 個 skill 各有一列
   - 每列至少記錄：
     - `skill_name`
     - `source_exists`
     - `target_exists_before`
     - `migrated_before`
     - `diff_status_before`
     - `action`
     - `result`
     - `post_verify`
     - `notes`

## Architecture / compliance 自查

- **符合**
  - 只讀 source repo 的 `.codex/skills/`
  - 只寫 target repo 的 `.agents/skills/`
  - 以 `AGENTS.md` 鎖定 repo-local discovery contract
  - 明確維持 skills / agents / blockers 分流

- **不符合即阻擋**
  - 讀 `.github/skills/*` 當 source
  - 寫 `skills/*`
  - 在 topic 內碰 `.github/agents/*`
  - 繼續把 `.codex/skills/*` 當 active target
  - 不更新 `AGENTS.md` 就宣稱 `.agents/skills/` 可 discovery

- **需豁免才可前進**
  - 若後續需要處理本次 32 個 skill 以外的 target roots

## 驗證

必要檢查：

1. 八份 topic / governance 工件都存在：
   - `AGENTS.md`
   - requirements
   - technical-spec
   - plan
   - step
   - checklist
   - audit
   - corrective-prompt
2. `.agents/skills/` 存在
3. 對每個 frozen name：
   - source 存在
   - target 於執行後存在
   - `post_verify = aligned`
4. target 內不應殘留 target-only drift
5. `.codex/skills/*` 不再作為本 topic 成功條件

建議指令：

```bash
test -f AGENTS.md
test -f analysis/codex-skill-projection/requirements.md
test -f analysis/codex-skill-projection/technical-spec.md
test -f plan/codex-skill-projection/codex-skill-projection.plan.md
test -f plan/codex-skill-projection/codex-skill-projection.step.md
test -f plan/codex-skill-projection/codex-skill-projection.checklist.md
test -f plan/codex-skill-projection/codex-skill-projection.audit.md
test -f plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md
test -d .agents/skills
```

## 停止條件

若出現以下情況，必須停止並請求人工作審：

- frozen 32 names 中任何 source skill 缺失
- 執行中發現需碰 `.github/agents/*`
- 執行中發現需碰 blockers
- 執行中發現需建立 `skills/*`
