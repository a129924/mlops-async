# Project Guidelines

## Scope and authority

專案決策的優先順序如下：

1. `docs/project-goal.md`
2. `docs/project-guidelines.md`
3. `analysis/api-client-porting-contract/requirements.md`
4. `analysis/api-client-porting-contract/technical-spec.md`
5. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
6. `plan/api-client-porting-contract/api-client-porting-contract.step.md`

若新任務與上述文件衝突，先停下並更新文件，再進入實作。

## Contract-first execution rules

1. 先做 source discovery 與 request contract extraction。
2. request tests 必須先於 minimal implementation。
3. response / error contract 在 request gate 通過後才可展開。
4. compatibility label 不可任意擴張，必須與證據一致。

## Migration evidence order

每個 API 工作項目都要遵守：

1. 先更新 `docs/migration-map.md`（mapping 與狀態）。
2. 再更新 `docs/porting-ledger.md`（完整證據與決策）。

## Labels contract

### Compatibility labels

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

### Decision labels

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

## Stop conditions (must pause for human review)

遇到以下任一條件，必須停止自動擴展：

1. upload/download
2. streaming
3. polling / wait-loop
4. pagination expansion with hidden behavior
5. global session side effects
6. conditional endpoint selection
7. unclear source behavior or unclear response schema

## Git workflow policy

每個 topic 固定流程：

1. 以 `dev` 為 base 建立獨立 feature branch（可搭配 worktree）。
2. 在 topic 範圍內分批 commit / push。
3. 開 ready PR 到 `dev`。
4. 停在 wait-human-merge。
5. merge 後再做 post-merge cleanup 與必要 release。

## Staging policy

1. 只 stage 本 topic 允許檔案。
2. 禁止使用 `git add -A` 或 `git add .`。
3. 如果工作樹有其他既有未提交變更，需保持隔離，不可混入 topic commit。
