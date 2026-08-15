# Model Repository Projects Champion Technical Specification

## Test collection isolation

- Implement exactly one empty family-local package marker at `tests/unit/clients/projects/__init__.py` before the Projects test modules are collected.
- The marker gives `tests/unit/clients/projects/test_client.py` a family-qualified module identity distinct from the existing Models sibling `test_client.py`, so full pytest collection does not raise an import-file-mismatch collision.
- This is test-collection infrastructure only: it changes neither public/runtime behavior nor the Projects/Models peer-family boundary. Do not add or require a Models marker, parent-package marker, or repo-wide test packaging change in this topic.

## Analysis routing

- 模式：strict；human override 已明確取代既有 aggregate scope。
- Business guardrail：`analysis/model-repository-projects-champion/requirements.md`。
- Execution source of truth：本 technical spec；它完整轉譯 corrected requirements。
- Human override：Projects / Models 是 peer endpoint families；只保留 Projects list/get/exact lookup/champion metadata，移除所有 cross-family aggregate。

## D1 verdict

```json
{"verdict":"non-trivial","reason":"新增 public async Projects family，以及帶有跨頁不變量的 repository-wide sequential exact-name lookup。"}
```

## Public contract 與實作落點

新增 `mlops_async.clients.projects` family package，只在其 `__init__.py` re-export；不得在 `mlops_async.clients` 或 root 建 shortcut。

```python
class ProjectsClient:
    def __init__(self, requester: Requester) -> None: ...
    async def list_projects(self, *, start: int = 0, limit: int = 20) -> ProjectsPage: ...
    async def get_project(self, project_id: str) -> ProjectDetail: ...
    async def get_project_by_name(self, name: str, *, page_size: int = 1000) -> ProjectSummary | None: ...
    async def get_champion(self, project_id: str) -> ChampionModel: ...
```

`ProjectsResponseError` 維持繼承 `MlopsAsyncBaseException`，只處理 semantic response/invariant errors。public VOs 僅包含 `ProjectSummary`、`ProjectDetail`、`ProjectsPage`、`ChampionFile`、`ChampionModel`。`ChampionModel.score_code_type` 是 `str | None`：response 的 `scoreCodeType` 缺失或 JSON `null` 解析為 `None`，只有 JSON string 可成為值，其他型別一律為 `ProjectsResponseError`。`ChampionModel.files` 是 caller-observable `tuple[ChampionFile, ...]`；`ChampionFile.id` 與 `ChampionFile.name` 是 nullable metadata references。content download 或 aggregate result type 不屬於此 family。

## Request、parsing 與 pagination

- `list_projects`：pre-I/O 驗證 non-bool `start >= 0`、non-bool `limit > 0`，以 literal path GET 和 `{"start": str(start), "limit": str(limit)}` 呼叫 Requester 一次。
- `get_project`/`get_champion`：驗證 non-empty id，使用 `EndpointPath.from_segments("modelRepository", "projects", project_id[, "champion"])`，無 query/body。
- JSON/non-JSON/transport/HTTP error 沿用既有 Models family decoding boundary；不重建 transport/auth/client lifecycle，也不改 public error contract。
- page parser 要求 `count`、`start`、`limit`、`items`；list/detail 要求 `id`、`name`。只 materialize 支援的語義欄位。
- name lookup 驗證 non-empty name/positive page_size，自 start 0 sequential `list_projects()`。first page establishes expected count；每頁必須驗證 response start、limit、count、items length；scan exact name 後，只有 empty/short/final full page 的真正 exhaust 才 `None`。非終止頁用 `len(items)` 前進，絕不以 metadata mismatch 正常結束。
- `get_champion` 要求 `id`、`name`；`scoreCodeType` 缺失或 JSON `null` 成為 `ChampionModel.score_code_type is None`，只有 JSON string 可 materialize，非字串且非 null 值拋出 `ProjectsResponseError`。raw `files` absent 成為空 tuple，present files 逐一 materialize 為 `ChampionFile`，供 caller 觀察及後續自行編排。

## Peer-family boundary

- `ProjectsClient` constructor 僅接收 caller-owned `Requester`。Projects source、tests、annotations 與 exports 均不得 import、construct、inject 或 type-only reference Models family 的 client、VO 或 result type。
- 不得有 private helper、duck-typed collaborator、callback 或其他 hidden cross-family orchestration。
- caller 在 `get_champion()` 回傳後，自己選擇是否以 `ModelsClient.get_model_content(champion.id, file.id)` 使用 Champion file references，並自己決定 gather、failure/cancellation、result aggregation 與 lifecycle policy；Projects 不定義或測試這些 policy。

## Tach boundary

- 已檢查 `tach.toml`：它只宣告 `mlops_async.clients.models`、`.models.client`、`.models.value_objects`，沒有任何 `mlops_async.clients.projects` module。
- 已檢查既有 direct-boundary precedent：Models value objects 直接依賴 `mlops_async.exceptions` 的 `MlopsAsyncBaseException`；Models client 直接依賴 `mlops_async.transport.exceptions` 的 JSON error/context。Projects 的 corrected family 必須沿用相同的 direct boundaries，不能以新 facade、exception relocation 或 public error change 迴避它們。
- Human 已授權 `tach.toml` 作為 bounded post-review implementation path。Implementer 必須新增以下 declaration，且只可用這些 existing boundary edges：

```toml
[[modules]]
path = "mlops_async.clients.projects"
depends_on = ["mlops_async.clients.projects.client", "mlops_async.clients.projects.value_objects"]

[[modules]]
path = "mlops_async.clients.projects.value_objects"
depends_on = ["mlops_async.core", "mlops_async.exceptions"]

[[modules]]
path = "mlops_async.clients.projects.client"
depends_on = ["mlops_async.clients.projects.value_objects", "mlops_async.core", "mlops_async.transport"]
```

- `mlops_async.clients.models` 不得出現在任何 Projects declaration。Plan-Creator 不修改 `tach.toml`；實際 config edit 屬於 post-review Implementer。

## Future implementation/test paths

- `src/mlops_async/clients/projects/__init__.py`
- `src/mlops_async/clients/projects/client.py`
- `src/mlops_async/clients/projects/value_objects.py`
- `tests/unit/clients/projects/__init__.py`
- `tests/unit/clients/projects/test_client.py`
- `tests/unit/clients/projects/test_value_objects.py`
- `tach.toml`

上述 allowed code/test paths 不含 aggregate test targets。它們保留 request construction、encoding、pre-I/O validation、semantic parser error、全部 pagination invariants、exact match/exhaustion/later request failure、Champion `scoreCodeType` missing/null/non-string parser matrix、metadata/file-reference parsing、immutability 與 peer-family import/signature isolation。`tach.toml` 僅能依上列 exact declaration 由 post-review Implementer 修改。

## Metadata/release boundary

feature stage metadata action 是 no-change。`README.md`、`VERSION`、`pyproject.toml` 僅能由 separately authorized post-merge minor-release topic 修改。該 topic 先確認 baseline 仍為 `v0.17.0`，才可指定 candidate `v0.18.0`；否則停止並重新決定版本。
