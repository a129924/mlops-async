# 請求合約審查可讀性技術規格

## Source requirements

本技術規格落實下列需求來源：

- `analysis/request-contract-review-readability/requirements.md`

全域 guardrails 仍來自：

- `docs/project-goal.md`
- `docs/project-guidelines.md`
- `analysis/request-contract-testing/requirements.md`
- `analysis/request-contract-testing/technical-spec.md`

## Goal

把 `request-contract-review-readability` 的 frozen baseline 轉成後續可規劃、可實作、可回滾的技術基線：

- 保留 source-observed evidence
- 讓 test file 成為 primary human-readable contract surface
- 不把 implementation 推進到 production code、dependency enablement、或未核准的 test-scope rewrite

本文件**不授權直接進入實作**；後續若要修改 repo 內容，仍需再進 implementation plan。

## Current repository fit

目前 repo 已同時存在兩種測試表現型態：

1. `tests/unit/core/**`、`tests/unit/transport/**`
   - 偏向 inline、行為導向、reviewer 一眼可讀

2. `tests/unit/request_contract/models_request_gate/**`
   - 保留 source-observed capture 與 fixture evidence
   - 但主要 contract intent 仍有相當比例藏在 fixture 與 helper 之間

因此本 topic 的技術工作不是發明全新測試系統，而是把 `models_request_gate` 一帶的表現方式往 repo 既有的
review-friendly style 收斂，同時不破壞 source-evidence contract。

## Allowed file scope for this phase

### Allowed now

- `analysis/request-contract-review-readability/requirements.md`
- `analysis/request-contract-review-readability/technical-spec.md`

### Not yet allowed in this phase

- `tests/**`
- `src/**`
- `docs/**`
- `plan/**`
- `pyproject.toml`
- `uv.lock`

理由：本階段只凍結 requirements 與 technical translation，尚未進入 implementation planning。

## Requirement traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| reviewer 在 PR diff / test file 中不需翻 fixture 就能理解主要 contract | future tests must expose an inline contract surface inside the test file that names endpoint, method, path, query semantics, body, header subset, and fake-response intent | existing `models_request_gate` tests, reviewer-facing naming rules, future implementation plan | medium build effort; low runtime burden; medium review-design burden | feasible |
| evidence 必須保留且與 human-readable surface 分離 | retain request-flow fixture and mock-response fixture as separate evidence artifacts; future implementation must keep one-to-one or traceable linkage between readable test case and evidence files | current fixture layout and source-observed harness | low-to-medium build effort; low ongoing burden | feasible |
| canonical truth 仍由 source evidence 仲裁 | future implementation must encode a drift policy: inline contract mismatch cannot auto-win; mismatch routes to human review or explicit rebaseline | human review path, repo-visible evidence ownership | medium process burden; low code burden | feasible |
| implementer / maintainer 也要能沿用 readable authoring path | future helper design must distinguish readable test surface from evidence loading internals; JSON-only semantics must not remain the primary authoring surface | current helper/fixture loading model | medium build effort; medium migration burden | feasible |
| readability 優先於早期泛化 | future DSL/helper extraction must reject abstractions that require helper hopping to understand the main contract | design review discipline, implementation plan gate | medium review burden; protects long-term maintenance cost | feasible |
| 複雜 flow 不得重新把語意藏起來 | if multi-request cases arise, future plan must prefer case splitting or explicit flow presentation over opaque aggregation | real multi-request examples, human review | medium-to-high future design burden; not needed immediately | feasible with prerequisites |

## Technical workstreams

### 1. Readable contract surface design

未來 implementation 需定義一種 tests-side readable surface（名稱可為 `EndpointContractCase` 或等價設計），
使 reviewer 在 test file 內可直接看到：

- case identity
- request semantics
- response stub intent
- evidence linkage

**實作限制：**

- 不可要求 reviewer 先理解 fixture schema 才能讀懂主要 contract
- 不可只把既有 JSON 結構換個名字包起來，卻仍把主要語意留在 helper 深處

### 2. Evidence ownership and drift handling

未來 implementation 需把 evidence ownership 明確固定：

- test file = primary human-readable contract surface
- fixture = source-observed evidence surface
- drift = human review / explicit rebaseline

**技術重點：**

- 需要明確的 case-to-evidence linkage
- 需要 drift detection / review rule，而不是單靠默契

### 3. Migration strategy for existing models request gate

第一批 migration target 應聚焦：

- `tests/unit/request_contract/models_request_gate/conftest.py`
- `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
- `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
- 對應 fixtures

**技術策略：**

- 先在現有少量 cases 驗證 readability rewrite 是否成立
- 不要先為未知 family 做過度泛化

### 4. Directory strategy

目前對齊結果偏向未來落在：

- `tests/contract/sasctl_source/`
- `tests/contract/target_client/`

但這屬於 implementation 階段決策，不是本 technical-spec 階段的立即寫入範圍。

