Analysis-layer routing: **strict mode** — both
`analysis/request-header-policy-normalization/requirements.md` and
`analysis/request-header-policy-normalization/technical-spec.md` exist. This plan
treats `analysis/request-header-policy-normalization/technical-spec.md` as the
execution-facing source of truth and uses
`analysis/request-header-policy-normalization/requirements.md` as the business
guardrail. Chat-time context is used only where it does not conflict with the
analysis layer.

## Goal / Outcome

建立 `request-header-policy-normalization` 的 repo-visible execution contract，
使 creator 能在不改 public API 的前提下，將 request-side header policy 依 family
差異集中化，並在 topic 進入 release step 時同步處理 `README.md`、`VERSION`、
`pyproject.toml`、`uv.lock` 與相關 docs。

Topic 完成後，repo 應具備：

- 單一 internal request-header policy source of truth
- 受控的 JSON domain request / auth token request family policy
- 對 family-specific `Accept` 差異的明確邊界
- 與 implementation truth 對齊的 docs / release surfaces

## Scope

- **In scope**:
  - `analysis/request-header-policy-normalization/requirements.md`
  - `analysis/request-header-policy-normalization/technical-spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`
  - `src/mlops_async/core/headers.py`
  - `src/mlops_async/core/requester.py`
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/core/test_request_headers.py`
  - `tests/unit/core/test_requester_auth_boundary.py`
  - `tests/unit/core/test_token_endpoint_client.py`
  - `tests/unit/transport/test_http_client.py`
  - `tests/unit/request_contract/header_families.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
  - `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `README.md`
  - `VERSION`
  - `pyproject.toml`
  - `uv.lock`

- **Out of scope**:
  - public-facing API redesign
  - response-side `ResponseHeaders` refactor
  - request-contract fixture JSON rewrite
  - new content/binary runtime family implementation
  - auth lifecycle / refresh / timeout / cancellation policy changes
  - workflow governance file changes

## Locked Decisions

- 本 topic 是 **stable-library-affecting topic with declared release timing**，
  但 stable effect 限於 README/docs/release metadata synchronization，不代表新增
  public API。
- `src/mlops_async/core/headers.py` 會成為 request-side policy helper surface；
  不新增通用 mutable `Headers` class。
- JSON domain request family 與 auth token request family 會共享 helper surface，
  但仍保留分開的 family semantics。
- `Requester` 保持唯一 domain request composition layer。
- `TokenEndpointClient` 保持 token endpoint collaborator。
- `HttpClient` 保持 transport-only substrate，不吸收 auth lifecycle。
- `jobExecution/jobs/state` family-specific `Accept` 與
  `models/content` content/binary 差異作為 read-only evidence；本 topic 不擴張為新
  runtime family client。
- release timing 為 `release`；版本同步與 tag/publish 不在 creator phase 執行。
- 不使用 correction/delta artifact family；不需要 `review-log`。

## Boundaries / Exclusions

- planning actor 只 author / revise repo-visible analysis / plan artifacts，不直接做
  release/publish。
- creator implementation 必須先完成 RED tests，再修改 production code。
- reviewer 必須以 locked decisions、exact artifact paths、與 analysis strict mode
  作為評估基準，不得憑推測把 topic 擴成 broader endpoint-family runtime work。
- Main Agent release flow 只在 topic merge 並進入 release step 後處理
  `VERSION`、`pyproject.toml`、`uv.lock`、`README.md` 與 tag。

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge
  path; this topic declares release work, so post-merge flow may continue to
  `released`.
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
  - `merged` -> `released`
  - `released` -> terminal

Routing notes:

- Analysis-layer strict mode applies.
- Shared-file coordination warning: `analysis/`, `plan/`, `README.md`, `docs/`,
  `VERSION`, `pyproject.toml`, and `uv.lock` are shared surfaces; any drift
  outside listed paths is a plan-alignment issue.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/request-header-policy-normalization/requirements.md` | Planning actor | Frozen business baseline and scope guardrail |
