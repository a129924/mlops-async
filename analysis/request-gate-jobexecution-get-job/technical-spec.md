# Request Gate JobExecution Get Job Technical Spec

## Source requirements

本技術規格對應下列需求來源：

- `analysis/request-gate-jobexecution-get-job/requirements.md`

全域 workflow / planning guardrails 來自：

- `AGENTS.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`
- `docs/request-shape-priority-workflow/standards.md`

## Goal

把 `GET /jobExecution/jobs/{jobId}` 的 bounded planning baseline 轉成 execution-facing
technical contract，供後續 implementation topic 使用；本 topic 本身不進行 implementation。

## Current state summary

目前 repo 已有：

- `jobExecution/jobs` 與 `jobExecution/jobs/state` 的 swagger / markdown surfaces
- `docs/request-shape-priority-workflow/checklist.md` 的 queue baseline，將
  `jobExecution/jobs / get_job` 排在 `09`
- `docs/request-shape-priority-workflow/checklist.md` 將
  `jobExecution/jobs/state / get_job_state` 維持 blocked `10`
- `tests/unit/request_contract/models_request_gate/**` 與
  `tests/unit/request_contract/projects_request_gate/**` 作為 request-gate precedent

目前 repo 尚無：

- `src/**` 下的 `get_job` endpoint wrapper
- `tests/unit/request_contract/job_execution_jobs_request_gate/` topic-local request gate
- active repo 內的 `utils/_api/job_execution.py`

## Allowed file scope

本 topic 只允許新增或更新：

- `analysis/request-gate-jobexecution-get-job/requirements.md`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`

下列路徑在本 topic 中不得修改：

- `docs/request-shape-priority-workflow/**`
- `src/**`
- `tests/**`
- 其他 `jobExecution` future topic artifacts

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結 endpoint inventory、scope / non-goals、boundary、與 human-check baseline |
| `technical-spec.md` | 把需求映射成 execution-facing contract、allowed scope、risk、與 stop rules |
| `plan.md` | 提供本 topic 的 canonical workflow contract |
| `step.md` | 提供本 topic 唯一的 topic-local completion gate |

## Endpoint family map

- In scope family：`jobExecution/jobs / get_job`
- Adjacent family：`jobExecution/jobRequests/jobs / start_job`
- Boundary-only family：`jobExecution/jobs/state / get_job_state`

Boundary rule：

- `get_job` 不得與 `start_job` 或 `get_job_state` 併批
- `jobExecution/jobs/state` 只可作為 boundary reference，不可在本 topic 內吸收 polling、
  state gate、或 stop condition implementation

## Request contract draft

- Method：`GET`
- Path：`/jobExecution/jobs/{jobId}`
- Path params：
  - `jobId`：required，string
- Query params：none
- Request body：none
- Required headers：
  - `Authorization: Bearer {token}`
  - `Accept: application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, application/vnd.sas.error+json, application/json`
- Conditional / evidence-only headers：
  - `Delegate-Domain`
    - source-doc-present，但 GET detail endpoint 是否必須保留為 mandatory 未被 active source
      file 再證實
- Explicit non-requirement：
  - `Content-Type` 不列為 required，因本 endpoint 無 request body
- Auth behavior：Bearer token required

## Risk classification

- Classification：`medium`
- Reasons：
  - method / path / path param 在 swagger 中清楚
  - legacy source file 缺件，無法直接以 source code 再驗證 header helper 用法
  - `jobExecution/jobs` 與 `jobExecution/jobs/state` 相鄰，需強化 boundary 防漂移

## Stop flags

- `polling_job_wait: true`
  - 理由：本 endpoint 容易被誤擴成 polling/state topic
- `unclear_source_behavior: true`
  - 理由：legacy source `utils/_api/job_execution.py` 不在 active repo
- `state_topic_scope_drift: true`
  - 理由：`jobExecution/jobs/state` 在 shared queue 中明確 blocked

## Human-review notes

- `sasctl.ScoreExecution.get_score_execution_results()` 只能作為 adjacent precedent，不得當作
  direct source authority
- swagger / json reference 均記錄 `get_job_info` 使用 header helper 時有
  `is_text=True` 已知 bug；本 topic 只記錄 evidence，不進行 bug fix planning
- `Delegate-Domain` 對 GET detail endpoint 的 requiredness 只保留 source-doc wording，不自行擴張

## Requirement-to-technical mapping

| Requirement | Technical realization |
| --- | --- |
| Endpoint inventory 完整 | `requirements.md` 的 inventory 與 contradiction sections |
| Queue / boundary freeze | `technical-spec.md` 的 family map、risk、stop flags、validation |
| Bounded write set 精確 | `technical-spec.md` 的 allowed file scope 與 `plan.md` artifact paths |
| Future test landing 命名固定 | `requirements.md`、`technical-spec.md`、`plan.md` 一致使用 `tests/unit/request_contract/job_execution_jobs_request_gate/` |
| Completion gate 停在 human-check | `plan.md` 只把 `human-check` 保留為 routing boundary；workflow completion 只依 `step.md` 的 `## Implementation Steps` 勾選語意判定，全部為 `[X]` 時才可對齊 `review-ready` |

## Required technical tasks

1. 建立 `requirements.md` 並凍結 endpoint inventory、scope / non-goals、boundary 與 human-check 規則
2. 建立 `technical-spec.md` 並凍結 request contract draft、risk、stop flags、allowed file scope
3. 建立 `plan.md` 並寫入 canonical workflow contract、locked decisions、artifact paths
4. 建立 `step.md` 並鏡像 topic-local implementation steps，作為唯一 completion gate

## Deferred prerequisites and explicit non-work

以下事項在本 topic 明確 defer：

- `start_job`
- `get_job_state`
- polling / state gate contract
- `tests/unit/request_contract/job_execution_jobs_request_gate/` 的建立
- `src/**` 下任何 client / wrapper implementation

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language default | compatible | analysis / plan 以繁體中文撰寫 |
| Docs-first workflow compatibility | compatible | topic 只引用 shared workflow docs，不改寫它們 |
| Production boundary | compatible | 不觸碰 `src/**`、`tests/**`、shared workflow docs |
| Topic isolation | compatible | write set 限定於 topic-local `analysis/**` 與 `plan/**` |

## Validation

必要檢查：

1. 下列四個 artifacts 存在：
   - `analysis/request-gate-jobexecution-get-job/requirements.md`
   - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
   - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
   - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`
2. artifacts 明確寫出：
   - `jobExecution/jobs/state` 是 boundary，不是 in-scope deliverable
   - future test landing path 是 `tests/unit/request_contract/job_execution_jobs_request_gate/`
   - forbidden paths 包含 `src/**`、`tests/**`、`docs/request-shape-priority-workflow/**`
3. `plan.md` 使用 canonical required sections，且 `Reviewer Handoff` 是單一 JSON object
4. 沒有建立 `spec.md`

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 要求擴到 `start_job`
- 要求擴到 `jobExecution/jobs/state`
- 要求把 polling / state gate 混入本 topic
- 要求修改 shared queue / workflow board
- 要求把 write set 擴到 `src/**`、`tests/**`、或 `docs/request-shape-priority-workflow/**`
