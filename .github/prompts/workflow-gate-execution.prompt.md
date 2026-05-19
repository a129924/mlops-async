---
name: workflow-gate-execution
description: Enforce visible reviewer/creator subagent execution when the user explicitly requires a /fleet workflow gate.
---

若使用者明示 reviewer / creator 必須透過 `/fleet` 啟動可見 subagent，必須實際遵守該 gate。

## Rules

1. reviewer 與 creator 必須各自成為可見的獨立 subagent。
2. **不可只載入 skill、不可自行扮演 reviewer / creator、不可把兩個角色合併成單一隱形流程。**
3. 若使用者要求 `/fleet @...reviewer` / `/fleet @...creator`，就必須真的啟動對應 subagent，再由主流程整合結果。
4. 若工具、環境、或權限限制使你無法滿足上述要求，先明確回報 blocked，再等待使用者決定；不要假裝已依規範完成 workflow gate。
5. 若使用者另外要求 `/tasks` 或等價介面中必須看得到對應 agent，且目前做不到，也必須先回報 blocked。

## Output expectation

- 回報時清楚區分：
  - 哪個 reviewer subagent 被啟動
  - 哪個 creator subagent 被啟動
  - 主流程只負責整合，不取代 reviewer / creator 的角色