| Topic technical specification | `analysis/request-header-policy-normalization/technical-spec.md` | Planning actor | Execution-facing technical baseline |
| Topic plan | `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md` | Planning actor | Repo-visible topic plan plus Python implementation contract |
| Topic specification | `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md` | Planning actor | Acceptance and behavioral contract |
| Topic step tracker | `plan/request-header-policy-normalization/request-header-policy-normalization.step.md` | Planning actor | Completion gate mirror |
| TDD verdict artifact | `plan/request-header-policy-normalization/request-header-policy-normalization.tdd-test-authoring.yaml` | Creator | RED-test mapping and verdict evidence before production code changes |
| Request header policy surface | `src/mlops_async/core/headers.py` | Creator | Internal helper / constants source of truth for request families |
| Domain request composition | `src/mlops_async/core/requester.py` | Creator | JSON domain request family consumer |
| Token request composition | `src/mlops_async/core/token_endpoint_client.py` | Creator | Auth token request family consumer |
| Transport support | `src/mlops_async/transport/http_client.py` | Creator | Minimal transport-side alignment without auth scope creep |
| Header helper unit tests | `tests/unit/core/test_request_headers.py` | Creator | Direct proof for shared helper merge/default semantics |
| Requester regression tests | `tests/unit/core/test_requester_auth_boundary.py` | Creator | JSON domain request policy, merge order, and auth boundary proof |
| Token request regression tests | `tests/unit/core/test_token_endpoint_client.py` | Creator | Token family request policy proof |
| Transport regression tests | `tests/unit/transport/test_http_client.py` | Creator | JSON/no-JSON request behavior and transport-only scope proof |
| Request-contract family constants | `tests/unit/request_contract/header_families.py` | Creator | Shared test-only constants for repeated endpoint-family header literals |
| Job request-contract alignment | `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py` | Creator | Endpoint-local alias to the shared jobExecution/jobRequests family `Accept` constant |
| Job-state request-contract alignment | `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py` | Creator | Endpoint-local alias to the shared jobExecution/jobRequests family `Accept` constant |
| Start-job request-contract alignment | `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py` | Creator | Endpoint-local alias to the shared jobExecution/jobRequests family `Accept` constant |
| Models-content request-contract evidence | `tests/unit/request_contract/models_content_request_gate/conftest.py` | Creator | Read-only content/binary family evidence; writable only if narrow alignment is required |
| Architecture doc | `docs/ARCHITECTURE.md` | Creator | Runtime/header-family architecture narrative |
| Header boundary standard | `docs/standards/http-client-auth-boundary.md` | Creator | Request-header policy and boundary documentation |
| Project status / release note surface | `README.md` | Creator / Main Agent | Runtime summary during creator phase; release-status alignment during release |
| Release version surface | `VERSION` | Main Agent | Patch bump at release |
| Packaging version surface | `pyproject.toml` | Main Agent | Version synchronization at release |
| Lockfile version surface | `uv.lock` | Main Agent | Version synchronization evidence at release |

Artifact path notes:

- This topic **does** interact with `README.md`, `VERSION`, `pyproject.toml`,
  and `uv.lock`.
- Listed paths are an executable contract.
- If creator work drifts outside these paths, stop and realign the plan first.

## Stable library metadata

- `README row`: add one new status/release entry summarizing request-header policy
  normalization and doc alignment; no broader README restructuring.
- `VERSION bump`: patch bump.
- `timing`: `release`
- `rationale`: repo uses `README.md`, `VERSION`, `pyproject.toml`, and `uv.lock`
  as shared release surfaces; this topic must keep those surfaces aligned with the
  delivered runtime/documentation truth.
- `release-note expectation`: mention that request-header policy is now centralized
  for JSON domain and token request families, while content/binary evidence remains
  read-only input for future runtime topics.

## Implementation Steps

