# sas-docker-api 重構 Cookbook

## 目的與適用範圍

這份文件是給重構 `sas-docker-api` 的 Agent 使用的消費端整合手冊。它只涵蓋已完成的
`mlops-async` MVP：token、Models、Projects/Champion、Job Execution 與 CAS Tables。

它不是 legacy endpoint evidence、OpenAPI contract 或 FastAPI compatibility specification。
是否保留既有 route、HTTP status code、response schema 與錯誤 payload，必須由
`sas-docker-api` 的重構 topic 明確決定及測試；不可從本文件推論為相容承諾。

不要把下列工作混入這次整合：新增 endpoint family、手刻 Viya HTTP request、SWAT/CAS
execution、champion 模型執行，或 model-files metadata 擴充。

## 1. 建立一個 app-owned runtime

`MlopsAsyncClient` 擁有 HTTP transport、password-grant token endpoint、token storage 與
已支援的 endpoint-family clients。請在 FastAPI lifespan 建立一次，讓所有 route 透過
dependency 取得同一個 instance；constructor 不會發出 HTTP request，第一個需要認證的
domain call 才會取得 token。

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from mlops_async import MlopsAsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = MlopsAsyncClient(
        base_url=settings.viya_base_url,
        client_id=settings.viya_client_id,
        client_secret=settings.viya_client_secret,
        username=settings.viya_username,
        password=settings.viya_password,
    )
    app.state.mlops_client = client
    try:
        yield
    finally:
        await client.aclose()


def get_mlops_client(request: Request) -> MlopsAsyncClient:
    return cast(MlopsAsyncClient, request.app.state.mlops_client)


app = FastAPI(lifespan=lifespan)
```

`settings` 是 target app 自己的設定物件；本 cookbook 不指定環境變數名稱，也不應將
credential 或 token 寫入文件、log、response 或 `app.state`。

不要在 route 裡建立 `httpx.AsyncClient`、手動加 `Authorization`/`Accept` header、組 URL，
或將 access token 當成 route 間共用 state。若 route 真的需要直接取得 token，使用
`await client.auth.get_access_token()`，並只在該呼叫端使用回傳的 `AccessToken`；一般
endpoint-family call 不需要這一步。

## 2. Legacy helper 對應

下表的「adapter 責任」仍屬 `sas-docker-api`；client 不回傳 legacy raw `httpx.Response`。

| Legacy helper / 用途 | 改用 `MlopsAsyncClient` | 回傳與 adapter 責任 |
| --- | --- | --- |
| `_async/_token.obtain_access_token` | `await client.auth.get_access_token()` | 回傳 `AccessToken`；僅在 legacy auth route 仍存在時，由 route 決定如何序列化。其他 family 由 client 自行取得/refresh token。 |
| `get_all_models` | `await client.models.list_models(start=..., limit=..., project_id=...)` | `ModelsPage` 和 `ModelSummary`；adapter 決定 legacy envelope 或 response model。 |
| `get_one_model` | `await client.models.get_model(model_id)` | `ModelDetail`；只提供受支援的 semantic fields，不是 legacy JSON passthrough。 |
| `fetch_all_projects_response` | `await client.projects.list_projects(start=..., limit=...)` | `ProjectsPage`；adapter 轉換為 target route 所需輸出。 |
| `process_projects_response_by_project_name` | `await client.projects.get_project_by_name(name)` | `ProjectSummary | None`；這個 method 會做受控的 sequential page traversal。`None` 時由 adapter 決定 404 或其他 domain 結果。 |
| `fetch_champion_model` | `await client.projects.get_champion(project_id)` | `ChampionModel` 和 raw `ChampionFile` references；檔案挑選與 payload 組裝留在 adapter。 |
| `start_job` | `await client.job_execution.start_job(job_request_id)` | `Job`；不新增 polling 或 state machine。 |
| `get_job_info` | `await client.job_execution.get_job(job_id)` | `Job`；legacy route 的 path parameter 必須在 adapter 明確改名為 `job_id`，不可延續誤導性的 `job_request_id`。 |
| `get_job_state` | `await client.job_execution.get_job_state(job_id)` | `JobState`；若 target route 仍要求純文字，adapter 使用 `state.value`。 |
| `get_table_infos` | `await client.cas_tables.list_tables(data_source_id, start=..., limit=...)` | `TablesPage`；`data_source_id` 必須經設定式 resolver 取得。 |
| `get_table` | `await client.cas_tables.get_table(data_source_id, table_name)` | `TableDetail`；不得自行組 `casManagement` path。 |
| `change_castable_state` | `await client.cas_tables.change_table_state(server, caslib, table_name, state)` | `TableDetail`；目前受支援 state 僅為 `"loaded"`。 |

## 3. 必須留在 adapter 的邏輯

### CAS data-source resolver

Legacy code 將 `caslib` 與固定的 `cas-shared-default` 拼成 URL。新 client 有意要求
`data_source_id`，因此 target app 應以設定/明確 resolver 提供該識別值，而非重新硬編
legacy path 規則。

```python
from mlops_async.clients.cas_tables import TableDetail


