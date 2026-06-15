---
name: python-implementation-workflow
description: Wrapper workflow recipe for parent Codex sessions that need to coordinate Python topic delivery with repo-local planner, implementer, and reviewer agents while preserving shared artifact-contract boundaries.
---

# Python Implementation Workflow

當 parent Codex session 需要針對單一 topic 使用 repo-local Python implementation workflow，並完成 plan、implementation 與 review handoff 時，使用此 skill。

執行前請先閱讀 [reference.md](./reference.md)。

## Role

此 skill 是提供給 parent Codex session 的 wrapper recipe。

- 它不會以自己的 engine 取代 runtime orchestration。
- 它不會重新定義屬於 custom agents 的核心 workflow contract。
- 它不會建立對 legacy `.github/agents/*.agent.md` 檔案的 runtime dependency。

## Required Inputs

- 單一 active topic 與其對應的 plan artifacts
- Repo-local custom agents:
  - `planner`
  - `implementer`
  - `reviewer`
- 當建立或審查 workflow artifacts 時，需使用共享的 `workflow-artifact-contract` skill

## Wrapper Handoff Recipe

1. 使用 `planner` 依據目前的 repo artifacts 確認或細化 topic execution plan。
2. 使用 `implementer` 進行滿足已核准 plan 的 scoped repository changes。
3. 使用 `reviewer` 檢查 correctness、path compliance、contract boundaries 與 validation coverage。
4. 所有 workflow artifacts 只能保留在正式的 repo-local paths。

## Required Returned Artifacts

- `planner` 必須針對單一 active topic 回傳具體的 execution plan，包含 scoped steps、assumptions、constraints，以及 workflow 預期使用的 repo-local artifact paths。
- `implementer` 必須回傳實際套用的 repository change set、精簡的 implementation summary，以及用來證明已執行核准 plan 的 validation results。
- `reviewer` 必須回傳 review findings、residual risks 或 open questions，以及明確的 pass/fail recommendation，說明該 topic 是否可離開 review 階段。
- 回傳的 artifacts 必須建立在目前 repo-local workflow outputs 之上，且執行時不得依賴 legacy `.github/agents/*.agent.md` 檔案。
- Legacy `.github/agents/*.agent.md` 檔案僅作為 frozen provenance 保留，並非此 wrapper skill 所需的 runtime artifact source。

## Required Gates

- Planning gate: `planner` 必須先產出或確認可用的 topic plan，`implementer` 才能開始進行 scoped repository changes。
- Implementation gate: `implementer` 必須維持在已核准的 topic scope 內，並在 handoff 給 `reviewer` 之前回傳已套用的 change summary 與 validation evidence。
- Review gate: 在 parent Codex session 將 topic 視為 review-complete 之前，`reviewer` 必須驗證 correctness、path compliance、artifact-contract boundaries 與 validation coverage。
- Path gate: 所有 workflow artifacts 必須留在正式的 repo-local paths；此 wrapper skill 不可將 runtime artifacts 轉導到 legacy `.github/agents/*.agent.md` 檔案或 repo-root `agents/openai.yaml`。
- Workflow boundary gate: git commit、push 與 pull request actions 仍屬於此 workflow 之外，不屬於滿足這些 gates 的一部分。

## Human-Review Stop Boundary

- 一旦 `reviewer` 已針對 scoped topic 回傳 findings 與最終 pass/fail recommendation，parent Codex session 就必須停下來交由人工審查。
- 此 wrapper skill 會協調 `planner`、`implementer` 與 `reviewer`，但不得將自己呈現為可自行核准 release 或 merge 決策的 autonomous runtime orchestration engine。
- 若 `reviewer` 回報 blocking findings、unresolved risks 或 validation 不足，workflow 必須返回 parent Codex session，由人類明確指示下一步。
- 即使 review 通過，commit、push 與 pull request 的決策仍在此 workflow boundary 之外，必須由人類另行處理。

## Boundaries

- Parent Codex session 仍負責 sequencing 與 tool execution。
- 此 skill 是提供給該 session 的描述性指引，不是獨立的 orchestrator。
- Git commit、push 與 pull request actions 仍在此 workflow skill 之外。
