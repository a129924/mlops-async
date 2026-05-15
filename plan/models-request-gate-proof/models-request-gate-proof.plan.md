> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/models-request-gate-proof/technical-spec.md`
> - Business guardrail:
>   `analysis/models-request-gate-proof/requirements.md`
> - Global porting governance remains an upstream constraint set through
>   `analysis/api-client-porting-contract/requirements.md` and
>   `analysis/api-client-porting-contract/technical-spec.md`.
> - No human `override` instruction changes that priority rule for this topic.

## Goal / Outcome

- Produce the first repo-visible execution contract for `models-request-gate-proof` so later creator
  work can freeze the business baseline and topic-local technical spec for the first
  `model-repository/models` request-gate proof without guessing scope, re-opening the client-mode
  decision, or widening into production implementation.

## Scope

- **In scope**:
  - `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
  - `plan/models-request-gate-proof/models-request-gate-proof.step.md`
  - `analysis/models-request-gate-proof/requirements.md`
  - `analysis/models-request-gate-proof/technical-spec.md`

- **Out of scope**:
  - `src/mlops_async/**` production implementation
  - `tests/**` request tests, fixture tests, or implementation tests
  - concrete `HttpClient` implementation
  - fake client implementation
  - intercepted capture runs, request-flow fixtures, and mock-response answer sets
  - `docs/migration-map.md` and `docs/porting-ledger.md` updates
  - `README.md`, `VERSION`, release-note work, or repository release actions

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**. Stable-library intent is
  explicitly absent.
- The topic name is fixed as `models-request-gate-proof`.
- The family boundary is fixed as the read-only `model-repository/models` family.
- The initial source API set is fixed as:
  - `sasctl.ModelRepository.list_models`
  - `sasctl.ModelRepository.get_model`
  - `legacy src/sas_api/utils/_api/get_model.py::get_all_models`
  - `legacy src/sas_api/utils/_api/get_model.py::get_one_model`
- The business framing is fixed as **request-gate proof**, not full first port.
- The primary actor is fixed as `porting_maintainer`.
- The success signal is fixed as `workflow_proof`.
- The completion boundary is fixed as:
  - `list_models` and `get_model` both reach request-contract extraction
  - `list_models` and `get_model` both reach request-contract tests
- Response / error / ledger completeness are explicitly outside this topic's completion boundary.
- `auth` remains out of scope for this topic.
- Client mode is fixed as `mock_first_no_concrete_client`; a concrete `HttpClient` implementation
  is not a blocker for this topic's planning and request-gate proof alignment.
- Environment bootstrap strategy is fixed as `defer_until_execution_topic`; this planning topic must
  not add dev dependencies, run `uv add --dev ...`, or treat `uv sync` as a completion gate.
- The next execution topic must record environment bootstrap explicitly before any capture or request
  test work begins.
- The future raw request-evidence layer is expected to live under
  `tests/unit/request_contract/models_request_gate/fixtures/`.
- The future mock/interception code layer is expected to live under
  `tests/unit/request_contract/models_request_gate/`.
- The managed worktree boundary for the current branch is fixed as `planning_only`; creator work
  under this topic must not silently drift into implementation.

## Boundaries / Exclusions

- Planning actor owns this topic plan and the topic-local analysis artifacts only.
- Creator work for this topic is limited to repo-visible planning/analysis artifacts in the exact
  paths listed below.
- Reviewer owns the independent verdict and must not author topic content while reviewing.
- Main Agent owns worktree lifecycle, publish routing, PR flow, merge follow-up, and any later
  transition into planner/implementer execution.
- The immediate next action for this topic is a light review of the existing planning artifacts; this
  topic does not directly transition into request capture, fixture authoring, or request-test
  execution.
- If work expands into request capture, fixtures, request tests, production code, or migration
  evidence, stop and open a follow-up implementation-facing topic or amend this plan first.
- If work expands into dependency installation, `pyproject.toml`, or `uv.lock`, stop and move that
  decision to the execution-facing topic instead of widening this planning topic.
- The global porting governance files remain authoritative inputs, but this topic does not rewrite
  them unless a later human-approved plan amendment explicitly adds those paths.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this
  topic stops at `merged` and does not declare a release action.
