# Model Repository Projects Champion Requirements

## 測試收集隔離修正

- `tests/unit/clients/projects/__init__.py` 是本 topic 唯一新增的測試 package boundary；它必須是空的 family-local package marker。
- 此 marker 只讓 Projects 的 `test_client.py` 取得不同於 Models sibling 的 module identity，以消除 full pytest collection 的同名 module collision。
- 它不改變任何 public API、runtime behavior、Models family 規則或其他測試目錄的 package policy；不得藉此擴大為 repo-wide 或 peer-family packaging 變更。

## 目標

在不改變既有 Models family 的前提下，為 `modelRepository/projects` 提供可測試的 read-only Projects client：單頁清單、依識別碼取得專案、全 repository 的精確名稱查找，以及 Champion metadata 與檔案參照。

## 證據邊界

- `projects_request_gate` 是 `sasctl-direct` request baseline，僅能支持 request implementation truth，不能證明 live runtime、auth/session 或 response semantics。
- `reference/legacy_code/.../utils/_api/project.py` 是無 remote 的 local snapshot；只提供 historical Champion metadata/file-reference 欄位線索，不能覆寫本 topic 的 public contract。
- `projects-spec.json` 與 upstream `modelRepository-openapi.yml` 用於端點/schema 路由；client request path 使用 gateway 的 `/modelRepository` 前綴。

## 可驗證需求

1. `ProjectsClient.list_projects(*, start: int = 0, limit: int = 20) -> ProjectsPage` 僅一次 GET `/modelRepository/projects`，傳送字串化 `start`/`limit`，不得自動抓下一頁。
2. `ProjectsClient.get_project(project_id: str) -> ProjectDetail` 驗證 non-empty identifier、使用 `EndpointPath.from_segments()`，且只一次 GET。
3. `ProjectsClient.get_project_by_name(name: str, *, page_size: int = 1000) -> ProjectSummary | None` 從 start 0 sequential pages 搜尋，只做精確 `==` name 比較；只有完整耗盡才回傳 `None`。
4. 每一頁皆須：固定 `count`、response `start` 等於 request start、response `limit` 等於 page_size、`count` 不變、`0 <= len(items) <= limit`。任何違反拋出 `ProjectsResponseError`；後續 request error 原樣傳播。
5. `ProjectsClient.get_champion(project_id: str) -> ChampionModel` 要求 Champion `id`、`name`、`scoreCodeType`；raw `files` 缺失時 materialize 空 tuple。`ChampionModel.files` 保留 `ChampionFile` tuple，且每一 file 的 `id`/`name` 是 caller-observable reference。
6. Projects 與 Models 是 peer endpoint families。Projects 不得 import、construct、inject 或以 type-only 方式依賴 Models；不得有任何 private cross-family orchestration、content result type 或 hidden download 行為。
7. `tach.toml` 是本 topic 的 bounded future configuration path：Projects package/client/value-objects 只可宣告對 `mlops_async.core`、`mlops_async.transport`、`mlops_async.exceptions` 的既有 direct-boundary dependencies；不得宣告 `mlops_async.clients.models` edge。
8. cross-family orchestration 完全由 caller 擁有：caller 在取得 `ChampionModel` 後，自行選擇是否呼叫 `ModelsClient.get_model_content(champion.id, file.id)`，以及自行選擇 gather、failure/cancellation 與 result aggregation policy。這些行為不是 Projects contract。
9. Project/Champion VOs 為 frozen、slotted、strictly typed 的語義資料，未知 raw fields 不能成為 public surface。
10. feature stage 不得改 `README.md`、`VERSION`、`pyproject.toml`。只有 separately authorized post-merge minor release 可處理 metadata；只有 release baseline 仍為 `v0.17.0`，candidate 才是 `v0.18.0`。

## 非目標

- 不加入 mutation、project tables、parallel page prefetch、retry、timeout、streaming、background work、server filter 或 live Viya E2E。
- 不改 `ModelsClient.get_model_content()`、Models public contract、Requester/auth/transport ownership，也不新增依賴。
- 不將 request gate 或 local legacy snapshot 當成 runtime response truth。
- 不在本 feature topic 發版或變更 metadata/release notes。
