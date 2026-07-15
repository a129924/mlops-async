# PasswordTokenEndpointClient

## Goal / Outcome

### Analysis routing

`analysis/password-token-endpoint-client/requirements.md` 與 `analysis/password-token-endpoint-client/technical-spec.md` 是 strict analysis layer。technical spec 是 execution-facing source of truth，requirements 是 business-intent guardrail；兩者均由已核准的 human locked architecture 建立，無衝突或未解決項。

### Goal

以 capability-family package 取代平鋪 concrete client，將 client-credentials 與 password grant 收斂為 `core/token_endpoint/`，新增 internal-only `PasswordTokenEndpointClient`，並維持 auth lifecycle、既有 `TokenEndpointClient` internal import 與 client-credentials request contract。

## Scope

### In-Scope

- 建立 analysis、plan、spec、step、TDD YAML workflow artifacts。
- 建立 `token_endpoint/__init__.py`、`_shared.py`、`client_credentials.py`、`password.py`。
- 遷移 client-credentials implementation，將 `token_endpoint_client.py` 改為 compatibility shim。
- 更新 client-credentials fake-transport tests，新增 password-client fake-transport tests。
- human gate 前，以 ReadOnly 方式評估 README、VERSION、pyproject、release/PR impact。

### Out-Of-Scope

- 修改 `src/mlops_async/core/auth.py` 的 `TokenManager`、`TokenEndpointClientProtocol`、`AuthProvider` 或 lifecycle 行為。
- 新增 public `AuthClient`、package-root export、CLI、environment variable、secret persistence 或 real Viya E2E。
- OAuth refresh-token、authorization-code、Kerberos、browser login、retry、timeout、concurrency 或 transport lifecycle redesign。
- 建立 `src/mlops_async/core/auth/` package，或在未獲 human authorization 下發佈。

## Locked Decisions

- D1 verdict：`non-trivial`；原因是 capability-family refactor、new async Protocol collaborator、compatibility shim 與 request-contract regression 均須同時可驗證。
- `auth.py` 僅保留 lifecycle/orchestration；grant-specific request implementation 不得放入該檔。
- family 結構固定為 `token_endpoint/{__init__.py,_shared.py,client_credentials.py,password.py}`；不建立 `core/auth/`。
- `_shared.py` 唯一承載 `AuthTokenEndpoint`、`TokenEndpointClientError`、`TokenEndpointClientException`、credential validation、token response parser 與 expiry conversion pure logic。
- `client_credentials.py` 的 form body 仍為 `grant_type=client_credentials`、`client_id`、`client_secret`，不可改成 Basic auth。
- password request 固定 `POST /SASLogon/oauth/token`、JSON Accept、urlencoded Content-Type，Basic auth 放 client ID/secret，form 僅含 `grant_type=password`、`username`、`password`。
- PasswordTokenEndpointClient 的 username、password、client ID 一律 reject 空白或僅含空白字元；client secret 亦同，唯一例外是精確 `client_id == "sas.ec"` 時允許精確空字串 `""`。此例外的 Basic encoding input 必須是 `sas.ec:`；僅含空白字元的 secret 與所有其他 client ID 的空／空白 secret 均須拒絕。`client_credentials.py` 不得採用此例外，對 `sas.ec` 亦維持既有 non-empty secret contract。
- password refresh 忽略舊 token、再次 password obtain；不是 refresh-token grant。
- `token_endpoint_client.py` 只 re-export 現有四個 symbols，不得含 request implementation。
- 此 topic 是 stable-library release/PR assessment topic：README、VERSION、pyproject、release timing 由 human gate 決定；scoped implementation 不修改它們。

## Boundaries / Exclusions

