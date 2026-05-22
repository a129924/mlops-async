# token-manager-test-rigor-review Specification

## Acceptance Criteria

1. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md` 必須維持 13-section 結構，且 `## Implementation Steps` 對齊 BR-1~BR-3 主體交付。
2. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md` 必須 mirror plan 的 4 個步驟，且全部初始化為 `- [ ]`。
3. `analysis/token-manager-test-rigor-review/technical-spec.md` 必須凍結三個主體輸出路徑與欄位 schema（inventory/matrix/verdict）。
4. `Validation Commands` 必須為可直接執行命令，不含 `<repo-root>` 或模板殘留語句。
5. 本 topic 工件變更不得包含 `src/**` 與 `tests/**` 內容修改。

## Behavioral Scenarios

### Scenario 1: reviewer checks python-plan-authoring completeness
- **Given**: topic 已有 requirements 與 technical-spec，但 implementer/reviewer 持續回報三個 blocker
- **When**: planner 將 plan/step/technical-spec 改為主體交付導向（inventory/matrix/verdict）並補齊 schema 與可執行命令
- **Then**: reviewer 可客觀檢查 BR-1~BR-5 對齊與可重現性，而不再只看到「修計畫文件」步驟

### Scenario 2: async applicability remains exempt
- **Given**: this topic only edits planning/analysis artifacts
- **When**: reviewer inspects the `Async-planning status` line
- **Then**: exemption evidence is explicitly stated and no triggered async subsections are required

## Error / Edge Cases

- 若 plan/step 任何一步未對應 inventory/matrix/verdict 主體交付，標記 `INCOMPLETE`。
- 若 technical-spec 缺任一必要 schema 欄位，標記 `needs-rework` 並阻止 review-ready。
- 若 Validation Commands 含佔位符或模板語句，視為不可執行契約缺陷。
- 若任何 `src/**` 或 `tests/**` 檔案出現在本 topic diff，視為 scope violation 並停止推進。
