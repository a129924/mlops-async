# Windows WSL pre-commit bridge 操作指南

## 目的與範圍

此 bridge 讓 Windows Git 保持負責 commit 與 hook dispatch，但在 worktree 明確 opt-in 時，改由選定的 WSL distro 執行 Linux `.venv/bin/python`、`uv` 與 pre-commit。它不會使用 Windows Python，也不會建立 virtualenv、同步相依套件、修改 Git config 或 fallback 至 `.git/hooks`。

未啟用 `hooks.wslRunner` 的 worktree 保持既有行為：`.githooks/pre-commit` 會從 Windows `PATH` 執行 `pre-commit hook-impl`。

## 唯讀 preflight

在實作、啟用或驗收前，必須在目前 checkout 執行下列唯讀檢查：

```powershell
git config --show-origin --get-all core.hooksPath
git --version
git rev-parse --show-toplevel
git rev-parse --absolute-git-dir
Get-Content .githooks/pre-commit
```

`core.hooksPath` 必須只有一個值，且恰為 `.githooks`。它不存在、重複、指向其他路徑或無法讀取時，必須停止。本 topic 不設定或修正它，也不會改用 `.git/hooks`。

## Worktree config：human-gated 啟用與設定

Git metadata 是 local state，啟用 `extensions.worktreeConfig` 與寫入 worktree config 都需要獨立 human gate。先確認目前 Git 能支援、目前值可讀，接著才可依下列順序執行：

```powershell
git --version
git config --get extensions.worktreeConfig
git config extensions.worktreeConfig true
git config --get extensions.worktreeConfig
git config --worktree hooks.wslRunner false
git config --worktree --get-all hooks.wslRunner
```

必須確認設定讀回為 `true`，並確認目標 worktree 的設定檔已能建立及讀回；任一步失敗即停止，不能改用 `--local`。接著，僅在要使用 bridge 的目標 worktree 設定：

```powershell
git config --worktree hooks.wslRunner true
git config --worktree hooks.wslDistro Ubuntu
```

`hooks.wslRunner` 缺失代表 `false`，且只接受單一 `true` 或 `false`。`hooks.wslDistro` 若存在，必須是單一非空值。重複、空白、無效或讀取失敗都會使 hook 以非零停止；bridge 不會猜取最後一個值。停用可設為 `false`，或在確認沒有其他同名值後使用 `git config --worktree --unset-all hooks.wslRunner`。

## WSL 選擇與 Git metadata

WSL distro 依下列順序選擇：

```text
hooks.wslDistro -> CODEX_WSL_DISTRO -> WSL default distro
```

明確指定或預設 distro 不可用、`wslpath` 不可用、無預設 distro 或 Linux virtualenv 不可用時，bridge 都會明確失敗，且沒有 Windows Python fallback。

bridge 先由 Windows Git 取得 Windows 絕對 worktree root 和實際 gitdir，再由選定 distro 的 `wslpath` 轉換。這同時支援一般 clone 的 `.git` directory 與 linked worktree 的 `.git` pointer；WSL 不會先對 Windows linked-worktree `.git` pointer 執行 `git rev-parse`。執行 Linux 子程序前會注入轉換後的 `GIT_DIR` 與 `GIT_WORK_TREE`。

## Linux 執行契約與失敗行為

bridge 會先確認以下 Linux executable 存在：

```text
.venv/bin/python
```

bridge 在解碼 payload 前也會確認選定 WSL distro 的 `base64` 位於 `PATH`；缺少時會以明確訊息非零停止，且沒有 Windows Python fallback。

然後只執行：

```text
uv run --frozen --no-sync python -m pre_commit hook-impl --config=.pre-commit-config.yaml --hook-type=pre-commit -- <hook arguments>
```

hook arguments 與子程序 exit code 都會原樣傳遞。任何 Git、worktree config、WSL、distro、`wslpath`、Linux virtualenv、`base64`、`uv` 或 pre-commit 失敗都會非零停止，不會改用 Windows Python、`--local`、`.git/hooks` 或自動修正設定。

formatter 若回寫 Windows worktree 的檔案，pre-commit 依既有行為會讓當次 commit 失敗。使用者必須檢視並重新 stage 寫回的檔案後，才可重試 commit。
