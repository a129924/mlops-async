# Custom Agent Codex Compat Requirements

## Purpose

本文件凍結 `mlops-async` 在 custom agent Codex compatibility 上的需求基線：

- 以 `.github/agents/python-implementation-workflow.agent.md` 為單一分析對象
- 明確記錄目前尚無 `.codex/agents` 既成治理契約
- 為未來 agent compatibility planning 保留邊界、假設缺口、與 stop conditions

## Scope

本需求只涵蓋：

- `.github/agents/python-implementation-workflow.agent.md`

Out of scope:

- `.github/skills/*`
- `.codex/skills/*`
- `.codex/agents/*` 的直接建立
- runtime execution / orchestration implementation
- release / version promotion

## Actors and ownership

- Planner agent：凍結 agent compatibility baseline 與 governance gap
- PlanCreator agent：建立 repo-visible topic plan / step / checklist
- Human reviewer：決定是否接受未來 `.codex/agents` 契約方向

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Single-agent scope**
   - Condition: topic baseline 凍結時
   - Required outcome: analysis 對象只限
     `.github/agents/python-implementation-workflow.agent.md`
   - Acceptance signal: 不可把其他 agents 或 skills 混入此 topic

2. **No-existing-governance assumption**
   - Condition: future Codex-compatible agent planning
   - Required outcome: 不得假設 `.codex/agents` 已有現成治理、路徑規則或 runtime contract
   - Acceptance signal: 任何 topic artifact 若把 `.codex/agents/*` 當既成可用 surface，
     即視為需求違反

3. **Governance-gap visibility**
   - Condition: topic package 建立時
   - Required outcome: 必須明確寫出至少三類缺口：
     - path / folder governance
     - execution / runtime semantics
     - validation / acceptance method
   - Acceptance signal: 若缺口被省略或被假設自動解決，topic package 不成立

4. **No-adapter-shortcut rule**
   - Condition: agent compatibility 被規劃為 future work
   - Required outcome: 不得把 `platform-projection-adapter` 當成 agent solution
   - Acceptance signal: topic 工件不得宣稱 adapter 可處理 `.github/agents/*`

5. **Repo-visible planning package**
   - Condition: 本 topic draft package 建立時
   - Required outcome: 必須存在 requirements、technical-spec、plan、step、checklist
   - Acceptance signal: 缺一不可

## Contradictions surfaced and resolved

1. 想讓 agent 也被 Codex consume vs repo 目前只對 `.codex/skills` 有明確治理語言
   - Resolution: 先把 custom-agent 留在獨立 planning lane，不假設治理已存在

2. 想沿用 skill projection tooling vs adapter 明確只支援 skills
   - Resolution: 禁止把 adapter 當 agent migration shortcut

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- 直接建立 `.codex/agents/python-implementation-workflow.agent.md` 並宣稱完成
- 把 `.github/agents/*` 說成只是另一種 skill
- 把 runtime dispatch / orchestration 假設寫成既成事實
- 在未補治理契約前前進到 implementation

## Non-goals

- 本 topic 不建立 `.codex/agents/`
- 本 topic 不修改 `.github/agents/python-implementation-workflow.agent.md`
- 本 topic 不處理 skills canonicalization / projection
- 本 topic 不處理 runtime implementation

## Blockers

- 目前缺少 `.codex/agents` 治理契約，是此 topic 的核心 blocker。

## Freeze status

Status: `FROZEN`