1. Create `analysis/request-header-policy-normalization/requirements.md` and freeze the family-aware request-header policy scope, release/doc surfaces, and non-goals.
2. Create `analysis/request-header-policy-normalization/technical-spec.md` mapping the requirements baseline to helper design, runtime call sites, TDD evidence, and release/doc alignment.
3. Create `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`, `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`, and `plan/request-header-policy-normalization/request-header-policy-normalization.step.md` so the topic has repo-visible creator/reviewer contracts before implementation starts.
4. Author helper-first tests in `tests/unit/core/test_request_headers.py`, `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_token_endpoint_client.py`, and `tests/unit/transport/test_http_client.py` that prove centralized request-header policy expectations.
5. Record the TDD verdict and requirement-to-test mapping in `plan/request-header-policy-normalization/request-header-policy-normalization.tdd-test-authoring.yaml`, explicitly preserving any pre-existing production-diff exception instead of faking a clean RED proof.
6. Update `src/mlops_async/core/headers.py` to preserve `merge_headers()` and expose internal request-header policy helpers/constants for JSON domain and auth token request families.
7. Update `src/mlops_async/core/requester.py`, `src/mlops_async/core/token_endpoint_client.py`, and `src/mlops_async/transport/http_client.py` to consume the centralized policy surface without changing public behavior.
8. Normalize repeated jobExecution/jobRequests request-contract `Accept` literals through `tests/unit/request_contract/header_families.py` plus endpoint-local aliases in the three request-gate `conftest.py` files, while leaving `models_content` evidence topic-local.
9. Update `docs/ARCHITECTURE.md`, `docs/standards/http-client-auth-boundary.md`, and `README.md` so runtime and documentation match the final implementation truth.
10. Run bounded validation for helper/runtime/request-contract coverage plus repo-wide checks, then prepare Main Agent release evidence for `VERSION`, `pyproject.toml`, and `uv.lock` without mutating release metadata during creator implementation.

## Validation / Acceptance Checks

- Both analysis artifacts exist and match this plan's scope.
- The topic plan and Python implementation contract are reviewable without guessing.
- RED tests exist before production code changes and map back to plan requirements.
- `src/mlops_async/core/headers.py` becomes the request-side policy source of truth while keeping `merge_headers()` behavior intact.
- `Requester` still injects JSON defaults correctly and still rejects managed-auth caller `Authorization`.
- `TokenEndpointClient` still sends canonical form-urlencoded token requests.
- `HttpClient` remains transport-only and does not absorb auth lifecycle logic.
- `docs/ARCHITECTURE.md`, `docs/standards/http-client-auth-boundary.md`, and `README.md` reflect final implementation truth.
- Release surfaces are explicitly accounted for and remain untouched until the proper release phase.

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

- After merge, Main Agent must verify merge truth, branch truth, worktree truth,
  release truth, and workspace truth before mutating release surfaces.
- Release action, if executed:
  - update `VERSION`
  - synchronize version in `pyproject.toml`
  - refresh `uv.lock`
  - add README status/release entry
  - create/push release commit
  - create/push annotated tag
- If release is deferred, do not partially mutate version surfaces.

## Open Questions / Unresolved Items

- None.

## Goal

集中並正規化 request-side header policy，使既有 async-capable runtime surfaces 在不變更 public API 的前提下，共享一致的 request-family header defaults / override 規則，並以 TDD 與 release/doc alignment 作為 implementation completion gate。

## Non-goals

1. 本 change 不會新增 public-facing request helper 或改變 caller signatures。
2. 本 change 不會重做 response-side `ResponseHeaders` abstraction。
3. 本 change 不會把 `models/content` 擴張成新的 runtime client implementation。
4. 本 change 不會改 auth lifecycle、refresh policy、timeout policy、或 cancellation boundary。
5. 本 change 不會以抽象化為理由重寫 request-contract fixture JSON。

## Current Context

1. `src/mlops_async/core/headers.py` 目前只有 `merge_headers()`，尚未承載 family-aware request policy。
2. `src/mlops_async/core/requester.py` 與 `src/mlops_async/transport/http_client.py` 各自維護 JSON request defaults，存在 policy duplication。
3. `src/mlops_async/core/token_endpoint_client.py` 直接 hardcode token request headers。
4. `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py` 已呈現 family-specific `Accept` evidence。
5. `tests/unit/request_contract/models_content_request_gate/conftest.py` 已呈現 content/binary family evidence，但目前不屬於 `src/**` runtime implementation surface。
6. `README.md`、`docs/ARCHITECTURE.md`、`docs/standards/http-client-auth-boundary.md` 已描述 request composition / token collaborator baseline，因此本 topic 需要同步 doc truth。

