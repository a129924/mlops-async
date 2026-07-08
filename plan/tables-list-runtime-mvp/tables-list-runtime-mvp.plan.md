Analysis-layer routing: **strict mode**

- Execution-facing source of truth: `analysis/tables-list-runtime-mvp/technical-spec.md`
- Business guardrail: `analysis/tables-list-runtime-mvp/requirements.md`
- Human override in effect for module placement: `src/mlops_async/client.py` and `src/mlops_async/endpoints/tables.py` are fixed target paths for this topic.

## Goal / Outcome

?梁?? `tables-list-runtime-mvp` ??repo-visible execution contract???綽? creator work ?鞈剛? bounded scope ?鞈ｆ秘?????authenticated business runtime slice??client.tables.list_tables(project_id)`??
## Scope

- **In scope**:
  - `analysis/tables-list-runtime-mvp/requirements.md`
  - `analysis/tables-list-runtime-mvp/technical-spec.md`
  - `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.plan.md`
  - `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.spec.md`
  - `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.step.md`
  - `src/mlops_async/client.py`
  - `src/mlops_async/endpoints/__init__.py`
  - `src/mlops_async/endpoints/tables.py`
  - `tests/unit/endpoints/test_tables_client.py`
  - `tests/unit/test_client_tables_runtime.py`
  - bounded regression support in `tests/unit/core/test_requester_auth_boundary.py`

- **Out of scope**:
  - `get_table`
  - `change_table_state`
  - `projects` / `models` / `jobs` runtime families
  - `AuthClient` public UX or method naming freeze
  - retry / backoff / metrics / observability
  - generic tables response framework
  - `README.md`, `VERSION`, release notes, tagging, or release workflow

## Locked Decisions

- ??topic ??**review-ready-only with no stable-library surfaces**?????踐秧 topic ??? README / VERSION / release action??- public access point ?蝞???`client.tables.list_tables(project_id)`??- `PackageLevelClient` wiring ?蝞??鞈ｆ祗 `src/mlops_async/client.py`??- `TablesClient` ?蝞??鞈ｆ祗 `src/mlops_async/endpoints/tables.py`????`client.tables` ????皝抆窈??- `TablesClient` ?????`Requester`???綜????`AuthClient`?蹍okenManager`?蹍okenStorage`?蹓? `TokenEndpointClient`??- `list_tables` request path ?蝞??勗??嚗? fixed-path MVP??GET /modelRepository/projects/{project_id}/tables`??- ?????authenticated business request ??lazy resolve token?洩PackageLevelClient.__init__` ??`__aenter__` ?????? token??- response boundary ????????秋撮??隡????湔????謍船? response model system??
## Boundaries / Exclusions

- Main Agent / Worktree-Manager ????canonical managed worktree ?梁???????creator / reviewer work ??賃祗 `../mlops-async.worktrees/agent-20260707-tables-list-runtime-mvp` ??????- Planning actor ??author topic-local analysis / plan artifacts???? `src/**` ??`tests/**`??- Creator ??賃??踐秧 plan ?謅??exact artifact paths ??寧??遴馬??- Reviewer ?????? plan verdict????綜?隤券謚倦?株??plan ?謘????implementation??- ??implementation ???秋撫摮??秤?謅 path??????豯???plan??
## Status / Allowed Transitions

- **Current**: `pr-open`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops at `merged` and does not declare a release action.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- managed worktree path ?蝞???`../mlops-async.worktrees/agent-20260707-tables-list-runtime-mvp`
- branch ?蝞???`feat/andrew/tables-list-runtime-mvp`
- create worktree gate ??????????gate ?對??????reviewer ??plan review

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business baseline | `analysis/tables-list-runtime-mvp/requirements.md` | Planning actor | Frozen business / boundary baseline |
| Technical baseline | `analysis/tables-list-runtime-mvp/technical-spec.md` | Planning actor | Execution-facing technical source of truth |
| Topic plan | `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.plan.md` | Planning actor | Repo-visible execution contract |
| Topic spec | `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.spec.md` | Planning actor | Acceptance and behavior contract |
| Step tracker | `plan/tables-list-runtime-mvp/tables-list-runtime-mvp.step.md` | Planning actor -> Creator | Completion gate mirror |
| Package-level wiring | `src/mlops_async/client.py` | Creator | `PackageLevelClient` composition root and `client.tables` exposure |
| Endpoint exports | `src/mlops_async/endpoints/__init__.py` | Creator | Endpoint namespace exports for this topic |
| Tables endpoint module | `src/mlops_async/endpoints/tables.py` | Creator | `TablesClient`, request delegation, and minimal response boundary |
| Endpoint unit tests | `tests/unit/endpoints/test_tables_client.py` | Creator | Delegation, validation, and response translation coverage |
| Runtime wiring tests | `tests/unit/test_client_tables_runtime.py` | Creator | Lazy token resolve, token reuse, and `client.tables` wiring coverage |
| Auth-boundary regression tests | `tests/unit/core/test_requester_auth_boundary.py` | Creator | Preserve auth/header boundary after tables runtime lands |

Artifact path notes:

- `README.md`: no change in this topic
- `VERSION`: no change in this topic
- `docs/**`: read-only evidence only in this topic

## Implementation Steps

1. Open `src/mlops_async/client.py`. Add `PackageLevelClient` as the bounded composition root for this topic, wiring shared transport, auth collaborators, `Requester`, and `self.tables` without prefetching a token.
2. Create `src/mlops_async/endpoints/__init__.py`. Export only the endpoint symbols needed for this topic and keep the module boundary narrow.
3. Create `src/mlops_async/endpoints/tables.py`. Add `TablesClient` with a constructor that accepts only `Requester`.
4. In `src/mlops_async/endpoints/tables.py`, implement `list_tables(project_id: str)` so it validates the input, percent-encodes reserved characters as needed, and delegates a `GET /modelRepository/projects/{project_id}/tables` request through `Requester`.
5. In `src/mlops_async/endpoints/tables.py`, add the minimum repo-owned response boundary needed to read the required `list_tables` payload fields without introducing a broad response-model framework.
6. Open `tests/unit/endpoints/test_tables_client.py`. Add happy-path, invalid-input, edge-case, and boundary tests proving `TablesClient` delegates through `Requester`, never builds `Authorization` headers, and never touches auth internals directly.
7. Open `tests/unit/test_client_tables_runtime.py`. Add runtime tests proving `client.tables` wiring works, the first authenticated business request lazy-resolves a token, and the second request reuses the cached token.
8. Open `tests/unit/core/test_requester_auth_boundary.py`. Add only the minimum regression coverage needed if new tables runtime wiring would otherwise weaken existing auth/header guarantees.
9. Run bounded validation in the managed worktree: topic tests, request-contract comparison for `projects_tables_link_request_gate`, `ruff`, and `pyright`.

## Validation / Acceptance Checks

- `client.tables.list_tables(project_id)` exists and uses the exact fixed-path baseline.
- `TablesClient` holds only `Requester`; it does not hold `AuthClient`, `TokenManager`, `TokenStorage`, or `TokenEndpointClient`.
- first authenticated business request lazy-resolves a token; later request reuses the cached token when still valid.
- no family-local `Authorization` header construction is introduced.
- no unnecessary `Content-Type` is introduced when `json_body` is absent.
- response handling stays minimal and topic-bounded.
- validation commands remain bounded to the touched topic surface.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- After merge, no repository release action is required for this topic.
- No README update, VERSION bump, release-note work, or tag creation belongs to this topic.

## Open Questions / Unresolved Items

- None. ?鈭???reviewer ?歹?蹌?`client.py` ??`endpoints/tables.py` ??module placement ????方葭?桀?????? plan rework ?????????秋祗 implementation ????皝??綜垣??