- 僅 `Written` paths 可寫入；其他 path drift 必須回到 Plan-Creator。
- credential、Basic header、access token 不得出現在 log、exception、assertion message、fake transport record、repr 或 review evidence。
- `sas.ec` 是 PasswordTokenEndpointClient 的單一明示例外，不得泛化為任意 client ID、其他 grant、預設 client 或空 secret 寬鬆模式；例外驗證與 Basic structural check 均須保留 redaction。
- `Client` lifecycle 屬外層 composition owner；new clients 不建立、關閉或 context-manage it。
- TokenManager 的 existing refresh lock 和 error boundary 是 ReadOnly behavior。
- commit、push、PR、PR comment、release、README/VERSION/pyproject modifications 均停在 human authorization boundary；不得自動前進。

## Status / Allowed Transitions

- **Current**：`review-ready`（P1 corrective-test rework；已重新開啟 Plan Review）
- **Execution model**：Plan-Creator → Plan-Reviewer → Tester (TDD) → Implementer → Implementation Reviewer → Code Reviewer → human check。
- **Allowed transitions**：
  - `planned` → `creator-in-progress`
  - `creator-in-progress` → `review-ready`
  - `review-ready` → `reviewer-in-progress`
  - `reviewer-in-progress` → `approved` | `needs-rework`
  - `needs-rework` → `creator-in-progress`
  - `approved` → `creator-in-progress` | `publish-in-progress` (僅 human 明確授權)
  - `publish-in-progress` → `pr-open` | `merged`
  - `pr-open` → `needs-rework` | `merged`
  - `merged` → terminal
- initial implementation 的 Plan-Reviewer 未核准不得 TDD；historical TDD YAML 的 `red-tests-ready` 已完成且不得為 P1 重跑。P1 Plan-Reviewer 核准後，Implementer 先執行 corrective-test path，再修改 implementation；implementation review 未核准不得 code review；code review 後停止於 human check。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements | `analysis/password-token-endpoint-client/requirements.md` | Plan-Creator | Intent baseline |
| Technical spec | `analysis/password-token-endpoint-client/technical-spec.md` | Plan-Creator | Execution source of truth |
| Topic plan | `plan/password-token-endpoint-client/password-token-endpoint-client.plan.md` | Plan-Creator | Workflow/Python plan contract |
| Non-trivial spec | `plan/password-token-endpoint-client/password-token-endpoint-client.spec.md` | Plan-Creator | Acceptance scenarios |
| Step tracker | `plan/password-token-endpoint-client/password-token-endpoint-client.step.md` | Plan-Creator/Implementer | Six-stage gate |
| P1 TDD guard | `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` | Plan-Creator/Tester | immutable historical evidence；P1 僅 ReadOnly，禁止 rewrite 或 rerun `python-tdd-test-authoring` |
| P1 client-credentials guard | `src/mlops_async/core/token_endpoint/client_credentials.py` | Implementer | P1 ReadOnly、diff-free，維持 `require_non_empty_string()` |
| TDD verdict | `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` | Tester | Initial strict-non-empty contract 的 historical RED-test evidence；P1 ReadOnly |
| Family initializer | `src/mlops_async/core/token_endpoint/__init__.py` | Implementer | Internal package boundary |
| Shared logic | `src/mlops_async/core/token_endpoint/_shared.py` | Implementer | Common endpoint/error/parse logic |
| Client credentials | `src/mlops_async/core/token_endpoint/client_credentials.py` | Implementer | Migrated concrete client |
| Password grant | `src/mlops_async/core/token_endpoint/password.py` | Implementer | New concrete client |
| Compatibility shim | `src/mlops_async/core/token_endpoint_client.py` | Implementer | Existing import continuity |
| Regression tests | `tests/unit/core/test_token_endpoint_client.py` | Tester/Implementer | Existing grant protection |
| Password tests | `tests/unit/core/test_password_token_endpoint_client.py` | Tester/Implementer | New contract coverage |

Path drift is a plan-alignment failure. `README.md`, `VERSION`, and `pyproject.toml` are ReadOnly assessment inputs, not Written outputs.

## ReadOnly

