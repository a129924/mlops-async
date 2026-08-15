# Viya refresh-token E2E rerun

## Analysis-layer routing

`analysis/viya-password-token-e2e/requirements.md` 與
`analysis/viya-password-token-e2e/technical-spec.md` 均存在，但其舊有範圍不適用於本輪。
Human 已明確 override：

> 本輪以 `tests/integration/test_viya_password_token_e2e.py`、
> `tests/integration/viya_e2e_vpn.py`、
> `tests/unit/integration/test_viya_e2e_vpn.py` 的 E2E/VPN-preflight 範圍，取代
> `analysis/viya-password-token-e2e/technical-spec.md` 的舊 artifact 範圍。

因此本 plan 的 execution scope 只由此 override、目前 target worktree diff 與本文件
的 Locked Decisions 決定；requirements 僅作為歷史 business context，不是本輪 artifact
或實作範圍。任何超出下列四個 Artifact Paths 的工作都必須先取得新的 planning
alignment。

## Goal / Outcome

- 將既有 Viya refresh-token live E2E 的 VPN preflight 與其 unit coverage，作為單一、
  test-only topic 完成獨立審查與 PR 準備。
- 維持 refresh-token E2E 的明確 live opt-in 與秘密保護，不變更 runtime auth contract。

## Scope

- **In scope**:
  - `tests/integration/test_viya_password_token_e2e.py` 的 refresh-token E2E test-only
    調整。
  - `tests/integration/viya_e2e_vpn.py` 的 VPN preflight helper。
  - `tests/unit/integration/test_viya_e2e_vpn.py` 對 VPN preflight helper 的 unit tests。
  - 本 topic plan 的 review routing、證據語意與 PR 準備合約。

- **Out of scope**:
  - production runtime、public API、auth client contract、config loader、pytest global
    configuration、CI workflow 或任何非上述三個 test files 的程式碼。
  - `config/.env.test` 的讀取、輸出、stage、commit 或修改；它是秘密且只可作為 opaque
    runtime input，不是本 topic 的 artifact。
  - live E2E rerun，除非後續變更相關測試或設定，且先取得新的單次 live authorization
    與 fresh VPN confirmation。
  - merge、release、tag、VERSION/README/lockfile 更新，以及任何 worktree／branch cleanup。

## Locked Decisions

- 本輪只允許修改或提交 Artifact Paths 表列出的 topic plan 與三個 test files；不得以
  analysis 的舊 artifact inventory 擴張範圍。
- 目標 worktree 為
  `D:\code\python\mlops-async.worktrees\agent-20260803-viya-refresh-token-e2e-rerun`，
  branch 為 `feat/andrew/viya-refresh-token-e2e-rerun`，baseline HEAD 為
  `9efa8cfc0a41118b57affce63e4119ec8165e703`。
- 舊 worktree
  `D:\code\python\mlops-async.worktrees\agent-20260729-viya-refresh-token-e2e` 是
  evidence-only；不得讀寫、reset、clean、commit、刪除或以其他方式處理。
- VPN preflight 僅判斷進行 live E2E 前所需的可達性條件；它不得傳送 credentials、token
  或修改 runtime auth 行為，亦不得把可達性誤報為 token E2E 成功。
- `config/.env.test` 必須保持 opaque。不得在 code、test output、plan evidence、Git diff、
  staging 或 commit 中揭露或納入其內容。
- 本 topic 明確不影響 stable-library surfaces：不修改 `README.md`、`VERSION`、release
  notes、lockfile 或 release timing，因此不適用 `Stable library metadata`。

## Boundaries / Exclusions

- Plan-Creator 只維護 plan；Creator 只處理三個 test files；Plan-Reviewer、implementation
  reviewer、code reviewer 與 Main Agent 各自獨立執行其 gate。
- Main Agent 才能於所有必要 review 通過後，路由 commit、push、Ready PR、CI observation
  與 merge eligibility；此 plan 不授權其中任何動作。
- review-ready、PR CI 綠燈與已完成 required review 都不等於 merge authorization。
- Windows host 上所有 Python、uv、pytest、Pyright 或 Ruff project tooling 必須透過 WSL
  執行；不得使用 Windows Python。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Reason**: Plan-Creator 已依 Human override 將 artifact scope、角色界線、驗證證據與
  publication routing 收斂；下一步是獨立 Plan-Reviewer 審查。