## Requirements

1. JSON domain request family 必須由單一 internal helper surface 提供 defaults，且行為與目前 runtime 一致。
2. Auth token request family 必須由單一 internal helper surface 提供 defaults，且行為與目前 runtime 一致。
3. Family-specific `Accept` override 必須仍然能以 bounded policy 表達，不需要散落 call-site hardcode。
4. Content/binary family 差異必須被保留為 read-only policy input，而不是被忽略或被強行納入本 topic runtime expansion。
5. Public API、exception semantics、與 merge order 不得回歸。
6. Docs / release surfaces 必須能與最終 implementation reality 對齊。

## Decisions

- Async-planning status: exempt — cite exemption evidence: 本 topic 僅在既有 async-capable methods 內集中同步 request-header policy，沒有新增 async boundary、resource lifecycle、concurrency model、timeout policy、或 cancellation policy；`Requester` / `HttpClient` / `TokenEndpointClient` 的 async baseline 保持不變。
- Module/package placement: `src/mlops_async/core/headers.py` 承載 request-family helper / constants；`src/mlops_async/core/requester.py`、`src/mlops_async/core/token_endpoint_client.py`、`src/mlops_async/transport/http_client.py` 消費該 policy；docs/release surfaces 依 artifact paths 更新。
- New public API: no — 不新增 public helper、class、或 package-root re-export。
- Interface changes: no — 不變更 public signatures；僅允許 internal helper call-site rewiring 與必要 docs 調整。
- Breaking changes allowed: no — 本 topic 是 normalization/refactor，不允許改變 caller-visible behavior。
- New dependencies: no — 使用既有 stdlib 與現有 project dependency set。
- Error handling strategy: 保留既有 `AuthorizationConflictException`、`TokenEndpointClientError`、`HttpClient` default-header validation 與 transport/status error semantics；不新增新的 public exception contract。
- Typing strategy: fully typed internal helpers，使用 `Mapping[str, str]`、`dict[str, str]` 與必要的 internal constants；不引入 `Any` 或 public enum。

## Public Contract / API Changes

No public API changes.

Internal-only changes may include:

- new request-header helper functions or constants in `src/mlops_async/core/headers.py`
- internal call-site rewiring in `Requester`, `TokenEndpointClient`, and `HttpClient`

Backward compatibility:

- existing caller signatures remain unchanged
- existing exception names and transport/auth boundaries remain unchanged

## Affected Files / Modules

Likely affected files:
- `analysis/request-header-policy-normalization/requirements.md`
- `analysis/request-header-policy-normalization/technical-spec.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/token_endpoint_client.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_request_headers.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/request_contract/header_families.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

Candidate files to inspect:
- `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/models_content_request_gate/conftest.py`
- `src/mlops_async/core/types.py`

## Implementation Steps

1. Create `analysis/request-header-policy-normalization/requirements.md` and freeze the family-aware request-header policy scope, release/doc surfaces, and explicit non-goals.
2. Create `analysis/request-header-policy-normalization/technical-spec.md` mapping the requirements baseline to helper design, runtime call sites, TDD evidence, and release/doc alignment.
3. Create `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`, `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`, and `plan/request-header-policy-normalization/request-header-policy-normalization.step.md` so the topic has repo-visible creator/reviewer contracts before implementation starts.
4. Add RED tests to `tests/unit/core/test_requester_auth_boundary.py` for centralized JSON domain request defaults, merge ordering, and managed-auth collision regression.
5. Add RED tests to `tests/unit/core/test_token_endpoint_client.py` for centralized token request defaults while preserving form-urlencoded behavior.
6. Add RED tests to `tests/unit/transport/test_http_client.py` for shared JSON-domain policy consumption without changing no-json-body and per-request override behavior.
7. Record the RED-test verdict and requirement mapping in `plan/request-header-policy-normalization/request-header-policy-normalization.tdd-test-authoring.yaml` before changing any production code.
8. Update `src/mlops_async/core/headers.py` to keep `merge_headers()` and add internal request-header policy helpers/constants for JSON domain and auth token request families.
9. Update `src/mlops_async/core/requester.py`, `src/mlops_async/core/token_endpoint_client.py`, and `src/mlops_async/transport/http_client.py` to consume the centralized policy surface without changing public behavior.
10. Update `docs/ARCHITECTURE.md`, `docs/standards/http-client-auth-boundary.md`, and `README.md`, then run bounded validation plus full-suite verification and prepare release-surface follow-up evidence for `VERSION`, `pyproject.toml`, and `uv.lock`.

## Test Plan

Test files:

- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/transport/test_http_client.py`

