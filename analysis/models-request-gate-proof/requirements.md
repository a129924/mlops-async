# Models Request-Gate Proof Requirements

## Purpose

本文件凍結 `models-request-gate-proof` 的業務基線，目的是讓 `porting_maintainer`
能以最低風險、可追溯、mock-first 的方式，驗證第一個 `model-repository/models`
family 的 request-gate workflow 可以穩定落地，而不把 topic 擴張成完整 port 或
production implementation。

## Scope

本需求只涵蓋第一個 request-gate proof topic 的業務邊界：

- family 固定為 read-only `model-repository/models`
- source API 固定為：
  - `sasctl.ModelRepository.list_models`
  - `sasctl.ModelRepository.get_model`
  - `legacy src/sas_api/utils/_api/get_model.py::get_all_models`
  - `legacy src/sas_api/utils/_api/get_model.py::get_one_model`
- 成功範圍只到：
  - request contract extraction
  - request-contract tests

本需求不涵蓋：

- response / error contract
- `docs/migration-map.md` 更新
- `docs/porting-ledger.md` 更新
- auth family implementation
- concrete `HttpClient` implementation
- `src/mlops_async/**` production code
- `tests/**` 實際 request tests 落地

## Actors and ownership

- Primary actor：`porting_maintainer`
- Supporting actor：Human reviewer

Ownership model:

- `maintainer-led with human review gate`

## Measurable requirements

1. **First-family boundary freeze**
   - Actor: `porting_maintainer`
   - Condition: 第一個 request-gate proof topic 開始時
   - Required outcome: topic 只能以 `model-repository/models` read-only family 作為第一批範圍
   - Metric / decision rule: topic 的 in-scope source API 必須且只能是已凍結的四個 source
     API；若擴張到 auth、download、polling、mutation family，則視為超出基線
   - Evidence signal: topic plan、requirements、technical spec 三者都指向相同 family 與
     source API set
   - Failure meaning: 若第一批 family 邊界不穩定，後續 planner / implementer 會重新打開
     scope，失去「最低風險驗證 workflow」的目的

2. **Request-gate-only completion boundary**
   - Actor: `porting_maintainer`
   - Condition: 第一個 request-gate proof topic 進入 creator implementation 時
   - Required outcome: `list_models` 與 `get_model` 都必須完成 request contract extraction
     與 request-contract tests；不得把 response / error / ledger completeness 當成同 topic
     的完成條件
   - Metric / decision rule: 只有當兩個 API 都進入 request gate，topic 才算達成主要成功
     訊號；只完成其中一個 API，不算 topic 完成
   - Evidence signal: step tracker 與後續 reviewer 驗收規則都以兩個 API 的 request gate
     為 completion gate
   - Failure meaning: 若 completion boundary 被擴成 full port，topic 會被額外風險拖住，
     無法作為第一個低風險 workflow proof

3. **Mock-first entry gate**
   - Actor: `porting_maintainer`
   - Condition: repo 尚無 concrete `HttpClient` implementation，且 topic 仍停留在
     request-gate proof 階段
   - Required outcome: topic 可使用 mock-first / intercepted-fixture 前提繼續規劃與後續
     request gate 工作，不因 concrete client 缺席而被標記 blocked
   - Metric / decision rule: 若 topic 邊界未擴張到 target runtime call path，則
     concrete `HttpClient` implementation 不是 blocker
   - Evidence signal: requirements、technical spec、topic plan 均明確記錄
     `mock_first_no_concrete_client`
   - Failure meaning: 若錯把 concrete client 視為先決條件，topic 會被不必要地改寫成
     基礎設施 implementation，而非 request-gate proof

