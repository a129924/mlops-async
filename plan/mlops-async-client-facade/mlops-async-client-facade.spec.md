---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
d1_verdict: non-trivial
---

# MlopsAsyncClient Specification

## Authoritative completion status (2026-08-13)

All acceptance validation and independent reviews are complete and approved.
The verified feature snapshot was rebuilt in an isolated Linux-native ext4
detached checkout from base `e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`; six
tracked diffs and eight topic-untracked files hash-matched before validation.
`uv sync --frozen`, full non-E2E pytest (`694 passed, 9 skipped, 1 deselected`,
94.38% coverage), Ruff, Pyright, Tach, and `git diff --check` passed. Results
remain available in
`/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
(SHA-256 `2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`);
the disposable checkout and bare cache were deleted.

Earlier pending wording is historical only. `publish` remains pending, so no
publication or release action is represented by this status.

## Implementation-review rework record (2026-08-12)

Independent main-workflow and Python-companion plan-review verdicts remain `approved`; `plan-review` is complete. The later independent implementation review is `needs-rework`, so current status is `creator-in-progress` via `needs-rework -> creator-in-progress`. Tach correction, full validation, implementation-review recheck, code review, and publish remain pending.

## Acceptance Criteria

1. Package root exports `MlopsAsyncClient` with five required keyword-only password-grant parameters.
2. Facade creates one shared runtime and exposes readonly, identity-stable `auth`, `models`, `projects`, `cas_tables`, `job_execution` clients.
3. Runtime uses concrete `InMemoryTokenStorage()`; constructor/context entry has no I/O and first auth is lazy.
4. Facade alone closes its `HttpClient`; close/context exit are idempotent; existing errors and cancellation propagate unchanged.
5. `tach.toml` is **Modify**, not Written, and its existing `mlops_async` list is exactly `mlops_async.clients`, `mlops_async.core`, `mlops_async.transport`, `mlops_async.clients.cas_tables`, `mlops_async.clients.job_execution`, `mlops_async.clients.models`, `mlops_async.clients.projects`.
6. Its existing `mlops_async.transport` list remains exactly `mlops_async.core`, `mlops_async.exceptions`; no other Tach block, global flag, exclude, interface, config or production code changes.
7. Exact config diff/shape inspection validates criteria 5–6 and `tach check` passes without cycle.
8. Existing facade/root export/tests/docs and their scoped TDD/focused/full-validation evidence are retained as user-authorized provisional/historical work; final validation, independent implementation review, independent code review and publish remain pending.
9. The root seven targets use the locked order `clients`, `core`, `transport`, `cas_tables`, `job_execution`, `models`, `projects`; facade tests cover post-close readable identity-stable properties, existing closed-transport failure from a domain requester call, and first authenticated domain-request lazy password-token flow through TokenManager/AuthProvider.

## Behavioral Scenarios

### Construction and namespaces

Given valid password-grant configuration, construction performs no I/O and all fixed namespaces share planned collaborators.

### First authenticated operation

Given a constructed facade, the first domain request uses the existing requester/auth/token/password-endpoint chain for lazy token acquisition.

### Lifecycle

Given explicit close or `async with`, repeated close only affects the owned transport and succeeds idempotently.

### Exact Tach repair

Given the root composition edge, applying the exact root seven-target list while retaining the transport exact two-target list removes the allowed graph violation without config scope drift.

## Error / Edge Cases

- Existing blank/non-string credential, invalid URL, auth, transport, response and `asyncio.CancelledError` behaviors are not rewrapped.
- Property reassignment is unavailable; repeated close is safe.
- A missing, reordered, duplicate, or extra root target; a changed transport target; or any other Tach diff fails the exact shape acceptance test and blocks publication.
- This spec is `creator-in-progress`: implementation-review `needs-rework` is being resolved without reopening the completed plan-review gate. Full non-E2E WSL validation remains pending because only the linked-worktree `.git` Windows-pointer policy guard ends nonzero.
