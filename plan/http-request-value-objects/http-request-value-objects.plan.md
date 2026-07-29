> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth: `analysis/http-request-value-objects/technical-spec.md`
> - Business guardrail: `analysis/http-request-value-objects/requirements.md`

## ReadOnly

- `src/mlops_async/core/types.py`
- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/headers.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/transport/http_client.py`

## Written

- `analysis/http-request-value-objects/requirements.md`
- `analysis/http-request-value-objects/technical-spec.md`
- `plan/http-request-value-objects/http-request-value-objects.plan.md`
- `plan/http-request-value-objects/http-request-value-objects.spec.md`
- `plan/http-request-value-objects/http-request-value-objects.step.md`

## Modified

無；本次只修正 planning/analysis artifacts，不修改 implementation、tests、README、VERSION 或 release artifact。

## Modify

無 implementation modification；本次僅修正本 topic 的五份 planning/analysis artifacts。

## Deleted

無。

## Goal / Outcome

建立 internal JSON-domain request contract：`HttpRequest` 以 single body variant 與唯一
canonical URL 承載 request data；Requester immutable composition、HttpClient execution-only，
且 token/form raw primitive path 不變。

## Scope

### In-Scope

- `HttpMethod`、`BaseUrl`、`EndpointPath`、`QueryParams`、`Headers`、`JsonBody`、`RawBody`、
  `HttpRequest` 及 endpoint-family return contract。
- body union、readonly compatibility properties、lowercase last-wins headers、exact query
  encoding、EndpointPath literal/from-segments、JSON primitive adapter。
- JSON-domain Requester/HttpClient migration plan 與 regression tests。

### Out-Of-Scope

- TokenEndpointClient、password token、token/form、concrete endpoint catalog port。
- primitive adapter cleanup、retry、timeout、auth lifecycle、response model、public facade。
- README、VERSION、release、package-root export。

### Non-Goal

- 不建立 `json_body`/`content` construction fields、XOR、implicit priority 或 library override。
- 不重設 header merge precedence或建立第二套 URL/body semantics。
- 不將 token/form 納入 JSON-domain Requester。

## Locked Decisions

- internal-only/non-stable；README、VERSION、release 均 no change。
- BaseUrl origin-only：http/https、host、optional port；拒絕 path-prefix/user-info/query/fragment；
  API prefix 屬 EndpointPath。
- EndpointPath.literal() 只供 static path；from_segments() 對 raw dynamic segment encode 一次
  並拒絕 pre-encoded ID。
- QueryParams 為 ordered duplicate pairs；`str|int|float|bool|None`，empty key reject，empty
  value `key=`，None omit，bool lowercase，UTF-8 `%20` no-plus/no-sort/no-double-encode。
- Headers lowercase canonical、case-insensitive、last-wins、no duplicates；既有 merge precedence
  不變且 final output lowercase。
- `HttpRequest.body: JsonBody | RawBody | None` 是唯一 body construction variant；JsonBody
  validate/snapshot only，RawBody immutable bytes/no automatic content type；readonly
  `json_body`/`content` compatibility properties only。
- Requester immutable JSON-domain composition；HttpClient execution-only canonical URL/body。
- endpoint family 僅 return `EndpointPath` contract；無 concrete port。
- JSON primitive surface 僅 compatibility adapter，cleanup future topic。
- Token/password token/token-form 維持 raw primitive path，不進 Requester。

## Boundaries / Exclusions

- Planning actor 僅修正本 topic artifacts；Creator 只可依 Artifact Paths 實作。
- Reviewer 只做獨立 verdict；Main Agent 只在 approved 後路由。
- token modules 是明確 exclusion；發現需要改動即停止並另立 topic。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: 本 topic 的 planning、implementation 與 review ledger 均已完成；下一次狀態轉移僅在正式發布開始時由 `approved` -> `publish-in-progress`。
- **Allowed transitions**:
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes: 無 release action、無 round cap；所有 implementation steps 與 workflow stages 均已完成。未經正式發布開始，不得離開 `approved`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements | `analysis/http-request-value-objects/requirements.md` | Planning actor | Business guardrail |
| Technical spec | `analysis/http-request-value-objects/technical-spec.md` | Planning actor | Execution source of truth |
| Topic plan | `plan/http-request-value-objects/http-request-value-objects.plan.md` | Planning actor | Review-ready execution contract |
| Topic spec | `plan/http-request-value-objects/http-request-value-objects.spec.md` | Planning actor | Non-trivial acceptance contract |
| Step tracker | `plan/http-request-value-objects/http-request-value-objects.step.md` | Planning actor -> Creator | Review/implementation step status |
| Request model | `src/mlops_async/core/http_request.py` | Creator | Value objects, body union, primitive adapter |
| Shared types | `src/mlops_async/core/types.py` | Creator | Necessary HttpMethod/JSONValue integration |
| Header policy | `src/mlops_async/core/headers.py` | Creator | Preserve precedence, lowercase final output |
| Client/Requester/transport | `src/mlops_async/core/client.py`, `src/mlops_async/core/requester.py`, `src/mlops_async/transport/http_client.py` | Creator | Execution/composition boundaries |
| Tests | `tests/unit/core/test_http_request.py`, `tests/unit/core/test_client_contract.py`, `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_request_headers.py`, `tests/unit/transport/test_http_client.py` | Creator | JSON-domain contract evidence |
| JSON-domain GET request-contract tests | `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`, `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py` | Creator | 唯一重開的 narrow follow-up：GET body/header canonicalization regression evidence |
| Token regression tests | `tests/unit/core/test_token_endpoint_client.py`, `tests/unit/core/test_password_token_endpoint_client.py` | Creator | Raw primitive non-regression |

Artifact path notes: README/VERSION/.github/copilot-instructions.md no change. Any path outside this table requires re-plan.

## Implementation Steps

1. 建立 `src/mlops_async/core/http_request.py`，實作 value objects、JsonBody、RawBody、single body union 與 readonly compatibility properties。
2. 實作 BaseUrl origin-only、EndpointPath literal/from-segments、QueryParams exact encoding rules。
3. 整合 `src/mlops_async/core/headers.py` 與 request Headers：保留 merge precedence、final lowercase last-wins/no-duplicate output。
4. 修改 `src/mlops_async/core/client.py`，新增 execution-first contract 與 JSON primitive compatibility adapter。
5. 修改 `src/mlops_async/core/requester.py`，只做 immutable JSON-domain composition。
6. 修改 `src/mlops_async/transport/http_client.py`，只執行 canonical URL/body，無 library default/override second semantics。
7. 建立 value-object/body/query/endpoint contract tests。
8. 僅更新 `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py` 與 `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`，補 JSON-domain GET shape coverage：`body is None`、無 `Content-Type`，且 authorization/accept 以 canonical lowercase lookup 驗證；既有 client/requester/header/transport tests 僅為已完成 evidence，不屬於本次重開工作。
9. 更新 token/password-token tests，驗證 raw primitive non-regression 與 Requester exclusion。
10. 不 port concrete endpoint catalog；以 contract/type tests 驗證 future family 回傳 EndpointPath。

## Validation / Acceptance Checks

### TestCase

- BaseUrl origin-only rejection 與 EndpointPath API prefix。
- EndpointPath.literal static path、from_segments raw encode-once/pre-encoded ID rejection。
- Query duplicate order、empty-key reject、empty-value `key=`、None/bool/UTF-8/%20/no-plus/no-sort/no-double-encode。
- Headers lowercase/case-insensitive/last-wins/no-duplicate，且 merge precedence/final lowercase output。
- JsonBody validation/snapshot/no serialization；RawBody immutable bytes/no automatic Content-Type。
- HttpRequest body union only、readonly json_body/content compatibility、無 XOR/priority/default/override。
- Requester immutable JSON-domain composition；HttpClient canonical execution-only；primitive adapter parity。
- JSON-domain GET request-contract：body 為 `None` 時無 `Content-Type`；`authorization`／`accept` 以 lowercase canonical lookup 驗證。
- Endpoint family return-type contract only，無 concrete port。
- Token/password-token raw primitive path 與 Requester exclusion regression。

Acceptance checks: value objects 無 HTTP library/I-O、internal-only boundary 無 drift，所有驗證命令通過才可進 implementation review。

Validation commands:

```powershell
uv run pytest tests/unit/core/test_http_request.py tests/unit/core/test_client_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_request_headers.py tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_password_token_endpoint_client.py tests/unit/transport/test_http_client.py tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py
uv run ruff check src tests
uv run pyright
uv run pytest --cov=src/mlops_async --cov-report=term-missing
```

## Reviewer Handoff

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

無 README、VERSION、tag 或 release action；若 merge，Main Agent 僅能在新的 HUMAN resume 後做一般 local sync。

## Open Questions / Unresolved Items

None。下一個 gate 僅為正式發布開始時的 `approved` -> `publish-in-progress`。

## Design Background

此設計避免 URL、query、body、headers 的 cross-layer drift；本節不是 correction-parent 或 historical-truth claim。
