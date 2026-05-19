# Request Contract Review Readability Requirements

## Purpose

本文件凍結 `request-contract-review-readability` 的 business baseline，目標是在不犧牲
source-observed evidence 的前提下，改善 request contract tests 的 reviewer 可讀性，讓主要
review 情境不再依賴翻查 fixture 才能理解測試在驗證什麼 contract。

## Scope

本需求只涵蓋 source-observed request contract tests 的**人類可讀性、evidence ownership、與
review decision rule**。

本需求目前聚焦的起點：

- `tests/unit/request_contract/models_request_gate/**`

本需求不涵蓋：

- production code behavior
- auth / session / refresh implementation
- response / error contract
- dependency additions
- 直接執行 tests 或進入 implementation

## Actors and ownership

- Primary actor: code reviewer
- Secondary actors:
  - API porter / implementer
  - test maintainer
- Human arbiter: 當 inline contract 與 source evidence 發生語意漂移時，負責決定是否需要
  explicit rebaseline

Ownership model:

- `reviewer-first with source-evidence arbitration`

## Measurable requirements

1. **Reviewer-first single-file readability**
   - Condition: code reviewer 在 PR diff 或單一 test file 中檢視 request contract case 變更時
   - Required outcome: reviewer 不需要打開 fixture 檔案，也能從 test file 本體判斷此 case 的主要
     endpoint contract，包括：
     - endpoint / case 名稱
     - method
     - path
     - query semantics
     - body expectation
     - required headers
     - fake response intent
   - Acceptance signal: test file 內存在可直接閱讀的 inline contract surface 或等價表達方式；fixture
     不是理解主要 contract 的必要前置
   - Failure meaning: reviewer 需要額外追查 fixture / helper 才能完成理解，導致 review time 過高

2. **Evidence remains preserved and separate**
   - Condition: topic 改善可讀性時
   - Required outcome: source-observed request-flow fixture 與 mock-response fixture 仍保留為獨立
     evidence artifacts，不得因為 readable inline case 出現就被靜默取代
   - Acceptance signal: human-readable test surface 與 machine-verifiable evidence 同時存在，且能對應到同一
     case
   - Failure meaning: 若 evidence 被吸收到 test surface 或失去獨立性，contract drift 會更難追蹤

3. **Canonical truth remains source-evidence-backed**
   - Condition: inline contract 與 source-observed evidence 出現 method / path / query / body /
     header subset 語意差異時
   - Required outcome: source evidence 在 explicit rebaseline 前仍為 canonical arbiter；不得因 inline
     test wording 比較好讀就自動覆寫 evidence truth
   - Acceptance signal: 發生語意差異時，流程必須升級為 human review 或 rebaseline decision，而不是由
     inline case 靜默勝出
   - Failure meaning: 若 canonical ownership 混亂，reviewer 與 maintainer 會無法判斷哪裡才是 baseline

4. **Readable maintenance path for secondary actors**
   - Condition: implementer 或 maintainer 新增、修改、或維護 request contract case 時
   - Required outcome: 次要 actor 可以把 test file 視為主要的人類可讀 contract surface，而 fixture 視為
     evidence surface，而不是反向從 JSON-only semantics 猜測 test intent
   - Acceptance signal: case authoring 與 maintenance 流程明確區分「test file 負責人類可讀 contract」
     與「fixture 負責 evidence」
   - Failure meaning: 若維護路徑仍以 hidden fixture semantics 為主，後續會重新引入可讀性債

5. **Readability wins over early generalization**
   - Condition: 測試抽象設計同時面臨「提高 DSL 泛化能力」與「維持 reviewer 可讀性」的取捨時
   - Required outcome: 第一版一律優先保留 reviewer 可讀性，而不是先接受需要多層 helper hopping 的高泛化
     設計
   - Acceptance signal: 若某設計要求 reviewer 必須跳轉 helper 定義或 fixture 才能理解主要 contract，該
     設計不得作為第一優先
   - Failure meaning: 若過早泛化勝出，topic 會把既有 JSON 隱性規格問題換成另一種 abstraction debt

6. **Complex flows must not erase reviewer readability**
   - Condition: 未來 case 從單次 request 成長為 multi-request flow 或較複雜的 observed sequence 時
   - Required outcome: 仍優先維持 reviewer readability；必要時拆成多個明確 case，而不是把複雜 flow
     隱藏在單一 opaque test entrypoint
   - Acceptance signal: 當 flow complexity 上升時，設計決策必須先回答 reviewer 如何在 test file 中看懂主要
     contract；若做不到，需 split 或 BLOCKED
   - Failure meaning: 若複雜 flow 直接被包進不可讀抽象，topic 會再次失去 review-facing value

## Contradictions surfaced and resolved

1. `reviewer 可讀性最大化` vs `source-observed evidence 必須保留`
   - Resolution: test file 成為 primary human-readable contract surface；fixtures 保留為獨立 source evidence
     artifacts，不互相取代

2. `inline case 應該是 reviewer 第一眼看到的 contract` vs `canonical truth 不能脫離 source evidence`
   - Resolution: inline case 負責閱讀與審查；source evidence 在 explicit rebaseline 前仍是 canonical
     arbiter

3. `希望 DSL 夠通用` vs `不能再把語意藏進抽象`
   - Resolution: 第一版一律先保 reviewer readability；通用化能力可延後，但不可讓主要 contract 需要 helper
     hopping 才看得懂

4. `未來 flow 可能更複雜` vs `single-file readability 仍是 primary promise`
   - Resolution: 當複雜度上升時，優先 split cases 或阻擋 scope 擴張；不允許以 opaque mega-case 滿足複雜 flow

## Extreme-boundary checks

1. **PR-diff-only review**
   - 若 reviewer 只看 PR diff，不打開 fixture，test file 仍必須足以表達主要 contract

2. **20+ endpoint cases**
   - 若 case 數量成長，命名、inline contract surface、與 evidence 對應關係仍必須保持 reviewer 可讀

3. **Multi-request flow**
   - 若單一業務語意需要多步 request flow，必須先回答 readable representation；否則 split 或 BLOCKED

4. **Evidence drift**
   - 若 inline contract 與 source evidence 漂移，必須升級 human review；不得靠較好讀的文案自動蓋過
     evidence

5. **Wrong ownership assumption**
   - 若 secondary actor 把 fixture 視為唯一 contract source，代表 baseline 未被正確落實

## Assumptions

- 主要 review 情境是 GitHub PR diff / 單一 test file 閱讀，而不是先讀 fixture 再回推 test intent
- 目前最迫切的 pain point 來自 `tests/unit/request_contract/models_request_gate/**`
- source-observed request-flow 與 mock-response fixtures 對此 repo 仍有保留價值，不應在此 topic 中移除
- 可讀性改善的首要目標是降低 reviewer 理解成本，而不是同時解決所有未來 request-family abstraction needs

## Non-goals

- 不在此需求中直接改寫 `tests/**`
- 不在此需求中設計 production API 或修改 `src/mlops_async/**`
- 不在此需求中新增 `requests-mock`、`respx`、`pytest-httpx` 或其他 dependencies
- 不在此需求中保證所有未來 family 都可直接沿用同一 DSL 而無調整
- 不在此需求中重新定義 source-observed evidence 的上游 capture policy

## Blockers

本需求目前無未決 blocker，可進入 technical translation。

## Freeze status

Status: `FROZEN`
