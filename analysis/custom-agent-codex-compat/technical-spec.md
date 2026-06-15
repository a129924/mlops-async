# Custom Agent Codex Compat 技術規格

## Source requirements

本技術規格落實下列需求來源：

- `analysis/custom-agent-codex-compat/requirements.md`

## Goal

把既有 custom-agent topic 從 paused planning baseline 改成 execution-facing
implementation baseline，讓後續 workflow 可以依據 repo-local discovery contract，
實作下列 downstream artifacts：

- `./.codex/agents/python-implementation-workflow.toml`
- `./.agents/skills/python-implementation-workflow/SKILL.md`
- `./.agents/skills/python-implementation-workflow/agents/openai.yaml`

本輪僅更新 planning artifacts；不得在此 technical spec topic 內建立上述實作檔案。

## Allowed file scope for this round

### Allowed

- `analysis/custom-agent-codex-compat/requirements.md`
- `analysis/custom-agent-codex-compat/technical-spec.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.spec.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md`

### Downstream implementation targets only

- `./.codex/agents/python-implementation-workflow.toml`
- `./.agents/skills/python-implementation-workflow/SKILL.md`
- `./.agents/skills/python-implementation-workflow/agents/openai.yaml`

### Forbidden in this round

- `./.codex/agents/*.toml`
- `./.agents/skills/*`
- `./tests/test_codex_custom_agent_baseline.py`
- `./codex/**`
- `./agents/openai.yaml`
- direct edits to `.github/agents/python-implementation-workflow.agent.md`

## Source evidence and target layout

### Read-only legacy source

- `.github/agents/python-implementation-workflow.agent.md`

此檔案是 migration source evidence，不是 downstream discovery surface，也不是本輪可修改目標。

### Required downstream layout

| Artifact | Path | Responsibility |
| --- | --- | --- |
| Custom agent entry | `./.codex/agents/python-implementation-workflow.toml` | 定義可被 Codex 以 repo-local agent discovery 載入的 agent metadata 與 instruction routing |
| Wrapper skill entry | `./.agents/skills/python-implementation-workflow/SKILL.md` | 定義 skill-facing handoff、使用邊界、以及如何呼叫 custom agent |
| Wrapper skill agent config | `./.agents/skills/python-implementation-workflow/agents/openai.yaml` | 讓 wrapper skill 透過官方 repo-local path 綁定 custom agent |

## Execution decisions

1. **Official repo-local discovery only**
   - downstream implementation 只能使用：
     - `./.codex/agents/*.toml`
     - `./.agents/skills/<skill-name>/SKILL.md`
     - `./.agents/skills/<skill-name>/agents/openai.yaml`
   - 不得寫成 `./codex/...`
   - 不得寫成 `./agents/openai.yaml`

2. **Legacy dependency boundary**
   - `.github/agents/python-implementation-workflow.agent.md` 僅作為 read-only source evidence。
   - downstream implementation 必須從 legacy source 轉譯 phase/gate/boundary semantics，但不得把 `.github/agents/*` 當成最終 runtime discovery path。

3. **Wrapper skill boundary**
   - `SKILL.md` 與 `agents/openai.yaml` 是 wrapper layer，不是新的 orchestration implementation surface。
   - wrapper skill 的責任是把 repo-local skill discovery 導向 custom agent；不得把原本屬於 custom agent 的核心 workflow semantics 搬進 wrapper skill 以取代 agent artifact。

4. **No legacy adapter shortcut**
   - 不得把 legacy projection tooling、path aliasing、或非官方 wrapper 寫法當成完成條件。
   - downstream implementation 必須直接落在官方 repo-local discovery paths，而不是先建立另一層 adapter。

5. **Planning-artifacts-only this round**
   - 本輪 completion 條件是 planning artifacts ready for downstream implementation。
   - Phase 3 以後才允許建立 custom agent / wrapper skill artifacts。

## Phase contract

### Phase 1 Plan Review input

- `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`
- `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md`

### Phase 2 TDD / behavior-contract input

- `plan/custom-agent-codex-compat/custom-agent-codex-compat.spec.md`

此 topic 的 Phase 2 需要 `spec.md`，因為 downstream implementation 同時涉及 agent artifact、
wrapper skill artifact、與官方 path contract；若沒有獨立 behavior contract，Phase 2 將無法精確判斷 artifact family、cross-reference 與 boundary 是否正確。

### Phase 3 implementation gate target

只在所有 canonical `## Implementation Steps` 完成後，才可宣稱 downstream implementation ready for review。

## Acceptance gate

1. planning artifacts 必須把 topic 明確描述為 implementation baseline，而不是 paused draft baseline。
2. 所有 implementation target paths 必須是官方 repo-local discovery paths。
3. planning artifacts 必須清楚列出三個 downstream artifacts：
   - `./.codex/agents/python-implementation-workflow.toml`
   - `./.agents/skills/python-implementation-workflow/SKILL.md`
   - `./.agents/skills/python-implementation-workflow/agents/openai.yaml`
4. planning artifacts 必須清楚列出 legacy dependency boundary。
5. planning artifacts 必須清楚列出 wrapper skill boundary。
6. planning artifacts 必須清楚標示本輪不建立 implementation artifacts。

## Validation

必要檢查：

1. `technical-spec.md`、`plan.md`、`step.md`、`checklist.md` 內容一致地使用官方 repo-local discovery paths。
2. `plan.md` 與 `step.md` 的 downstream work 都以建立三個 implementation artifacts 為主，而不是停在治理缺口描述。
3. `checklist.md` 明確檢查 legacy dependency boundary 與 wrapper skill boundary。
4. `spec.md` 若存在，必須能作為 Phase 2 的 primary behavior contract。

## Stop conditions

若出現以下情況，必須停止並交 reviewer 驗證：

- downstream implementation 企圖建立 `./codex/**` 或 `./agents/openai.yaml`
- wrapper skill 被設計成直接取代 custom agent artifact
- implementation 需要修改 `.github/agents/python-implementation-workflow.agent.md` 才能繼續
- implementation 企圖在本 topic 內新增測試或其他非規劃允許 artifacts
