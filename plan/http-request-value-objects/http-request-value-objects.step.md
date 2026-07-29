---
topic: http-request-value-objects
phase: code-review
created: 2026-07-29
---

# http-request-value-objects — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/http-request-value-objects/http-request-value-objects.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. 建立 request value objects、JsonBody、RawBody、single body union 與 readonly compatibility properties。
- [X] 2. 實作 BaseUrl、EndpointPath literal/from-segments、QueryParams exact encoding rules。
- [X] 3. 整合 request Headers 與 header policy：保留 precedence、final lowercase last-wins/no-duplicate output。
- [X] 4. 修改 Client contract，新增 execution-first contract 與 JSON primitive compatibility adapter。
- [X] 5. 修改 Requester，只做 immutable JSON-domain composition。
- [X] 6. 修改 HttpClient，只執行 canonical URL/body，無 library default/override second semantics。
- [X] 7. 建立 value-object/body/query/endpoint contract tests。
- [X] 8. 僅更新 `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py` 與 `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`：body=None 無 Content-Type，authorization/accept 使用 lowercase canonical lookup。
- [X] 9. 更新 token/password-token tests，驗證 raw primitive non-regression 與 Requester exclusion。
- [X] 10. 以 contract/type tests 驗證 future endpoint family 回傳 EndpointPath，且不 port concrete catalog。
