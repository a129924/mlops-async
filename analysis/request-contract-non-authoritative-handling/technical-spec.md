# request-contract-non-authoritative-handling technical spec

## Baseline

- current-truth source for this topic:
  - `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`
  - `docs/request-shape-priority-workflow/checklist.md`
  - `tests/unit/request_contract/**`
- current historical decision:
  - `projects_tables_link_request_gate` 已被標為 `superseded-fixed-path-mvp`
  - `job_execution_jobs_*` 已被標為 `internal-wrapper-shape-only`
  - `casmanagement_*` 與 `saslogon_*` 已被標為 `custom-client-shape-only`

## Frozen decisions

- 本 topic 使用單一 authority vocabulary：
  - `upstream-aligned`
  - `non-authoritative-shape-only`
  - `historical-superseded`
  - `pseudo-endpoint-or-contract`
- 本 topic 使用單一 allowed-use vocabulary：
  - `implementation-truth`
  - `keep-as-shape-baseline`
  - `keep-as-historical-only`
  - `delete-candidate`
- `projects_tables_link_request_gate` 在本 topic 固定落到：
  - authority class: `historical-superseded`
  - allowed use: `keep-as-historical-only`
- `internal-wrapper-shape-only` 與 `custom-client-shape-only` topics 在本 topic
  固定落到：
  - authority class: `non-authoritative-shape-only`
  - allowed use: `keep-as-shape-baseline`
- 本 topic 不新增 pytest markers；改用 repo-visible docs、fixture metadata、模組
  docstring 與 topic-local collection guard 來表達 boundary。

## Write set

- `analysis/request-contract-non-authoritative-handling/requirements.md`
- `analysis/request-contract-non-authoritative-handling/technical-spec.md`
- `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.plan.md`
- `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.spec.md`
- `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.step.md`
- `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`
- `docs/request-shape-priority-workflow/request-contract-non-authoritative-ledger.md`
- selected `tests/unit/request_contract/**` non-authoritative topics:
  - `projects_tables_link_request_gate/**`
  - `job_execution_jobs_request_gate/**`
  - `job_execution_jobs_state_request_gate/**`
  - `casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
  - `casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json`
  - `casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
  - `saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json`
  - `saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`

## Out-of-scope write surfaces

- `src/mlops_async/**`
- `docs/api-endpoints/swagger-spec/upstream/*.yml`
- `docs/api-endpoints/swagger-spec/*.yaml`
- old worktree cleanup
- release surfaces such as `README.md`, `VERSION`, `pyproject.toml`, `uv.lock`

## Implementation approach

1. 先建立 topic-local planning artifacts，凍結 authority vocabulary、allowed use、
   write set、與 stop boundary。
2. 更新 evidence matrix，讓 implementer 可以直接看出 topic 是
   `implementation-truth`、`keep-as-shape-baseline` 還是
   `keep-as-historical-only`。
3. 新增 non-authoritative ledger，集中列出每個 topic 的 authority class、
   allowed use、與禁止用途。
4. 在受影響 tests surfaces 中同步 authority metadata。
5. 對 historical superseded topic 加入 collection guard，避免它在非 topic-scoped
   run 中被當成一般 request gate。

## Verification

- scoped pytest 只針對被修改的 request-contract topics 執行。
- `ruff check` 驗證 docs / tests 改動無 lint 問題。
- `pyright` 只作 repo baseline 檢查；若現有 unrelated issue 存在，必須明確回報。
