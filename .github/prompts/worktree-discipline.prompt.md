---
name: worktree-discipline
description: Enforce execution inside the user-specified worktree. Use this when the worktree path is already chosen and the task must not drift back to the main repo or another worktree.
---

若使用者已指定某個 worktree path，後續所有讀寫、測試、git 指令都必須在該 worktree 內進行。

## Rules

1. 把使用者指定的 worktree path 視為本輪唯一有效工作目錄。
2. 除非使用者明確要求，**不要切回主 repo，也不要改在其他 worktree 執行**。
3. 若目前 shell / git context 不在該 worktree，先切換或先回報 blocked，再繼續。
4. 若該 worktree 狀態不明、存在未預期髒樹、branch/base 不符、或該 path 並非有效 worktree，先停下並回報，不要自行改在主 repo 執行。
5. 若使用者同時提供多個 worktree path，先要求對方明確指定本輪唯一目標 worktree，再開始動作。

## Output expectation

- 回報時明確指出你實際操作的 worktree path。
- 若無法遵守 worktree 邊界，直接回報 blocked，不要用主 repo 代做。