Test cases:

- Happy path:
  - `Requester` 透過 centralized helper 仍產生 `Accept: application/json`
  - `TokenEndpointClient` 透過 centralized helper 仍產生 canonical token headers
- Invalid input:
  - managed auth 啟用時 caller `Authorization` 仍被拒絕
  - token request family 不接受被 JSON defaults 污染的錯誤 header 組合
- Edge case:
  - `json_body is None` 時不自動補 `Content-Type`
  - per-request override 與 default header 共存時順序維持不變
- Regression:
  - `merge_headers()` case-insensitive merge behavior 不回歸
  - `HttpClient` transport-only behavior 不回歸
- Backward compatibility:
  - full-suite `uv run pytest tests/ -q` 維持綠燈
  - docs / README 描述與既有 runtime semantics 一致

## Validation Commands

```bash
uv run pytest tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_endpoint_client.py tests/unit/transport/test_http_client.py
uv run pytest tests/unit/request_contract/job_execution_jobs_state_request_gate tests/unit/request_contract/models_content_request_gate
uv run ruff check src tests
uv run pyright
uv run pytest tests/ -q
```

## Risks

1. 若 `Requester` 與 `HttpClient` 的 JSON defaults 共用方式設計不當，可能把 auth 或 transport concerns 混進錯的層。
2. 若 helper naming 過度抽象，reviewer 仍需回頭讀 call sites 才能理解 family 差異。
3. 若 docs / README / release surfaces 未同步，topic 會留下 current truth drift。

## Rollback Plan

- Revert topic artifacts and implementation paths via git:
  - `analysis/request-header-policy-normalization/requirements.md`
  - `analysis/request-header-policy-normalization/technical-spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`
  - `src/mlops_async/core/headers.py`
  - `src/mlops_async/core/requester.py`
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/core/test_requester_auth_boundary.py`
  - `tests/unit/core/test_token_endpoint_client.py`
  - `tests/unit/transport/test_http_client.py`
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `README.md`
- If release metadata was already changed later in the workflow, revert `VERSION`,
  `pyproject.toml`, and `uv.lock` as one release-surface unit.

## Open Questions

None.

## In-Scope

- `analysis/request-header-policy-normalization/**`
- `plan/request-header-policy-normalization/**`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/token_endpoint_client.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_request_headers.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/request_contract/header_families.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Out-Of-Scope

- public API redesign
- response header abstraction refactor
- request-contract fixture rewrites
- new content/binary runtime client implementation
- auth lifecycle / timeout / cancellation redesign

## ReadOnly

- `AGENTS.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`
- `tests/unit/request_contract/models_content_request_gate/conftest.py`
- `tests/unit/request_contract/**/fixtures/*.json`

## Written

- `analysis/request-header-policy-normalization/requirements.md`
- `analysis/request-header-policy-normalization/technical-spec.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`
- `plan/request-header-policy-normalization/request-header-policy-normalization.tdd-test-authoring.yaml`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/token_endpoint_client.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_request_headers.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/request_contract/header_families.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Deleted

- none by default

## TestCase

1. `Requester` 仍以 centralized helper 產生 JSON domain defaults，且 merge order 不變。
2. `TokenEndpointClient` 仍以 centralized helper 產生 canonical token headers。
3. `HttpClient` 在無 `json_body` 時不自動補 `Content-Type`。
4. managed auth 啟用時 caller `Authorization` 仍被拒絕。
5. repo-wide validation 維持綠燈，且 docs / release surfaces 能與 implementation truth 對齊。
