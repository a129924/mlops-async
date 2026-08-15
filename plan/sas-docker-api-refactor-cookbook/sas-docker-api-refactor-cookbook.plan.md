# sas-docker-api-refactor-cookbook

> **Analysis-layer routing: incomplete.** This documentation topic has no
> `analysis/sas-docker-api-refactor-cookbook/requirements.md` or
> `analysis/sas-docker-api-refactor-cookbook/technical-spec.md`. Its scope is
> locked from the completed MVP public surface, the local legacy snapshot, and
> the explicit human decisions recorded below.

## Goal / Outcome

Deliver a self-contained cookbook that lets the `sas-docker-api` refactoring
agent replace its legacy Viya HTTP helpers with the completed `mlops-async`
MVP, while preserving a clear boundary for application-owned adapters.

## Scope

- **In scope**:
  - `docs/cookbooks/sas-docker-api-refactor.md`
  - this topic plan and its matching step tracker
  - lifecycle, dependency-injection, family migration, adapter, error, and
    validation guidance for the consuming application

- **Out of scope**:
  - `src/**`, `tests/**`, `README.md`, `VERSION`, OpenAPI specifications, and
    endpoint-client contracts
  - new infrastructure endpoint families, including Model Repository Directory
  - a promise to preserve legacy FastAPI routes, response schemas, or status
    codes
  - SWAT/CAS execution and champion model execution

## Locked Decisions

- This is a documentation-only, non-stable-library topic. It makes no README,
  VERSION, release-note, or release change.
- The consuming FastAPI app creates one `MlopsAsyncClient` in its lifespan,
  exposes it through a dependency, and calls `aclose()` once at shutdown.
- The client owns token acquisition and refresh. Consumers must not retain a
  bearer token in `app.state`, construct a request URL/header, or create a
  per-route `httpx.AsyncClient` for Viya calls.
- The cookbook maps existing legacy calls to typed client operations but leaves
  FastAPI output serialization and exception-to-HTTP translation to the
  consuming application's adapter layer.
- CAS `data_source_id` and server values come from a configuration-backed
  resolver. The legacy `cas-shared-default` path construction is not copied.
- Legacy model-file routes are explicitly unsupported: `ModelDetail` does not
  expose files metadata from which an adapter can resolve a filename to a
  content identifier. They stop pending a separately approved metadata topic.
- Champion file selection, content decoding, `ChampionModelPayload` assembly,
  and all SWAT/CAS execution remain in `sas-docker-api`.

## Boundaries / Exclusions

- The creator writes only the three listed documentation and planning
  artifacts. The reviewer independently checks their accuracy. The Main Agent
  owns later worktree, publication, and PR routing.
- Existing `docs/legacy-viya-outbound-endpoints/**` documents remain historical
  endpoint evidence; they are not rewritten as a consumer guide.
- Any request to change public client behavior, add model-files metadata, or
  define target FastAPI compatibility is a separate topic.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: creator work is complete and awaits independent review;
  this topic stops before any release action.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved` or `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress` or `publish-in-progress`
  - `publish-in-progress` -> `pr-open` or `merged`
  - `pr-open` -> `needs-rework` or `merged`
  - `merged` -> terminal

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/sas-docker-api-refactor-cookbook/sas-docker-api-refactor-cookbook.plan.md` | Planning actor | Execution contract and locked decisions |
| Step tracker | `plan/sas-docker-api-refactor-cookbook/sas-docker-api-refactor-cookbook.step.md` | Creator | Completion evidence for the documentation pass |
| Cookbook | `docs/cookbooks/sas-docker-api-refactor.md` | Creator | Self-contained handoff for the consuming refactoring agent |

`README.md`, `VERSION`, `.github/**`, runtime code, and tests are intentionally
outside this executable artifact contract. Work outside these paths requires
plan realignment.

## Implementation Steps

1. Create a self-contained cookbook with the facade lifecycle and dependency
   pattern, with no secrets or target-app-specific configuration keys.
2. Map every completed legacy outbound family to its current client method and
   typed result; distinguish adapter-owned serialization from client behavior.
3. Document the configuration-backed CAS resolver, champion-content adapter
   boundary, error boundary, and the explicit model-file stop condition.
4. Add a consumer-side testing checklist and validate all new Markdown and
   changed-path scope.

## Validation / Acceptance Checks

- `git diff --check` passes.
- The new untracked Markdown files pass `git diff --no-index --check` against
  an empty file.
- The changed paths exactly match `Artifact Paths`.
- Examples use only the current `MlopsAsyncClient` public namespaces and
  methods.
- The cookbook names the app-lifespan ownership, CAS resolver, typed-value
  adapter boundary, and unsupported model-file route boundary.

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

No repository release action is required. Merge does not authorize a
`sas-docker-api` refactor, a public-library release, or any additional endpoint
work.

## Open Questions / Unresolved Items

None. The consuming repository must separately decide whether to preserve,
adapt, or retire each legacy FastAPI HTTP contract.
