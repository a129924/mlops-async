> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth: `analysis/http-request-value-objects/technical-spec.md`
> - Business-intent guardrail: `analysis/http-request-value-objects/requirements.md` (ReadOnly)
> - HUMAN rework override: only the six selected PR #57 thread IDs in this plan
>   may change the execution contract. The unselected threads in the review log
>   are excluded from all scope, steps, and acceptance work.

## Goal / Outcome

Complete a bounded rework plan for the internal JSON-domain request contract so
that the six HUMAN-selected PR #57 defects have explicit implementation and
test obligations, without reopening the previously locked architecture.

## Scope

### In-Scope

- The six selected thread mappings: JSON `null` wire preservation, direct
  value-object constructor invariants, canonical static paths, invalid BaseUrl
  authority rejection, removal of implicit httpx `Accept`, and primitive
  embedded-query compatibility parity.
- Rework changes only in `src/mlops_async/core/http_request.py`,
  `src/mlops_async/transport/http_client.py`, and their two named unit-test
  modules under the recorded independent approval.
- The six named planning artifacts, including the Tester-owned TDD verdict,
  a review-log intake, and the
  Plan-Reviewer handoff contract.

### Out-Of-Scope

- The three HUMAN-excluded active threads and the one HUMAN-excluded outdated
  unresolved thread recorded in the review log; they remain unprocessed and
  unresolved.
- Origin-only BaseUrl policy, the body union, lowercase Headers model, endpoint
  family migration, token/form migration, primitive-adapter cleanup, retry,
  timeout, auth lifecycle, response model, and public facade changes.
- README, VERSION, package-root exports, release metadata, commits, pushes, PR
  comments, or GitHub thread resolution.

### Non-Goal

- Do not add a new `json_body`/`content` construction field, XOR, implicit
  body precedence, library override semantics, or a second URL construction
  path.
- Do not migrate token/password-token/token-form callers into Requester or
  port a concrete endpoint family.
- Do not retire the primitive adapter; it remains a compatibility adapter.

## Locked Decisions

- This is an internal-only, non-stable-library rework: README and VERSION have
  no change, no release action exists, and `## Stable library metadata` is not
  applicable.
- `BaseUrl` stays origin-only (`http`/`https`, host, optional port); API
  prefixes belong to `EndpointPath`.
- `HttpRequest.body: JsonBody | RawBody | None` remains the only construction
  body union. Readonly `json_body` and `content` remain compatibility reads.
- `Headers` remains a lowercase, case-insensitive, last-wins, no-duplicate
  request model; existing merge precedence remains unchanged.
- Endpoint-family work remains a return-`EndpointPath` contract only; no
  concrete family migration occurs.
- TokenEndpointClient, password-token, and token/form remain on their raw
  primitive path and outside JSON-domain Requester.
- The primitive request surface remains a compatibility adapter. The selected
  embedded-query fix preserves existing callers; it is not cleanup or a public
  API redesign.

## Boundaries / Exclusions

- For this TDD-contract correction, Planning actor modifies only this topic
  plan, topic specification, step tracker, and review log; the technical
  specification already supplies the needed behavior contract. Creator may
  implement only the exact `Modify` paths after the recorded independent
  Plan-Reviewer approval and the separately authorized Tester TDD pass.
- The TDD verdict is an exception to Planning actor and Creator ownership:
  only Tester may create or update
  `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml`,
  and only during `rework-tdd-test-authoring`. This planning correction must
  not create that YAML artifact.
- Plan-Reviewer independently checks the six selected IDs, HUMAN locks,
  exclusions, paths, step state, and handoff JSON. Main Agent owns routing;
  neither Creator nor reviewer resolves or replies to GitHub threads.
- A change needed outside `Modify`, or an attempt to address any excluded ID,
  is plan drift and requires a new HUMAN decision.

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **TDD contract correction**: the appended independent Plan-Reviewer
  `approved` verdict approves this amended TDD contract. The canonical
  `approved` -> `creator-in-progress` transition begins the Tester-owned TDD
  pass.
