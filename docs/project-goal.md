# Project Goal

## Mission

`mlops-async` 的使命是把既有 `sasctl` / legacy SDK 的可用能力，以
**contract-first、async-first、可追溯** 的方式平移成可維護的 Python library。

## Success criteria

這個專案達標時，至少應符合：

1. 主要 API 平移流程遵守 request-contract-first，且有對應測試。
2. 每個已處理 API 都能在 `docs/migration-map.md` 與 `docs/porting-ledger.md`
   找到一致且可追溯的紀錄。
3. 高風險情境（streaming、polling、upload/download、隱性 side effects）會被明確
   停下並交人工決策，而非自動硬做。
4. 公開介面維持 async-first、型別明確、錯誤處理可預期。

## Non-goals

目前不以以下事項為目標：

1. 一次性達成所有 `sasctl` 與 legacy SDK 功能全覆蓋。
2. 在無 source evidence 的情況下推測 endpoint 行為。
3. 為了短期速度跳過 migration map / ledger / request tests。
4. 在單一 topic 內同時做大規模架構重寫與 API 平移。

## Phase boundary

目前階段聚焦：

1. 固化治理與 workflow（planner / implementer / migration map / ledger）。
2. 以 family 為單位逐步平移與驗證。

尚未進入：

1. 全面 feature parity 宣告。
2. 大範圍公共 API 穩定版承諾。

## Definition of done (topic level)

每個 porting topic 結束時至少要有：

1. request-contract tests（先於 implementation）。
2. migration-map row 更新。
3. ledger entry 更新。
4. 明確 decision label：`continue`、`stable`、`needs-human-review`、`blocked`。
