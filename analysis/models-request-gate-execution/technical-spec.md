# Models Request-Gate Execution Technical Spec

## Source requirements

本技術規格落實下列需求來源：

- `analysis/models-request-gate-execution/requirements.md`
- `analysis/models-request-gate-proof/requirements.md`
- `analysis/models-request-gate-proof/technical-spec.md`

全域 guardrails 仍來自：

- `docs/project-goal.md`
- `docs/project-guidelines.md`
- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `docs/standards/request-contract-testing.md`

## Goal

把已核准的 `models-request-gate-proof` planning baseline 轉成 execution-facing technical contract，讓後續 workflow 只在 request-only boundary 與既有 repo dependencies 內建立 tests-side evidence artifacts，並在依賴或 request semantics 不足時主動 BLOCKED。

## Allowed file scope

### Allowed

- `analysis/models-request-gate-execution/requirements.md`
- `analysis/models-request-gate-execution/technical-spec.md`
- `plan/models-request-gate-execution/models-request-gate-execution.plan.md`
- `plan/models-request-gate-execution/models-request-gate-execution.spec.md`
- `plan/models-request-gate-execution/models-request-gate-execution.step.md`
- `tests/unit/request_contract/models_request_gate/**`

### Bootstrap gate (resolved)

- `pyproject.toml`
  - current status: forbidden in this topic
  - execution rule: 不得修改；execution 必須使用既有 repo dependencies
- `uv.lock`
  - current status: forbidden in this topic
  - execution rule: 不得修改；若既有 dependencies 不足，直接回報 `BLOCKED`

### Forbidden

- `src/mlops_async/**`
- `docs/migration-map.md`
- `docs/porting-ledger.md`
- `tests/unit/request_contract/**` 之外的測試路徑
- dependency additions
- response / error contract artifacts
- runtime behavior outside tests-side mock/interception boundary

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結 execution topic 的 request-only business baseline、allowed scope、blockers、與 completion gate |
| `technical-spec.md` | 將 baseline 映射成 file scope、planner handoff、artifact layout、acceptance gate、與 stop rules |
| `models-request-gate-execution.plan.md` | 供 `python-implementation-workflow` Phase 1 使用的 implementation contract |
| `models-request-gate-execution.spec.md` | 供 Phase 2 TDD authoring 使用的 primary behavior contract |
| `models-request-gate-execution.step.md` | 供 Phase 3 implementation gate 使用的 pending/completed step source |
| `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json` | 保存 raw observed request flow，供 request-contract tests 反推語意 assertions |
| `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json` | 保存與同一 flow 對應的 mock answer set |
| `tests/unit/request_contract/models_request_gate/*.py` | 保存 mock/interception helpers 與 request-contract tests |

## Planner-ready handoff

### Evidence sources available now

- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
- `docs/api-endpoints/markdown-reference/SASCTL_MLOPS_OPERATIONS.md`
- `docs/api-endpoints/swagger-spec/models-spec.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`

### Source API list

| Source API | Evidence status | Notes |
| --- | --- | --- |
| `legacy ...::get_all_models` | confirmed | repo-visible docs confirm `GET /modelRepository/models` |
| `legacy ...::get_one_model` | confirmed | repo-visible docs confirm `GET /modelRepository/models/{modelId}` |
| `sasctl.ModelRepository.list_models` | confirmed family alignment | repo-visible docs align it to the same models collection endpoint |
| `sasctl.ModelRepository.get_model` | partially confirmed | repo-visible docs align the direct request branch to `GET /modelRepository/models/{modelId}`; non-direct variants remain unresolved |

### Request contract draft

| API | Method | Path | Required headers | Query semantics | Body shape | Auth behavior | Evidence status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `legacy ...::get_all_models` | `GET` | `/modelRepository/models` | `Authorization`, `Accept` | no required query params confirmed; `filter` example is evidenced; other query fields unresolved | no body | bearer token required; auth flow out of scope | partial |
| `sasctl.ModelRepository.list_models` | `GET` | `/modelRepository/models` | `Authorization`, `Accept` on outbound request | inherits same base collection path; kwargs beyond evidenced `filter` remain unresolved | no body | session-managed auth exists upstream but not mirrored in target scope | partial |
| `legacy ...::get_one_model` | `GET` | `/modelRepository/models/{modelId}` | `Authorization`, `Accept` | no query params evidenced | no body | bearer token required; auth flow out of scope | confirmed |
| `sasctl.ModelRepository.get_model` | `GET` for direct request branch only | `/modelRepository/models/{modelId}` | `Authorization`, `Accept` on outbound request | no query params evidenced for direct request branch | no body | session-managed auth exists upstream but not mirrored in target scope | partial |

