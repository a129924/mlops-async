# Request Shape Priority Workflow Requirements

## Purpose

本文件凍結 `request-shape-priority-workflow` 的需求基線，目的是把 request-shape 工作的
session-entry surface、`surface + API` 實作順序、共享 implementation board、與 review
節奏固定下來，降低多個 session 同時工作時的狀態污染與接口排序混亂。

## Scope

本 topic 的需求只涵蓋：

- session-entry docs contract
- session resume checklist template contract
- global surface/API implementation board contract
- `surface + API` queue 與 blocked policy
- `analysis/**` 與 `plan/**` 相對於 session-entry docs 的階層定位
- `standards.md` 作為實作標準文件的責任邊界

本 topic 不涵蓋：

- `src/**`
- request-contract tests 內容實作
- response / error contract
- release 流程
- `tests/contracts` 功能擴張

## Actors and ownership

- Primary actor：workflow maintainer
- Secondary actor：human reviewer
- Consuming actor：new session maintainer / implementer / reviewer

Ownership model：

- docs-first workflow governance with shared implementation board

## Measurable requirements

1. **Canonical session-entry artifacts freeze**
   - Actor: workflow maintainer
   - Condition: 新 session 需要進入 `request-shape-priority-workflow` topic 時
   - Required outcome: canonical session-entry artifacts 固定為：
     - `docs/request-shape-priority-workflow/README.md`
     - `docs/request-shape-priority-workflow/standards.md`
     - `docs/request-shape-priority-workflow/checklist.md`
   - Metric / decision rule: 若新 session 需要從其他 surface 起步，或上述三份文件缺任一，即不符合基線
   - Evidence signal: 三份文件存在且被明示為唯一 primary entry set
   - Failure meaning: session 入口不固定時，後續工作會回到臨時口述與對話記憶

2. **README requiredness**
   - Actor: workflow maintainer
   - Condition: 建立 session-entry surface 時
   - Required outcome: `README.md` 是必需 artifact，不是選配
   - Metric / decision rule: 若 `standards.md` 與 `checklist.md` 存在，但 `README.md` 不存在或被視為 optional，即不合格
   - Evidence signal: requirements、technical-spec、plan、docs 皆一致宣告 `README.md` required
   - Failure meaning: 缺少固定第一入口時，新 session 無法快速取得 artifact hierarchy

3. **Fixed entry order**
   - Actor: new session maintainer / implementer / reviewer
   - Condition: 新 session 進入 topic 時
   - Required outcome: 固定依序讀取：
     1. `docs/request-shape-priority-workflow/README.md`
     2. `docs/request-shape-priority-workflow/standards.md`
     3. `docs/request-shape-priority-workflow/checklist.md`
   - Metric / decision rule: 若順序被打亂、跳過任一文件、或直接從 `analysis/**` / `plan/**` 起步，視為不符合基線
   - Evidence signal: docs 與 workflow artifact 內都寫死相同順序
   - Failure meaning: session 會在排序與實作標準尚未讀取前就誤進 planning 或 implementation

4. **Workflow artifacts are not primary entry**
   - Actor: workflow maintainer
   - Condition: 定義 topic artifact hierarchy 時
   - Required outcome: `plan/**` 與 `analysis/**` 被明確定義為 workflow artifacts，不是新 session 的 primary entry
   - Metric / decision rule: 若文件把 `analysis/**` 或 `plan/**` 當成 session 的第一讀入口，即不合格
   - Evidence signal: `README.md`、requirements、technical-spec、plan 一致宣告 docs-first hierarchy
   - Failure meaning: planning 工件與 session context 混疊，會提高恢復上下文成本

5. **Shared resume checklist must be template-only**
   - Actor: workflow maintainer
   - Condition: 定義 `docs/request-shape-priority-workflow/checklist.md` 用途時
   - Required outcome: session resume checklist 只能作為 template，不得在共享文件直接打勾
   - Metric / decision rule: 若共享 `checklist.md` 出現可直接被多個 session 共用勾選的 resume checkbox，即不合格
   - Evidence signal: checklist 明寫「請複製到 session-local artifact 後再使用」
   - Failure meaning: 多個 session 會互相誤讀共享勾選狀態

6. **Global surface/API implementation board**
   - Actor: workflow maintainer
   - Condition: 定義 `docs/request-shape-priority-workflow/checklist.md` 的共享真值表面時
   - Required outcome: `checklist.md` 必須包含一個 `surface + API` 級 implementation board
   - Metric / decision rule: board 至少要有 `State`、`Surface`、`API`、`Order`、`Injection hint`、`Notes`
   - Evidence signal: session 可直接依 board 指定下一個 interface surface、順序、與注入內容
   - Failure meaning: 多 session 難以共享哪個 concrete surface 先做、哪個 surface 已完成

