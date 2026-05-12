# Python Plan Review Examples

Use these examples after `SKILL.md` has already narrowed the task to reviewing a
Python `*.plan.md` for executability.

---

## Approved / fully complete plan

A plan that:
- contains all 13 required sections
- Decisions section addresses all 7 required decision topics with concrete answers
- Non-goals has 3 explicit "will not" items
- Implementation Steps are numbered, each naming a specific file and action
- Test Plan names specific test case types
- Validation Commands list specific runnable commands
- Risks and Rollback Plan each have at least one concrete item
- Open Questions has no blocking entries

**Abbreviated plan (relevant sections shown):**

```markdown
## Goal
Add a CSV parser to `src/weather/parser.py` that converts raw weather station data
into `WeatherRecord` dataclass instances.

## Non-goals
- Will not support any format other than CSV.
- Will not add async I/O to the parser.
- Will not change the existing `WeatherService` public API.

## Decisions
- Module placement: `src/weather/parser.py` (new file)
- Public API: no changes to existing public surface
- Interface changes: none; the parser is an internal utility
- Breaking changes: none
- New dependencies: none (stdlib `csv` module only)
- Error-handling strategy: raise `ValueError` with a descriptive message on malformed
  rows; caller is responsible for catching
- Typing strategy: strict mypy; all functions fully annotated

## Implementation Steps
1. Create `src/weather/parser.py` with `parse_csv(path: Path) -> list[WeatherRecord]`.
2. Add `WeatherRecord` dataclass to `src/weather/models.py`.
3. Add `tests/test_parser.py` covering the cases in the Test Plan.
4. Update `src/weather/__init__.py` to export `parse_csv`.

## Test Plan
- Happy path: valid CSV with correct headers → list of `WeatherRecord` instances
- Invalid input: missing required header column → `ValueError`
- Edge case: empty CSV (headers only, no data rows) → empty list
- Error path: file not found → `FileNotFoundError` propagated to caller

## Validation Commands
pytest -v tests/test_parser.py && ruff check src/weather/parser.py && mypy src/

## Risks
- If `WeatherRecord` field names change later, CSV column mapping silently breaks.

## Rollback Plan
- Revert the feature commit and remove `src/weather/parser.py`; no migration needed
  because the parser is additive.

## Open Questions
- None.
```

**Why each section passes:**

| Section | Passes because |
|---|---|
| Goal | Single concrete outcome; names the file and type |
| Non-goals | 3 explicit "will not" items |
| Decisions | All 7 topics answered with concrete specifics |
| Public Contract | Explicitly states "no changes" |
| Affected Files | `src/weather/parser.py`, `src/weather/models.py`, `src/weather/__init__.py` named |
| Implementation Steps | 4 numbered steps; each names a file and action |
| Test Plan | 4 test case types: happy path, invalid input, edge case, error path |
| Validation Commands | `pytest`, `ruff check`, `mypy` — all specific and runnable |
| Risks | One concrete risk with a named failure mode |
| Rollback Plan | Concrete action; explains why no migration is needed |
| Open Questions | Empty; no blockers |

**Verdict:**

```yaml
verdict: approved
blocking_issues: []
```

---

## Needs-rework / multiple section failures

A plan that is missing Non-goals, has a Decisions section that is a single vague
sentence, has high-level Implementation Steps, and an empty Validation Commands section.

**Abbreviated plan (relevant sections shown):**

```markdown
## Goal
Improve the weather data ingestion pipeline.

## Current Context
We have a legacy ingestion script that is hard to maintain.

## Requirements
- The new pipeline should be faster and easier to test.

## Decisions
We will follow standard Python engineering practices and pick the right abstractions.

## Public Contract / API Changes
No significant changes expected.

## Affected Files / Modules
The ingestion module and related tests.

## Implementation Steps
1. Refactor the ingestion module.
2. Write tests for the new code.
3. Update the documentation.

## Test Plan
Add tests for the new ingestion logic.

## Validation Commands
Run the tests.

## Risks
Could be risky if something breaks.

## Rollback Plan
Undo the changes if needed.

## Open Questions
- None.
```

**What fails:**

- **Non-goals** — section is entirely absent.
- **Decisions** — one vague sentence; none of the 7 required topics are addressed.
- **Implementation Steps** — no step names a concrete file; step 1 says "Refactor the
  ingestion module" without naming the module or what to refactor; step 2 says "Write
  tests" without naming the test file.
- **Test Plan** — "Add tests for the new ingestion logic" names no test case types.
- **Validation Commands** — "Run the tests" is not a specific runnable command.
- **Risks** — "Could be risky if something breaks" is a placeholder, not a concrete risk.
- **Rollback Plan** — "Undo the changes if needed" is a placeholder, not a concrete
  rollback action.

