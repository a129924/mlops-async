# tests-remove-nonessential-xxx-module-helpers — Requirements Baseline

## Status

**Frozen（可供 technical translation 使用）**

## Problem Statement

`tests/` 目前仍有大量 `*_module()` / `xxx_module` helper-style import 存在於一般行為測試，讓測試意圖與 import contract 驗證混淆，且可能透過 helper/fixture 形式規避規則。本 topic 需要在不修改 `src/` 前提下，建立全域可執行的移除與例外邊界。

## Frozen Inputs（已凍結）

1. 移除測試中的所有非必要 `*_module()` / `xxx_module` helper-style imports。
2. 唯一例外：測試目的為 import path / importability / import contract validation。
3. `patch-before-import` 不是一般豁免；仍僅能在第 2 點例外中使用。
4. 範圍是整個 `tests/` tree。
5. 零容忍驗收：行為測試中 helper-style usage 必須為 0；不可把 helper 邏輯移到 fixture 迴避政策。
6. 不修改 `src/`；僅做 tests semantic translation。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule |
| --- | --- | --- | --- | --- |
| BR-01 | 測試維護者 | 當案例屬於行為測試 | 不使用 `*_module()` / `xxx_module` helper-style import | `tests/` 行為測試檔案出現 helper-style usage 即不合格 |
| BR-02 | 測試維護者 | 當案例屬 import contract（path/importability/contract） | 可保留必要 import helper，但限於該目的 | 若非 import contract 目的而保留 helper，判定違規 |
| BR-03 | 測試維護者 | 當案例含 `patch-before-import` | 仍須先通過 import-contract 分類 | 未被分類為 import-contract 的 `patch-before-import` 一律違規 |
| BR-04 | Reviewer | 當執行全域稽核 | `tests/` 全樹完成分類：allowed / rewrite / BLOCKED | 三類清單缺一不可，缺少則不得標記 complete |
| BR-05 | Reviewer | 當遇到難以判定「行為測試 vs import-contract」 | 案例進入 BLOCKED，等待人工定版 | 不允許預設歸類；無穩定結論即 BLOCKED |
| BR-06 | Executor | 當需要驗證 `tests` scope 證據時 | 若存在 `tests/**` 變更，相關 evidence path 全部位於 `tests/**`；若沒有 `tests/**` 變更，此 guard 仍可通過 | 只有在觀察到 `tests/**` 變更時才檢查其 path 邊界；不得把「必須有 `tests/**` 變更」當成通過前提 |
| BR-07 | Reviewer | 當驗收完成 | 行為測試 helper-style usage = 0，且無 fixture 轉移規避 | 偵測到 helper 轉移到 fixture/helper wrapper 仍判違規 |

## Assumptions

1. 既有 `tests/contracts/` 可承接 import contract 類測試。
2. 人工 recheck 角色可對 BLOCKED 案例做語意判定並回填決策。
3. 本次交付的是 `tests/**` rewrite topic 的需求/規格基線；實作改寫會在後續 implementation phase 依此文件落地。
4. `BR-06` 是 `tests` scope evidence guard，不等同於「整個 patch 必須 tests-only」或「一定要有 `tests/**` 變更」。

## Non-goals

1. 不變更 `src/` 模組結構、公開 API、runtime import 行為。
2. 不修改 CI/release 流程。

## Contradiction Register

| ID | Statement A | Statement B | Conflict | Resolution |
| --- | --- | --- | --- | --- |
| CR-01 | import-contract 可使用 helper-style import | 行為測試零容忍 helper-style | 邊界模糊時易誤放寬 | 無法判定即 BLOCKED，待人工 recheck |
| CR-02 | patch-before-import 可在特定測試必要 | patch-before-import 不是一般豁免 | 容易被當成通用例外 | 凍結規則：僅在 import-contract 案例可接受 |

## Blockers

| ID | Type | Description | Required Human Input |
| --- | --- | --- | --- |
| B-01 | Classification ambiguity | 個別測試無法穩定判定為行為測試或 import-contract | 指定 reviewer/owner 進行人工分類定版 |
| B-02 | Scope breach risk | 為移除 helper-style usage 而提議變更 `src/` | 明確否決或重新定義 topic scope |

## Freeze Decision

- 本需求基線已凍結，可進 technical translation。
- 任何觸發 B-01 的案例必須走 **BLOCKED**，不可自動放行。
