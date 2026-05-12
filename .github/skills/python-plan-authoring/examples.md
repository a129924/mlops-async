# Python Plan Authoring Examples

Detailed examples for `python-plan-authoring`.

---

## Complete positive example: adding `validate_email()` to a utils module

**Feature request**
> Add a `validate_email(email: str) -> bool` function to the existing `src/utils/validation.py` module. It should raise `ValueError` for obviously malformed input and return `True` for valid addresses.

**Decisions supplied by the user**
- Module: `src/utils/validation.py`
- New public API: yes — `validate_email(email: str) -> bool`
- Interface changes: no existing interfaces modified
- Breaking changes: no
- New dependencies: no — use `re` from the standard library
- Error handling: raise `ValueError("Invalid email format: <value>")` for strings that are clearly not email addresses (empty, no `@`, no domain)
- Typing: fully typed with `str` parameter and `bool` return; no `Any`

**Non-goals supplied by the user**
- Will not modify the existing `validate_url()` function
- Will not add a CLI command or script
- Will not introduce an external email-validation library

---

**Resulting plan.md**

~~~markdown
# Add validate_email() to utils/validation

## Goal
Add `validate_email(email: str) -> bool` to `src/utils/validation.py` so callers can
check basic email format without importing an external library.

## Non-goals
- Will not modify the existing `validate_url()` function.
- Will not add a CLI command, script, or entry point.
- Will not introduce an external email-validation package.
- Will not implement full RFC 5322 compliance — basic structural checks only.

## Current Context
`src/utils/validation.py` already contains `validate_url(url: str) -> bool` and
`validate_phone(phone: str) -> bool`. The module imports only `re` from the standard
library. There are existing tests in `tests/test_validation.py` for the two current
validators.

## Requirements
1. `validate_email("user@example.com")` returns `True`.
2. `validate_email("notanemail")` returns `False`.
3. `validate_email("")` raises `ValueError("Invalid email format: ")`.
4. `validate_email("a@b")` returns `False` (no TLD-like suffix).
5. The function is fully annotated and passes `mypy --strict`.
6. All existing tests in `tests/test_validation.py` continue to pass.

## Decisions
- Module/package placement: `src/utils/validation.py` — added below the existing validators.
- New public API: yes — `validate_email(email: str) -> bool`.
- Interface changes: no — existing function signatures are unchanged.
- Breaking changes allowed: no.
- New dependencies: no — uses `re` from the standard library (already imported).
- Error handling strategy: raise `ValueError(f"Invalid email format: {email!r}")` when
  `email` is empty; return `False` for non-empty strings that fail the regex.
- Typing strategy: fully typed, no `Any`, `bool` return, `str` parameter.

## Public Contract / API Changes
New function added to `src/utils/validation.py`:

```python
def validate_email(email: str) -> bool:
    """Return True if email has a valid basic structure, False otherwise.

    Raises:
        ValueError: if email is an empty string.
    """
```

Backward compatibility: no existing functions or signatures are changed.

## Affected Files / Modules
Likely affected files:
- src/utils/validation.py
- tests/test_validation.py

Candidate files to inspect:
- src/utils/__init__.py  (check if validate_email needs to be re-exported)

## Implementation Steps
1. Open `src/utils/validation.py`. Import `re` is already present — no new imports needed.
2. After the existing `validate_phone()` function, add:
   ```python
   _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

   def validate_email(email: str) -> bool:
       if not email:
           raise ValueError(f"Invalid email format: {email!r}")
       return bool(_EMAIL_RE.match(email))
   ```
3. Open `src/utils/__init__.py`. If `validate_url` and `validate_phone` are re-exported,
   add `validate_email` to the same `__all__` list.
4. Open `tests/test_validation.py`. Add `TestValidateEmail` class with five test methods
   (see Test Plan).
5. Run `pytest tests/test_validation.py -v` and confirm all tests pass.
6. Run `mypy src/utils/validation.py --strict` and resolve any type errors.

## Test Plan
Test file: `tests/test_validation.py`

Test cases:
- Happy path: `validate_email("user@example.com")` returns `True`.
- Invalid input — returns False: `validate_email("notanemail")` returns `False`;
  `validate_email("a@b")` returns `False`; `validate_email("@nodomain.com")` returns `False`.
- Edge case — raises ValueError: `validate_email("")` raises `ValueError`.
- Regression: all existing `TestValidateUrl` and `TestValidatePhone` tests still pass
  after adding the new function.
- Backward compatibility: importing `from src.utils import validate_url` still works
  without modification.

## Validation Commands
```
pytest tests/test_validation.py -v
mypy src/utils/validation.py --strict
ruff check src/utils/validation.py
```

## Risks
- The compiled `_EMAIL_RE` pattern is a module-level constant; if another test patches
  `re.compile` at module load time, the regex may not be initialized correctly.
- If `validate_email` is added to `__all__` in `__init__.py`, callers that do
  `from src.utils import *` will now see the new symbol — this is intentional but
  should be noted in the PR description.

## Rollback Plan
Revert the following files via git:
- `src/utils/validation.py` — remove `_EMAIL_RE` and `validate_email`.
- `src/utils/__init__.py` — remove `validate_email` from `__all__` if it was added.
- `tests/test_validation.py` — remove `TestValidateEmail` class.

