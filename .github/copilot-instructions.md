# Copilot Instructions — mlops-async

This file defines decision rules for AI agents writing code in this repository.

---

## Language Requirement

**All project communication must be in Traditional Chinese (繁體中文):**
- Code comments, docstrings, and messages
- Git commit messages
- Issue descriptions and pull request content
- Internal documentation

---

## Core Principles

### Async-First Architecture
- **Always use `httpx.AsyncClient`** for all HTTP operations
- All public APIs that perform I/O must be async functions or methods
- No `asyncio.to_thread` wrapping around blocking code
- Structured concurrency: use context managers, respect `CancelledError`

### Strict Type Safety
- Run `pyright --strict` and fix all errors before commit
- All public function/method signatures fully typed (no `Any`)
- `pydantic >= 2.0` for all API response validation
- No `type: ignore` comments except with explicit justification

### No Side Effects at Import
- Module imports must not make network calls
- No global state modification on import
- All async initialization deferred to function/method calls

---

## API Design

### Source SDK Porting
- Before porting any `sasctl` or legacy SDK API, read `analysis/api-client-porting-contract/requirements.md` and `analysis/api-client-porting-contract/technical-spec.md`
- Use `.github/skills/api-client-porting-planner/` for endpoint-family discovery, request contract drafts, risk classification, porting order, and stop flags
- Use `.github/skills/api-client-porting-implementer/` only after planner output or equivalent source/request contract evidence exists
- Update `docs/porting-ledger.md` for every ported API before claiming compatibility
- Stop for human review on upload/download, streaming, polling, retry, pagination expansion, global session side effects, conditional endpoint selection, unclear source behavior, or unclear response schema

### Response Models
- Use `pydantic.BaseModel` for every SAS Viya API response type
- One model per endpoint; reuse common field definitions
- Explicit validation rules; fail fast on invalid responses

### Error Handling
- Create domain-specific exception hierarchy
- Map SAS API error responses → custom exceptions
- Always chain exceptions when translating across boundaries
- No bare `except: pass`

### Public API Surface
- Export only via `src/mlops_async/__init__.py`
- Internal functions/classes use `_prefix_` naming
- Google-style docstrings with intent, args, returns, raises, examples

---

## Code Organization

### Layout
- All source code: `src/mlops_async/`
- Tests import from installed package (not relative imports)
- Clear split: `tests/unit/` (no I/O) vs `tests/integration/` (real API)

### Dependencies
- See `pyproject.toml` for current versions
- Runtime: `httpx`, `pydantic`
- Dev: `pytest`, `pytest-asyncio`, `ruff`, `pyright`, `pytest-cov`

### Style
- Ruff enforced (line length 100, auto-format)
- No `# noqa` without comment explaining why
- All public APIs must have docstrings

---

## Testing

### Unit Tests (`tests/unit/`)
- Pure logic, no external I/O
- Mock HTTP responses with `pytest` fixtures
- Use `@pytest.mark.asyncio` for async tests

### Integration Tests (`tests/integration/`)
- Real `httpx.AsyncClient` calls to SAS Viya
- Optional; can require live SAS instance

### Coverage
- Minimum **90%** coverage (checked before commit)
- `pytest --cov=src/mlops_async --cov-report=term-missing`

---

## Quality Gates

### Before Commit
```
✓ pytest tests/ (all pass)
✓ coverage >= 90%
✓ pyright --strict (no errors)
✓ ruff check (no violations)
```

### Type Checking
- Run `pyright --strict` — strict mode mandatory
- All public APIs typed; internal use strict discipline

---

## References

For detailed guidance, see:

- **`blueprint.md`**: Project acceptance criteria, quality thresholds, sensing assertions
- **`pyproject.toml`**: Authoritative tool versions, dependencies, build config
- **`README.md`**: Installation, quick start, examples
- **`.github/CONTRIBUTING.md`**: Git workflow, commit convention, dev setup
- **`docs/ARCHITECTURE.md`**: Human-facing design intent and skill map
- **`.github/skills/`**: 28 installed Agent Skills with detailed rule references
- **`.github/agents/`**: workflow orchestration agents for plan-to-review execution
- **`analysis/api-client-porting-contract/`**: frozen requirements and technical spec for contract-first API porting
- **`docs/porting-ledger.md`**: compatibility and evidence ledger for ported source SDK APIs

---

## When in Doubt

1. For source SDK porting, start with `analysis/api-client-porting-contract/requirements.md`
2. Use `.github/skills/api-client-porting-planner/SKILL.md` before implementation
3. Use `.github/skills/api-client-porting-implementer/SKILL.md` only after request contract evidence exists
4. Refer to `.github/skills/python-async-await/SKILL.md` for async patterns
5. Refer to `.github/skills/python-error-handling/SKILL.md` for exception design
6. Refer to `.github/skills/python-testing-pytest/SKILL.md` for test structure
7. Use `.github/agents/python-implementation-workflow.agent.md` when the task needs gated plan → implementation → review orchestration
8. Ask: "Does this decision affect how I write code right now?" If no → check documentation instead

---

*Control plane for mlops-async AI agents. Last updated: Phase 6 project initialization.*
