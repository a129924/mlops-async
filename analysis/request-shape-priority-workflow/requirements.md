# Request Shape Priority Workflow Requirements

## Purpose

本文件凍結 `request-shape-priority-workflow` 的需求基線，目的是把 request-shape 工作的
session-entry surface、family dispatch order、Observer / Dispatcher 角色邊界與 review
節奏固定下來，降低工作在 shape discovery、workflow 討論與 review 排隊之間來回切換的成本。

## Scope

本 topic 的需求只涵蓋：

- session-entry docs contract
- cross-family dispatch board contract
- family queue 與 blocked policy
- Observer / Dispatcher routing 邊界
- `analysis/**` 與 `plan/**` 相對於 session-entry docs 的階層定位

本 topic 不涵蓋：

- `src/**`
- request-contract tests 內容實作
- response / error contract
- release 流程
- `tests/contracts` 功能擴張

## Actors and ownership

- Primary actor：workflow maintainer
- Secondary actor：human reviewer
- Consuming actor：new session Observer / Dispatcher

Ownership model：

- docs-first workflow governance with human review gate

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
   - Actor: new session Observer / Dispatcher
   - Condition: 新 session 進入 topic 時
   - Required outcome: 固定依序讀取：
     1. `docs/request-shape-priority-workflow/README.md`
     2. `docs/request-shape-priority-workflow/standards.md`
     3. `docs/request-shape-priority-workflow/checklist.md`
   - Metric / decision rule: 若順序被打亂、跳過任一文件、或直接從 `analysis/**` / `plan/**` 起步，視為不符合基線
   - Evidence signal: docs 與 workflow artifact 內都寫死相同順序
   - Failure meaning: session 會在 phase、queue、role boundary 尚未讀取前就誤進 planning 或 implementation

4. **Workflow artifacts are not primary entry**
   - Actor: workflow maintainer
   - Condition: 定義 topic artifact hierarchy 時
   - Required outcome: `plan/**` 與 `analysis/**` 被明確定義為 workflow artifacts，不是新 session 的 primary entry
   - Metric / decision rule: 若文件把 `analysis/**` 或 `plan/**` 當成 session 的第一讀入口，即不合格
   - Evidence signal: `README.md`、requirements、technical-spec、plan 一致宣告 docs-first hierarchy
   - Failure meaning: planning 工件與 session context 混疊，會提高恢復上下文成本

5. **Checklist as cross-family dispatch board**
   - Actor: workflow maintainer
   - Condition: 定義 `docs/request-shape-priority-workflow/checklist.md` 用途時
   - Required outcome: `checklist.md` 是跨 family 的 dispatch board，不與任何單一 topic 的 `*.step.md` 混用
   - Metric / decision rule: 若 checklist 被用來承載單一 topic implementation completion gate，即不合格
   - Evidence signal: checklist 只記錄 queue、phase、blocked reason、next dispatch、resume checks
   - Failure meaning: cross-family routing 與 topic-local completion gate 混在一起，review 邊界會失焦

6. **Family queue freeze**
   - Actor: workflow maintainer
   - Condition: request-shape family 排隊時
   - Required outcome: family queue 固定為：
     1. `models`
     2. `projects`
     3. `tables` = `BLOCKED`
   - Metric / decision rule: 若在無新人工決策下調整順序或自動解鎖 `tables`，視為超出基線
   - Evidence signal: docs / analysis / plan 皆記錄相同 queue
   - Failure meaning: queue 重新漂移後，review cadence 與風險排序就失去穩定性

7. **Observer / Dispatcher role boundary**
   - Actor: consuming Observer / Dispatcher
   - Condition: session 開始實際調度時
   - Required outcome: Observer / Dispatcher 只負責 state check、phase decision、dispatch、triage；不得直接做實作、改檔、commit、push、開 PR、或 release
   - Metric / decision rule: 若角色自行落手執行而非 dispatch，視為違反基線
   - Evidence signal: `standards.md` 對 allowed roles、禁止事項、dispatch rules 有明文 contract
   - Failure meaning: workflow 重新退回單代理混合作業，節奏不可審查

8. **Primary request-shape surface freeze**
   - Actor: workflow maintainer
   - Condition: 定義 family request-shape 工作面時
   - Required outcome: request-shape 主測試面固定為 `tests/unit/request_contract/**`
   - Metric / decision rule: 若把 `tests/contracts` 升格為 family request-shape 主面，即不合格
   - Evidence signal: standards 與 technical-spec 明確把 `tests/contracts` 定位為 policy / guard surface
   - Failure meaning: shape implementation 與 policy guard 混淆，會再次增加探索成本

## Contradictions surfaced and resolved

1. `analysis/**` / `plan/**` 已是 repo-visible artifact` vs `新 session 不應先從這裡起步`
   - Resolution: 保留它們作為 workflow artifacts，但 session 入口改由 docs trio 固定承擔

2. `checklist` 常被當作 completion gate` vs `這裡需要的是 cross-family queue`
   - Resolution: 此 topic 的 `checklist.md` 只做 dispatch board；單一 topic 的 completion gate 仍留在 `*.step.md`

3. `tables` 也屬 model-repository family` vs `目前無法安全放進 request-shape queue`
   - Resolution: `tables` 維持 `BLOCKED`，不因 queue completeness 而強行納入

## Extreme-boundary checks

1. **Missing docs**
   - 若 `README.md`、`standards.md`、`checklist.md` 任一缺失，必須先標記 planning insufficiency，而不是用 `analysis/**` / `plan/**` 補位

2. **Wrong entry path**
   - 若新 session 直接從 `analysis/**` 或 `plan/**` 進場，必須回頭走 docs-first entry order

3. **Queue skip**
   - 若要求在 `models` review / triage 未完成時直接推進 `projects`，視為 workflow drift

4. **Blocked family bypass**
   - 若要求在沒有新人工決策前自動推進 `tables`，必須停在 `human-check`

5. **Role collapse**
   - 若 Observer / Dispatcher 被要求直接實作、修 review comments、或做 publish / release，視為違反角色邊界

## Assumptions

- `models_request_gate` 已足夠作為 shape-only 模板 family
- `projects_request_gate` 是自然的下一批
- `tables` 的阻擋原因仍是 conditional endpoint selection / HATEOAS routing
- 本 topic 只處理 workflow governance，不修改 `src/**` 或測試行為

## Non-goals

- 不在此 topic 內修改 `src/**`
- 不在此 topic 內修改 request-contract tests
- 不在此 topic 內新增 response / error contract work
- 不在此 topic 內變更 release 流程
- 不在此 topic 內把 `tests/contracts` 轉成主 request-shape surface

## Blockers

本需求在目前範圍內無未決 blocker；若有人要求改 queue、解鎖 `tables`、或繞過 docs-first 入口，即進入 `human-check`

## Freeze status

Status: `FROZEN`