## Open Questions
None.
~~~

**Why this plan is correct**
- All 13 sections are present in order.
- `Decisions` answers all 7 required items with concrete detail.
- `Non-goals` has 4 items — exceeds the minimum of 3.
- `Implementation Steps` name specific files and specific actions at each step.
- `Test Plan` covers all 5 required categories by name.
- `Validation Commands` are explicit and executable.
- `Risks` and `Rollback Plan` name concrete items rather than placeholders.

---

## Anti-pattern: plan that triggers `needs-rework`

The following plan is missing critical sections. Each failure is explained below.

~~~markdown
# Email validation

## Goal
Add email validation to the utils module.

## Current Context
There is a utils module with some validators.

## Implementation Steps
- Refactor the validation module to support emails.
- Add tests.

## Test Plan
Add unit tests for the new function.

## Validation Commands
Use existing project validation commands from pyproject.toml / Makefile / README.
~~~

**Why each failure triggers `needs-rework`**

| Missing item | Why it matters |
| --- | --- |
| `Non-goals` absent | Scope is unbounded. An executor could add a CLI command, change `validate_url`, or pull in an external library without violating anything written in the plan. |
| `Decisions` absent | No one knows which module receives the code, what the function signature is, whether the API is public, whether breaking changes are allowed, how errors are raised, or what the typing strategy is. Executor must guess all of this. |
| `Requirements` absent | There are no measurable targets. The reviewer cannot verify whether the implementation is complete or correct. |
| `Affected Files / Modules` absent | The executor does not know which files to open, modify, or check for downstream impact. |
| `Implementation Steps` vague | "Refactor the validation module to support emails" is a wish, not an executable step. It names no file, no function, and no action boundary. |
| `Test Plan` not specific | "Add unit tests" does not name the test file, the test class, or any of the required categories (happy path, invalid input, edge case, regression, backward compatibility). |
| `Risks` absent | There is no record of what could go wrong. A reviewer cannot assess whether risks were considered. |
| `Rollback Plan` absent | If the change needs to be reverted, there is no documented list of affected files. |
| `Open Questions` absent | It is unclear whether all decisions are resolved or whether unresolved items were silently dropped. |

**Correct behavior**: return the plan to the author with a list of all missing sections before any coding begins.

---

## Stop-and-ask: insufficient context before drafting

**User request**
```
Create a plan for adding retry logic to our HTTP client.
```

**Why this is not authorable yet**

The request is missing all required decision content and Non-goals. Drafting now would
require inventing module names, API shapes, and retry strategies — all of which could
be wrong.

**What the skill should ask before drafting**

```
Before I draft the plan, I need answers to the following:

Decisions (all required):
1. Which module or package should receive the retry logic?
   (e.g., src/http/client.py, src/utils/retry.py, or a new module?)
2. What is the public API?
   (e.g., a decorator @retry(max_attempts=3), a function retry(fn, *, max_attempts),
   or a configuration option on the existing client class?)
3. Are any existing interfaces being modified?
   If yes, are breaking changes allowed?
4. Are new dependencies required?
   (e.g., tenacity, backoff, or pure stdlib with time.sleep?)
5. What is the error handling strategy?
   (e.g., retry only on requests.Timeout, on any HTTPError, or on a caller-specified
   exception list? What happens after all retries are exhausted — raise the last
   exception or return a sentinel?)
6. What is the typing strategy?
   (e.g., fully typed with generics, typed with Callable, or untyped for now?)

Non-goals (at least 3 required):
Please state at least 3 things this change will NOT do.
Examples: no circuit-breaker logic, no async support, no changes to existing
timeout configuration, no new external library.

Validation Commands:
Does the project have existing validation commands in pyproject.toml, a Makefile,
or a README that I should reference? Or should I specify explicit commands?

Implementation Steps:
Can you describe the rough steps at a file level? (e.g., "create a new
src/utils/retry.py, add a decorator, wire it into src/http/client.py")
This helps me write executable steps rather than high-level wishes.
```

**What the skill must NOT do**: draft a plan that invents a module path such as
`src/utils/retry.py`, assumes `tenacity` is available, or writes `Implementation Steps`
as "Add retry logic to the HTTP client" — because every one of those invented details
could be wrong and would need to be rewritten before coding can begin.

---

## Anti-pattern summary

| Anti-pattern | Why it fails |
| --- | --- |
| Omit `Decisions` and jump to `Implementation Steps` | Executor must guess module, API, errors, typing — every guess is a bug risk |
| Fewer than 3 `Non-goals` | Scope creep has no written boundary; reviewer cannot flag out-of-scope additions |
| `Implementation Steps` as high-level wishes | Executor cannot follow them; reviewer cannot verify them step by step |
| `Test Plan` says only "add tests" | No named test file, no required categories — coverage is unknown |
| `Risks` says "none" or is absent | Reviewers cannot assess whether risks were considered |
| `Rollback Plan` is absent or says "revert changes" | No file list means the rollback is not executable without re-reading the entire diff |
| Draft the plan before stop-and-ask conditions are resolved | Produces an invented plan that must be rewritten, not a frozen contract |