- **Rework routing**: the formerly `approved` artifact received selected PR #57
  feedback, was recorded as `needs-rework`, and completed the canonical
  `needs-rework` -> `creator-in-progress` -> `review-ready` ->
  `reviewer-in-progress` -> `approved` -> `creator-in-progress` route. This
  recorded provenance does not add an `approved` -> `needs-rework` workflow
  transition.
- **Execution model**: Tester may now perform the TDD pass under the recorded
  independent approval. Production implementation, publication, merge, and
  release remain prohibited without their separate authorization.
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

Routing notes: no round cap and no release action. The immediate gate is the
Tester-owned `rework-tdd-test-authoring` pass in `creator-in-progress` under
the recorded independent Plan-Reviewer approval.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements | `analysis/http-request-value-objects/requirements.md` | Planning actor | ReadOnly business guardrail |
| Technical specification | `analysis/http-request-value-objects/technical-spec.md` | Planning actor | Rework execution constraints |
| Topic plan | `plan/http-request-value-objects/http-request-value-objects.plan.md` | Planning actor | Repo-visible rework contract |
| Topic specification | `plan/http-request-value-objects/http-request-value-objects.spec.md` | Planning actor | Six TestCase acceptance scenarios |
| Step tracker | `plan/http-request-value-objects/http-request-value-objects.step.md` | Planning actor | Preserved history plus pending rework ledger |
| Review log | `plan/http-request-value-objects/http-request-value-objects.review-log.md` | Planning actor; Plan-Reviewer may append its final verdict only | Selected/excluded thread intake and handoff |
| TDD verdict | `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml` | Tester, during `rework-tdd-test-authoring` only | Fixed machine-readable D1, mapping, and RED-evidence verdict; not created by planning |
| Value objects | `src/mlops_async/core/http_request.py` | Creator | Selected constructor, BaseUrl, EndpointPath work |
| Canonical transport and adapter | `src/mlops_async/transport/http_client.py` | Creator | Selected JSON-null, Accept, and embedded-query work |
| Value-object tests | `tests/unit/core/test_http_request.py` | Tester during TDD; Creator during implementation | Constructor/BaseUrl/EndpointPath TestCase evidence |
| Transport tests | `tests/unit/transport/test_http_client.py` | Tester during TDD; Creator during implementation | JSON-null wire, Accept, and adapter parity evidence |

### ReadOnly

