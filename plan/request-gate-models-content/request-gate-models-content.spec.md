# Request Gate Models Content Specification

## Acceptance Criteria

1. `analysis/request-gate-models-content/requirements.md` 明確凍結本 topic 只處理
   `GET /modelRepository/models/{modelId}/contents/{fileId}/content`，且不擴到其他 endpoint。
2. `analysis/request-gate-models-content/technical-spec.md` 明確凍結
   `ModelRepository.get_model_contents()` 不得作為正向入口，並把
   `tests/unit/request_contract/models_content_request_gate/` 定義為唯一 future
   implementation root。
3. `plan/request-gate-models-content/request-gate-models-content.plan.md` 使用 canonical
   required sections，並將 topic 定義為 `non-stable`、`request-only`、`single-endpoint`
   implement lane，且本輪 workflow 只推進到 `human-check` 前。
4. `plan/request-gate-models-content/request-gate-models-content.step.md` 鏡像 `plan.md` 的
   implement-plan workflow steps，並明確表達：
   `plan-authoring`、`draft-plan-commit`、`plan-review`、`plan-review-fix-loop`、
   `human-check`。
5. 所有 topic-local artifacts 都明確寫出 future implementation 只驗：
   method、path、query=`{}`、body=`None`、required header subset、單一 outbound request。
6. 所有 topic-local artifacts 都明確排除：
   response payload semantics、file-type behavior、host、query order、transport-generated
   headers、timeout、auth proof、retries。
7. 所有 topic-local artifacts 都明確寫出：
   draft-plan commit 是下一個 workflow step，但本輪不自動 commit。

## Behavioral Scenarios

### Scenario 1: Implement-plan draft enters review
- **Given**:
  - shared board 已將 `modelRepository/models/content / get_model_content` 排在 order `03`
  - local source 已證明 `ModelRepository.get_model_contents()` 不是 direct positive entry
- **When**:
  - creator 已完成 topic-local implement-plan artifacts
  - draft-plan commit 被列為下一個 workflow step
- **Then**:
  - reviewer 進入 plan review 時不需要再猜測 scope、oracle、write set、或 stop condition
  - 本 topic 仍不進 implementation

### Scenario 2: Reviewer requests rework
- **Given**:
  - reviewer 在 plan review 中回傳 `needs-rework`
- **When**:
  - creator 進入 `plan-review-fix-loop`
- **Then**:
  - 只允許修改這個 topic 的 5 個 plan artifacts
  - 不得提前建立 `tests/unit/request_contract/models_content_request_gate/**`
  - 不得擴到 shared workflow files、`src/**`、`pyproject.toml`、或 `uv.lock`

### Scenario 3: Reviewer approves the implement plan
- **Given**:
  - reviewer 已通過 plan review
- **When**:
  - Main Agent 檢查本 topic 的 workflow 停點
- **Then**:
  - 本 topic 停在 `human-check`
  - 不自動進 implementation

### Scenario 4: Oracle boundary review
- **Given**:
  - `SASCTL_ALIGNMENT.md` 對本 endpoint 有 alignment summary
  - local `sasctl` source inventory 只顯示 `/contents` list-follow pattern
- **When**:
  - reviewer 檢查 future implementation 的 evidence basis
- **Then**:
  - `ModelRepository.get_model_contents()` 不得被當成 direct-path positive oracle
  - future harness 必須以 abstract repository evidence 為基礎

## Error / Edge Cases

- 若 future implementation 需要退回 `get_model_contents()` 或任何 HATEOAS follow path，
  topic 必須標記為 `blocked`。
- 若有人要求在 draft-plan commit 前就進 reviewer gate，topic 必須標記為 `needs-rework`。
- 若 reviewer 回 `needs-rework` 後企圖修改 5 個 topic-local artifacts 之外的檔案，
  topic 必須標記為 `blocked`。
- 若 reviewer 通過後企圖直接進 implementation，topic 必須停在 `human-check`。
- 若 future implementation 需要修改 `docs/request-shape-priority-workflow/**`、`src/**`、
  `pyproject.toml`、`uv.lock`、或既有 `models_request_gate/**` / `projects_request_gate/**`，
  topic 必須標記為 `blocked`。
- 若 reviewer 發現 implement-plan artifacts 或 future implementation contract 混入 response payload semantics 或 file-type behavior，
  topic 必須回到 `needs-rework`。
- 若 reviewer 發現 implement-plan workflow 將 shared workflow docs 或 shared board 當成可寫
  surface，topic 必須回到 `needs-rework`。
