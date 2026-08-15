# Resilient Request Execution Requirements

## Goal

讓既有 endpoint client 可在不改變其公開 method、value object 或 request shape 的前提下，接收 raw `Requester` 或以多個可注入 policy 包裝的 `RequestExecutor`。安全的 authenticated `GET`/`HEAD` 請求可依受限規則處理暫時性失敗，並在 classified 401 後最多 conditional refresh 一次及 replay 一次。

## Non-Goal

- 不為 `POST`、`PUT`、`PATCH`、`DELETE` 做 transient retry 或 401 replay。
- 不包裝 token endpoint；`TokenEndpointClient.request_json` 保持 raw transport route。
- 不新增 aggregate facade、DI container、package-root re-export、persistent token storage、live Viya E2E、version bump、release 或 merge。

## In-Scope

- 穩定、非 package-root 的 `mlops_async.core.request_execution` contract 與 `mlops_async.resilience` public policy/pipeline surface。
- `Requester` 維持 raw auth/header composition，並以 immutable per-attempt result 暴露 auth recovery capability；它不自行安裝 resilience policy。
- 外層 `PolicyRequestExecutor(raw, policies)` decorator、可替換 `RequestPolicy`、可注入 `RequestFailureClassifier`，以及 transport-backed default classifier。
- `UnauthorizedRecoveryPolicy`、`TransientRetryPolicy`、`TokenManager.refresh_if_current`、failure metadata、Projects/Models/Job Execution client annotations、focused tests 與 boundary documentation。

## Out-Of-Scope

- mutation retry/replay、token-endpoint retry、public root export、constructor shape 改動、endpoint-family method/value/request-contract 改寫。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、release notes、tag、release、merge、cleanup。

## ReadOnly

- `src/mlops_async/core/token_endpoint_client.py`; the raw `TokenEndpointClient.request_json` route is bypass evidence only and is not policy-wrapped.
- package root `src/mlops_async/__init__.py` 及所有既有 package-root exports。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/*`、live Viya E2E surfaces。
- `TokenEndpointClient.request_json` 的 raw transport route；只允許以 tests 證明其未經 policy chain。

## Written

- `plan/resilient-request-execution/resilient-request-execution.python.plan.md`
- `src/mlops_async/core/request_execution.py`
- `src/mlops_async/resilience/__init__.py`
- `src/mlops_async/resilience/classifier.py`
- `src/mlops_async/resilience/executor.py`
- `src/mlops_async/resilience/policies.py`

## Modify

- `analysis/resilient-request-execution/requirements.md`
- `analysis/resilient-request-execution/technical-spec.md`
- `plan/resilient-request-execution/resilient-request-execution.plan.md`
- `plan/resilient-request-execution/resilient-request-execution.spec.md`
- `plan/resilient-request-execution/resilient-request-execution.step.md`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/request_failure.py`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/transport/exceptions.py`
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/clients/projects/client.py`
- `src/mlops_async/clients/models/client.py`
- `src/mlops_async/clients/job_execution/client.py`
- `tach.toml`
- `tests/unit/core/test_request_failure.py`
- `tests/unit/core/test_request_resilience.py`
- `tests/unit/core/test_client_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/clients/projects/test_client.py`
- `tests/unit/clients/models/test_client.py`
- `tests/unit/clients/job_execution/test_job_execution_client.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`

## Deleted

- None. The previous private fixed decorator and `Client.failure_for` coupling are removed from their existing files; no repository path is deleted.

## Architecture Projection

- `tach.toml` is a required Modify path. Add exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`.
- This is the already-approved one-way architecture projection for the new resilience package. It is not a global relaxation, suppression, wildcard, exception for another module, or permission for `core` to depend on `resilience` or transport.
- The approved resilience placement is `resilience/__init__.py`, `classifier.py`, `executor.py`, and `policies.py`. Current classifier/executor code in `policies.py` alone is implementation drift; split it into the locked files rather than changing these artifacts to follow the drift.

## TestCase

- raw `Requester` performs no retry/recovery; a single custom policy and a left-to-right built-in policy chain are substitutable endpoint dependencies.
- `UnauthorizedRecoveryPolicy` performs exactly one classified authenticated GET/HEAD recovery, preserves changed/cleared-token behavior and cancellation, and re-enters the inner transient retry policy for replay.
- `TransientRetryPolicy` uses literal `match/case` GET/HEAD eligibility, retries only connection/timeout/429/502/503/504 with locked budgets, jitter/backoff, `Retry-After`, and cancellation propagation.
- invalid policy pipeline construction, `classifier -> None`, unauthenticated 401 pass-through, duplicate built-ins, token-endpoint bypass, and endpoint request-shape compatibility are proven.

## Evidence and Risk Boundary

The policy contract is mock/unit-test evidence, not proof that Viya mutations are replay-safe. The explicit human decision keeps all mutations outside the policy eligibility set. A WSL linked-worktree Git guard failure remains a disclosed environment exception; it must not be described as a fully green full-suite result.
