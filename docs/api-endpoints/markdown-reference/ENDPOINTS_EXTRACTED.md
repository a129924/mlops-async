# SAS Viya API 端點清單（完整提取）

> **來源**: Legacy `sas_api` 專案（`/Users/andrew/code/python/sas_api`）
> **分析時間**: 嚴格依據原始程式碼，無任何推測或幻想

---

## 認證（Authentication）

| # | HTTP Method | 端點路徑 | 功能說明 | 來源函式 |
|---|-------------|----------|----------|----------|
| 1 | `POST` | `/SASLogon/oauth/token` | **Password Grant**：使用帳密取得 Access Token | `_token.py::obtain_access_token` |
| 2 | `POST` | `/SASLogon/oauth/token` | **Refresh Token Grant**：使用 Refresh Token 更新 Access Token | `_token.py::refresh_sas_access_token` |

**認證 Headers（`access_token_headers()`）**：
```
Content-Type: application/x-www-form-urlencoded
Authorization: Basic c2FzLmNsaTo=
```

---

## 模型管理（Model Repository - Models）

| # | HTTP Method | 端點路徑 | 功能說明 | 來源函式 |
|---|-------------|----------|----------|----------|
| 3 | `GET` | `/modelRepository/models` | 取得所有模型清單 | `get_model.py::get_all_models` |
| 4 | `GET` | `/modelRepository/models/{modelId}` | 取得單一模型完整詳情（含 files、inputVariables、outputVariables） | `get_model.py::get_one_model` |
| 5 | `GET` | `/modelRepository/models/{modelId}/contents/{fileId}/content` | 下載模型檔案內容（SAS score code、metadata JSON 等） | `get_model.py::get_model_file_content`、`project.py::_fetch_file_content` |

**Models Headers（`sas_viya_get_headers(access_token)`）**：
```
Authorization: Bearer {access_token}
Accept: application/vnd.sas.models.model+json, application/json
```

**檔案下載 Headers（`sas_viya_get_content_headers(access_token)`）**：
```
If-Range: ""
Range: ""
Access-Quarantine: ""
Authorization: Bearer {access_token}
```

---

## 專案管理（Model Repository - Projects）

| # | HTTP Method | 端點路徑 | 功能說明 | 來源函式 |
|---|-------------|----------|----------|----------|
| 6 | `GET` | `/modelRepository/projects?limit={limit}` | 取得所有專案清單（預設 limit=1000） | `project.py::fetch_all_projects_response` |
| 7 | `GET` | `/modelRepository/projects/{projectId}/champion` | 取得指定專案的 Champion Model（含 files） | `project.py::fetch_champion_model` |

**重要說明**：
- **「依名稱查詢專案」** 是 client 端過濾（`process_projects_response_by_project_name`），**不是**獨立的 API 呼叫
- Project Headers 與 Models 相同：`sas_viya_get_headers`

---

## CAS 資料表管理（CAS Management）

| # | HTTP Method | 端點路徑 | 功能說明 | 來源函式 |
|---|-------------|----------|----------|----------|
| 8 | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables?limit={limit}&start=0` | 取得 Caslib 下的所有資料表清單 | `table.py::get_table_infos` |
| 9 | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}` | 取得特定資料表詳細資訊 | `table.py::get_table` |
| 10 | `PUT` | `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state?value={state}` | 切換資料表載入狀態（loaded ⇔ unloaded） | `table.py::change_castable_state` |

**路徑說明**：`cas~fs~cas-shared-default~fs~{caslib}` 是 SAS Viya dataSource 的路徑式識別碼
**⚠️ 已知 Bug**：`table.py` 引用了不存在的 3 個 header 函式（詳見下方「已知問題」）

---

## 作業執行（Job Execution）

| # | HTTP Method | 端點路徑 | 功能說明 | 來源函式 |
|---|-------------|----------|----------|----------|
| 11 | `POST` | `/jobExecution/jobRequests/{jobRequestId}/jobs` | 依 Job Request 啟動新的 Job 執行 | `job_execution.py::start_job` |
| 12 | `GET` | `/jobExecution/jobs/{jobId}` | 取得 Job 完整資訊（含 state、results） | `job_execution.py::get_job_info` |
| 13 | `GET` | `/jobExecution/jobs/{jobId}/state` | 取得 Job 執行狀態（輕量輪詢用） | `job_execution.py::get_job_state` |

**Jobs Headers（`sas_viya_post_job_execution_headers(access_token)`）**：
```
Delegate-Domain: ""
Content-Type: application/json
Authorization: Bearer {access_token}
Accept: application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, ...
```

**⚠️ 已知 Bug**：`job_execution.py` 傳入了不存在的 `is_text` 參數（詳見下方「已知問題」）

---

## URL 常數一覽

```python
# 來源：utils/_api/*.py
BASE_PROJECT_URL           = f"{base_url}modelRepository/projects"
BASE_PROJECT_MODEL_URL     = f"{base_url}modelRepository/models"
JOB_EXECUTION_URL          = f"{base_url}jobExecution/jobRequests"
JOBS_URL                   = f"{base_url}jobExecution/jobs"
TABLE_INFO_BASE_URL        = f"{base_url}casManagement/dataSources"
```

---

## ⚠️ 已知程式碼問題

### Bug #1：`table.py` 引用不存在的 Header 函式

```python
# table.py 的 import（有問題）
from sas_api.config.headers_variable import (
    sas_viya_item_get_headers,    # ❌ 不存在
    sas_viya_table_get_headers,   # ❌ 不存在
    sas_viya_table_put_headers,   # ❌ 不存在
)

# headers_variable.py 實際只有 4 個函式
# ✅ access_token_headers()
# ✅ sas_viya_get_headers(access_token)
# ✅ sas_viya_get_content_headers(access_token)
# ✅ sas_viya_post_job_execution_headers(access_token)
```

**影響**：所有 table 相關端點（#8、#9、#10）在執行時會拋出 `ImportError`

### Bug #2：`job_execution.py` 傳入不存在的參數

```python
# job_execution.py 的呼叫（有問題）
sas_viya_post_job_execution_headers(access_token=access_token, is_text=False)  # ❌
sas_viya_post_job_execution_headers(access_token=access_token, is_text=True)   # ❌

# 實際函式簽名
def sas_viya_post_job_execution_headers(access_token: str) -> dict:  # 無 is_text 參數
```

**影響**：所有 job 相關端點（#11、#12、#13）在執行時會拋出 `TypeError`

---

## 端點統計

| 分類 | 端點數量 | GET | POST | PUT |
|------|----------|-----|------|-----|
| Authentication | 2 | 0 | 2 | 0 |
| Models | 3 | 3 | 0 | 0 |
| Projects | 2 | 2 | 0 | 0 |
| Tables | 3 | 2 | 0 | 1 |
| Job Execution | 3 | 2 | 1 | 0 |
| **合計** | **13** | **9** | **3** | **1** |
