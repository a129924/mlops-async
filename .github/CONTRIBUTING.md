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

When porting behavior from `sasctl` or a legacy SDK:

1. Start from `analysis/api-client-porting-contract/requirements.md` and `analysis/api-client-porting-contract/technical-spec.md`.
2. Use `api-client-porting-planner` to produce source evidence, request contract drafts, risk classification, porting order, and stop flags.
3. Use `api-client-porting-implementer` only after request contract evidence exists.
4. Write request-contract tests before minimal implementation.
5. Update `docs/porting-ledger.md` for every ported API before claiming compatibility.
6. Stop for human review when source behavior, response schema, pagination, polling, upload/download, streaming, or global session side effects are unclear.

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
- `docs/porting-ledger.md` — API porting evidence and compatibility ledger