**技術含義：**

- path migration 是獨立 workstream，不應與 readable surface design 混成單一步驟
- 若 path migration 產生過高 churn，應允許先原地驗證 contract readability 改寫，再決定是否搬遷

## Cost of realization

| Workstream | Build effort | Sequencing pressure | Integration / migration burden | Ongoing operational load |
| --- | --- | --- | --- | --- |
| requirements + technical-spec freeze | low | must happen first | low | low |
| readable contract surface design | medium | must happen before bulk test rewrite | medium | low |
| existing models cases rewrite | medium | follows surface design | medium | low-to-medium |
| directory migration to `tests/contract/**` | medium | should follow proof on current cases | medium-to-high churn risk | low |
| future multi-request support | high if generalized too early | should be deferred until real examples exist | high | medium |

## Architecture-compliance self-check

| Area | Result | Notes |
| --- | --- | --- |
| analysis-layer artifact placement | fits existing architecture | `analysis/<topic>/requirements.md` 與 `technical-spec.md` 符合既有 repo 結構 |
| source-evidence preservation | fits existing architecture | 與既有 request-contract-testing 基線一致，沒有推翻 source-observed fixture 模型 |
| reviewer-friendly test style | fits existing architecture | 與 `tests/unit/core/**`、`tests/unit/transport/**` 的 inline readable style 一致 |
| future `tests/contract/**` path split | fits with prerequisites | 需在 implementation planning 時確認與 repo 現有 `tests/unit` / `tests/integration` 慣例如何共存 |
| no dependency addition | fits existing architecture | 與 repo 既有 bootstrap gate 相容；若 implementation 需要新套件，必須 rollback |
| canonical truth via source evidence | fits existing architecture | 延續 contract-first 與 evidence-first 原則 |

## Conflicts and rollback triggers

### Conflict 1: readability promise vs helper abstraction depth

- Failing assumption: readable DSL 可以在不增加 helper hopping 的前提下成立
- Contradicting technical fact: 若設計後 reviewer 仍需跳 helper / fixture 才能理解主要 contract，則 readable surface 並未真正成立
- Required rollback: 回到 alignment / planning，重談 readable contract surface 的定義，而不是帶著失真的 promise 繼續實作

### Conflict 2: future path migration vs migration burden

- Failing assumption: `tests/contract/**` 遷移可以與 readable rewrite 同步低成本完成
- Contradicting technical fact: 若 path migration 造成過高 churn、test discovery 調整、或 reviewer 認知成本，則需先分離成後續 workstream
- Required rollback: 保留 readable rewrite 與 path migration 為兩段，不得把 path migration 強行綁成第一步

### Conflict 3: source evidence ownership vs inline contract convenience

- Failing assumption: inline contract 可同時兼任 canonical truth 與 readable surface
- Contradicting technical fact: 一旦 inline case 與 source evidence 漂移，若沒有 explicit rebaseline，canonical ownership 會失真
- Required rollback: 維持 source evidence canonical，並要求 human review / rebaseline；不得為了 convenience 改寫 business promise

### Conflict 4: multi-request generalization pressure

- Failing assumption: 第一版就必須承載通用 multi-request abstraction
- Contradicting technical fact: 目前 repo-visible need 主要來自少量 single-request-dominant cases；過早 generalization 會把 topic 從 review readability 拉回 abstraction design
- Required rollback: 先限制 implementation 在已知 cases；待真實 multi-request examples 出現再重開 baseline

## Future implementation prerequisites

後續若要從本 technical spec 進入 implementation planning，至少需滿足：

1. 建立 repo-visible implementation plan
2. 明確定義 allowed file scope
3. 決定第一批改寫是否先原地進行，或直接搬到 `tests/contract/**`
4. 將 drift handling 與 rebaseline decision 寫成 plan-visible gate
5. 確認不新增 dependency 的前提下，可用既有 helper / fixture 模型完成第一版

## Validation

必要檢查：

```bash
test -f analysis/request-contract-review-readability/requirements.md
test -f analysis/request-contract-review-readability/technical-spec.md
```

內容檢查：

1. requirements 明確列出 primary actor、secondary actors、success rule、failure meaning、contradictions、extreme-boundary checks
2. technical spec 將每個 requirement 映射到 technical realization 或 rollback trigger
3. technical spec 明確標示本階段尚未授權 implementation

## Stop conditions

若出現以下情況，必須停止並回到 alignment 或 implementation planning，而不是直接寫 code：

- 使用者要求直接改 `tests/**`、`src/**`、或 `docs/**`
- readable surface 需要新增 dependency 才能成立
- `tests/contract/**` 路徑策略與 repo 現有測試分層發生衝突
- multi-request flow 的真實需求改變了 `single-file readability` 的原始 business promise
- inline contract 與 source evidence 發生 baseline-changing drift，但尚未有 explicit rebaseline decision