- `analysis/http-request-value-objects/requirements.md`
- `src/mlops_async/core/types.py`
- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/requester.py`
- `tests/unit/core/test_client_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_request_headers.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/core/test_password_token_endpoint_client.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`
- `README.md`
- `VERSION`

### Written

- `plan/http-request-value-objects/http-request-value-objects.review-log.md`
- `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml`

### Modify

- `analysis/http-request-value-objects/technical-spec.md`
- `plan/http-request-value-objects/http-request-value-objects.plan.md`
- `plan/http-request-value-objects/http-request-value-objects.spec.md`
- `plan/http-request-value-objects/http-request-value-objects.step.md`
- `plan/http-request-value-objects/http-request-value-objects.review-log.md`
- `src/mlops_async/core/http_request.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_http_request.py`
- `tests/unit/transport/test_http_client.py`

### Deleted

None.

Artifact path notes: README, VERSION, `.github/agents/*`, and all paths not
listed in `Modify` are outside this rework. Any such path requires re-planning.
The Planning actor writes the review-log intake; a future Plan-Reviewer is
allowed to append only its final independent verdict to that same `Modify` path.
It must not rewrite the HUMAN selection, exclusions, locks, or acceptance
contract. Tester alone may write the `Written` TDD verdict path, and only in
`rework-tdd-test-authoring`; it is not a Planning actor, Creator, or reviewer
write target. During that TDD phase, the only allowed test-file writes are
`tests/unit/core/test_http_request.py` and
`tests/unit/transport/test_http_client.py`.

## Implementation Steps

0. **Rework TDD contract — after new independent plan approval only**:
   Tester must perform D1 as `{"verdict":"non-trivial","reason":"six selected PR #57 behavioral defects require new request-contract tests"}` and create
   only `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml`.
   Its top-level YAML keys, in this exact order, are
   `verdict`, `d1_verdict`, `test_mapping`, `validation_checks`, `issues`, and
   `next_step`; no alternate schema is allowed. `verdict` is one of
   `red-tests-ready`, `needs-rework`, `insufficient-context`,
   `skip_with_reason`, or `BLOCKED`; `issues` is a list and `next_step` is a
   string. `d1_verdict` has exactly
   `verdict` and `reason`; `test_mapping` entries have exactly
   `requirement_id`, `test_case_name`, and `coverage_category`; and
   `validation_checks` has the fixed keys `d1_decision`,
   `behavior_contract_source`, `requirements_mapped`,
   `public_contract_coverage`, `test_categories_present`,
   `expected_initial_status`, `production_code_modified`, and
   `red_failure_evidence`. It records `expected_initial_status: red` and
   `production_code_modified: false`. The mapping must cover exactly the six
   selected IDs and no excluded ID. Tester may write tests only in
   `tests/unit/core/test_http_request.py` and
   `tests/unit/transport/test_http_client.py`; it must not write production
   code. Before any TDD test write, Tester runs `git diff --quiet HEAD -- src/`.
   Exit `0` is required and proves the HEAD comparison covers both staged and
   unstaged content throughout `src/`; Tester then records
   `production_code_modified: false`. Do not use `git reset`, `git clean`, or
   `git checkout` to make that guard pass. After the new tests are written,
   `red_failure_evidence` must record the command, non-zero result, and each
   mapped `test_case_name` as an individual pytest RED failure from `uv run
   pytest --no-header -rN tests/unit/core/test_http_request.py
   tests/unit/transport/test_http_client.py` before Creator changes production
   code.

   The fixed `test_mapping` is exactly:

   | requirement_id | test_case_name | coverage_category |
   | --- | --- | --- |
   | `PRRT_kwDOSTt_386VAaWm` | `test_execute_serializes_json_null_as_json_literal` | `happy path` |
   | `PRRT_kwDOSTt_386VAaWr` | `test_direct_construction_matches_named_invariants` | `state/side effects` |
   | `PRRT_kwDOSTt_386VAaWs` | `test_endpoint_path_literal_rejects_noncanonical_static_paths` | `boundary/edge` |
   | `PRRT_kwDOSTt_386VAaWw` | `test_base_url_rejects_invalid_authority_characters` | `error/exception` |
   | `PRRT_kwDOSTt_386VAaWx` | `test_execute_removes_implicit_accept_but_preserves_explicit_accept` | `error/exception` |
   | `PRRT_kwDOSTt_386VAaW2` | `test_primitive_request_adapters_preserve_embedded_query` | `integration points` |

   `coverage_category` accepts only these exact five names: `happy path`,
   `error/exception`, `boundary/edge`, `state/side effects`, and `integration
   points`. The six rows above collectively cover all five categories.
1. `PRRT_kwDOSTt_386VAaWm`: in canonical transport execution, discriminate on
   `HttpRequest.body` so `JsonBody(None)` passes JSON `None` to serialization
   and emits `b"null"`; keep `JsonBody` as validation/snapshot only.
2. `PRRT_kwDOSTt_386VAaWr`: make direct and named construction of `BaseUrl`,
   `EndpointPath`, `QueryParams`, and `Headers` enforce identical validation
   and canonical storage, with no raw-field or dataclass-initializer bypass.
3. `PRRT_kwDOSTt_386VAaWs`: reject non-canonical static literals before
   `HttpRequest.url` is formed, so transport never percent-encodes or
   normalizes a literal path a second time.
4. `PRRT_kwDOSTt_386VAaWw`: reject malformed authority/hostname input during
   `BaseUrl` construction, including spaces, backslashes, and percent-encoded
   NUL, with `ValueError`.
5. `PRRT_kwDOSTt_386VAaWx`: extend hidden-httpx-default removal so absent
   canonical `accept` remains absent on direct `execute()` wire requests while
   an explicit canonical value survives.
6. `PRRT_kwDOSTt_386VAaW2`: split embedded primitive `path` query pairs into
   `EndpointPath` and `QueryParams` for both `request()` and `request_json()`,
   then delegate through canonical execution without changing the compatibility
   adapter surface.

## Validation / Acceptance Checks

### TestCase

- The six scenarios in `http-request-value-objects.spec.md` map one-to-one to
  the six selected IDs, use only the four Creator-owned source/test paths, and
  do not reference an excluded thread.
- Before implementation, the Tester-owned TDD verdict must use the fixed YAML
  schema above, state D1 `non-trivial`, set `expected_initial_status: red`,
  map exactly those six IDs using the fixed six-row mapping and only the five
  exact `coverage_category` names, and retain individual pytest RED evidence
  for every mapped `test_case_name`.
- Before TDD test writing, `git diff --quiet HEAD -- src/` must exit `0` and
  its HEAD comparison must cover staged and unstaged `src/` content; Tester
  then records `production_code_modified: false`. Only the two named test
  modules may change in that phase. Do not use `git reset`, `git clean`, or
  `git checkout` to satisfy this guard.
- Review the changed planning artifacts for exact `ReadOnly`, `Written`,
  `Modify`, and `Deleted` inventories; `requirements.md` remains unmodified.
- `git diff --check` must pass before independent review. Code/test commands
  are intentionally deferred until a separately authorized implementation pass.

## Reviewer Handoff

The appended independent Plan-Reviewer `approved` verdict covers this TDD
contract. The current canonical transition is `approved` ->
`creator-in-progress`, and Tester may begin `rework-tdd-test-authoring`.
Production implementation remains prohibited until separate implementation
authorization. The recorded reviewer verdict remains in the review log as
allowed by the `Written` and `Modify` inventory above.

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [
      {"comment": "PRRT_kwDOSTt_386VAaWm: JsonBody(None) must send JSON null on the wire.", "location": "src/mlops_async/transport/http_client.py::HttpClient.execute", "why": "HUMAN-selected transport serialization defect; TestCase 1 fixes the required wire contract."},
      {"comment": "PRRT_kwDOSTt_386VAaWr: direct constructors must preserve named-construction invariants.", "location": "src/mlops_async/core/http_request.py::BaseUrl, EndpointPath, QueryParams, Headers", "why": "HUMAN-selected value-object invariant defect; TestCase 2 fixes the constructor contract."},
      {"comment": "PRRT_kwDOSTt_386VAaWs: static literal paths must reject non-canonical input.", "location": "src/mlops_async/core/http_request.py::EndpointPath.literal", "why": "HUMAN-selected path canonicalization defect; TestCase 3 prevents transport normalization."},
      {"comment": "PRRT_kwDOSTt_386VAaWw: BaseUrl must reject invalid authority characters.", "location": "src/mlops_async/core/http_request.py::BaseUrl", "why": "HUMAN-selected construction-boundary validation defect; TestCase 4 requires ValueError."},
      {"comment": "PRRT_kwDOSTt_386VAaWx: direct execute must not add an implicit Accept header.", "location": "src/mlops_async/transport/http_client.py::HttpClient.execute", "why": "HUMAN-selected wire-header defect; TestCase 5 preserves explicit accept only."},
      {"comment": "PRRT_kwDOSTt_386VAaW2: primitive adapters must preserve embedded-query parity.", "location": "src/mlops_async/transport/http_client.py::HttpClient.request and HttpClient.request_json", "why": "HUMAN-selected compatibility defect; TestCase 6 keeps both adapters on canonical execution."}
    ],
    "DISCUSS": [],
    "SKIP": [
      {"comment": "PRRT_kwDOSTt_386VAaWz", "why": "HUMAN-excluded outdated unresolved thread; no acceptance, implementation, or test work is authorized."},
      {"comment": "PRRT_kwDOSTt_386VA3PF", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."},
      {"comment": "PRRT_kwDOSTt_386VA3PN", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."},
      {"comment": "PRRT_kwDOSTt_386VA3PS", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."}
    ]
  }
}
```

## Post-merge / release actions

None. This planning rework authorizes neither publication nor a repository
release; no `merged` -> `released` transition is declared.

## Open Questions / Unresolved Items

None. The four excluded threads deliberately remain unresolved on GitHub but
are not open questions for this rework.
