# coverage-agent Specification

## Acceptance Criteria

1. `pyproject.toml` `[tool.coverage.report]` uses `fail_under = 90`.
2. `.pre-commit-config.yaml` `coverage-check` hook name and entry use 90% semantics.
3. Existing `.pre-commit-config.yaml` `pytest` hook keeps `stages: [manual]` behavior.
4. `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing` generates `.coverage-reports/coverage.json`.
5. Agent triage uses pytest-cov JSON fields such as `files[*].missing_lines` and `files[*].functions[*].missing_lines`.
6. `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py` are absent.
7. Current-truth artifacts do not require a deleted helper or generated placeholder tests.
8. README describes coverage JSON / human feedback triage, not helper-based test generation.

---

## Behavioral Scenarios

### Scenario 1: 90% coverage gate

- **Given**: repository governance requires 90% unit-test coverage.
- **When**: validation or the `coverage-check` hook runs.
- **Then**: coverage below 90% returns non-zero exit code and shows missing-line evidence.

### Scenario 2: pytest-cov JSON evidence

- **Given**: pytest-cov has produced `.coverage-reports/coverage.json`.
- **When**: an Agent needs to inspect coverage gaps.
- **Then**: the Agent reads Coverage.py JSON `totals`, `files`, `missing_lines`, and `functions` data.

### Scenario 3: Human review instead of generated placeholders

- **Given**: coverage JSON shows a gap outside the current topic Test Plan or involving a stop condition.
- **When**: the Agent triages the gap.
- **Then**: the Agent reports `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` and does not write tests.

### Scenario 4: Superseded helper remains deleted

- **Given**: the old helper design was superseded by `coverage-agent-simplification`.
- **When**: the repository is searched for current-truth requirements.
- **Then**: no active contract requires `scripts/coverage_agent.py` or generated `assert False` placeholders.

---

## Error / Edge Cases

- If coverage falls below 90%, stop and report JSON-derived gaps rather than creating placeholder tests.
- If `.coverage-reports/coverage.json` appears in `git status --short`, remove it from tracked/staged changes before publish.
- If a stale current-truth reference requires the superseded helper, treat parent artifact backfill as incomplete.
- If local pre-commit cannot find `python` on PATH but `uv run python` works, rerun with `PATH="$PWD/.venv/bin:$PATH"` rather than changing hooks.
