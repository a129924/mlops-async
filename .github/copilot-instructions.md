# Copilot Instructions — mlops-async

This file defines decision rules for AI agents writing code in this repository.

---

## Language Requirement

**本 repo 預設以繁體中文（Traditional Chinese）撰寫下列內容：**
- repo 自有文件、註解與使用者可見訊息
- Git commit messages
- Issue descriptions and pull request content
- project-specific analysis / plan / ledger artifacts

**例外：**
- 若內容屬於 upstream / imported / shared assets，為了保留同步與可攜性，可維持原始語言
- 新增的 repo 專屬補充內容仍優先使用繁體中文

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
- 在 porting 任何 `sasctl` 或 legacy SDK API 之前，先閱讀 `analysis/api-client-porting-contract/requirements.md` 與 `analysis/api-client-porting-contract/technical-spec.md`
- 使用 `.github/skills/api-client-porting-planner/` 做 endpoint-family discovery、request contract drafts、risk classification、porting order 與 stop flags
- 只有在 planner output 或等價的 source / request contract evidence 已存在後，才可使用 `.github/skills/api-client-porting-implementer/`
- 每個 ported API 都必須先更新 `docs/migration-map.md` 的對照狀態，再更新 `docs/porting-ledger.md` 的證據內容，之後才能宣告 compatibility
- 遇到 upload/download、streaming、polling、retry、pagination expansion、global session side effects、conditional endpoint selection、unclear source behavior 或 unclear response schema 時，停止並交給人工 review

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
- **`docs/migration-map.md`**: source API 到 target async API 的集中 migration 對照表
- **`docs/porting-ledger.md`**: compatibility and evidence ledger for ported source SDK APIs

---

## When in Doubt

1. For source SDK porting, start with `analysis/api-client-porting-contract/requirements.md`
2. Use `.github/skills/api-client-porting-planner/SKILL.md` before implementation
3. Use `.github/skills/api-client-porting-implementer/SKILL.md` only after request contract evidence exists
4. Use `docs/migration-map.md` to keep source-to-target mapping and status centralized
5. Refer to `.github/skills/python-async-await/SKILL.md` for async patterns
6. Refer to `.github/skills/python-error-handling/SKILL.md` for exception design
7. Refer to `.github/skills/python-testing-pytest/SKILL.md` for test structure
8. Use `.github/agents/python-implementation-workflow.agent.md` when the task needs gated plan → implementation → review orchestration
9. Ask: "Does this decision affect how I write code right now?" If no → check documentation instead

---

## Migration Context — Source Code Reference Paths

**This section is auto-loaded by agents during porting workflows. Reference as needed, not for every request.**

### Source SDK Locations
- **sasctl SDK**: Official Viya REST API client (upstream)
- **Legacy Service Code**: `<LOCAL_LEGACY_SERVICE_CODE_PATH>` (reference implementation)
  - Use for: endpoint patterns, request/response contracts, error handling precedents
  - Note: This is source material only; do NOT copy code directly; always adapt to async-first patterns

### Migration Target
- **Target Library**: `src/mlops_async/` (this repository)
  - Async-first, fully typed, Pydantic response models
  - All APIs exposed via `src/mlops_async/__init__.py`

### When Planning a Porting Task
- Query source SDK for endpoint family (use `api-client-porting-planner`)
- Extract request contracts from sasctl or legacy service code
- Ensure target design follows async-first principles (see § Core Principles)
- Document status in `docs/migration-map.md` and `docs/porting-ledger.md`

---

*Control plane for mlops-async AI agents. Last updated: Phase 6 project initialization + migration context.*
