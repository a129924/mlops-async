# SAS Viya API — `sasctl` 對齊分析報告

> **sasctl 版本**: `1.11.7`（已安裝於 `.venv/`）
> **比較基準**: Legacy `sas_api` 的 13 個實際端點
> **分析方式**: 直接讀取 `.venv/lib/python*/site-packages/sasctl/_services/` 原始碼

---

## 對齊概覽

| 功能分類 | Legacy `sas_api` 做法 | `sasctl` 對應服務 | 對齊程度 |
|---------|----------------------|-------------------|----------|
| 認證 | 手動 `POST /SASLogon/oauth/token` | `sasctl.core.Session` 自動管理 | ✅ sasctl 完整封裝 |
| 模型清單 | `GET /modelRepository/models` | `ModelRepository.list_models()` | ✅ 完整對應 |
| 單一模型 | `GET /modelRepository/models/{id}` | `ModelRepository.get_model()` | ✅ 完整對應 |
| 模型檔案內容 | `GET .../contents/{fileId}/content` | `ModelRepository.get_model_contents()` | ✅ 完整對應 |
| 專案清單 | `GET /modelRepository/projects` | `ModelRepository.list_projects()` | ✅ 完整對應 |
| Champion Model | `GET .../projects/{id}/champion` | 無直接對應方法 | ⚠️ 需自行實作 |
| CAS 資料表清單 | `GET /casManagement/dataSources/.../tables` | `CASManagement.list_tables()` | ✅ 完整對應 |
| CAS 資料表詳情 | `GET .../tables/{tableName}` | `CASManagement.get_table()` | ✅ 完整對應 |
| CAS 表狀態切換 | `PUT .../tables/{name}/state` | `CASManagement.update_state_table()` | ✅ 完整對應 |
| 啟動 Job | `POST /jobExecution/jobRequests/{id}/jobs` | `ScoreExecution.create_score_execution()` | ⚠️ 部分對應（見下） |
| 查詢 Job 狀態 | `GET /jobExecution/jobs/{id}/state` | `ScoreExecution.poll_score_execution_state()` | ✅ 完整對應 |
| 查詢 Job 詳情 | `GET /jobExecution/jobs/{id}` | `ScoreExecution.get_score_execution_results()` | ✅ 對應（結果面） |

---

## 詳細比較

### 1. 認證（Authentication）

**Legacy `sas_api` 做法**：
```python
# utils/async/_token.py
async def obtain_access_token(setting, username, password):
    # 手動 POST /SASLogon/oauth/token
    # grant_type=password
    # 手動管理 token 過期（expires_in_date）
```

**`sasctl` 做法**：
```python
from sasctl import Session

# sasctl 的 Session 自動處理：
# - OAuth token 取得（password grant）
# - token 自動刷新
# - 重試機制
with Session(host, username, password) as sess:
    # 後續所有 API 呼叫自動帶 token
```

**結論**：`sasctl` 的 `Session` 完整封裝了認證邏輯，包含 token 自動更新，**建議改用 `sasctl.Session` 取代手動 token 管理**。

---

### 2. 模型查詢（Models）

**Legacy `sas_api`**：
```python
# get_model.py
GET /modelRepository/models                         # get_all_models
GET /modelRepository/models/{model_id}              # get_one_model
GET /modelRepository/models/{id}/contents/{fid}/content  # get_model_file_content
```

**`sasctl`（`_services/model_repository.py`）**：
```python
ModelRepository.list_models()          # 對應 GET /modelRepository/models
ModelRepository.get_model(model)       # 對應 GET /modelRepository/models/{id}
ModelRepository.get_model_contents(model)  # 對應 GET .../contents
ModelRepository.get_astore(model)      # 取得 astore 類型模型的特定內容
ModelRepository.get_score_code(model)  # 取得 score code 檔案
```

**對齊程度**：✅ 完整對應，`sasctl` 還提供更多輔助方法（`get_astore`、`get_score_code`）

---

### 3. 專案查詢（Projects）

**Legacy `sas_api`**：
```python
# project.py
GET /modelRepository/projects?limit=1000    # fetch_all_projects_response
GET /modelRepository/projects/{id}/champion # fetch_champion_model（⚠️ sasctl 無直接對應）
```

**`sasctl`（`_services/model_repository.py`）**：
```python
ModelRepository.list_projects()        # 對應 GET /modelRepository/projects
ModelRepository.get_project(project)   # 取得特定專案
ModelRepository.create_project(...)    # 建立專案（legacy 無此功能）
ModelRepository.list_project_versions(project)  # 取得專案版本
```