4. **Planning-only pre-implementation gate**
   - Actor: `porting_maintainer`
   - Condition: 在 spec worktree 內執行本 topic 的第一輪 creator pass 時
   - Required outcome: 只能建立 repo-visible analysis / plan artifacts，並在完成後停在
      human review；若之後要進入 mock/interception、fixture、或 request-test work，必須由
      獨立 execution-facing topic 承接，不得直接把目前 topic 擴張成 execution topic
    - Metric / decision rule: 第一輪 creator pass 僅允許建立：
      - `analysis/models-request-gate-proof/requirements.md`
      - `analysis/models-request-gate-proof/technical-spec.md`
      - `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
      - `plan/models-request-gate-proof/models-request-gate-proof.step.md`
    - Evidence signal: git diff 僅包含上述 planning artifacts；後續若進入 request-only execution，
      應有新的 execution-facing topic plan 明確承接 `tests/**`、fixtures、與 bootstrap 規則
    - Failure meaning: 若第一輪就跨進 implementation，會混淆 planning 與 execution gate，
      使 reviewer 無法只審 planning baseline

5. **Deferred environment bootstrap rule**
   - Actor: `porting_maintainer`
   - Condition: planning-only topic 尚未進入 execution-facing request-gate work時
   - Required outcome: 不以 dependency 安裝作為本 topic 的前提；`uv add --dev ...`、
     `uv sync`、`pyproject.toml` / `uv.lock` 變更都延後到下一個 execution topic 再決定
   - Metric / decision rule: 只要本 topic 仍屬 planning-only，則 environment bootstrap
     不能成為 blocker，也不能成為本 topic 的交付內容
   - Evidence signal: plan、requirements、technical spec 都明確記錄
     `defer_until_execution_topic`
   - Failure meaning: 若在 planning topic 內先改動依賴或 lockfile，會把 execution 風險與
     planning baseline 混在一起，增加不必要變更面

6. **Evidence-layer separation**
   - Actor: `porting_maintainer`
   - Condition: 下一個 execution topic 開始設計 mock/interception 與 request evidence 時
   - Required outcome: 高層範圍與決策必須留在 `analysis/...` / `plan/...`；raw observed
     request evidence 與 mock answers 必須留在 tests-side fixture layer
   - Metric / decision rule: endpoint / request semantics 的原始觀察證據不得只存在 Markdown
     敘述中；必須有對應 fixture artifact
   - Evidence signal: 後續 execution topic 明確區分：
     - summary / decision layer
     - raw request-flow fixture layer
     - mock-response answer set layer
   - Failure meaning: 若不分層保存，reviewer 無法區分「決策摘要」與「實際觀察證據」，
     會削弱 request-contract traceability

## Contradictions surfaced and resolved

1. `低風險優先` vs `最接近真實業務價值優先`
   - Resolution: 第一個 topic 先以低風險 workflow proof 為主，不追求最大終端業務價值

2. `先做 read-only metadata family` vs `先做 auth 作為所有 family 的基底`
   - Resolution: 第一個 topic 不納入 auth；auth 另開 topic

3. `先完成第一個完整 port` vs `先完成 request gate`
   - Resolution: 第一個 topic 的 completion boundary 固定為 `request_gate_only`

4. `沒有 concrete HttpClient 就不能動` vs `mock-first 足以支撐 request gate`
   - Resolution: 在未進入 target runtime implementation 前，採 mock-first，不以
      concrete client 缺席作為 blocker

5. `先把依賴裝好比較省事` vs `不想污染目前 branch 的 lockfile`
   - Resolution: environment bootstrap 延後到下一個 execution topic，並由該 topic 明確承接
     `pyproject.toml` / `uv.lock` 變更責任

## Extreme-boundary checks

1. **No network / degraded dependency**
   - 若外部 SAS 環境暫時不可用，本 topic 仍可完成 planning artifacts 與 frozen baseline，
     但不得宣稱 request capture 已完成

2. **Wrong role / missing approval**
   - 只有 `porting_maintainer` 可推進 creator work；是否進入下一階段 execution 需經
     human reviewer 明確確認

3. **Interrupted / partial completion**
   - 若只完成 `list_models` 或只完成 planning artifacts 的一部分，不算 request-gate proof
     topic 完成

4. **Lowest-volume / peak-volume**
   - 第一個 topic 不處理 pagination、filtering 壓力或大量 model volume 行為；若需要，
     應在後續 topic 明確擴 scope

5. **Audit / traceability**
   - 第一個 topic 必須保留 source evidence、family 邊界、完成條件與 stop boundaries 的
     repo-visible 紀錄；不得只留在對話中

## Assumptions

- `sasctl 1.11.8` 與 legacy source commit `6b8d2e41ac9a9a9a7fb671db9b2b38faeced0f8a`
  仍是本 topic 的主要 source baseline。
- 目前 repo 只有 internal `Client` Protocol，尚無 concrete implementation。
- 這個 topic 的主要價值是 workflow proof，而不是交付下游可直接使用的 public API。
- 下一個 execution topic 會在獨立 worktree / branch 中承接 environment bootstrap 決策。
- 下一個 execution topic 會承接 planner handoff、mock/interception、fixtures、與 request
  tests；目前 topic 不直接跳進 `api-client-porting-implementer`。

## Non-goals

- 不在此 topic 中實作 `src/mlops_async/**`
- 不在此 topic 中新增 `tests/**` request tests
- 不在此 topic 中跑 intercepted capture
- 不在此 topic 中更新 migration map 或 porting ledger
- 不在此 topic 中宣告任何 stable-library surface 變更
- 不在此 topic 中修改 `pyproject.toml` 或 `uv.lock`

## Blockers

本需求目前無未決 blocker，可進入 technical translation。

## Freeze status

Status: `FROZEN`
