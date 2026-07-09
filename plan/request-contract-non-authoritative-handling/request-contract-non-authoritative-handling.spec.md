# request-contract-non-authoritative-handling acceptance spec

## Required scenarios

1. `projects_tables_link_request_gate` 被 repo-visible artifacts 明確標成
   `historical-superseded`，且預設不再作為 current implementation truth。
2. `job_execution_jobs_request_gate` 與
   `job_execution_jobs_state_request_gate` 被明確標成
   `non-authoritative-shape-only`，allowed use 是 `keep-as-shape-baseline`。
3. `casmanagement_*` 與 `saslogon_*` 的 fixture metadata 明確標成
   `non-authoritative-shape-only`，且只允許 repo-local shape baseline 解讀。
4. `request-contract-evidence-matrix.md` 與 non-authoritative ledger 的 authority
   class、allowed use、與禁止用途一致。
5. 若 implementer 只閱讀 repo-visible docs，就能先看到 authority boundary，而不是先
   被 historical / shape-only request gate 誤導。

## Failure scenarios

- `projects_tables_link_request_gate` 仍被描述成 current truth 或 upstream endpoint
- shape-only topics 被改成 historical-only，導致必要 shape baseline 消失
- implementation drift 到 `src/**`、release surfaces、或 upstream raw specs
- docs 與 fixture metadata 對同一 topic 給出不同 authority class 或 allowed use

## Stop boundary

- implementation 完成並通過獨立 review 後，topic 停在 `human-check`
- 不在本 topic 內做 commit、push、PR、merge、release