**Champion Model（`GET .../projects/{id}/champion`）**：
`sasctl` **沒有**直接取得 Champion Model 的方法。`sasctl` 的 `model_management.py` 有 `ModelManagement` 服務，但其 `champion` 相關方法是管理冠軍模型的生命週期，不是直接查詢。

**⚠️ GAP**：若需要取得 Champion Model，仍需自行呼叫 `GET /modelRepository/projects/{id}/champion`。

---

### 4. CAS 資料表管理（Tables）

**Legacy `sas_api`**：
```python
# table.py（⚠️ 有 import bug，實際無法執行）
GET  /casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables
GET  /casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{name}
PUT  /casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{name}/state
```

**`sasctl`（`_services/cas_management.py`）**：
```python
CASManagement.list_tables(caslib, server)      # 完整對應 GET 清單
CASManagement.get_table(name, caslib, server)  # 完整對應 GET 單一
CASManagement.update_state_table(...)          # 完整對應 PUT state
CASManagement.upload_file(...)                 # 額外功能：上傳檔案
CASManagement.save_table(...)                  # 額外功能：儲存 CAS 表
CASManagement.del_table(...)                   # 額外功能：刪除 CAS 表
CASManagement.promote_table(...)               # 額外功能：提升 CAS 表
```

**對齊程度**：✅ 完整對應，且 `sasctl` 功能更豐富。

---

### 5. 作業執行（Job Execution）

**Legacy `sas_api`**：
```python
# job_execution.py（⚠️ 有 is_text 參數 bug）
POST /jobExecution/jobRequests/{id}/jobs   # start_job
GET  /jobExecution/jobs/{id}               # get_job_info
GET  /jobExecution/jobs/{id}/state         # get_job_state
```

**`sasctl`（`_services/score_execution.py`）**：
```python
ScoreExecution.create_score_execution(...)      # 建立 Score Execution（較高層封裝）
ScoreExecution.poll_score_execution_state(...)  # 輪詢狀態（對應 get_job_state）
ScoreExecution.get_score_execution_results(...) # 取得結果（對應 get_job_info）
```

**⚠️ 部分差異**：
- Legacy `sas_api` 使用 `/jobExecution/jobRequests/{id}/jobs`（直接用 Job Request ID 觸發）
- `sasctl` 的 `ScoreExecution` 是更高層的封裝，管理整個評分流程（Score Definition → Score Execution）

若現有的 Job Request 是預先在 SAS Viya 中設定好的，直接用 Job Execution API 觸發更簡單；若需要動態建立評分流程，使用 `sasctl.ScoreExecution` 更完整。

---

## 建議：使用 `sasctl` 取代 Legacy 端點

| 優先程度 | 功能 | 建議方案 |
|---------|------|----------|
| 🔴 高優先 | 認證 | 改用 `sasctl.Session`，廢棄手動 token 管理 |
| 🔴 高優先 | Table 管理 | 改用 `sasctl.CASManagement`，修正 import bug |
| 🔴 高優先 | Job Execution | 修正 `is_text` 參數 bug，或改用 `sasctl.ScoreExecution` |
| 🟡 中優先 | 模型查詢 | 可改用 `sasctl.ModelRepository.list_models / get_model` |
| 🟡 中優先 | 專案查詢 | 可改用 `sasctl.ModelRepository.list_projects` |
| 🟢 保留現有 | Champion Model | `sasctl` 無直接對應，保留 `GET /projects/{id}/champion` |

---

## `sasctl` 使用範例

```python
from sasctl import Session
from sasctl._services.model_repository import ModelRepository
from sasctl._services.cas_management import CASManagement

with Session(host='https://your-sas-viya', username='user', password='pass') as sess:
    # 取得所有專案
    projects = ModelRepository.list_projects()

    # 取得模型清單
    models = ModelRepository.list_models()

    # 取得特定模型
    model = ModelRepository.get_model('my_model_name')

    # 取得 CAS 資料表
    tables = CASManagement.list_tables(caslib='CASUSER', server='cas-shared-default')

    # 切換資料表狀態
    CASManagement.update_state_table(
        name='SCORING_INPUT',
        caslib='CASUSER',
        server='cas-shared-default',
        state='loaded'
    )
```

> **注意**：Champion Model 查詢目前無 `sasctl` 對應，需保留直接 HTTP 呼叫方式。
