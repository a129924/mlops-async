# HTTP Request Value Objects — PR #57 Rework Review Log

## Intake Status

- **Topic**: `http-request-value-objects`
- **PR**: `#57`
- **Current phase**: `review-ready`
- **Purpose**: record the HUMAN-selected rework set and preserve an auditable
  exclusion boundary for independent Plan-Reviewer review.
- **TDD contract amendment**: the appended independent Plan-Reviewer `approved`
  verdict approves the Tester-only TDD verdict and RED-evidence contract. The
  canonical `approved` -> `creator-in-progress` transition now starts the
  Tester-owned TDD pass.
- **GitHub write actions**: none. No comment, reply, resolution, or review was
  submitted.

## HUMAN-Selected Threads — ADDRESS

| Thread ID | Required rework outcome |
| --- | --- |
| `PRRT_kwDOSTt_386VAaWm` | `JsonBody(None)` sends wire `b"null"`; JsonBody itself remains snapshot-only. |
| `PRRT_kwDOSTt_386VAaWr` | Direct value-object constructors enforce canonical invariants. |
| `PRRT_kwDOSTt_386VAaWs` | `EndpointPath.literal()` validates canonical static path input. |
| `PRRT_kwDOSTt_386VAaWw` | BaseUrl rejects invalid authority/hostname characters at construction. |
| `PRRT_kwDOSTt_386VAaWx` | Canonical direct execute removes implicit httpx `Accept`. |
| `PRRT_kwDOSTt_386VAaW2` | Primitive compatibility adapter preserves embedded-query parity. |

## HUMAN Locks — Do Not Reopen

- BaseUrl remains origin-only; API prefix ownership remains with `EndpointPath`.
- `HttpRequest.body: JsonBody | RawBody | None` remains the only body union.
- Headers remains the lowercase, case-insensitive, last-wins canonical model.
- Concrete endpoint-family migration remains excluded.
- Token/form and password-token migration remains excluded from JSON-domain
  Requester.
- The primitive adapter remains a compatibility adapter; this rework does not
  clean it up or replace its public surface.

## HUMAN-Excluded Threads — Not Processed

The following unresolved threads are explicitly excluded. Their comment content
was not used to define acceptance, implementation scope, or test work. No
thread is resolved as part of this planning pass.

| Thread ID | State at read-only intake | Handling |
| --- | --- | --- |
| `PRRT_kwDOSTt_386VA3PF` | active, unresolved | HUMAN-excluded; not processed. |
| `PRRT_kwDOSTt_386VA3PN` | active, unresolved | HUMAN-excluded; not processed. |
| `PRRT_kwDOSTt_386VA3PS` | active, unresolved | HUMAN-excluded; not processed. |
| `PRRT_kwDOSTt_386VAaWz` | outdated, unresolved | HUMAN-excluded; not processed and not resolved. |

All remaining threads outside the six selected IDs are HUMAN-excluded and not
processed by this rework.

## Plan-Reviewer Handoff

Plan-Reviewer must independently verify that the plan, specification, and step
ledger map one-to-one only to the six selected IDs; preserve every HUMAN lock;
exclude the four IDs above; retain non-stable-library intent; and verify the
Tester-only fixed-schema YAML verdict path, two allowed TDD test paths,
`expected_initial_status: red`, the fixed six-row mapping across exactly
`happy path`, `error/exception`, `boundary/edge`, `state/side effects`, and
`integration points`, and individual pytest RED evidence for every mapped test
name. Before test writing, the guard is `git diff --quiet HEAD -- src/`; exit
`0` covers staged and unstaged `src/` content, is recorded as
`production_code_modified: false`, and must not be made to pass with `git
reset`, `git clean`, or `git checkout`. The current status is
`creator-in-progress` under the appended independent `approved` verdict. The
Tester-owned `rework-tdd-test-authoring` pass may now begin. Production
implementation remains prohibited until separate authorization dispatches it.