7. **Surface / API queue freeze**
   - Actor: workflow maintainer
   - Condition: request-shape `surface + API` 排隊時
   - Required outcome: queue 必須以明確 base API surface 表示，至少區分：
     - `modelRepository/models`
     - `modelRepository/models/content`
     - `modelRepository/projects`
     - `modelRepository/projects/champion`
     - `modelRepository/projects -> tables-link surface`
     - `jobExecution/jobRequests/jobs`
     - `jobExecution/jobs`
     - `jobExecution/jobs/state`
   - Metric / decision rule: 若在無新人工決策下使用抽象 `tables` 代表多套 surface、調整既定順序、或自動解鎖 blocked surface，視為超出基線
   - Evidence signal: docs / analysis / plan 皆記錄相同 queue；board 由上而下可讀，且 `tables` 不再被單獨使用
   - Failure meaning: queue 重新漂移後，review cadence 與注入順序都失去穩定性

8. **Standards must stay implementation-focused**
   - Actor: workflow maintainer
   - Condition: 定義 `docs/request-shape-priority-workflow/standards.md` 內容時
   - Required outcome: `standards.md` 必須是 implementation standards，不得寫成 workflow handoff prompt 或角色扮演腳本
   - Metric / decision rule: 若文件主體落在 persona、allowed subAgent list、或 prompt-style output guidance，即不合格
   - Evidence signal: `standards.md` 主體只記錄實作順序、board / step 分工、blocked policy、artifact precedence、與 request-shape scope
   - Failure meaning: 標準文件會偏成 prompt，而不是可長期維護的 repo-visible contract

9. **Primary request-shape surface freeze**
   - Actor: workflow maintainer
   - Condition: 定義 request-shape 工作面時
   - Required outcome: request-shape 主測試面固定為 `tests/unit/request_contract/**`
   - Metric / decision rule: 若把 `tests/contracts` 升格為本 workflow 的 request-shape 主面，即不合格
   - Evidence signal: standards 與 technical-spec 明確把 `tests/contracts` 定位為 policy / guard surface
   - Failure meaning: shape implementation 與 policy guard 混淆，會再次增加探索成本

## Contradictions surfaced and resolved

1. `analysis/**` / `plan/**` 已是 repo-visible artifact` vs `新 session 不應先從這裡起步`
   - Resolution: 保留它們作為 workflow artifacts，但 session 入口改由 docs trio 固定承擔

2. `checklist` 常被當作 completion gate` vs `這裡需要的是共享 implementation board`
   - Resolution: `checklist.md` 分成 template 與 board 兩個共享用途；單一 topic completion gate 仍留在 `*.step.md`

3. `standards.md` 需要規則` vs `不能退化成 prompt`
   - Resolution: 只保留實作順序、artifact precedence、board / step 邊界、與 blocked policy，不保留 prompt 化 persona

4. `tables` 是既有業務詞` vs `repo 內其實同時存在不同 tables surface`
   - Resolution: 停止使用抽象 `tables` 當 queue 單位；改成明確區分 `modelRepository/projects -> tables-link surface` 與 `casManagement/.../tables`

## Extreme-boundary checks

1. **Missing docs**
   - 若 `README.md`、`standards.md`、`checklist.md` 任一缺失，必須先標記 planning insufficiency，而不是用 `analysis/**` / `plan/**` 補位

2. **Shared-check pollution**
   - 若共享 `checklist.md` 出現直接勾選的 session resume 狀態，必須改回 template-only

3. **Queue skip**
   - 若要求在前一個 API / surface 未完成時直接推進下一列，視為 workflow drift

4. **Blocked surface bypass**
   - 若要求在沒有新人工決策前自動推進 `modelRepository/projects -> tables-link surface` 或 `jobExecution/jobs/state`，必須停在 `human-check`

5. **Prompt drift**
   - 若 `standards.md` 被重新寫成 handoff prompt、persona、或 subAgent 腳本，視為違反本 topic 邊界

## Assumptions

- `models_request_gate` 已足夠作為 `modelRepository/models` 的 shape-only 模板
- `projects_request_gate` 已足夠作為 `modelRepository/projects` 的既有 precedent
- `modelRepository/projects -> tables-link surface` 的阻擋原因仍是 conditional endpoint selection / HATEOAS routing
- `casManagement/.../tables` 與 `SASLogon/oauth/token` 雖存在於 repo surface，但本輪維持 `OUT-OF-SCOPE`
- 本 topic 只處理 workflow governance，不修改 `src/**` 或測試行為

## Non-goals

- 不在此 topic 內修改 `src/**`
- 不在此 topic 內修改 request-contract tests
- 不在此 topic 內新增 response / error contract work
- 不在此 topic 內變更 release 流程
- 不在此 topic 內把 `tests/contracts` 轉成主 request-shape surface

## Blockers

本需求在目前範圍內無未決 blocker；若有人要求改 queue、重新把 `tables` 當抽象單位、解鎖 blocked surface、把共享 template 當成真值勾選、或把 `standards.md` 重新寫成 prompt，即進入 `human-check`

## Freeze status

Status: `FROZEN`
