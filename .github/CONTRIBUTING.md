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

## Git conventions

- Prefer short-lived topic branches
- Use semantic commit messages
- Keep commits atomic and reviewable

## Source of truth

- `pyproject.toml` — dependencies and tool configuration
- `blueprint.md` — initialization contract and acceptance criteria
- `.github/copilot-instructions.md` — AI-facing coding rules
- `.github/skills/` — detailed skill-level guidance
