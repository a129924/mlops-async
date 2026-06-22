## Workflow State Contract

- current_step: 8. Write required topic-plan sections in canonical order
- next_step: DONE
- status: COMPLETE

## Analysis Layer Routing

- Strict mode 生效：`analysis/request-gate-jobexecution-start-job/technical-spec.md`
  是 execution-facing source of truth；
  `analysis/request-gate-jobexecution-start-job/requirements.md`
  是 business-intent guardrail。
- 本 plan 100% 依據本 topic 的 technical spec 與 requirements 撰寫，不擴張到聊天脈絡
  之外的相鄰 surfaces。
- Semantic warning：repo 內不存在 legacy `job_execution.py` source file，且使用者指定的
  installed precedent 路徑
  `.venv/lib/python3.10/site-packages/sasctl/_services/score_execution.py`
  在此 worktree 無法解析；兩者都只能作為 human-check boundary，不能當成本次已驗證的
  source evidence。

## Goal / Outcome

建立 `request-gate-jobexecution-start-job` 的 repo-visible planning handoff，使後續執行者只會
針對 `jobExecution/jobRequests/jobs` / `start_job` 的 future request-only gate 工作，並在
human-check 前不擴到 `jobExecution/jobs`、`jobExecution/jobs/state`、polling / state gate、
shared workflow board、或任何 implementation surface。

## Scope

- **In scope**:
  - 建立並維護本 topic 的四個 planning artifacts：
    `analysis/request-gate-jobexecution-start-job/requirements.md`、
    `analysis/request-gate-jobexecution-start-job/technical-spec.md`、
    `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.plan.md`、
    `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.step.md`
  - 凍結 `POST /jobExecution/jobRequests/{jobRequestId}/jobs` 的 planning boundary
  - 凍結 future request-contract test directory 名稱：
    `tests/unit/request_contract/job_requests_jobs_request_gate/`
  - 明寫 human-check boundary：legacy source 缺失與 installed `sasctl` precedent 路徑未解析

- **Out of scope**:
  - `src/**` 與 `tests/**` 的 implementation
  - `jobExecution/jobs` detail request gate
  - `jobExecution/jobs/state` polling/state gate
  - `docs/request-shape-priority-workflow/**` 的任何修改
  - shared workflow board、其他 topic artifacts、commit、review、publish、merge、release

## Locked Decisions

- 本 topic 只處理 `jobExecution/jobRequests/jobs` / `start_job`
- 本 topic 只做 planning，不做 implementation
- 本 topic 是 future request-only gate 的 planning handoff，不是 execution topic
- 不得擴到 `jobExecution/jobs` 或 `jobExecution/jobs/state`
- 不得把 polling / state gate 納入本 topic
- 不得修改 shared workflow board
- bounded write set 只限四個 planning artifacts
- future test directory name 固定為
  `tests/unit/request_contract/job_requests_jobs_request_gate/`
- 規劃證據以 repo-local swagger/reference 與
  `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md` 的 installed precedent 摘要為主；
  缺失的 legacy `job_execution.py` source file 不在 repo，必須保留 human-check boundary
- 本 topic 不影響 stable-library surfaces；不修改 `README.md`、`VERSION` 或 release notes
- 本 topic 完成後停在 human-check

## Boundaries / Exclusions

- Planning actor 只負責 authoring 本 topic 的 planning artifacts
- Creator 若承接後續 execution topic，只能在本 plan 鎖定的 `start_job` request-only gate 內工作
- Reviewer 只負責獨立評估 topic plan / 後續 draft，不負責重定義 scope
- Main Agent 才擁有 publish、PR、merge 與 post-merge orchestration；這些工作不屬於本 topic
- 若後續發現需要 `jobExecution/jobs` 或 `jobExecution/jobs/state`，必須開新 topic，不得回填到本 topic
- 若後續需要驗證缺失的 legacy source 或 installed `sasctl` 檔案，必須先經 human-check 接受其替代證據策略

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；本 topic
  在 planning handoff 完成後停在 human-check，且不包含 release phase
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
  - `merged` -> terminal

Routing notes:

- 本 topic 採用 standard Phase 4.5 rule，topic-local completion gate 只讀
  `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.step.md`
  的 `## Implementation Steps` 核取方塊
- 即使四個 planning artifacts 已建立，若 human-check 尚未接受 legacy source surrogate
  策略，也不得把本 topic 解讀成可直接進入 execution
- 本 topic 不宣告 round cap，亦不修改 shared workflow queue 順序

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements baseline | `analysis/request-gate-jobexecution-start-job/requirements.md` | Planning actor | 凍結 business baseline、scope、non-goals 與 human-check boundary |
| Technical spec | `analysis/request-gate-jobexecution-start-job/technical-spec.md` | Planning actor | 凍結允許寫入範圍、證據清單、stop flags 與 future test layout |
| Topic plan | `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.plan.md` | Planning actor | 本 topic 的 canonical planning contract |
| Topic step tracker | `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.step.md` | Planning actor | topic-local completion gate，只追蹤 planning handoff steps |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`
- 上列四個路徑是可執行的 bounded contract；若後續工作需要任何其他檔案路徑，即表示 topic scope 漂移

## Implementation Steps

1. 以 repo-local swagger/reference、shared workflow docs 與 topic-local analysis artifacts 凍結
   `start_job` request-only gate 的 planning baseline。
2. 在 topic plan 中明確寫入 exact artifact paths、locked decisions、strict analysis routing、
   future test directory 名稱，以及不得觸及 `jobExecution/jobs` / `jobExecution/jobs/state`
   的邊界。
3. 在 topic step tracker 中建立未完成的 planning handoff completion gate。
4. 將缺失的 legacy source 與不可解析的 installed `sasctl` precedent 路徑記錄為 human-check
   邊界，然後停止，不進入 implementation。

## Validation / Acceptance Checks

- 四個 artifacts 都存在於本 topic 的 exact paths，且內容互相一致
- `Scope`、`Locked Decisions`、`Boundaries / Exclusions` 都只指向
  `jobExecution/jobRequests/jobs` / `start_job`
- `Status / Allowed Transitions` 只使用 canonical transitions，current status 為 `planned`
- `Artifact Paths` 僅列出四個 bounded planning artifacts，沒有隱含 `src/**` 或 `tests/**` 實作
- `Reviewer Handoff` 是單一 machine-consumable JSON 物件
- `Post-merge / release actions` 明確寫出無 release action
- future test directory 名稱固定為
  `tests/unit/request_contract/job_requests_jobs_request_gate/`
- plan 明確禁止 scope 漂移到 `jobExecution/jobs`、`jobExecution/jobs/state`、polling/state gate、
  shared workflow board 或其他 topic artifacts
- human-check 邊界已明寫：legacy source 不在 repo，installed `sasctl` precedent 路徑未解析

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

本 topic 沒有 release action。若未來需要進入 execution topic，必須由新的 topic artifact
重新定義實作與驗證範圍；本 topic merge 後也不觸發 `README.md`、`VERSION` 或 release note
變更。

## Open Questions / Unresolved Items

- human-check：是否接受缺失的 legacy `job_execution.py` source 與不可解析的 installed
  `sasctl` 路徑，由 repo-local swagger/reference 加上
  `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md` 作為
  `start_job` request-only gate 的充分 surrogate evidence
