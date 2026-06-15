# mlops-async agent governance contract

## Governance source

- `AGENTS.md` 是本 repository 的 repo-local agent governance contract。
- 涉及 skill discovery、skill authority、repo-level agent language default 時，
  以 `AGENTS.md` 為第一層規則來源。

## Language default

- repo 自有文件、agent 回覆、`analysis/`、`plan/`、ledger artifacts 預設使用繁體中文。
- upstream、imported、shared assets 可保留原始語言。
- canonical headings、fixed labels、workflow names、必要技術術語可保留英文原文。

## Discoverable skill surface

- repo-local discoverable skills 位於 `.agents/skills/`。
- 對 `codex-skill-projection` topic 而言，managed target set 限於
  `.agents/skills/<name>/` 下已 materialized 的 frozen same-name skills。

## Authority and precedence

- 涉及 discoverable skills 的讀取、比對、對齊、引用與 authority 判定時，
  以 `AGENTS.md` 與 `.agents/skills/*` 為準。
- 若其他 agent guidance 文件（包含 `.github/copilot-instructions.md`）對 skill
  surface 或 authority 有不同描述，以 `AGENTS.md` 為準。

## Non-active surfaces

- `.codex/skills/` 不是此 repository 在本 topic 的 active discovery surface。
- `.github/skills/` 不是此 repository 在本 topic 的 source-of-truth 或 active
  discovery surface。

## Workflow agent boundary

- `.github/agents/*` 仍在 skill discovery alignment scope 之外。

## Scope guard

- `AGENTS.md` 僅負責 repo-level agent governance、language default、skill
  discovery 與 authority boundary。
- async、typing、testing、coverage、API design、release workflow 等一般
  engineering policy 不在 `AGENTS.md` 的承載範圍內。
