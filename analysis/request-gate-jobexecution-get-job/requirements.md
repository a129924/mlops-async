# Request Gate JobExecution Get Job Requirements

## Purpose

本文件凍結 `request-gate-jobexecution-get-job` 的需求基線，將本 topic 明確定義回
`GET /jobExecution/jobs/{jobId}` 的 `request-shape / shape-only` topic。
本次 human re-scope 只允許修復 topic-local 合約；shared workflow / queue surfaces 只可
作為背景參照，不再作為 active topic-contract basis，亦不把工作擴回 `src/*` 或
typed-response topic。
latest staged reality 已包含 request-contract test surface；本次 repair pass 只負責讓
topic-local artifacts 準確反映該 shape-only reality，而不是再開啟新的測試或程式碼範圍。

## Scope

本 topic 涵蓋：

- `GET /jobExecution/jobs/{jobId}` 的 endpoint inventory 與 direct evidence
- primary implementation surface：
  - `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`
- reference-only contract surface：
  - `tests/contracts/__init__.py`
  - `tests/contracts/test_import_contract_http_client_module_path.py`
- topic-local analysis / plan artifacts：
  - `analysis/request-gate-jobexecution-get-job/requirements.md`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`
- `jobExecution/jobs` 與 `jobExecution/jobs/state` 的邊界切分

本 topic 不涵蓋：

- `src/**`
- `tests/unit/test_job_execution_jobs_api.py`
- 把 `tests/contracts/**` 當成 primary implementation surface
- `start_job`
- `get_job_state`
- polling / state gate
- 其他 `jobExecution/**` family
- `docs/request-shape-priority-workflow/**`
- shared workflow board edits
- shared workflow contract edits
- package-root re-export
- release / push / PR 動作

## Actors and ownership

- Primary actor：creator
- Secondary actor：reviewer
- Planning actor：topic-local analysis / plan contract author
- Main Agent：後續 routing、publish、PR、merge orchestration

Ownership model：

- 本 topic 的 primary implementation work 只允許落在
  `tests/unit/request_contract/job_execution_jobs_request_gate/**`
- `tests/contracts/**` 只可作為 reference，不可升格為主要實作面
- `src/**` 與 `tests/unit/test_job_execution_jobs_api.py` 不屬於本 topic 所有權

## Measurable requirements

1. **Endpoint inventory 必須完整**
   - 至少明列：
     - repo source inventory
     - swagger inventory
     - markdown reference inventory
     - precedent inventory
   - 若未把 `jobExecution/jobs/state` 明確列成 adjacent boundary reference，視為不合格

2. **Primary implementation surface 必須精確**
   - 只允許 primary implementation 落在：
     - `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
     - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
     - `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
     - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
     - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`
   - topic-local analysis / plan artifacts 只負責合約對齊，不是額外實作面
   - 若 scope 漂移到任何 `src/**`、`tests/unit/test_job_execution_jobs_api.py`、其他
     `tests/**`、或 shared workflow files，視為 drift

3. **Boundary 必須凍結**
   - 本 topic 只涵蓋 `jobExecution/jobs / get_job`
   - `jobExecution/jobs/state / get_job_state` 維持 adjacent boundary，不得回收進本 topic
   - 不得把 state polling contract 混入本 topic
   - shared workflow / queue surfaces 不得作為本 topic status、scope、或 completion
     gate 的 active 依據

4. **Request contract 必須鎖定**
   - method 固定為 `GET`
   - path 固定為 `/jobExecution/jobs/{jobId}`
   - request body 固定為 none
   - required header subset 至少包含：
     - `Authorization`
     - `Accept`
   - latest staged shape-only gate 另明確要求 outbound request headers：
     - 不出現 `Delegate-Domain`
     - 不出現 `Content-Type`
   - 不得因本 topic 自動納入 polling、state、`Content-Type`、或 typed-response
     requirement

5. **Response handling 必須維持 shape-only**
   - `get_job.mock-responses.json` 只作為 request-shape harness 的執行輔助
   - 本 topic 不承擔 typed job document decoding
   - latest staged request-contract test 只保留最小 decoded-result 驗證：
     - `result.id`
     - `result.state`
   - 上述最小 decoded-result 驗證只用來確認 harness 可完成既有 decode path，不升格為
     typed-response behavior acceptance contract
   - staged request-contract 測試若為了讓 harness 可執行而讀取 mock response 欄位，
     該觀察也不升格為 typed-response behavior validation 或 completion gate
   - `tests/unit/test_job_execution_jobs_api.py` 明確維持 out of scope

6. **Reference-only boundary 必須清楚**
   - `tests/contracts/__init__.py` 與
     `tests/contracts/test_import_contract_http_client_module_path.py`
     只可作為 reference
   - 不得把 `tests/contracts/**` 改寫成此 topic 的 primary gate 或 completion gate

7. **Completion gate 必須對齊 shape-only pass**
   - `plan.md` 與 `step.md` 必須以 shape-only request gate 為準，而不是 `src/*` 或
     typed-response implementation pass
   - `step.md` 必須把已 materialize 的
     `tests/unit/request_contract/job_execution_jobs_request_gate/**`
     視為最新 staged reality，而不是持續標示為未完成的未來工作
   - `step.md` 完成 wording 必須明確反映目前 staged reality 已包含：
     - `Delegate-Domain` / `Content-Type` 不出現在 outbound request headers 的 negative
       shape constraints
     - 僅限 `result.id` / `result.state` 的最小 decoded-result 驗證
   - `human-check` 只保留為外部 stop boundary，不是 workflow status，也不是 creator
     completion gate

## Endpoint inventory

### Source inventory

- active wrapper path：
  - `src/mlops_async/_api/job_execution_jobs.py`
- source inventory status：`present but out of scope for this topic`
- active primary implementation surface：
  - `tests/unit/request_contract/job_execution_jobs_request_gate/**`

### Swagger inventory

- `docs/api-endpoints/swagger-spec/jobs-spec.yaml`
- `docs/api-endpoints/swagger-spec/jobs-spec.json`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.json`

### Markdown reference inventory

- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`

### Precedent inventory

- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `tests/contracts/__init__.py`
- `tests/contracts/test_import_contract_http_client_module_path.py`

### Adjacent-but-out-of-scope precedent

- `tests/unit/test_job_execution_jobs_api.py`
- `sasctl` 結果面 precedent：`ScoreExecution.get_score_execution_results()`
- 上述 precedent 只可作為 adjacent reference，不是本 topic 的 primary implementation
  surface

## Contradictions surfaced and resolved

1. active repo 已有 `src/mlops_async/_api/job_execution_jobs.py`
   - Resolution：保留為 repo 現況 reference，但本 topic 合約明確把 `src/**` 排除在外

2. active repo 已有 `tests/unit/test_job_execution_jobs_api.py`
   - Resolution：typed-response validation 不屬於 shape-only topic，明確排除

3. `tests/contracts/**` 容易被誤當成 contract gate
   - Resolution：只列為 reference-only，不升格為 primary implementation surface

4. `get_job` 與 `get_job_state` path 相鄰，易被誤合併
   - Resolution：保留 `jobExecution/jobs/state` 為 boundary reference，明確排除 polling /
     state topic

## Extreme-boundary checks

以下情況直接停在 `human-check`：

1. 要求把 `src/**` 納回同 topic
2. 要求把 `tests/unit/test_job_execution_jobs_api.py` 納回同 topic
3. 要求把 `tests/contracts/**` 升格成 primary gate
4. 要求把 `start_job` 納入同 topic
5. 要求把 `jobExecution/jobs/state` 納入同 topic
6. 要求把 polling / state gate 混回 `get_job`
7. 要求修改 shared workflow board 或 shared workflow contract
8. 要求重開已鎖定的 path / contract / architecture decision

## Assumptions

- topic 名稱固定為 `request-gate-jobexecution-get-job`
- active authority 以 repo 內 swagger / markdown direct evidence、topic-local artifacts、
  與最新 staged request-contract surface 為主
- shape-only mode 只要求 request-shape gate，不要求 typed-response gate
- `jobExecution/jobs/state` 的 polling / state 決策仍由獨立 topic 處理

## Non-goals

- 不做 `src/**`
- 不做 `tests/unit/test_job_execution_jobs_api.py`
- 不做 `start_job`
- 不做 `get_job_state`
- 不做 polling / wait loop / timeout policy
- 不做 shared workflow contract 重開
- 不做 shared workflow board edits
- 不做 release / push / PR

## Blockers

本需求在目前範圍內無 execution blocker；若後續要求擴回 `src/**`、typed-response tests、
`tests/contracts/**` primary gate、family boundary、或 shared workflow artifacts，立即
升級為 `human-check`

## Freeze status

Status: `FROZEN`
