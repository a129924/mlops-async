## Goal / Outcome

- 修正 request-contract 高優先真值落差，讓 `tests/unit/request_contract/**`、repo-local spec、upstream raw spec、evidence class 重新對齊。
- Topic 完成時，後續靜態 audit 應能一致回答：
  - 哪個測試對應哪個 endpoint
  - 對應哪份 repo-local spec
  - 對應哪份 upstream raw spec
  - 該測試是否可視為 upstream truth，或僅能視為 repo-local shape baseline

## Scope

- **In scope**:
  - `plan/request-contract-truth-alignment/request-contract-truth-alignment.plan.md`
  - `plan/request-contract-truth-alignment/request-contract-truth-alignment.step.md`
  - `docs/api-endpoints/swagger-spec/projects-spec.yaml`
  - `docs/api-endpoints/swagger-spec/projects-spec.json`
  - `docs/api-endpoints/swagger-spec/authentication-spec.yaml`
  - `docs/api-endpoints/swagger-spec/authentication-spec.json`
  - `docs/api-endpoints/swagger-spec/jobs-spec.yaml`
  - `docs/api-endpoints/swagger-spec/jobs-spec.json`
  - `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
  - `docs/api-endpoints/swagger-spec/openapi-complete.json`
  - `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`
  - `docs/request-shape-priority-workflow/checklist.md`，但只有在 matrix 不足以防誤讀時才可最小幅度修改

- **Out of scope**:
  - `tests/unit/request_contract/**` fixture / test shape 改寫
  - `casmanagement_*` family-level upstream realignment
  - `projects_tables_link_request_gate` 重新啟動
  - `job_execution_jobs_state_request_gate` 擴張成 polling / state-machine workflow
  - `README.md`
  - `VERSION`
  - release / publish / commit / push

## Locked Decisions

- Topic slug 固定為 `request-contract-truth-alignment`。
- 本 topic 是 **review-ready-only with no stable-library surfaces**；不新增 `## Stable library metadata`。
- `models-spec.yaml` 與 `projects-spec.yaml` 的 upstream source-of-truth 固定是 `modelRepository-openapi.yml`。
- `tables-spec.yaml` 的 upstream source-of-truth 仍採分流：
  - list/get table -> `dataTables-v3-openapi.yml`
  - table state -> `casManagement-openapi.yml`
- `/modelRepository/...` 與 upstream `"/models"`、`"/projects"` 的差異一律視為 service-root normalization，不得直接判成 endpoint mismatch。
- `start_job` 本輪只修 truth labeling，不修改 fixture；upstream truth 與 repo-local invocation shape 必須分開描述。
- `get_champion_model` 若 fixture 仍標示 `sas-api legacy source`，就不得在 governance 文件中無條件描述成 `sasctl-direct`。
- `job_execution_jobs_request_gate` 與 `job_execution_jobs_state_request_gate` 維持 `internal-wrapper-shape-only`。
- `projects_tables_link_request_gate` 維持 `superseded-fixed-path-mvp`，不得升格為 current truth。
- 本輪只做靜態核對與文件 / 治理修正；不執行測試。

## Boundaries / Exclusions

- Creator work 僅能修改本 plan 列出的精確路徑。
- Reviewer work 只審查 topic plan 合約與 implementation contract，不代替 creator 改檔。
- Main Agent 負責 worktree 建立、子代理路由、結果整合、最終 human check 停點。
- 若工作漂移到 `tests/unit/request_contract/**`、`src/**`、stable-library surfaces，必須停止並回到 human check 或新 topic。
- `checklist.md` 只有在 `request-contract-evidence-matrix.md` 無法單獨承擔警語時才可動；不得在沒有需要的情況下擴張共享 board。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；本 topic 目標停在 creator/reviewer completion 與靜態核對完成，不進 publish。
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

- 先建立 managed worktree，再 author repo-visible plan，之後才可進 implementation。
- plan reviewer 必須獨立於 plan creator。
- implementation 可拆成不重疊 write scope 的子代理：
  - spec alignment
  - evidence governance
- bounded static verification 可與 implementation 後段並行，但不得重做 implementation。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/request-contract-truth-alignment/request-contract-truth-alignment.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/request-contract-truth-alignment/request-contract-truth-alignment.step.md` | Planning actor | Topic-local completion gate |
| Projects spec | `docs/api-endpoints/swagger-spec/projects-spec.yaml` | Code-Implementer | 補齊 `get_project` repo-local contract |
| Projects JSON output | `docs/api-endpoints/swagger-spec/projects-spec.json` | Code-Implementer | 同步 repo-local published JSON output |
| Authentication spec | `docs/api-endpoints/swagger-spec/authentication-spec.yaml` | Code-Implementer | 補齊 `client_credentials` 與 token flow truth boundary |
| Authentication JSON output | `docs/api-endpoints/swagger-spec/authentication-spec.json` | Code-Implementer | 同步 repo-local published JSON output |
| Jobs spec | `docs/api-endpoints/swagger-spec/jobs-spec.yaml` | Code-Implementer | 分離 upstream empty-body truth 與 repo-local `{}` invocation shape |
| Jobs JSON output | `docs/api-endpoints/swagger-spec/jobs-spec.json` | Code-Implementer | 同步 repo-local published JSON output |
| Merged published spec outputs | `docs/api-endpoints/swagger-spec/openapi-complete.yaml`、`docs/api-endpoints/swagger-spec/openapi-complete.json` | Code-Implementer | 同步 merged published outputs，避免 split spec 與 Swagger UI surface 漂移 |
| Evidence matrix | `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md` | Code-Implementer | 修正 evidence class / truth posture 敘述 |
| Shared checklist | `docs/request-shape-priority-workflow/checklist.md` | Code-Implementer | 僅在 matrix 不足以防誤讀時補共享警語 |

Artifact path notes:

- `README.md`: no change
- `VERSION`: no change
- `.github/copilot-instructions.md`: no change
- `tests/unit/request_contract/**`: no change
- `src/**`: no change
- 若後續工作漂移到未列路徑，必須先回 planner / human-check 修 topic contract，不得直接擴 scope。

## Implementation Steps

1. 建立 `plan/request-contract-truth-alignment/request-contract-truth-alignment.plan.md`。
2. 建立 `plan/request-contract-truth-alignment/request-contract-truth-alignment.step.md`。
3. 更新 `docs/api-endpoints/swagger-spec/projects-spec.yaml`，補齊 `GET /modelRepository/projects/{projectId}`，並明確標示它對應 upstream `"/projects/{projectId}"` 的 service-root normalization。
4. 更新 `docs/api-endpoints/swagger-spec/authentication-spec.yaml`，把 `/SASLogon/oauth/token` 的 password / refresh_token / client_credentials flow 分開描述，並使 `saslogon_token_request_gate` 的 truth posture 可被正確對照。
5. 更新 `docs/api-endpoints/swagger-spec/jobs-spec.yaml`，把 `start_job` upstream empty-body contract 與 repo-local `{}` request shape 分開標示。
6. 同步 `projects-spec.json`、`authentication-spec.json`、`jobs-spec.json` 與 `openapi-complete.yaml/json` 等 published outputs，避免 split specs 與 Swagger UI surface 漂移。
7. 更新 `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`，修正 `get_champion_model`、`job_execution_jobs_*`、`projects_tables_link_request_gate`、`saslogon_*`、`casmanagement_*` 的 truth posture 與 evidence class 說法。
8. 視需要最小幅度更新 `docs/request-shape-priority-workflow/checklist.md`。
9. 完成 bounded static verification（no-write 靜態複核），確認 `get_project`、`obtain_access_token`、`start_job` 三個高優先衝突已被消除或轉成明確治理結論。
## Validation / Acceptance Checks

- `projects-spec.yaml` 能明確對照 `get_project_by_id.request-flow.json` 與 upstream `modelRepository-openapi.yml` 的 `"/projects/{projectId}"`。
- `authentication-spec.yaml` 不再只有 password / refresh token 描述；`client_credentials` flow 有正式 repo-local contract，且 form-body baseline 與 Basic Auth variant 不再互相重疊。
- `jobs-spec.yaml` 不再把 `{}` body 描述成 upstream official truth。
- `projects-spec.json`、`authentication-spec.json`、`jobs-spec.json` 與 `openapi-complete.yaml/json` 已與 split specs 同步，不留 scope drift。
- `request-contract-evidence-matrix.md` 不再讓 `get_champion_model` 同時是 legacy-source fixture、又被無條件敘述成 `sasctl-direct`。
- `job_execution_jobs_request_gate` 與 `job_execution_jobs_state_request_gate` 仍明確維持 `internal-wrapper-shape-only`。
- `projects_tables_link_request_gate` 仍明確維持 superseded historical artifact。
- `casmanagement_*` 若未做 family realignment，最終靜態核對仍保留 `Needs human check`，不得偽裝成已解決。
- `checklist.md` 若被修改，必須是最小幅度且只補共享警語，不得重排 queue 或變更 board truth.
- bounded static verification 不會新增 repo-visible summary artifact；它只驗證既有 in-scope 檔案是否已達成 topic contract。

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

- 本 topic 不需要 release action。
- 本 topic 不更新 `README.md`、`VERSION`、release notes。
- 若後續要把本輪治理修正發佈到 release surface，必須另由主代理在 publish / merge 流程中處理。

## Open Questions / Unresolved Items

- `casmanagement_tables_list_request_gate` 與 `casmanagement_table_get_request_gate` 是否要另開新 topic 做 official family realignment；本 topic 只保留為 human-check follow-up，不阻擋目前規劃。