**Reviewer write authorization used**: the final independent verdict is
appended below. This is consistent with this log being listed as both `Written`
and `Modify` in the topic plan; no reviewer may rewrite intake, HUMAN locks,
selected IDs, exclusions, or acceptance work.
Tester alone may create or update the separate
`http-request-value-objects.tdd-verdict.yaml` during `rework-tdd-test-authoring`;
Plan-Reviewer does not write that verdict artifact.

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
      {"comment": "PRRT_kwDOSTt_386VA3PF", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."},
      {"comment": "PRRT_kwDOSTt_386VA3PN", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."},
      {"comment": "PRRT_kwDOSTt_386VA3PS", "why": "HUMAN-excluded active unresolved thread; it remains unprocessed."},
      {"comment": "PRRT_kwDOSTt_386VAaWz", "why": "HUMAN-excluded outdated unresolved thread; no acceptance, implementation, or test work is authorized."}
    ]
  }
}
```

## Final Plan-Reviewer Verdict

- **Reviewer closure status**: `approved`

```json
{"verdict":"approved","blocking_issues":[],"copilot_feedback_triage":{"ADDRESS":[{"comment":"PRRT_kwDOSTt_386VAaWm: JsonBody(None) must send JSON null on the wire.","location":"src/mlops_async/transport/http_client.py::HttpClient.execute","why":"HUMAN-selected transport serialization defect; TestCase 1 fixes the required wire contract."},{"comment":"PRRT_kwDOSTt_386VAaWr: direct constructors must preserve named-construction invariants.","location":"src/mlops_async/core/http_request.py::BaseUrl, EndpointPath, QueryParams, Headers","why":"HUMAN-selected value-object invariant defect; TestCase 2 fixes the constructor contract."},{"comment":"PRRT_kwDOSTt_386VAaWs: static literal paths must reject non-canonical input.","location":"src/mlops_async/core/http_request.py::EndpointPath.literal","why":"HUMAN-selected path canonicalization defect; TestCase 3 prevents transport normalization."},{"comment":"PRRT_kwDOSTt_386VAaWw: BaseUrl must reject invalid authority characters.","location":"src/mlops_async/core/http_request.py::BaseUrl","why":"HUMAN-selected construction-boundary validation defect; TestCase 4 requires ValueError."},{"comment":"PRRT_kwDOSTt_386VAaWx: direct execute must not add an implicit Accept header.","location":"src/mlops_async/transport/http_client.py::HttpClient.execute","why":"HUMAN-selected wire-header defect; TestCase 5 preserves explicit accept only."},{"comment":"PRRT_kwDOSTt_386VAaW2: primitive adapters must preserve embedded-query parity.","location":"src/mlops_async/transport/http_client.py::HttpClient.request and HttpClient.request_json","why":"HUMAN-selected compatibility defect; TestCase 6 keeps both adapters on canonical execution."}],"DISCUSS":[],"SKIP":[{"comment":"PRRT_kwDOSTt_386VAaWz","why":"HUMAN-excluded outdated unresolved thread; no acceptance, implementation, or test work is authorized."},{"comment":"PRRT_kwDOSTt_386VA3PF","why":"HUMAN-excluded active unresolved thread; it remains unprocessed."},{"comment":"PRRT_kwDOSTt_386VA3PN","why":"HUMAN-excluded active unresolved thread; it remains unprocessed."},{"comment":"PRRT_kwDOSTt_386VA3PS","why":"HUMAN-excluded active unresolved thread; it remains unprocessed."}]}}
```

## Independent Implementation-Reviewer Verdict ??Rework

- **Reviewer closure status**: `approved`
- **Blocking issues**: none.
- **Evidence reviewed**: the selected R1-R6 implementation and its six mapped
  TDD contracts; the recorded validation evidence of 26 passed for the single
  focused run, 70 passed for the combined focused run, and 383 passed / 10
  skipped with 95.13% coverage for the full suite; Ruff passed; Pyright exited
  `0`.
- **Boundary retained**: this verdict neither processes nor resolves
  `PRRT_kwDOSTt_386VA3PF`, `PRRT_kwDOSTt_386VA3PN`,
  `PRRT_kwDOSTt_386VA3PS`, or `PRRT_kwDOSTt_386VAaWz`. All HUMAN locks and
  exclusions remain unchanged.
- **Workflow effect**: `rework-implementation-review` is closed. The phase
  remains `creator-in-progress`; no Code-Reviewer verdict has been recorded
  and `rework-code-review` remains pending.

## Independent Code-Reviewer Handoff ??Pending

```json
{
  "handoff": "code-review",
  "topic": "http-request-value-objects",
  "phase": "creator-in-progress",
  "precondition": {
    "rework-implementation-review": "approved",
    "rework-code-review": "pending"
  },
  "scope": {
    "address": [
      "PRRT_kwDOSTt_386VAaWm",
      "PRRT_kwDOSTt_386VAaWr",
      "PRRT_kwDOSTt_386VAaWs",
      "PRRT_kwDOSTt_386VAaWw",
      "PRRT_kwDOSTt_386VAaWx",
      "PRRT_kwDOSTt_386VAaW2"
    ],
    "skip": [
      "PRRT_kwDOSTt_386VA3PF",
      "PRRT_kwDOSTt_386VA3PN",
      "PRRT_kwDOSTt_386VA3PS",
      "PRRT_kwDOSTt_386VAaWz"
    ]
  },
  "locked_boundaries": [
    "BaseUrl remains origin-only; EndpointPath owns API prefixes.",
    "HttpRequest.body remains JsonBody | RawBody | None.",
    "Headers remains lowercase, case-insensitive, and last-wins.",
    "Concrete endpoint-family migration and token/form migration remain excluded.",
    "The primitive adapter remains a compatibility adapter."
  ],
  "required_verdict": {
    "verdict": "approved|needs-rework",
    "blocking_issues": [],
    "copilot_feedback_triage": {
      "ADDRESS": [],
      "DISCUSS": [],
      "SKIP": []
    }
  }
}
```

## R4/R6 Hardening Implementation-Reviewer Verdict (appended)

- **Reviewer closure status**: `approved`
- **Blocking issues**: none.
- **R4 evidence accepted**: C0 validation occurs before `urlsplit`; authority
  rejection is enforced through both scheme and netloc validation, preventing
  parser-permitted invalid authority/hostname input from reaching later URL
  processing.
- **R6 boundary retained**: embedded primitive-query compatibility remains
  within the existing primitive-adapter role lock; no public-surface cleanup or
  endpoint-family migration was introduced.
- **Validation evidence**: the selected-module run recorded `80 passed` with
  functional failures `0`. Its `81.94%` coverage is a partial fail-under
  result and is classified as non-functional; it does not block this approval.
- **Boundary retained**: all R1-R6 locks and HUMAN exclusions remain unchanged;
  no excluded thread was processed or resolved.
- **Workflow effect**: `rework-implementation-review` remains complete,
  `rework-code-review` remains pending, and the phase remains
  `creator-in-progress`. This record authorizes neither publication nor PR
  actions.

## Independent Code-Reviewer Handoff ??R4/R6 Hardening

```json
{"handoff":"code-review","topic":"http-request-value-objects","phase":"creator-in-progress","precondition":{"rework-implementation-review":"approved","rework-code-review":"pending"},"review_scope":{"r4":"verify C0 precedes urlsplit and authority rejection covers scheme and netloc","r6":"verify embedded primitive-query compatibility remains within the locked adapter role"},"validation":{"selected_module":"80 passed; functional failures 0","coverage":"81.94% partial fail-under; non-functional"},"boundary":{"r1_r6_locks":"unchanged","human_exclusions":"unchanged","publish":"not authorized"},"required_verdict":{"verdict":"approved|needs-rework","blocking_issues":[]}}
```

## Independent Code-Reviewer Verdict ??Rework Closure

- **Reviewer closure status**: `approved`
- **Blocking issues**: none.
- **R4 evidence accepted**: `BaseUrl` rejects raw C0 characters before
  `urlsplit` (`http_request.py:61-66`); the focused C0 regression test is at
  `test_http_request.py:152`.
- **R6 evidence accepted**: both primitive adapters reject parsed `scheme` or
  `netloc`, including mixed-case absolute URLs and `//` network paths, before
  HTTP-library build/send (`http_client.py:186-243`; focused tests at
  `test_http_client.py:800` and `:875`). Embedded-query compatibility remains
  intact.
