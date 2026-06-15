# Custom Agent Codex Compat Spec

## Goal

提供 Phase 2 的 primary behavior contract，讓 downstream implementation 可以在不猜測
artifact layout 的前提下，建立 custom agent 與 wrapper skill 的完整 repo-local
discovery family。

## Source Evidence

- `.github/agents/python-implementation-workflow.agent.md`

此檔案提供 legacy workflow semantics：phase 順序、active gate、resume / blocked /
needs-rework 行為、以及 boundary 說明。它是 read-only source evidence，不是最終 target artifact。

## Required Downstream Artifacts

1. `./.codex/agents/python-implementation-workflow.toml`
2. `./.agents/skills/python-implementation-workflow/SKILL.md`
3. `./.agents/skills/python-implementation-workflow/agents/openai.yaml`

Phase 2 應把這三個檔案視為單一交付單位；缺任何一個都不算 red-tests-ready /
implementation-ready。

## Behavior Contract

### 1. Custom agent entry

`./.codex/agents/python-implementation-workflow.toml` 必須承接 legacy source 的核心行為：

- 單一 topic workflow
- 固定 phase 順序
- gate 失敗時阻擋或內部 needs-rework loop
- 不處理 git commit / push / PR
- Phase 3 completion 依 `step.md` 的 `## Implementation Steps`

它必須是 core orchestration owner；不得把這些責任外包給 wrapper skill。

### 2. Wrapper skill entry

`./.agents/skills/python-implementation-workflow/SKILL.md` 必須：

- 說明何時應使用此 skill
- 說明此 skill 的責任是 handoff 到 custom agent
- 保持 wrapper role，不重寫或取代 custom agent 的 phase/gate semantics

### 3. Wrapper skill agent config

`./.agents/skills/python-implementation-workflow/agents/openai.yaml` 必須：

- 存在於官方 repo-local wrapper binding 路徑
- 維持 wrapper skill 到 custom agent 的關聯
- 不引用 `./agents/openai.yaml`
- 不依賴 `./codex/**`

## Boundary Contract

### Legacy dependency boundary

- `.github/agents/python-implementation-workflow.agent.md` 只能讀，不能改
- legacy source 只提供 semantics，不提供最終 discovery path

### Wrapper skill boundary

- wrapper skill 不能吞掉 custom agent 的核心 orchestration
- wrapper skill 不能變成另一套平行 workflow implementation

### Path boundary

允許：

- `./.codex/agents/*.toml`
- `./.agents/skills/<skill-name>/SKILL.md`
- `./.agents/skills/<skill-name>/agents/openai.yaml`

禁止：

- `./codex/**`
- `./agents/openai.yaml`

## Phase 2 Assessment Gate

- `red-tests-ready` / equivalent readiness 只在 artifact family、path contract、legacy dependency boundary、wrapper skill boundary 都已被明確編碼時成立。
- 若 phase assessor 發現缺少三檔之一、路徑寫錯、或 wrapper skill boundary 不清，應回 `needs-rework` 或 `BLOCKED`。
- 若 `spec.md` 與 `plan.md` 衝突，以本 spec 的 artifact/path/boundary contract 為準，並要求回補 plan 對齊。

## Reviewer Focus

- Reviewer 應確認本 spec 足以支撐 downstream implementation，不需要再回頭推測 artifact family。
- Reviewer 應確認本 spec 沒有把 wrapper skill 當成 custom agent 的替代品。