- `AGENTS.md`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/types.py`
- `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml`（immutable historical evidence；P1 禁止 rewrite 或 rerun）
- `src/mlops_async/core/token_endpoint/client_credentials.py`（P1 diff-free；client-credentials 維持 `require_non_empty_string()`）
- `src/mlops_async/__init__.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_token_storage.py`
- `docs/api-endpoints/swagger-spec/upstream/SASLogon-openapi.yml`
- `docs/api-endpoints/swagger-spec/upstream/README.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`
- `.agents/skills/plan-creator/`
- `.agents/skills/plan-reviewer/`
- `.agents/skills/python-plan-authoring/`
- `.agents/skills/python-async-planning/`
- `.agents/skills/python-plan-review/`
- `.agents/skills/python-tdd-test-authoring/`
- `.agents/skills/python-implementation-review/`
- `.agents/skills/python-code-review/`
- `.agents/skills/plan-step-tracker/`
- `.agents/skills/workflow-artifact-contract/`
- `.agents/skills/python-implementation-workflow/`
- `README.md`
- `VERSION`
- `pyproject.toml`

## Written

- `analysis/password-token-endpoint-client/requirements.md`
- `analysis/password-token-endpoint-client/technical-spec.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.plan.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.spec.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.step.md`
- `src/mlops_async/core/token_endpoint/__init__.py`
- `src/mlops_async/core/token_endpoint/_shared.py`
- `src/mlops_async/core/token_endpoint/password.py`
- `src/mlops_async/core/token_endpoint_client.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/core/test_password_token_endpoint_client.py`

Test cache outputs such as `.coverage`, `.coverage-reports/coverage.json`, and `.pytest_cache/` are not repo-visible Written artifacts.

## Deleted

None. `src/mlops_async/core/token_endpoint_client.py` is retained as the compatibility shim.

## Stable library metadata

- **README row**：no change in this topic; human assesses whether a subsequent documentation topic is needed.
- **VERSION bump**：no bump in this topic; only human may decide a release bump.
- **timing**：release/PR/comment/commit/push consideration starts only after Code Reviewer and explicit human authorization.
- **rationale**：internal migration needs a visible release-impact decision, but no automatic stable-library modification or publication is authorized.

## Implementation Steps

Steps 1–6 are completed historical initial-implementation steps. P1 rework executes only step 7; it does not reopen TDD.

1. Historical: update `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` and create RED cases in `tests/unit/core/test_token_endpoint_client.py` and `tests/unit/core/test_password_token_endpoint_client.py`; preserve production-code-unmodified guard.
2. Create `src/mlops_async/core/token_endpoint/_shared.py` and move the endpoint enum, errors, non-empty validation, token parser, and explicit expiry conversion inputs into shared pure logic.
3. Create `src/mlops_async/core/token_endpoint/client_credentials.py` and move `TokenEndpointClient` without changing its POST, headers, form fields, refresh-as-obtain, or `AccessToken` behavior.
4. Create `src/mlops_async/core/token_endpoint/password.py` and implement the locked password-grant request, constructor validation, token parsing, and refresh-as-reobtain behavior.
5. Create `src/mlops_async/core/token_endpoint/__init__.py` as an internal boundary and replace `src/mlops_async/core/token_endpoint_client.py` with the locked four-symbol compatibility re-export.
6. Update the two target test files with credential-free fake records, run scoped and full validation, and mark the corresponding implementation steps complete in the topic `.step.md` only after those checks succeed.
7. P1 corrective-test path：在重新開啟的 Plan Review 核准後，先於 `tests/unit/core/test_password_token_endpoint_client.py` 新增並執行精確 `sas.ec` empty-secret acceptance、non-`sas.ec` empty/whitespace rejection、`sas.ec` whitespace rejection tests，並於 `tests/unit/core/test_token_endpoint_client.py` 新增並執行 `sas.ec` empty-secret strict regression；不得修改或重跑 historical TDD YAML。再修改 `src/mlops_async/core/token_endpoint/_shared.py` 與 `src/mlops_async/core/token_endpoint/password.py` 的最小 validation/Basic behavior，執行 scoped/full validation，並重新完成 Implementation Review 與 Code Review。

### P1 scope guards

- `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` 為 immutable historical evidence。P1 將它視為 ReadOnly：禁止 rewrite，亦禁止 rerun `python-tdd-test-authoring`。
- `src/mlops_async/core/token_endpoint/client_credentials.py` 在 P1 為 ReadOnly 與 diff-free。`TokenEndpointClient` 持續使用 `require_non_empty_string()`；僅 `tests/unit/core/test_token_endpoint_client.py` 可新增 strict regression。
- `sas.ec` empty-secret exception helper 僅屬 password。它只能由 `src/mlops_async/core/token_endpoint/password.py` 呼叫；P1 production diff 其餘僅限 `_shared.py` 與 `password.py`。

## Validation / Acceptance Checks

- `auth.py` and package-root exports have no diff; `token_endpoint_client.py` contains no request implementation.
- client-credentials POST/path/headers/form contract is behaviorally unchanged.
- password form contains exactly the three locked fields; client credentials only appear in Basic auth.
- PasswordTokenEndpointClient 的 username、password、client ID reject blank values; its client secret rejects blank values except exact `client_id == "sas.ec"` with `client_secret == ""`; `client_credentials.py` rejects blank secrets for every client ID; parser rejects non-object/missing/invalid fields.
- the `sas.ec` exception produces Basic input `sas.ec:` without recording or outputting the raw Basic header; every other client ID with an empty or whitespace-only secret is rejected.
- P1 corrective-test execution order is fixed: add/run `sas.ec` acceptance, non-`sas.ec` rejection, and client-credentials strict-regression cases before touching production code; historical TDD YAML is neither updated nor rerun.
- password refresh creates a second password obtain; expired token through TokenManager follows existing Protocol refresh.
- fake records and failure output contain no sensitive data.
- artifact paths are exact, step markers canonical, reviewer handoff required JSON shape.

## Reviewer Handoff

After all Implementer-owned steps are complete, submit the scoped diff and redacted validation evidence to Implementation Reviewer. Implementation Reviewer approval is required before independent Code Review; Code Reviewer approval ends automatic work at the human release/PR assessment boundary.

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

Code Reviewer approval ends automatic work. Human evaluates README, VERSION, pyproject, release impact, commit/push/PR intent and any PR comment. A human-authorized PR comment may only contain structural migration and redacted validation evidence. Any release or metadata change requires separately authorized bounded action.

## Open Questions / Unresolved Items

None.

## Non-goals

- This change will not modify `src/mlops_async/core/auth.py` or TokenManager orchestration.
- This change will not add a public AuthClient, package-root export, CLI, environment variables, or secret persistence.
- This change will not implement refresh-token, authorization-code, browser, Kerberos, retry, timeout, or concurrency policy.
- This change will not release, commit, push, open a PR, or post a PR comment without human authorization.

## Current Context

`src/mlops_async/core/token_endpoint_client.py` currently combines endpoint enum, errors, validation, parsing, expiry conversion, client-credentials behavior, and refresh-as-obtain. `src/mlops_async/core/auth.py` imports `TokenEndpointClient`, but TokenManager depends only on `TokenEndpointClientProtocol`. `Client.request_json()` is the async transport boundary and `token_request_headers()` supplies shared headers.

## Requirements

1. Preserve existing TokenEndpointClient behavior and imports after moving it to the family package.
2. Add internal PasswordTokenEndpointClient with explicit injected transport, username, password, client ID, client secret, optional endpoint.
3. Enforce password request/response contract without leaking sensitive values.
4. Keep shared logic pure and transport ownership outside concrete clients.
5. Cover request shape, PasswordTokenEndpointClient exact `sas.ec` empty-secret validation/Basic behavior, rejection of every other empty-secret pairing, client-credentials `sas.ec` empty-secret regression rejection, parsing, refresh, compatibility and TokenManager Protocol integration with fake transport tests.

## Decisions

- Async-planning status: triggered — cite trigger evidence: `TokenEndpointClient.fetch_access_token()` already directly awaits `Client.request_json()`, and this topic relocates that async I/O boundary while adding a second async concrete client.
- Module/package placement: `src/mlops_async/core/token_endpoint/` owns grant implementations/shared logic; `src/mlops_async/core/token_endpoint_client.py` is compatibility re-export only.
- New public API: no; PasswordTokenEndpointClient is internal-only with no package-root export.
- Interface changes: no; TokenEndpointClientProtocol, TokenManager, AuthProvider, and Client remain unchanged; new class structurally conforms to existing Protocol.
- Breaking changes allowed: no; old module exposes its four internal symbols and client-credentials behavior remains unchanged.
- New dependencies: no; use existing standard-library encoding/time APIs and repository types.
- Error handling strategy: credential/schema failures raise shared TokenEndpointClientError; the sole credential exception is PasswordTokenEndpointClient with `client_id == "sas.ec"` and `client_secret == ""`; client-credentials has no such exception; transport/JSON/cancellation use existing TokenManager boundary without sensitive details.
- Typing strategy: strict pyright-compatible complete annotations; use existing Client, AccessToken, JSONValue; no Any, casts, or type ignores.

### Async boundary decision

Only concrete client fetch/refresh methods await `Client.request_json()`; headers, form encoding, validation, parsing and expiry conversion stay synchronous pure logic. Auth orchestration remains unchanged.

### Resource lifecycle decision

Outer composition owner creates, injects, shares and closes Client. Family modules and shim never call `aclose()` or use transport as context manager.

### Concurrency model

Each obtain/refresh is a single sequential direct await. No new task, gather, lock, queue, worker, retry or fan-out; TokenManager refresh lock unchanged.

### Failure model

`asyncio.CancelledError` propagates. Transport/JSON failures retain existing TokenManager behavior; credential/schema failures are shared TokenEndpointClient errors. No grouped failures.

### Cancellation / timeout policy

No timeout, retry, cancellation handler, or cleanup behavior added. Caller/TokenManager owns cancellation; concrete client does not swallow cancellation or close transport.

### Validation plan

Fake transport structural records test direct-await request shape and redaction; test constructor/schema failure, second obtain refresh, compatibility import, Protocol injection, TokenManager expiry. No real network/timeout/cancellation test newly required.

### Handoff notes for the implementer

Do not change `auth.py`, `token_storage.py`, `client.py`, `headers.py`, `types.py`, package exports, README, VERSION, or pyproject. Complete Tester RED tests/YAML before production code; shim contains only re-exports.

### Async contradiction log

No async contradictions.

## Public Contract / API Changes

No public API changes. Internal addition: `PasswordTokenEndpointClient(transport: Client, *, username: str, password: str, client_id: str, client_secret: str, endpoint: AuthTokenEndpoint = AuthTokenEndpoint.OAUTH_TOKEN)`. It exposes `async fetch_access_token() -> AccessToken` and `async refresh_access_token(token: AccessToken) -> AccessToken`, structurally fulfilling existing Protocol. Old module four-symbol imports remain compatible.

## Affected Files / Modules

Likely affected files:

P1 僅可寫入的 corrective paths 是 `src/mlops_async/core/token_endpoint/_shared.py`、`src/mlops_async/core/token_endpoint/password.py`、`tests/unit/core/test_password_token_endpoint_client.py` 與 `tests/unit/core/test_token_endpoint_client.py`。historical TDD YAML 與 `client_credentials.py` 均為 ReadOnly/diff-free guard，不屬於 P1 可寫範圍。

- `analysis/password-token-endpoint-client/requirements.md`
- `analysis/password-token-endpoint-client/technical-spec.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.plan.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.spec.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.step.md`
- `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml`（historical evidence；P1 ReadOnly）
- `src/mlops_async/core/token_endpoint/__init__.py`
- `src/mlops_async/core/token_endpoint/_shared.py`
- `src/mlops_async/core/token_endpoint/client_credentials.py`
- `src/mlops_async/core/token_endpoint/password.py`
- `src/mlops_async/core/token_endpoint_client.py`
- `tests/unit/core/test_token_endpoint_client.py`（P1 新增 strict-regression case）
- `tests/unit/core/test_password_token_endpoint_client.py`（P1 新增 acceptance/rejection cases）

Candidate files to inspect:

- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/types.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_token_manager.py`
- `docs/api-endpoints/swagger-spec/upstream/SASLogon-openapi.yml`
- `README.md`
- `VERSION`
- `pyproject.toml`

