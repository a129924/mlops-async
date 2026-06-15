# Custom Agent Codex Compat Requirements

## Purpose

本文件凍結 `mlops-async` 在 custom agent Codex compatibility 上的 implementation
planning baseline：

- 以 `.github/agents/python-implementation-workflow.agent.md` 為 read-only source evidence
- 明確指定 downstream implementation 應建立的官方 repo-local discovery artifacts
- 明確限制本輪只更新 planning artifacts，不建立 custom agent / wrapper skill 實作檔

## Scope

本需求涵蓋：

- `.github/agents/python-implementation-workflow.agent.md` 的 read-only source 對照
- `./.codex/agents/python-implementation-workflow.toml`
- `./.agents/skills/python-implementation-workflow/SKILL.md`
- `./.agents/skills/python-implementation-workflow/agents/openai.yaml`
- topic-local planning artifacts

Out of scope:

- `./codex/**`
- `./agents/openai.yaml`
- 本輪直接建立 `./.codex/agents/*.toml`
- 本輪直接建立 `./.agents/skills/*`
- `./tests/test_codex_custom_agent_baseline.py`

## Actors and ownership

- Planner agent：維護 requirements 與 technical spec 的 implementation baseline
- PlanCreator agent：維護 repo-visible plan / spec / step / checklist
- Future creator：在後續 phase 依 planning artifacts 建立 repo-local custom agent 與 wrapper skill artifacts
- Human reviewer：驗證 path contract、legacy dependency boundary、與 wrapper skill boundary

## Measurable requirements

1. **Official discovery path contract**
   - Required outcome: downstream implementation 只能使用：
     - `./.codex/agents/*.toml`
     - `./.agents/skills/<skill-name>/SKILL.md`
     - `./.agents/skills/<skill-name>/agents/openai.yaml`
   - Failure meaning: 若任何 planning artifact 改寫成 `./codex/...` 或 `./agents/openai.yaml`，即違反需求

2. **Artifact family contract**
   - Required outcome: topic 必須明確列出 custom agent entry、wrapper skill entry、wrapper skill agent config 三個 artifacts
   - Failure meaning: 若只規劃其中一部分，或把 wrapper files 當成可省略，則 downstream implementation contract 不完整

3. **Legacy dependency boundary**
   - Required outcome: `.github/agents/python-implementation-workflow.agent.md` 只能作為 read-only source evidence
   - Failure meaning: 若 planning artifact 把 `.github/agents/*` 當成最終 discovery surface 或要求直接改寫 legacy source，則違反需求

4. **Wrapper skill boundary**
   - Required outcome: wrapper skill 只負責 skill discovery 與 custom-agent handoff，不得吞併 custom agent 核心 workflow semantics
   - Failure meaning: 若 `SKILL.md` 或 `agents/openai.yaml` 被規劃成 agent artifact 的替代品，則 topic scope 漂移

5. **Planning-only current round**
   - Required outcome: 本輪 completion 僅為 planning artifacts ready for downstream implementation
   - Failure meaning: 若本輪要求直接建立 custom agent / wrapper skill artifacts，則違反本輪限制

## Non-goals

- 本輪不建立 `./.codex/agents/python-implementation-workflow.toml`
- 本輪不建立 `./.agents/skills/python-implementation-workflow/SKILL.md`
- 本輪不建立 `./.agents/skills/python-implementation-workflow/agents/openai.yaml`
- 本輪不建立 `./tests/test_codex_custom_agent_baseline.py`

## Freeze status

Status: `FROZEN`
