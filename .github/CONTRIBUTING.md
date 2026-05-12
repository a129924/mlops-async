# Contributing

## Development workflow

1. Sync dependencies with `uv sync`.
2. Make changes inside `src/mlops_async/` and `tests/`.
3. Run local checks before pushing:
   - `uv run pytest`
   - `uv run pyright`
   - `uv run ruff check .`
   - `uv run ruff format .`

## Quality expectations

- All I/O code must stay async-first
- Public APIs must be fully typed
- Unit tests must avoid external I/O
- Integration tests may talk to a real SAS Viya environment
- Coverage target is `>= 90%`

## Contract-first API porting

當你要從 `sasctl` 或 legacy SDK 平移行為時：

1. 先從 `analysis/api-client-porting-contract/requirements.md` 與 `analysis/api-client-porting-contract/technical-spec.md` 開始。
2. 使用 `api-client-porting-planner` 產生 source evidence、request contract drafts、risk classification、porting order 與 stop flags。
3. 只有在 request contract evidence 已經存在後，才能使用 `api-client-porting-implementer`。
4. 在 minimal implementation 之前，先寫 request-contract tests。
5. 先把 source API -> target async API 的對照狀態更新到 `docs/migration-map.md`。
6. 每個 ported API 都要更新 `docs/porting-ledger.md`，之後才能宣告 compatibility。
7. `docs/migration-map.md` 用於集中追蹤 mapping、狀態與 review notes；`docs/porting-ledger.md` 用於完整證據。
8. 當 source behavior、response schema、pagination、polling、upload/download、streaming 或 global session side effects 不清楚時，停止並交給人工 review。

## Git conventions

- Prefer short-lived topic branches
- Use semantic commit messages
- Keep commits atomic and reviewable

## Source of truth

- `pyproject.toml` — dependencies and tool configuration
- `blueprint.md` — initialization contract and acceptance criteria
- `analysis/` — repo-visible requirements and technical specs for governed topics
- `plan/` — repo-visible implementation plans and step trackers
- `.github/copilot-instructions.md` — AI-facing coding rules
- `.github/skills/` — detailed skill-level guidance
- `.github/agents/` — workflow orchestration guidance for multi-phase implementation work
- `docs/migration-map.md` — source API 到 target async API 的集中遷移對照表
- `docs/porting-ledger.md` — API porting evidence and compatibility ledger