## Test Plan

Test files: `tests/unit/core/test_token_endpoint_client.py`, `tests/unit/core/test_password_token_endpoint_client.py`.

- Happy path: both concrete clients return AccessToken; password POST/path/header family/Basic scheme/three-field form use redacted structural records.
- Invalid input: PasswordTokenEndpointClient rejects blank username/password/client ID and blank/whitespace-only client secret except exact `sas.ec` plus empty-string secret; client-credentials rejects blank/whitespace-only secret for every client ID; reject invalid token response shapes.
- Edge case: reserved-character form encoding; client credentials absent from password form; records/assertions expose no sensitive values.
- Regression: migrated client-credentials body/refresh-as-obtain unchanged; shim exports all legacy symbols.
- Backward compatibility: `auth.TokenEndpointClient` and existing imports remain valid; expired token through TokenManager invokes Password client Protocol refresh.

### TestCase

1. client-credentials migration emits the existing POST/path/headers/form contract.
2. compatibility shim re-exports the four legacy internal symbols and `auth.TokenEndpointClient` remains importable.
3. password obtain uses the locked endpoint, Basic auth, and exactly three form fields.
4. password reserved characters encode correctly; client credentials never appear in its form body.
5. exact `client_id == "sas.ec"` with `client_secret == ""` is accepted and uses redacted structural verification of Basic input `sas.ec:`.
6. each blank username/password/client ID is rejected; each non-`sas.ec` empty/whitespace-only client secret and `sas.ec` whitespace-only client secret is rejected without echoing a value.
7. TokenEndpointClient continues to reject `sas.ec` with an empty client secret, preserving its existing client-credentials contract.
8. invalid response payloads reject with TokenEndpointClientError.
9. password refresh emits a second password obtain rather than a refresh-token grant.
10. an expired token in TokenManager triggers the existing Protocol refresh path.
11. fake records, assertion failures, exceptions, logs, and reviewer evidence expose no sensitive values.

