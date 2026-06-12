# Codex Skill Blockers Requirements

## Purpose

本文件凍結 `mlops-async` 在 Codex skill migration 中的 blocker baseline：

- 辨識目前只有 `.github/skills/`、但在 `agent-skills/skills/` 中沒有同名 canonical
  source 的 skill
- 明確說明這些 skill 為何不能直接進入 projection topic
- 為後續單獨 canonicalization topic 保留可追溯前置條件

## Scope

本需求只涵蓋下列 blocker skills：

- `api-client-porting-implementer`
- `api-client-porting-planner`

Out of scope:

- 其他同名可 projection skill
- `.github/agents/*`
- `.codex/agents/*`
- 直接執行 canonicalization / projection
- runtime implementation

## Actors and ownership

- Planner agent：凍結 blocker 定義與前置條件
- PlanCreator agent：建立 repo-visible topic plan / step / checklist
- Human reviewer：後續決定是否接受 canonicalization 方向

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Exact blocker inventory**
   - Condition: blocker baseline 凍結時
   - Required outcome: inventory 必須只包含兩個 skill
   - Acceptance signal: 不可混入同名可 projection candidates

2. **No-direct-projection rule**
   - Condition: 後續評估 Codex-compatible migration
   - Required outcome: 這兩個 skill 不得直接進入 `platform-projection-adapter`
   - Acceptance signal: topic 工件不得把 `.github/skills/<name>/` 視為可立即 projection
     source

3. **Canonicalization prerequisite**
   - Condition: 未來想讓這兩個 skill 進入 `.codex/skills/`
   - Required outcome: 必須先建立對應 canonical `skills/<name>/`
   - Acceptance signal: 未來 topic 若缺少 canonical folder contract，就不得前進到
     projection execution

4. **Semantic-fit requirement**
   - Condition: future canonicalization planning
   - Required outcome: 不可僅因名稱相近、功能相關、或 upstream prompt 名稱接近，就把
     其他 skill 視為替代 canonical source
   - Acceptance signal: 若無 exact same-name canonical source，就必須留在 blocker lane

5. **Repo-visible planning package**
   - Condition: 本 blocker topic draft package 建立時
   - Required outcome: 必須存在 requirements、technical-spec、plan、step、checklist
   - Acceptance signal: 缺任何一份都表示 blocker topic 尚未可追溯

## Contradictions surfaced and resolved

1. 想快速進入 `.codex/skills` vs 缺少 canonical `skills/<name>/`
   - Resolution: 先停在 blocker lane，不能跳過 canonicalization prerequisite

2. 名稱相近即可替代 vs canonical source 必須可追溯
   - Resolution: 僅接受 exact same-name canonical source；否則列 blocker

## Extreme-boundary checks

以下情境不得被此 topic 靜默放行：

- 把任一 blocker skill 直接加入 projection candidate set
- 把 `.github/skills/api-client-porting-*` 直接當成 adapter source
- 以其他 skill 的部分內容推定可替代 canonical source
- 在無需求補強下宣稱 blocker 已解除

## Non-goals

- 本 topic 不直接建立 `skills/api-client-porting-implementer/`
- 本 topic 不直接建立 `skills/api-client-porting-planner/`
- 本 topic 不直接 materialize `.codex/skills/api-client-porting-*`
- 本 topic 不處理 agents

## Blockers

- 缺少同名 canonical source，是本 topic 的核心 blocker 本體；因此後續只允許停在
  planning / draft-plan lane，不得直接切入 projection execution。

## Freeze status

Status: `FROZEN`