- **Step-tracker alignment**:
  `plan/models-request-gate-proof/models-request-gate-proof.step.md` 的
  `## Implementation Steps` 已完成，因此本輪 creator pass 可前進到 `review-ready`。
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

- The current managed worktree path for this planning pass is
  `../mlops-async.worktrees/spec-20260515-models-request-gate-proof`.
- This topic stops at human review after the repo-visible plan is authored; any transition into
  creator execution requires an explicit human resume message.
- The recommended route after review is:
  1. open a separate execution-facing topic for request-only mock/interception work;
  2. freeze planner handoff, bootstrap rules, and artifact paths inside that follow-up topic;
  3. then choose the execution orchestrator for that follow-up topic.
- `api-client-porting-implementer` is not the direct next step from this planning topic. Use it only
  after the follow-up execution topic has planner-ready handoff, request-contract evidence, and
  explicit authorization to modify `tests/**`.
- If an execution orchestrator is needed for the follow-up request-only topic,
  `python-implementation-workflow` is the preferred entry because it can respect the narrower
  request-only boundary without assuming immediate migration-map or ledger work.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical status model and required topic-plan sections |
| Global porting requirements | `analysis/api-client-porting-contract/requirements.md` | Planning actor | Business/workflow guardrail until a topic-local requirements file exists |
| Global porting technical spec | `analysis/api-client-porting-contract/technical-spec.md` | Planning actor | Global contract mapping and stop-condition reference for this topic |
| Topic plan | `plan/models-request-gate-proof/models-request-gate-proof.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/models-request-gate-proof/models-request-gate-proof.step.md` | Creator | Machine-readable completion gate for this topic's implementation steps |
| Topic requirements baseline | `analysis/models-request-gate-proof/requirements.md` | Creator | Repo-visible business baseline for the request-gate-proof topic |
| Topic technical spec | `analysis/models-request-gate-proof/technical-spec.md` | Creator | Repo-visible technical translation for the request-gate-proof topic |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- `pyproject.toml`: no change in this topic.
- `uv.lock`: no change in this topic.
- If later work drifts outside these exact paths, stop and repair this topic plan before
  continuing.

## Implementation Steps

1. Create `analysis/models-request-gate-proof/requirements.md` and freeze the business baseline for
   the first request-gate proof topic using the already-locked decisions in this plan.
2. Create `analysis/models-request-gate-proof/technical-spec.md` and map the topic-local business
   baseline to exact artifact scope, validation expectations, and stop boundaries without widening
   into implementation.
3. Create `plan/models-request-gate-proof/models-request-gate-proof.step.md` so completion reads
   only from the topic's implementation steps.
4. Keep `plan/models-request-gate-proof/models-request-gate-proof.plan.md` aligned with the
   topic-local analysis artifacts if reviewer feedback requires scope repair before publish.

## Validation / Acceptance Checks

- `plan/models-request-gate-proof/models-request-gate-proof.plan.md` exists and uses the canonical
  topic-plan sections in the workflow contract order.
- The plan explicitly enters strict mode against:
  - `analysis/models-request-gate-proof/requirements.md`
  - `analysis/models-request-gate-proof/technical-spec.md`
- `plan/models-request-gate-proof/models-request-gate-proof.plan.md` keeps stable-library intent
  explicitly absent.
- `Artifact Paths` are exact, repo-visible, and bounded to planning/analysis outputs only.
- The topic plan does not authorize `src/mlops_async/**`, `tests/**`, `docs/migration-map.md`, or
  `docs/porting-ledger.md` changes.
- The topic plan does not authorize `pyproject.toml` or `uv.lock` changes.
- `Reviewer Handoff` is a single machine-consumable JSON object.
- Later creator work should be accepted only if it adds:
  - `analysis/models-request-gate-proof/requirements.md`
  - `analysis/models-request-gate-proof/technical-spec.md`
  - `plan/models-request-gate-proof/models-request-gate-proof.step.md`
  and stays inside the exact artifact paths declared above.

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

- After merge, Main Agent may perform the normal local sync flow only after an explicit human
  resume message.
- No README update, VERSION bump, release-note work, or repository release action belongs to this
  topic.
- This topic is terminal at `merged`.

## Open Questions / Unresolved Items

- None.
