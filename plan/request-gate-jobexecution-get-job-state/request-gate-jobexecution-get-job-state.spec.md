# Request Gate JobExecution Get Job State Specification

## Acceptance Criteria

1. `analysis/request-gate-jobexecution-get-job-state/requirements.md` 與 `technical-spec.md` 明確凍結本 topic 只處理 `GET /jobExecution/jobs/{jobId}/state` 的 request-shape / shape-only contract。
2. `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md` 使用 canonical required sections，且保留 managed worktree path、branch、與 boundary references。
3. `tests/unit/request_contract/job_execution_jobs_state_request_gate/` 成為唯一 primary implementation surface，且與既有 `get_job` gate 分離。
4. request-contract 測試明確驗證：
   - method `GET`
   - path `/jobExecution/jobs/{jobId}/state`
   - query `{}`
   - body `None`
   - required headers `Authorization`、`Accept`
   - `Delegate-Domain` / `Content-Type` 不出現在 outbound request headers
5. request-contract 測試明確阻擋：
   - non-string identifier
   - dict-like identifier
   - blank identifier
   - unregistered request path

## Behavioral Scenarios

### Scenario 1: direct identifier request shape
- **Given**:
  - caller 提供 `job-id-abc-123`
  - fixture `get_job_state.request-flow.json#direct_identifier` 存在
- **When**:
  - harness 執行 `get_job_state("job-id-abc-123")`
- **Then**:
  - 只送出一個 outbound request
  - request path 為 `/jobExecution/jobs/job-id-abc-123/state`
  - outbound request 不含 `Delegate-Domain` 或 `Content-Type`

### Scenario 2: blocked identifier variant
- **Given**:
  - caller 傳入 non-string、dict-like、或 blank identifier
- **When**:
  - harness 企圖執行 `get_job_state(...)`
- **Then**:
  - 立即以 bounded scope error 阻擋
  - 不送出 outbound request

### Scenario 3: unregistered request fast-fail
- **Given**:
  - test case 的 expected request shape 與實際 request path 不一致
- **When**:
  - harness 執行 request-contract case
- **Then**:
  - 立即以 `Unexpected outbound request` 失敗
  - 不把 mismatched path 視為可接受 drift

## Error / Edge Cases

- 若任何測試把 `get_job_state` 擴成 polling / wait / timeout 行為，topic 必須標記為 `needs-rework`。
- 若任何 implementation 需要修改 `tests/unit/request_contract/job_execution_jobs_request_gate/**`，topic 必須標記為 `needs-rework`。
- 若任何 implementation 需要修改 shared workflow 文件作為本 topic 的順手修補，topic 必須標記為 `needs-rework`。
- 若 mock response 被擴成 state transition matrix 或 response oracle，topic 必須標記為 `needs-rework`。
- 若 reviewer 發現 `get_job` 與 `get_job_state` 被重新合併，topic 必須回到 `needs-rework`。
