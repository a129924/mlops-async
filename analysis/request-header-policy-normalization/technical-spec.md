# request-header-policy-normalization technical specification

## Status

- `FROZEN`

## Source Baseline Summary

- technical spec 以
  `analysis/request-header-policy-normalization/requirements.md` 為 business baseline
- read-only architecture / behavior baseline：
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `README.md`
  - `src/mlops_async/core/headers.py`
  - `src/mlops_async/core/requester.py`
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
  - `tests/unit/request_contract/models_content_request_gate/conftest.py`

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 JSON domain request baseline | 在 `src/mlops_async/core/headers.py` 建立 JSON domain request helper / constants，並讓 `Requester` / `HttpClient` 使用同一 policy source | existing `merge_headers`, `Requester`, `HttpClient` | 中；需避免 merge order regression | feasible |
| R2 auth token request baseline | 在 `src/mlops_async/core/headers.py` 明確提供 token request family policy，`TokenEndpointClient` 改為消費該 policy | existing `TokenEndpointClient` | 低到中；邏輯集中但不應改變 payload | feasible |
| R3 family-specific Accept override | policy surface 保留 family-specific `Accept` 表達能力；先以 read-only evidence 記錄 `jobExecution/jobs/state` 差異，必要時只補 helper hook，不在本 topic 導入新 runtime client | request-contract harness evidence | 中；需避免 scope creep | feasible |
| R4 content/binary evidence only | 將 `models/content` harness header 差異記錄在 docs/plan/analysis，作為未來 family 輸入，不修改 `src/**` 去消費它 | request-contract harness evidence | 低；主要是 planning/documentation discipline | feasible |
| R5 unchanged public/error contract | helper 設計維持 internal-only；沿用既有 exception boundaries 與 signatures | existing runtime/tests | 中；需靠 regression tests 守住 | feasible |
| R6 release/docs synchronization | 將 `docs/ARCHITECTURE.md`、`docs/standards/http-client-auth-boundary.md`、`README.md` 與 shared release surfaces 納入 artifact plan；release timing 放在 Phase 10 | existing release workflow surfaces | 中；涉及 Main Agent release follow-up | feasible |

## Technical Realization

### Workstream 1: Topic artifacts and review gates

- author：
  - `analysis/request-header-policy-normalization/requirements.md`
  - `analysis/request-header-policy-normalization/technical-spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`
  - `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`
- use `plan-reviewer` 與 `python-plan-review` 檢查：
  - topic-plan contract
  - Python 13-section implementation contract
  - release/doc surfaces 是否被顯式列入

### Workstream 2: Request-header policy surface

- 擴充 `src/mlops_async/core/headers.py` 成為 request-side policy source of truth。
- 預期最小能力：
  - 保留既有 `merge_headers(*mappings)` 行為
  - 新增 JSON domain request defaults helper
  - 新增 auth token request defaults helper
  - 新增 family label / helper naming，讓 call sites 無需直接散寫 core literals
- design constraints：
  - 不新增 mutable `Headers` class
  - 不把 response-side `ResponseHeaders` 混進 request-side abstraction
  - helper 只負責 defaults/policy，不接管 transport I/O 或 token lifecycle

### Workstream 3: Runtime call-site normalization

- `src/mlops_async/core/requester.py`
  - 改用 policy helper 取得 JSON domain request defaults
  - 保留 `AuthorizationConflictException`、merge order、`json_body` 才補 content type
- `src/mlops_async/core/token_endpoint_client.py`
  - 改用 policy helper 取得 token family headers
  - 保留 client-credentials form body 與 response parsing
- `src/mlops_async/transport/http_client.py`
  - 僅做最小調整，讓 JSON domain policy 與 `Requester` 共用 source of truth
  - 不吸收 auth logic，不處理 family-specific request-contract semantics

### Workstream 4: TDD-first regression proof

- RED test authoring 先於 production changes：
  - `tests/unit/core/test_requester_auth_boundary.py`
  - `tests/unit/core/test_token_endpoint_client.py`
  - `tests/unit/transport/test_http_client.py`
- test design focus：
  - JSON domain request defaults from shared helper
  - token request family remains isolated
  - merge order / override behavior preserved
  - non-JSON / no-json-body path does not regress
- request-contract harnesses:
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
    作為 family-specific `Accept` read-only evidence
  - `tests/unit/request_contract/models_content_request_gate/conftest.py`
    作為 content/binary read-only evidence

### Workstream 5: Docs and release surfaces

- creator phase:
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - 視 README 現況是否描述 request-header composition，最小更新 `README.md`
- Main Agent release phase:
  - `VERSION`
  - `pyproject.toml`
  - `uv.lock`
  - `README.md`
- release metadata decision：
  - patch bump
  - timing at `release`
  - README status entry 與 docs 必須反映 family-aware request-header normalization 已落地

## Architecture-compliance Self-check

### Dependency direction

- `fits existing architecture`
- expected:
  - `Requester` 仍是唯一 domain request composition layer
  - `TokenEndpointClient` 仍是 token endpoint collaborator
  - `HttpClient` 仍是 transport-only substrate
  - `core/headers.py` 只作 policy helper，不引入 transport/auth lifecycle ownership

### Public surface containment

- `fits existing architecture`
- no package-root export
- no public client signature change
- no new dependency on request-contract harness code from `src/**`

### Async-baseline containment

- `fits existing architecture with explicit exemption`
- topic 雖觸及 async-capable modules，但不新增 async boundary、resource lifecycle、
  concurrency、timeout、或 cancellation policy；只在既有 async methods 內集中同步
  header policy logic

## Cost-of-realization

- Artifact authoring：
  - 新增 analysis / plan / spec / step / TDD evidence
- Runtime normalization：
  - 低至中；主要集中 helper 與 call-site rewiring
- Regression proving：
  - 中；需以 TDD 證明 merge order 與 family semantics 未回歸
- Documentation / release alignment：
  - 中；需顯式維護 README/docs/release surfaces

## Conflicts and Rollback Triggers

### Rollback trigger 1

- Failing business assumption:
  單一 request-header helper surface 能同時覆蓋 JSON domain 與 token family
- Contradicting technical fact:
  call sites 需要不可共用的 stateful builder 或 transport-owned mutation
- Required decision:
  停止本 topic，拆成更小的 family-specific helper topics

### Rollback trigger 2

- Failing business assumption:
  content/binary family 只需作為 read-only evidence
- Contradicting technical fact:
  現有 runtime implementation 已實際需要 content/binary helper 才能維持 correctness
- Required decision:
  另開後續 runtime topic，不在本 topic 內靜默擴 scope

### Rollback trigger 3

- Failing business assumption:
  topic 可在無 public API 變更下完成
- Contradicting technical fact:
  某 family caller 需要新的 public parameter / helper 才能表達 header policy
- Required decision:
  停止 implementation，回到 planning 重新凍結 public contract

## Validation Artifacts

- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/transport/test_http_client.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

## Validation Commands

```bash
uv run pytest tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_endpoint_client.py tests/unit/transport/test_http_client.py
uv run pytest tests/unit/request_contract/job_execution_jobs_state_request_gate tests/unit/request_contract/models_content_request_gate
uv run ruff check src tests
uv run pyright
uv run pytest tests/ -q
```
