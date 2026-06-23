# Request Gate JobExecution Get Job Requirements

## Purpose

本文件凍結 `request-gate-jobexecution-get-job` 的需求基線，範圍只涵蓋
`jobExecution/jobs` surface 的 `get_job` planning contract，不包含 implementation、
review、release、或相鄰 state topic。

## Scope

本 topic 只涵蓋：

- `GET /jobExecution/jobs/{jobId}` 的 endpoint inventory
- repo 內 source / swagger / reference / precedent 盤點
- topic-local bounded write set
- `jobExecution/jobs` 與 `jobExecution/jobs/state` 的邊界切分
- 後續 implementation 應落的測試目錄名稱
- human-check boundary

本 topic 不涵蓋：

- `start_job`
- `get_job_state`
- polling / state gate
- `src/**`
- `tests/**`
- `docs/request-shape-priority-workflow/**`
- shared workflow board edits
- release / PR / publish 動作

## Actors and ownership

- Primary actor：planning actor
- Secondary actor：human reviewer
- Consuming actor：future creator / implementer / reviewer

Ownership model：

- 本 topic 只交付 topic-local analysis / plan artifacts，作為後續 implementation topic 的
  repo-visible baseline。

## Measurable requirements

1. **Endpoint inventory 必須完整**
   - 至少明列：
     - repo source inventory
     - swagger inventory
     - markdown reference inventory
     - precedent inventory
   - 若未把 `jobExecution/jobs/state` 明確列成 adjacent boundary reference，視為不合格

2. **Queue / boundary 必須凍結**
   - `jobExecution/jobs / get_job` 對應 queue `09`
   - `jobExecution/jobs/state / get_job_state` 維持 blocked `10`
   - 不得把 state polling contract 混入本 topic

3. **Bounded write set 必須精確**
   - 只允許：
     - `analysis/request-gate-jobexecution-get-job/**`
     - `plan/request-gate-jobexecution-get-job/**`
   - 若規格或計畫把 write set 擴到 `src/**`、`tests/**`、或
     `docs/request-shape-priority-workflow/**`，視為 drift

4. **Future implementation 測試落點必須固定命名**
   - 預定測試目錄名稱固定為：
     - `tests/unit/request_contract/job_execution_jobs_request_gate/`
   - 本輪不得建立該目錄，但所有規劃工件必須一致使用這個名稱

5. **Completion gate 必須停在 human-check**
   - 完成條件是四個 topic-local artifacts 存在：
     - `analysis/request-gate-jobexecution-get-job/requirements.md`
     - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
     - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
     - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`
   - artifact 建立完成後必須明確停在 `human-check`

## Endpoint inventory

### Source inventory

- Swagger / markdown 均把來源標成 `utils/_api/job_execution.py::get_job_info`
- active repo 內未 materialize `utils/_api/job_execution.py`
- source file 狀態：`source file absent in active repo`
- line range：`unknown`
- commit provenance：`unknown`

### Swagger inventory

- `docs/api-endpoints/swagger-spec/jobs-spec.yaml`
- `docs/api-endpoints/swagger-spec/jobs-spec.json`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.json`

### Markdown reference inventory

- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`

### Precedent inventory

- `docs/request-shape-priority-workflow/checklist.md`
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`

### Adjacent-but-out-of-scope precedent

- `sasctl` 結果面 precedent：`ScoreExecution.get_score_execution_results()`
- 本 precedent 只可視為 `GET /jobExecution/jobs/{id}` 的結果面參照，不是同 path wrapper
  的 direct source authority

## Contradictions surfaced and resolved

1. swagger / markdown 指向 legacy source，但 active repo 無對應 source file
   - Resolution：以 swagger / markdown 作為 primary evidence，同時留下 human-review note

2. `sasctl` 有結果面對齊參照，但不是 repo 內 `jobExecution/jobs` 的 direct source wrapper
   - Resolution：只列為 adjacent precedent，不升格成 source-of-truth

3. `get_job` 與 `get_job_state` path 相鄰，易被誤合併
   - Resolution：保留 `jobExecution/jobs/state` 為 boundary reference，明確排除 polling / state
     topic

## Extreme-boundary checks

以下情況直接停在 `human-check`：

1. 要求把 `start_job` 納入同 topic
2. 要求把 `jobExecution/jobs/state` 納入同 topic
3. 要求把 polling / state gate 混回 `get_job`
4. 要求修改 shared workflow board 或 queue order
5. 要求直接進入 `src/**` 或 `tests/**`
6. 要求重開已鎖定的 path / contract / architecture decision

## Assumptions

- topic 名稱固定為 `request-gate-jobexecution-get-job`
- active authority 以 repo 內 swagger / markdown / workflow docs 為主
- legacy source 缺件不是本輪 blocker，但必須在規劃工件中保留 human-review note
- `jobExecution/jobs/state` 的 polling / state 決策仍由獨立 topic 處理

## Non-goals

- 不做 `start_job`
- 不做 `get_job_state`
- 不做 polling / wait loop / timeout policy
- 不做 response schema implementation
- 不做 shared workflow contract 重開
- 不做 future implementation topic 的 `src/**` 或 tests authoring

## Blockers

本需求在目前範圍內無 execution blocker；若後續要求改 queue、擴 family、重開 shared
workflow contract、或把 state topic 混入，立即升級為 `human-check`

## Freeze status

Status: `FROZEN`
