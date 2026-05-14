# Contributing

## Development workflow

1. Sync dependencies with `uv sync`.
2. Install commit hooks with `uv run pre-commit install`.
3. Make changes inside `src/mlops_async/` and `tests/`.
4. Run local checks before pushing:
   - `uv run pytest`
   - `uv run pyright`
   - `uv run ruff check .`
   - `uv run ruff format .`
   - `uv run tach check`
   - `uv run pre-commit run --all-files`

`pre-commit` 會在 commit 前攔截使用者家目錄型態的本機絕對路徑。若文件需要保留
環境中立的本機參考位置，請改用 `<LOCAL_LEGACY_SERVICE_CODE_PATH>` 這類佔位符。
它現在也會執行 `tach check`，確保 `src/mlops_async/` 的模組依賴邊界沒有被破壞。

## Tach 結構治理

- `tach.toml` 是本 repo 的 Python 結構邊界設定來源
- 目前採 **incremental** 方式，只治理現有的 `mlops_async` 與
  `mlops_async._repo_hooks`
- 若未來新增新的 package/module，應先更新 `tach.toml`，再導入新的跨模組 import

## Quality expectations

- All I/O code must stay async-first
- Public APIs must be fully typed
- Unit tests must avoid external I/O
- Integration tests may talk to a real SAS Viya environment
- Coverage target is `>= 90%`

## Contract-first API porting

當你要從 `sasctl` 或 legacy SDK 平移行為時：

1. 先從 `analysis/api-client-porting-contract/requirements.md` 與 `analysis/api-client-porting-contract/technical-spec.md` 開始。
2. 使用 `api-client-porting-planner` 產生 source evidence、request contract drafts、risk classification、porting order 與 stop flags。
3. 只有在 request contract evidence 已經存在後，才能使用 `api-client-porting-implementer`。
4. 在 minimal implementation 之前，先寫 request-contract tests。
5. 先把 source API -> target async API 的對照狀態更新到 `docs/migration-map.md`。
6. 每個 ported API 都要更新 `docs/porting-ledger.md`，之後才能宣告 compatibility。
7. `docs/migration-map.md` 用於集中追蹤 mapping、狀態與 review notes；`docs/porting-ledger.md` 用於完整證據。
8. 當 source behavior、response schema、pagination、polling、upload/download、streaming 或 global session side effects 不清楚時，停止並交給人工 review。

## Project goal and guidelines

開始新 topic 前，先閱讀：

1. `docs/project-goal.md`
2. `docs/project-guidelines.md`

若任務需求與上述文件衝突，先更新治理文件，再進行實作或 porting。

## Git conventions

- Prefer short-lived topic branches
- Use semantic commit messages
- Keep commits atomic and reviewable
- For larger or parallel topics, prefer worktree + feature branch isolation from `dev`

### Language policy

本 repo 以繁體中文為一般內文預設語言，規則如下：

- **一般內文**（治理文件、analysis / plan 文件、repo 專屬說明）→ 繁體中文
- **五類固定項目**可保留既有英文原文，不受繁中預設限制：
  1. canonical section headings（存在於既有模板或 workflow 的固定章節標題）
  2. plan / step tracker 固定章節名稱
  3. fixed labels（狀態標籤、欄位名稱等）
  4. workflow names（GitHub Actions 等 CI/CD pipeline 名稱）
  5. 必要 canonical terms（技術術語或專有名詞）
- **不確定情況**：若無法可靠判定某個標題 / label / workflow name / canonical term 是否屬於上述五類，預設保留既有 canonical English，而非自動翻譯。此預設僅限疑似固定項目，不適用於一般敘述內文。
- **commit / PR / Issue 標題**的語言政策另行規範，本節不處理。
- 完整決定規則見 `.github/copilot-instructions.md` 的 `Language Requirement` 一節，兩者為同一政策的正式來源，不得互相矛盾。

## Source of truth

- `pyproject.toml` — dependencies and tool configuration
- `blueprint.md` — initialization contract and acceptance criteria
- `analysis/` — repo-visible requirements and technical specs for governed topics
- `plan/` — repo-visible implementation plans and step trackers
- `.github/copilot-instructions.md` — AI-facing coding rules
- `.github/skills/` — detailed skill-level guidance
- `.github/agents/` — workflow orchestration guidance for multi-phase implementation work
- `docs/project-goal.md` — 專案目標、成功定義與非目標
- `docs/project-guidelines.md` — 專案執行準則與 topic workflow 規範
- `docs/migration-map.md` — source API 到 target async API 的集中遷移對照表
- `docs/porting-ledger.md` — API porting evidence and compatibility ledger