- **Other selected evidence**: R1 preserves `JsonBody(None)` as wire
  `b"null"` (`test_http_client.py:696`); R2 direct-constructor invariants are
  covered at `test_http_request.py:73`, `:98`, and `:106`; R5 removes implicit
  `Accept` while preserving explicit input (`test_http_client.py:721`).
- **Validation evidence**: Owner WSL focused validation recorded `80 passed`
  with functional failures `0`. The command exited `1` only because focused
  coverage was `81.94%`, below the repository-wide `90%` fail-under; that
  partial-coverage result is non-blocking. Ruff is recorded as passed and
  Pyright exited `0`.
- **Non-blocking observations**: test-only `type: ignore` comments lack
  rationale text; CRLF-only `git diff --check` output is a worktree artifact,
  not a code defect.
- **Boundary retained**: R1-R6 locks remain unchanged. No work was performed
  for `PRRT_kwDOSTt_386VA3PF`, `PRRT_kwDOSTt_386VA3PN`,
  `PRRT_kwDOSTt_386VA3PS`, or `PRRT_kwDOSTt_386VAaWz`.
- **Workflow effect**: `rework-code-review` is closed and the topic is
  `review-ready`. This verdict authorizes neither publication nor GitHub PR
  actions.

```yaml
verdict: approved
blocking_issues: []
warnings:
  - test-only type: ignore comments omit rationale text
  - CRLF-only diff-check output is a non-code worktree artifact
validation:
  owner_wsl_focused: "80 passed; functional failures 0"
  focused_coverage: "81.94%; exit 1 only for partial coverage fail-under; non-blocking"
  ruff: passed
  pyright: "exit 0"
scope:
  address:
    - PRRT_kwDOSTt_386VAaWm
    - PRRT_kwDOSTt_386VAaWr
    - PRRT_kwDOSTt_386VAaWs
    - PRRT_kwDOSTt_386VAaWw
    - PRRT_kwDOSTt_386VAaWx
    - PRRT_kwDOSTt_386VAaW2
  skip:
    - PRRT_kwDOSTt_386VA3PF
    - PRRT_kwDOSTt_386VA3PN
    - PRRT_kwDOSTt_386VA3PS
    - PRRT_kwDOSTt_386VAaWz
next_gate: human authorization for any publication or GitHub PR action
```