- **Execution model**: Plan-Reviewer approved 後，先進行 implementation review，再進行
  code review；兩者通過後才由 Main Agent 進入 `publish-in-progress`，commit、push 並開
  Ready PR。PR 只有在 CI 通過且所需 review 完成時才具備被考慮 merge 的資格；merge、
  release、tag、version/lockfile 與 cleanup 全部是本輪外的獨立授權 gate。
- **Allowed transitions**:
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- Plan-Reviewer 的 `needs-rework` 只回到 Plan-Creator 進行 bounded plan correction，
  然後重新獨立審查。
- implementation review 或 code review 的 rework 只由 Creator 修正三個 test files，
  再重跑相應 review；不得藉此擴張 artifact scope。
- 完成 PR CI 與 required review 前不得 merge。即使兩者完成，merge 仍需另一項明確
  authorization，並且本 plan 不包含任何 post-merge action。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/viya-password-token-e2e/viya-password-token-e2e.plan.md` | Planning actor | Human override 下的 repo-visible execution and review contract |
| Refresh-token E2E | `tests/integration/test_viya_password_token_e2e.py` | Creator | Test-only live refresh-token E2E 與 VPN preflight integration |
| VPN preflight helper | `tests/integration/viya_e2e_vpn.py` | Creator | 不含秘密的 VPN reachability preflight |
| VPN preflight unit tests | `tests/unit/integration/test_viya_e2e_vpn.py` | Creator | Preflight success/failure behavior 的 isolated unit coverage |

Artifact path notes:

- `config/.env.test` 是秘密與 opaque runtime input，不是 artifact；不可讀出、輸出、
  stage、commit 或列入此表。
- 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`、lockfile、release
  notes、CI workflow、config 或任何其他檔案。
- 若 diff 出現未列出的路徑，必須停止 publication routing 並先回到 plan alignment。

## Implementation Steps

1. Creator 僅在三個 test artifacts 內，保留或修正 refresh-token E2E 對 VPN preflight 的
   test-only integration；不得變更 production/runtime contract 或讀取秘密內容。
2. Creator 在 `tests/integration/viya_e2e_vpn.py` 實作可測的非秘密 VPN preflight，並在
   `tests/unit/integration/test_viya_e2e_vpn.py` 覆蓋其 success、unreachable 與不把
   preflight 當作 token success 的行為。
3. Creator 確保 `tests/integration/test_viya_password_token_e2e.py` 維持 explicit live
   opt-in；除非已同時取得新的單次 live authorization 與 fresh VPN confirmation，
   不得重跑 live E2E。
4. Creator 在相關測試或設定有變更時，以 WSL 執行被影響的 non-live validation；任何
   live rerun 只有在前項兩個 fresh gates 都滿足時才可執行，並必須維持秘密 redaction。

## Validation / Acceptance Checks

- Review diff 只包含本 plan 與三個 test artifacts；沒有 secret、runtime/public-contract
  drift、config、CI、release 或 scope drift。
- `config/.env.test` 未被讀出、輸出、stage 或 commit；其設定值不會出現在 test output
  或 evidence。
- 既有 Linux ext4 detached checkout non-live suite evidence 為
  `413 passed, 9 skipped, 1 deselected`；這是既有 evidence，非聲稱本 worktree 本輪
  已重新執行的結果。
- 目標 worktree 的 Linux Python evidence 為 `3.10.20`；後續 Python tooling 僅經 WSL。
- 最新一次已授權 live E2E 的 test result 為 `1 passed, 1 warning`。該單檔 pytest
  process exit `1` 的唯一原因是全域 coverage gate `65.26% < 90%`，不表示 E2E
  functionality 失敗，也不表示完整 pytest suite 綠燈。
- config loader 已以唯讀方式驗證可成功載入；不得輸出任何設定值。
- 若後續變更相關測試或設定，live E2E 只能在新的單次 live authorization 與 fresh VPN
  confirmation 後執行；沒有這兩項時，live validation 必須報告為未授權而非 pass/skip
  success。
- Plan-Reviewer 應驗證 canonical section order、`review-ready` current status、JSON
  handoff shape、artifact path exactness，以及本輪確實採用 Human override。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- 本輪沒有已授權的 post-merge 或 release action。不得在 merge 前開始 post-merge 工作。
- merge、release、tag、VERSION/README/lockfile 更新與 worktree/branch cleanup 都在本輪
  授權範圍外，需另行明確 authorization。

## Open Questions / Unresolved Items

- 無阻擋 plan review 的未決問題。
- live rerun 如因後續相關測試或設定變更而需要，仍須取得新的單次 live authorization 與
  fresh VPN confirmation；在那之前不執行。