**Verdict:**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Non-goals
    issue: Section is missing entirely.
    fix: Add a Non-goals section with ≥3 explicit "will not" statements scoping what
      this plan excludes (e.g., formats not supported, APIs not changed, platforms
      not targeted).
  - section: Decisions
    issue: The single sentence "We will follow standard Python engineering practices"
      addresses none of the 7 required decision topics.
    fix: Add explicit entries for module/package placement, public API intent,
      interface changes, breaking changes, new dependencies, error-handling strategy,
      and typing strategy.
  - section: Implementation Steps
    issue: Steps name no concrete files or components. "Refactor the ingestion module"
      and "Write tests" are high-level wishes.
    fix: Rewrite each step to name a specific file and action, e.g., "Update
      src/ingest/pipeline.py to replace the legacy loop with a generator" and "Add
      tests/test_pipeline.py covering the cases in the Test Plan."
  - section: Test Plan
    issue: '"Add tests for the new ingestion logic" names no test case types.'
    fix: List specific types such as happy path, invalid input, edge case, and error
      path; tie each to the concrete change being tested.
  - section: Validation Commands
    issue: '"Run the tests" is not a specific runnable command.'
    fix: Name exact commands such as "pytest -v tests/test_pipeline.py && ruff check
      src/ingest/" or reference a Makefile target by name.
  - section: Risks
    issue: '"Could be risky if something breaks" is a placeholder, not a concrete risk.'
    fix: Name a specific risk such as "If the generator yields records out of order,
      downstream aggregation may produce incorrect hourly averages."
  - section: Rollback Plan
    issue: '"Undo the changes if needed" is not an actionable rollback step.'
    fix: Provide a concrete action such as "Revert commit <SHA> and redeploy the
      previous release tag; no data migration is needed."
```

---

## Edge case / Decisions section partially complete

All 13 sections are present and structurally complete, but the Decisions section only
addresses 3 of the 7 required topics (module placement, public API, and new
dependencies). The remaining 4 topics are absent.

**Decisions section as authored:**

```markdown
## Decisions
- Module placement: `src/notify/sender.py` (new file)
- Public API: no changes
- New dependency: `httpx>=0.27` for async HTTP
```

**What is missing:** interface changes, breaking changes, error-handling strategy,
and typing strategy are not mentioned at all.

**Correct review behavior:**

- The section exists and 3 topics are answered — do not treat this as a missing section.
- Return `needs-rework` because the other 4 required topics are absent.
- Name every missing topic in one blocking issue for the Decisions section.
- Do not fill in the missing answers on the author's behalf.

**Verdict:**

```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: Only 3 of the 7 required decision topics are addressed. Missing topics:
      interface changes, breaking changes, error-handling strategy, typing strategy.
    fix: Add an explicit entry for each missing topic. For example, state whether
      the new module introduces any interface changes or breaking changes for callers,
      define the error-handling approach (e.g., raise HTTPError, return None, or
      propagate to caller), and specify the typing strategy (e.g., strict mypy with
      full annotations on all public functions).
```

---

## Insufficient-context / truncated plan document

A plan file that is cut off partway through, leaving several sections absent from the
visible content.

**Document as received:**

```markdown
## Goal
Add a CSV parser to `src/weather/parser.py`.

## Non-goals
- Will not support JSON.
- Will not add async I/O.
- Will not change the public API.

## Current Context
We have a legacy ingestion script at `src/legacy/ingest.py` that is hard to maintain.

## Requirements
- The parser must accept a `Path` and return `list[WeatherRecord]`.

[Document truncated at line 48]
```

**What is missing from the visible content:** Decisions, Public Contract / API Changes,
Affected Files / Modules, Implementation Steps, Test Plan, Validation Commands, Risks,
Rollback Plan, and Open Questions — 9 of 13 required sections are invisible.

**Correct review behavior:**
- Return `insufficient-context` immediately after step 2 of the Process.
- Name every section that cannot be assessed in `blocking_issues`.
- Do not attempt quality checks on the 4 visible sections.
- Do not return `needs-rework` — the author may have a complete plan; the reviewer
  simply did not receive the full document.
- Do not invent or infer what the missing sections might contain.

**Verdict:**

```yaml
verdict: insufficient-context
blocking_issues:
  - section: (document)
    issue: Plan is truncated at line 48; 9 of 13 required sections are absent from the
      visible content (Decisions, Public Contract / API Changes, Affected Files /
      Modules, Implementation Steps, Test Plan, Validation Commands, Risks, Rollback
      Plan, Open Questions).
    fix: Provide the complete *.plan.md file and re-run the review.
```

---

## Anti-pattern summary

| Anti-pattern | Why it fails |
|---|---|
| Approve a plan missing any of the 13 sections | Completeness check must pass before quality checks |
| Accept "standard Python practices" as a Decisions section | None of the 7 topics is answered |
| Accept 2 Non-goals items as "close enough" | Minimum is 3 explicit "will not" items |
| Accept "Refactor X" as an Implementation Step | No file reference means the executor must guess |
| Accept "Add tests" as a Test Plan | No specific test case types named |
| Accept "Run the tests" as a Validation Command | Not a specific runnable command |
| Ignore a question marked "BLOCKS" in Open Questions | Blocking questions prevent implementation start |
| Rewrite the plan instead of returning a verdict | Reviewer must only return the verdict block |
| Return `needs-rework` when the plan is simply truncated | The author may have a complete plan; use `insufficient-context` instead |
