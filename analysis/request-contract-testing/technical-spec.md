# 請求合約測試技術規格

## 來源需求

本技術規格落實下列需求來源：

- `analysis/request-contract-testing/requirements.md`

## 目標

把「Fully Intercepted Baseline Capture -> Contract Fixture -> Target Request Test」落成 repo-visible 標準與主題計畫，供後續 implementation topic 使用。

## 允許檔案範圍

此階段只能建立或更新：

- `analysis/request-contract-testing/requirements.md`
- `analysis/request-contract-testing/technical-spec.md`
- `plan/request-contract-testing/request-contract-testing.plan.md`
- `plan/request-contract-testing/request-contract-testing.step.md`
- `plan/agent-handoff-workflow.md`
- `docs/standards/request-contract-testing.md`

此階段不得修改：

- `src/mlops_async/**`
- `tests/**`
- 執行期相依設定

## 產物責任

| 產物 | 責任 |
| --- | --- |
| `requirements.md` | 凍結業務基線：capture gate、auth divergence、stop boundary、可量測 acceptance |
| `technical-spec.md` | 將需求映射成可實作的檔案範圍、規則責任與驗證方式 |
| `request-contract-testing.plan.md` | 後續 implementation topic 的執行合約 |
| `request-contract-testing.step.md` | 僅供 implementation 使用的 completion gate |
| `plan/agent-handoff-workflow.md` | 定義 agent handoff workflow 的跨主題 handoff 合約，避免 analysis 與 plan 在執行交接時語意漂移 |
| `docs/standards/request-contract-testing.md` | 規範性標準；skills 只引用並執行，不重複定義整份規範 |

## 技術需求對照

1. **Gate 合約**
   - 將 gate 通過條件定義為 `capture -> fixture -> derived request-contract test`。
   - 遇到 real-network escape 或 unregistered requests 時必須 fail-fast。

2. **Capture 輸出**
   - 持久化 `full_observed_flow` request-flow snapshot。
   - 另行持久化分離的 mock-response answer artifact。
   - 兩份 artifact 之間必須保留可追溯連結。

3. **用途分類**
   - 強制要求步驟層級的 purpose tags（`auth`、`preflight`、`target-api` 與其他可選值）。
   - 強制要求保留有序 flow 輸出。

4. **比對政策**
   - 對 method / path / required header subset / query semantics / body shape 強制採用語意比對。
   - 明確避免脆弱檢查：query order、transport-generated headers、host、content-length、connection headers。

5. **Auth 差異政策**
   - fixture 中必須保留 capture 到的 auth steps。
   - 只有在明確記錄 `intentionally_changed` 與 rationale 時，target equivalence comparison 才可排除該 auth steps。
   - 任何 capture-vs-review 的 baseline 衝突都必須阻擋並交由人工決策。

6. **停止條件**
   - 將 requirements 中第一版的 stop / escalation 清單編碼為規範性規則。

## 驗證

此階段僅限文件與規劃產物。

必要檢查：

1. 六份產物都存在於預期路徑。
2. 標準文件必須包含：
   - interception rule
   - full observed flow requirement
   - split request/answer artifacts
   - auth divergence handling
   - stop conditions
3. Plan 檔案必須明確引用分析輸入。

建議指令：

```bash
test -f analysis/request-contract-testing/requirements.md
test -f analysis/request-contract-testing/technical-spec.md
test -f plan/request-contract-testing/request-contract-testing.plan.md
test -f plan/request-contract-testing/request-contract-testing.step.md
test -f plan/agent-handoff-workflow.md
test -f docs/standards/request-contract-testing.md
```

## 停止條件

若出現以下情況，必須停止並請求人工作審：

- 此階段的請求變更需要動到 `src/mlops_async/**` 或 `tests/**`
- capture-vs-source-review 衝突無法在不改變 baseline semantics 的前提下被化解
- 標準文件文字漂移到屬於另一個 execution topic 的 implementation design