P1 corrective-test mapping (executed before production modification, without a new TDD YAML verdict):

12. `tests/unit/core/test_password_token_endpoint_client.py::test_password_client_accepts_sas_ec_empty_client_secret_with_redacted_basic_contract` accepts only exact `sas.ec` plus `""` and verifies the redacted Basic structural contract.
13. `tests/unit/core/test_password_token_endpoint_client.py::test_password_client_rejects_non_sas_ec_empty_or_whitespace_client_secret` rejects non-`sas.ec` empty/whitespace secrets and `sas.ec` whitespace-only secret without echoing values.
14. `tests/unit/core/test_token_endpoint_client.py::test_client_credentials_client_rejects_sas_ec_empty_client_secret` preserves strict client-credentials behavior.

## Validation Commands

```powershell
uv run pytest --no-cov tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_password_token_endpoint_client.py tests/unit/core/test_auth_contract.py tests/unit/core/test_token_manager.py
uv run ruff check src/mlops_async tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_password_token_endpoint_client.py
uv run pyright
uv run pytest
```

## Risks

- Moving symbols can break auth.py/internal imports if shim omits a symbol.
- Migration can accidentally change client-credentials form contract.
- Test fake/failure assertion can retain raw credential material.
- P1 could accidentally broaden the `sas.ec` exception to client-credentials or whitespace-only secrets; the three corrective cases must run before and after the minimal implementation change.
- Release/PR action can escape human authorization boundary.

## Rollback Plan

Revert the five planning artifacts plus listed family/shim/test paths via git. Do not modify auth.py, package-root exports, README, VERSION, or pyproject unless a separately authorized release action changed them.

## Open Questions

None.
