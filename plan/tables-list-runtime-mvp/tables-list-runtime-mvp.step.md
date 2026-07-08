---
topic: tables-list-runtime-mvp
phase: plan-authoring
created: 2026-07-07
---

# tables-list-runtime-mvp Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for implementation review.
> Update this file at: `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Open `src/mlops_async/client.py`. Add `PackageLevelClient` as the bounded composition root for this topic, wiring shared transport, auth collaborators, `Requester`, and `self.tables` without prefetching a token.
- [X] 2. Create `src/mlops_async/endpoints/__init__.py`. Export only the endpoint symbols needed for this topic and keep the module boundary narrow.
- [X] 3. Create `src/mlops_async/endpoints/tables.py`. Add `TablesClient` with a constructor that accepts only `Requester`.
- [X] 4. In `src/mlops_async/endpoints/tables.py`, implement `list_tables(project_id: str)` so it validates the input, percent-encodes reserved characters as needed, and delegates a `GET /modelRepository/projects/{project_id}/tables` request through `Requester`.
- [X] 5. In `src/mlops_async/endpoints/tables.py`, add the minimum repo-owned response boundary needed to read the required `list_tables` payload fields without introducing a broad response-model framework.
- [X] 6. Open `tests/unit/endpoints/test_tables_client.py`. Add happy-path, invalid-input, edge-case, and boundary tests proving `TablesClient` delegates through `Requester`, never builds `Authorization` headers, and never touches auth internals directly.
- [X] 7. Open `tests/unit/test_client_tables_runtime.py`. Add runtime tests proving `client.tables` wiring works, the first authenticated business request lazy-resolves a token, and the second request reuses the cached token.
- [X] 8. Reviewed `tests/unit/core/test_requester_auth_boundary.py`; no additional regression coverage was required because existing auth/header guarantees remained intact.
- [X] 9. Run bounded validation in the managed worktree: topic tests, request-contract comparison for `projects_tables_link_request_gate`, `ruff`, and `pyright`.