### Risk classification and stop flags

| API | Risk | Stop flags | Execution note |
| --- | --- | --- | --- |
| `legacy ...::get_all_models` | medium | `unclear source behavior` for non-evidenced query fields | safe to start from bare GET and evidenced `filter` example only |
| `sasctl.ModelRepository.list_models` | medium | `global session side effects`, `unclear source behavior` for kwargs mapping | do not auto-expand to unsupported query kwargs |
| `legacy ...::get_one_model` | low | none currently evidenced beyond auth out-of-scope | direct request path is suitable for first request-only gate |
| `sasctl.ModelRepository.get_model` | high | `conditional endpoint selection`, `global session side effects`, `unclear source behavior` | execution topic may cover only the direct identifier branch; other variants require human review |

### Recommended execution order

1. `legacy ...::get_one_model` direct request semantics
2. `legacy ...::get_all_models` bare GET and evidenced `filter` example
3. `sasctl.ModelRepository.list_models` same-family semantic alignment
4. `sasctl.ModelRepository.get_model` direct identifier branch only
5. stop before any non-direct `get_model` variant or non-evidenced `list_models` query expansion

## Request-only execution boundary

### In scope

- tests-side mock/interception strategy under `tests/unit/request_contract/models_request_gate/**`
- intercepted request capture design
- request-flow fixtures
- mock-response answer sets
- request-contract tests
- topic-local plan/spec/analysis alignment if evidence forces wording repair
- 使用既有 repo dependencies 實作 mock/interception

### Out of scope

- response / error contract extraction
- `docs/migration-map.md`
- `docs/porting-ledger.md`
- `src/mlops_async/**` production implementation
- auth family implementation
- full-port compatibility labels

## Planned artifact layout

- request-flow fixtures:
  - `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json`
  - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json`
- mock-response answer sets:
  - `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json`
  - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`
- request-contract tests / support code:
  - `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
  - `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
  - `tests/unit/request_contract/models_request_gate/conftest.py`

## Execution acceptance gate

1. `list_models` 與 `get_model` 兩者都必須產出 request-flow fixture、mock-response answer set、與 request-contract tests。
2. request tests 只能比對 semantic request behavior：
   - method
   - path
   - required header subset
   - query key/value semantics
   - body shape
3. request tests 明確不得比對：
   - query order
   - host
   - content-length
   - connection headers
   - transport-generated headers
4. `get_model` 僅接受 direct identifier branch 進入本 topic 的完成宣告；任何 name/object/refresh branch 都必須保持 BLOCKED。
5. `list_models` 僅接受 bare GET 與 repo-visible evidence 已確認的 query semantics；未確認 query fields 不得自動加入完成宣告。
6. `tests/unit/request_contract/models_request_gate/**` 下的 artifacts 只屬於 Layer 1 source-observed request-shape 證據；不得被當成 auth proof、session/refresh proof、real transport proof、或 target runtime behavior proof。

## Validation

必要檢查：

1. 下列文件存在：
   - `analysis/models-request-gate-execution/requirements.md`
   - `analysis/models-request-gate-execution/technical-spec.md`
   - `plan/models-request-gate-execution/models-request-gate-execution.plan.md`
   - `plan/models-request-gate-execution/models-request-gate-execution.spec.md`
   - `plan/models-request-gate-execution/models-request-gate-execution.step.md`
2. `plan.md` 的 Requirements、Implementation Steps、Test Plan、Open Questions 與本 technical spec 一致。
3. `spec.md` 明確把固定的 no-bootstrap policy 與 unresolved request variants 編碼為 execution gate。
4. 後續 execution 若新增 tests-side artifacts，必須全部落在 locked layout 內。

## Stop conditions

若出現以下情況，必須停止並交 human review：

- executor 需要修改 `pyproject.toml`、更新 `uv.lock`、或新增 dependency 才能完成 mock/interception
- executor 需要修改 `src/mlops_async/**`
- `sasctl.get_model` 的非 direct-request branch 被要求納入本 topic
- `list_models` 需要使用 repo-visible evidence 之外的 query semantics
- request tests 開始依賴 host、query order、content-length、connection headers、或 transport-generated headers
- capture / source review 與本 handoff matrix 衝突，且會改變 method、path、header subset、query semantics、或 body shape