class CasDataSourceResolver:
    def data_source_id_for(self, caslib: str) -> str:
        return settings.cas_data_source_ids[caslib]


async def get_table(caslib: str, table_name: str, client: MlopsAsyncClient) -> TableDetail:
    data_source_id = resolver.data_source_id_for(caslib)
    return await client.cas_tables.get_table(data_source_id, table_name)
```

`server` 也應由 target app 設定提供給 `change_table_state`。未知 caslib、缺少 mapping，或
不支援的 table state 都是 adapter 的 domain/configuration error；不要透過 fallback URL
或舊 HTTP helper 掩蓋。

### Champion content 與 legacy payload

`get_champion(project_id)` 提供 Champion metadata 與可能缺失的檔案 ID/name。若 target app
需要下載一個明確的 champion file，adapter 必須先選擇檔案、確認 `file.id` 為非空字串，才可
呼叫：

```python
champion = await client.projects.get_champion(project_id)
selected = select_champion_file(champion.files)  # target-app domain policy
if not selected.id:
    raise ChampionAdapterError("Champion file has no usable content identifier")

content = await client.models.get_model_content(champion.id, selected.id)
raw_bytes = content.content
```

依檔名選檔、bytes 的 JSON/text 解碼、檔案集合併、`ChampionModelPayload` 建構，以及後續
SWAT/CAS model execution 都在 adapter 層。不要把特定 filename、payload schema 或 `predict`
呼叫硬編進 `mlops-async`。

### 明確停止：legacy model-file routes

目前不得遷移 `/sas/model/{model_id}/files`、`/{filename}`、`/{filename}/content` 三條 legacy
routes。雖然 `get_model_content(model_id, content_id)` 已存在，`get_model(model_id)` 回傳的
`ModelDetail` 不含 legacy `files` metadata，無法可靠地由 filename 找到 `content_id`。

不要猜測 response 欄位、用 private API、回退到 legacy request helper，或將 content ID lookup
混入此整合。需求成立時，另開一個有 response/evidence contract 的 model-files metadata topic。

## 4. 錯誤、資源與測試 Checklist

- 讓 `mlops-async` 的 transport/auth/domain exceptions 抵達 adapter；由 target FastAPI 層統一
  轉換為它已決定的 HTTP error contract。不要依賴 legacy `httpx.Response.status_code` branch。
- route/adapter 只能使用 typed value objects 的公開欄位；不可假定未建模的 legacy JSON 欄位仍存在。
- 為 lifespan 寫測試：constructor 不做 I/O、所有 dependency 取得同一個 client、shutdown 只呼叫
  一次 `aclose()`。
- 以 mock/fake `MlopsAsyncClient` family client 測試各 adapter 的輸出轉換、`None` project lookup、
  CAS resolver 缺失、table state 限制、job state 的 `.value` 轉換與 champion 缺失 file ID。
- 對 model-file routes 寫明確的停止/retirement 測試或 migration note；不可留下會暗中走 legacy
  Viya helper 的 fallback。
- 用 integration test 驗證 target app 的選定 public HTTP contract；該 contract 是 target repo 的
  決策，非本 cookbook 的保證。

## 5. 重構完成前的檢查

1. 所有已支援 family 均透過同一個 injected `MlopsAsyncClient`。
2. 沒有新增手刻 Viya base URL、headers、bearer token、`verify=False` 或 per-request HTTP client。
3. CAS ID/server 均來自設定式 resolver；沒有複製舊的 `cas-shared-default` path formula。
4. champion domain orchestration 仍在 target app；library 未被要求知道 target 的檔名、payload 或
   execution framework。
5. model-file routes 有顯式的停止決策，且未將其偽裝為已由 MVP 支援。
