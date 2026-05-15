---
topic: core-concrete-client-minimal
type: correction-step
parent_correction: plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Correction Step Tracking

> 本檔追蹤 correction work 的順序、完成條件、以及哪一步需要測試。
> 它不取代主 `core-concrete-client-minimal.step.md`，而是補充本次 needs-rework 差異修正。

## Workflow Stages

- [X] correction-authoring
- [ ] correction-review
- [ ] parent-plan-sync
- [ ] creator-alignment
- [ ] correction-closed

## Correction Steps

- [ ] 1. 凍結 correction scope，只處理 exception placement 與 transport module placement drift。
  - **完成條件**：
    - correction-plan 與 correction-step 都明確寫出本次只修這兩類 drift
    - auth / retry / facade / request merge rules 沒被誤納入 correction scope
  - **需要測試**：否

- [ ] 2. 在 correction-plan 中標明哪些既有敘述可保留、哪些必須移除或改寫。
  - **完成條件**：
    - 至少明確列出 root `exceptions.py`、transport exceptions、`transport/http_client.py`
      三塊的 keep / remove 決策
    - 明確列出「不做 root re-export」與「不保留 alias / transition layer」
  - **需要測試**：否

- [ ] 3. 在 correction-plan 中重寫 architecture rule 與 acceptance criteria。
  - **完成條件**：
    - architecture rule 明確寫成：
      - root `exceptions.py` = base home only
      - `transport/exceptions.py` = transport-local exception home
      - 依賴方向單向
      - `transport/http_client.py` = 唯一正確 concrete client path
    - acceptance criteria 明確列出 must-pass / must-fail 條件
  - **需要測試**：否

- [ ] 4. 將 correction-review 結論回補到 parent artifacts。
  - **完成條件**：
    - `analysis/core-concrete-client-minimal/requirements.md` 不再把 root `exceptions.py`
      描述成 entry layer 或保留本 topic 的 re-export 空間
    - `analysis/core-concrete-client-minimal/technical-spec.md` 不再把 root `exceptions.py`
      描述成 entry layer 或保留本 topic 的 re-export 空間
    - `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
      與 `core-concrete-client-minimal.step.md` 同步移除舊 wording
  - **需要測試**：否

- [ ] 5. 在 creator work 開始前，確認 implementation / tests / docs 只依 corrected contract 行動。
  - **完成條件**：
    - implementation 不再以 root re-export 為前提
    - tests 不再驗證 root entry-layer import surface
    - `docs/ARCHITECTURE.md` 若有舊的 `core/http_client.py` 或 root entry-layer 敘述，
      已被列為需同步修正項
  - **需要測試**：部分需要；見下一步

- [ ] 6. 只有在 code changes 開始後，才執行與本 correction 直接相關的測試。
  - **完成條件**：
    - 與 exception placement / transport path 直接相關的程式碼已改動
    - 下列測試已依實際變更範圍執行：
      - `uv run pytest tests/unit/transport/test_exceptions.py`
      - `uv run pytest tests/unit/transport/test_http_client.py`
      - `uv run pytest tests/unit/core/test_client_contract.py`
    - 若這次只有 correction artifact 與主 plan wording 修正，則本步驟保持未執行，並註明
      原因為「尚未進入 code alignment」
  - **需要測試**：是

## Order Rationale

本 correction 的順序必須是：

1. **先定義差異是什麼**
2. **再定義哪些保留、哪些移除**
3. **再修 architecture rule 與 acceptance criteria**
4. **再回補 parent artifacts**
5. **最後才進 implementation / test alignment**

若跳過前面幾步直接改 code，會再次留下「只看到結果、看不到為何而改」的問題。

## Closure Condition

本 correction 可視為 closed，必須同時滿足：

1. correction-plan / correction-step 已經過 review
2. parent plan / step / analysis 已同步回補到 corrected contract
3. 後續 creator work 不再依賴 root entry-layer 假設
4. 若已進入 code alignment，相關測試已依實際變更範圍執行

## Historical Retention Note

即使 correction closed，本檔仍保留，作為後續流程改善與 decision audit 的歷史紀錄。
