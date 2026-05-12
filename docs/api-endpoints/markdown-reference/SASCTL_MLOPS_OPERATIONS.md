# sasctl MLOps 操作參考文件

> **版本**: sasctl 1.11.7
> **基於**: 原始碼分析 `.venv/lib/python*/site-packages/sasctl/`
> **分支**: `feature/sas-viya-endpoint-documentation`

---

## 全域 HTTP 慣例

### Authorization 自動注入機制

所有操作均透過 `sasctl.Session` 執行，`OAuth2.__call__` 會自動在每個請求注入：

```
Authorization: Bearer {access_token}
```

呼叫端**不需手動設定** Authorization Header，sasctl Session 會處理。

**Source**: `core.py` - `class OAuth2.__call__()`
```python
def __call__(self, r):
    r.headers["Authorization"] = "Bearer " + self.access_token
    return r
```

### ETag / If-Match（更新操作）

PUT（更新）操作前**必須先 GET 取得 ETag**，sasctl 的 `update_item()` 會自動讀取前次 GET response headers：

```
If-Match: {etag_from_prior_GET}
Content-Type: {content_type_from_prior_GET}
```

**Source**: `service.py` lines 292-307

### sasctl 路徑命名慣例

| sasctl 路徑 | 實際 HTTP 路徑 | 說明 |
|---|---|---|
| `/models#octetStream` | `/modelRepository/models` | `#` fragment 為命名提示，requests 傳送前自動去除 |
| `/files#multipartUpload` | `/files/files` | 同上，僅為 multipart 上傳的命名標記 |

---

## 一、檔案上傳操作（File Upload）

### 1.1 上傳單一檔案到模型

**函式**: `ModelRepository.add_model_content(model, file, name, role=None, content_type="multipart/form-data")`

**HTTP**:
```
POST /modelRepository/models/{modelId}/contents
```

#### Header 組成

**情況 A — 文字/JSON/dict 檔案（預設）**:
```http
POST /modelRepository/models/{modelId}/contents?role={role} HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}          ← 自動注入
Content-Type: multipart/form-data; boundary=---...  ← requests 自動設定

------...
Content-Disposition: form-data; name="files"; filename="{name}"
Content-Type: {content_type}

{file_content}
------...--
```

**情況 B — bytes 輸入（自動切換）**:
```http
POST /modelRepository/models/{modelId}/contents?role={role} HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}          ← 自動注入
Content-Type: application/octet-stream        ← 因 file 為 bytes 自動切換

{raw_bytes_content}
```

#### Query Parameters

| 參數 | 必填 | 說明 | 範例 |
|---|---|---|---|
| `role` | 否 | 檔案角色 | `Python pickle`, `score`, `log` |

#### 自動重試邏輯（409 衝突）

當同名檔案已存在時（HTTP 409），sasctl 會：
1. 查詢 `GET /modelRepository/models/{id}/contents`
2. 找到同名檔案後呼叫 `DELETE /modelRepository/models/{id}/contents/{fileId}`
3. 重新上傳

#### 程式碼範例

```python
import sasctl
from sasctl._services.model_repository import ModelRepository

with sasctl.Session(host="https://your-viya-host", username="user", password="pass"):
    # 上傳 pickle 檔案
    with open("model.pkl", "rb") as f:
        ModelRepository.add_model_content(
            model="my_logistic_regression",
            file=f.read(),          # bytes → 自動使用 application/octet-stream
            name="model.pkl",
            role="Python pickle"
        )

    # 上傳 JSON 輸入/輸出變數定義
    import json
    variables = {"inputVar": "age", "outputVar": "prob_event"}
    ModelRepository.add_model_content(
        model="my_logistic_regression",
        file=variables,             # dict → 自動序列化為 JSON，multipart/form-data
        name="inputVar.json"
    )

    # 上傳 Python score code（文字）
    with open("score.py", "r") as f:
        ModelRepository.add_model_content(
            model="my_logistic_regression",
            file=f,                 # file-like → multipart/form-data
            name="score.py",
            role="score"
        )
```

---

### 1.2 ZIP 檔案匯入整包模型

**函式**: `ModelRepository.import_model_from_zip(name, project, file, description=None, version="latest")`

**HTTP**:
```
POST /modelRepository/models?name={name}&description={desc}&type=ZIP&projectId={projectId}&versionOption={version}
```

> **注意**：sasctl source 中路徑為 `/models#octetStream`，`#octetStream` 是命名標記，實際 HTTP 請求路徑為 `/modelRepository/models`。

#### Header 組成

```http
POST /modelRepository/models?name=MyModel&description=...&type=ZIP&projectId={uuid}&versionOption=latest HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}          ← 自動注入
Content-Type: application/octet-stream        ← 明確指定（傳送 ZIP bytes）

{zip_file_binary_content}
```

#### Query Parameters

| 參數 | 必填 | 說明 | 範例 |
|---|---|---|---|
| `name` | 是 | 模型名稱 | `MyPythonModel` |
| `description` | 否 | 模型說明 | `Logistic regression v2` |
| `type` | 是（固定） | 固定為 `ZIP` | `ZIP` |
| `projectId` | 是 | 目標專案 UUID | `a1b2c3d4-...` |
| `versionOption` | 否 | 版本策略 | `latest`（預設）、`new`、`current` |

#### 程式碼範例

```python
import sasctl
from sasctl._services.model_repository import ModelRepository

with sasctl.Session(host="https://your-viya-host", username="user", password="pass"):
    with open("model_package.zip", "rb") as f:
        model = ModelRepository.import_model_from_zip(
            name="LogisticModel_v3",
            project="ChurnPrediction",       # 名稱或 UUID
            file=f,
            description="Retrained with 2024 data",
            version="latest"
        )
    print(f"匯入成功: {model.id}")
```

---

### 1.3 上傳通用檔案到 SAS Files 服務

**函式**: `Files.create_file(file, folder=None, filename=None, expiration=None)`

**HTTP**:
```
POST /files/files
```

> **注意**：sasctl source 中路徑為 `/files#multipartUpload`，`#multipartUpload` 是命名標記，實際 HTTP 請求路徑為 `/files/files`。

#### Header 組成

```http
POST /files/files?parentFolderUri={folderUri} HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}          ← 自動注入
Content-Type: multipart/form-data; boundary=---...  ← requests 自動設定

------...
Content-Disposition: form-data; name="{filename}"; filename="{filename}"

{file_content}
------...--
```

#### Query Parameters

| 參數 | 必填 | 說明 |
|---|---|---|
| `parentFolderUri` | 否 | 目標資料夾 HATEOAS URI（從 `Folders.get_folder()` 取得） |

#### 程式碼範例

```python
import sasctl
from sasctl._services.files import Files

with sasctl.Session(host="https://your-viya-host", username="user", password="pass"):
    # 上傳到根目錄
    with open("report.csv", "rb") as f:
        result = Files.create_file(file=f, filename="report.csv")
    print(f"File URI: {result.get('id')}")

    # 上傳到指定資料夾
    with open("data.parquet", "rb") as f:
        result = Files.create_file(
            file=f,
            folder="/Public/MyProject",    # 名稱或路徑，內部解析為 parentFolderUri
            filename="data.parquet"
        )
```

---

## 二、Model 模型操作

### 2.1 建立模型（Register Model）

**函式**: `ModelRepository.create_model(model, project, description=None, tool=None, function=None, ...)`

**HTTP**:
```
POST /modelRepository/models
```

#### Header 組成
```http
POST /modelRepository/models HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
Content-Type: application/vnd.sas.models.model+json

{
  "name": "MyModel",
  "projectId": "{uuid}",
  "tool": "Python 3",
  "function": "Classification",
  "scoreCodeType": "python",
  "inputVariables": [...],
  "outputVariables": [...],
  "version": 2
}
```

#### 常用參數

| 參數 | 型別 | 說明 |
|---|---|---|
| `model` | str / dict | 模型名稱或完整模型 dict |
| `project` | str / dict | 目標專案名稱或 UUID |
| `tool` | str | `"Python 3"`, `"Python 2"`, `"SAS"` |
| `function` | str | `"Classification"`, `"Prediction"`, `"Clustering"` 等 |
| `score_code_type` | str | `"python"`, `"ds2"`, `"datastep"` |
| `is_champion` | bool | 是否設為冠軍模型，預設 False |
| `is_challenger` | bool | 是否設為挑戰者模型，預設 False |
| `input_variables` | list | 輸入變數定義清單 |
| `output_variables` | list | 輸出變數定義清單 |

> ⚠️ **[需實測] 必填欄位**：從 sasctl source 可確認 `name` + `projectId` 是必要的，但 `tool`、`function`、`scoreCodeType` 是否為 server 端必填尚未驗證。建議測試：只傳 `{"name":"X","projectId":"uuid"}` 是否回 `201`，缺少 `tool` 是否回 `400`。

#### 程式碼範例
```python
model = ModelRepository.create_model(
    model="LogisticChurn_v1",
    project="ChurnPrediction",
    description="Logistic Regression - Q1 2024",
    tool="Python 3",
    function="Classification",
    score_code_type="python",
    is_champion=False
)
print(f"模型 ID: {model.id}")
```

---

### 2.2 查詢模型列表

**函式**: `ModelRepository.list_models(**kwargs)`

**HTTP**:
```
GET /modelRepository/models?{filters}
```

#### Header 組成
```http
GET /modelRepository/models?filter=in(projectId,"proj-uuid") HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
```

---

### 2.3 查詢單一模型

**函式**: `ModelRepository.get_model(model, refresh=False)`

**HTTP**:
```
GET /modelRepository/models/{modelId}
```

#### 回應特性
- Response headers 中含 **ETag**，sasctl 自動存入 `model._headers["etag"]`
- 後續 `update_model()` 需要此 ETag

---

### 2.4 更新模型

**函式**: `ModelRepository.update_model(model)`

**HTTP**:
```
PUT /modelRepository/models/{modelId}
```

#### Header 組成（ETag 來自前次 GET 回應）
```http
PUT /modelRepository/models/{modelId} HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
If-Match: "{etag_value}"
Content-Type: {content_type_from_GET_response}

{updated_model_json}
```

#### 程式碼範例
```python
# 必須先 GET 取得含 ETag 的物件
model = ModelRepository.get_model("LogisticChurn_v1")
model["description"] = "Updated description - Q2 2024"
ModelRepository.update_model(model)    # 自動帶 If-Match ETag
```

---

### 2.5 取得模型內容清單

**函式**: `ModelRepository.get_model_contents(model)`

**HTTP**:
```
GET /modelRepository/models/{modelId}/contents
```

> ⚠️ **[需實測] 回應格式**：從 5.2 節的防禦性寫法可知回傳可能是 plain `[...]` 也可能是 `{"count":N,"items":[...]}`. 未確認哪種是規範行為。建議測試：`print(type(resp.json()))` 確認頂層型別。

---

### 2.6 建立新模型版本

**函式**: `ModelRepository.create_model_version(model, minor=False)`

**HTTP**:
```
POST /modelRepository/models/{modelId}/modelVersions
```

#### Request Headers
```http
POST /modelRepository/models/{modelId}/modelVersions HTTP/1.1
Authorization: Bearer {access_token}
Content-Type: application/json

{"option": "major"}
```

| `option` 值 | 說明 |
|---|---|
| `"major"` | 建立主版本（1.0 → 2.0）|
| `"minor"` | 建立次版本（1.0 → 1.1）|

> **sasctl 細節**：sasctl 透過 HATEOAS `addModelVersion` link 找到此路徑，`minor=False` 時傳 `"major"`，`minor=True` 時傳 `"minor"`。純 HTTP 可直接使用上方路徑，不需要先查 HATEOAS link。

#### 程式碼範例（純 HTTP）
```python
resp = requests.post(
    f"{BASE}/modelRepository/models/{MODEL_ID}/modelVersions",
    json={"option": "major"},
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
)
resp.raise_for_status()
print(f"版本已建立: {resp.json()}")
```

---

### 2.7 查詢模型版本列表

**函式**: `ModelRepository.list_model_versions(model)`

**HTTP**:
```
GET /modelRepository/models/{modelId}/modelVersions
```

#### Request Headers
```http
GET /modelRepository/models/{modelId}/modelVersions HTTP/1.1
Authorization: Bearer {access_token}
```

#### 程式碼範例（純 HTTP）
```python
resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}/modelVersions",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
versions = resp.json().get("items", resp.json())
for v in versions:
    print(f"Version {v['modelVersionName']}: id={v['id']}, created={v['creationTimeStamp']}")
```

> ⚠️ **[需實測] 回應 field names**：`modelVersionName`、`creationTimeStamp` 為 sasctl source 中見到的 field name，但未實際驗證 SAS Viya API 回傳的完整 response schema。建議測試：`print(versions[0].keys())` 確認所有欄位名稱。

---

### 2.8 刪除模型

**函式**: `ModelRepository.delete_model(model)`

**HTTP**:
```
DELETE /modelRepository/models/{modelId}
```

---

## 三、Project 專案操作

### 3.1 建立專案

**函式**: `ModelRepository.create_project(project, repository, **kwargs)`

**HTTP**:
```
POST /modelRepository/projects
```

#### Header 組成
```http
POST /modelRepository/projects HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
Content-Type: application/vnd.sas.models.project+json

{
  "name": "ChurnPrediction",
  "repositoryId": "{repo-uuid}",
  "folderId": "{folder-uuid}",
  "function": "Classification",
  "targetVariable": "churn_flag",
  "targetLevel": "Binary"
}
```

> ⚠️ **[需實測] `folderId` 必填性**：sasctl `create_project()` source 會自動從 repository 取得 `folderId` 再帶入，但若純 HTTP 不傳 `folderId` SAS Viya 是否接受（自動使用 repo 根目錄）尚未驗證。建議測試：只傳 `{"name":"X","repositoryId":"uuid"}` 是否回 `201`。

#### 程式碼範例
```python
project = ModelRepository.create_project(
    project={
        "name": "ChurnPrediction",
        "description": "Customer churn prediction models",
        "function": "Classification",
        "targetVariable": "churn_flag"
    },
    repository="Public"    # 倉庫名稱或 UUID
)
print(f"專案 ID: {project.id}")
```

---

### 3.2 查詢專案列表

**函式**: `ModelRepository.list_projects(**kwargs)`

**HTTP**:
```
GET /modelRepository/projects
```

---

### 3.3 查詢單一專案

**函式**: `ModelRepository.get_project(project, refresh=False)`

**HTTP**:
```
GET /modelRepository/projects/{projectId}
```

---

### 3.4 更新專案

**函式**: `ModelRepository.update_project(project)`

**HTTP**:
```
PUT /modelRepository/projects/{projectId}
```

#### Header 組成（同模型更新，需 ETag）
```http
PUT /modelRepository/projects/{projectId} HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
If-Match: "{etag_value}"
Content-Type: {content_type_from_GET_response}

{updated_project_json}
```

#### 程式碼範例
```python
project = ModelRepository.get_project("ChurnPrediction")
project["description"] = "Updated project description"
ModelRepository.update_project(project)
```

---

### 3.5 刪除專案

**函式**: `ModelRepository.delete_project(project)`

**HTTP**:
```
DELETE /modelRepository/projects/{projectId}
```

---

### 3.6 查詢專案版本歷史

**函式**: `ModelRepository.list_project_versions(project)`

**HTTP**:
```
GET /modelRepository/projects/{projectId}/projectVersions
```

---

## 四、MLOps 進階操作

### 4.1 發佈模型（Publish to Destination）

**函式**: `ModelManagement.publish_model(model, destination, model_version="latest", name=None, force=False)`

**HTTP**:
```
POST /modelManagement/publish
```

#### Header 組成
```http
POST /modelManagement/publish?force=false&reloadModelTable=false HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
Content-Type: application/vnd.sas.models.publishing.request.asynchronous+json

{
  "name": "LogisticChurn_v1",
  "notes": "Model description",
  "modelContents": [{
    "modelName": "LogisticChurnv1_{uuid}",
    "sourceUri": "/modelRepository/models/{uuid}",
    "modelVersionID": "",
    "publishLevel": "model"
  }],
  "destinationName": "maslocal"
}
```

#### 程式碼範例
```python
from sasctl._services.model_management import ModelManagement

result = ModelManagement.publish_model(
    model="LogisticChurn_v1",
    destination="maslocal",         # MAS, CAS, SAS Micro Analytic Service 等
    model_version="latest",
    force=True                      # 覆蓋已存在的模型
)
print(f"發佈狀態: {result.get('state')}")
```

---

### 4.2 建立效能定義（Performance Monitoring）

**函式**: `ModelManagement.create_performance_definition(table_prefix, ...)`

**HTTP**:
```
POST /modelManagement/performanceTasks
```

---

### 4.3 執行效能定義

**函式**: `ModelManagement.execute_performance_definition(definition)`

**HTTP**: 透過 HATEOAS link（`POST` 到 definition 的執行 URI）

---

### 4.4 發佈模型到 CAS 目的地

**函式**: `ModelPublish.create_cas_destination(name, server, library, ...)`

**HTTP**:
```
POST /modelPublish/destinations
```

#### Header 組成
```http
POST /modelPublish/destinations HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
Content-Type: application/vnd.sas.models.publishing.destination.cas+json

{
  "name": "cas-shared-default",
  "destinationType": "cas",
  "casServerName": "cas-shared-default",
  "casLibrary": "Public"
}
```

---

### 4.5 發佈模型到 MAS 目的地

**函式**: `ModelPublish.create_mas_destination(name, uri, description=None)`

**HTTP**:
```
POST /modelPublish/destinations
```

#### Header 組成
```http
POST /modelPublish/destinations HTTP/1.1
Host: {sas-viya-host}
Authorization: Bearer {access_token}
Content-Type: application/vnd.sas.models.publishing.destination.microAnalyticService+json
```

---

## 五、Content 下載與管理

> 補足版控流程中「上傳後能取回」的完整循環。這些端點在舊文件中缺少或只有清單而無下載。

### 5.1 查詢可用 Repository 列表

`create_project()` 需要傳入 `repository` 參數，必須先查可用的 repository 名稱。

**函式**: `ModelRepository.list_repositories()`

**HTTP**:
```
GET /modelRepository/repositories
```

**Request Headers**:
```http
GET /modelRepository/repositories HTTP/1.1
Authorization: Bearer {access_token}          ← 自動注入
Accept: application/vnd.sas.collection+json
```

**Response**（重要欄位）:
```json
{
  "count": 1,
  "items": [
    {
      "id": "repo-uuid",
      "name": "Public",               ← create_project() 傳入這個名稱
      "type": "repository",
      "description": "Default public repository"
    }
  ]
}
```

**程式碼範例**:
```python
from sasctl._services.model_repository import ModelRepository as MR

with sasctl.Session(...):
    repos = MR.list_repositories()
    for r in repos:
        print(f"{r.name} ({r.id})")
    # 通常用 default_repository() 取得預設值
    default_repo = MR.default_repository()
    print(f"預設 repo: {default_repo.name}")  # → "Public"
```

**純 HTTP**:
```python
resp = requests.get(
    f"{BASE}/modelRepository/repositories",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
repos = resp.json()["items"]
public_repo = next(r for r in repos if r["name"] == "Public")
```

---

### 5.2 下載模型 pkl（非版本化路徑）

取回目前版本中已上傳的 pkl 檔案。

**函式**: 無直接對應（透過 `get_model_contents()` 取得 link 後 follow）

**HTTP**:
```
GET /modelRepository/models/{modelId}/contents/{contentId}
```

**Request Headers**:
```http
GET /modelRepository/models/{modelId}/contents/{contentId} HTTP/1.1
Authorization: Bearer {access_token}
Accept: application/octet-stream        ← 二進位（pkl / zip）
```
或：
```http
Accept: text/plain                      ← 文字檔（.py / .json）
```

**程式碼範例（sasctl）**:
```python
from sasctl._services.model_repository import ModelRepository as MR

with sasctl.Session(...):
    # 1. 取得所有 content 的清單
    model = MR.get_model("ChurnLogistic")
    contents = MR.get_model_contents(model)

    # 2. 找 pkl
    pkl_item = next(c for c in contents if c["name"].endswith(".pkl"))

    # 3. 下載（sasctl 用 request_link 跟隨 content link）
    from sasctl.core import get
    response = get(
        pkl_item["links"][0]["href"],   # "self" link uri
        format="response",             # 取得 raw response 物件
    )
    # 根據 Content-Type 取二進位
    pkl_bytes = response.content
    with open("downloaded.pkl", "wb") as f:
        f.write(pkl_bytes)
```

**純 HTTP**:
```python
# 步驟 1：取清單，找 contentId
list_resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}/contents",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
contents = list_resp.json()
# contents 可能是 list 或 {"items": [...]}
items = contents if isinstance(contents, list) else contents.get("items", [])
pkl_item = next(c for c in items if c["name"].endswith(".pkl"))
content_id = pkl_item["id"]

# 步驟 2：下載
dl_resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}/contents/{content_id}",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/octet-stream",
    },
    stream=True,  # 大檔案不緩衝
)
with open("downloaded.pkl", "wb") as f:
    for chunk in dl_resp.iter_content(chunk_size=1024 * 1024):
        f.write(chunk)
```

---

### 5.3 刪除特定 Content 檔案

刪除模型中的單一檔案（而非 `delete_model_contents()` 的全刪）。

**函式**: 透過 content item 的 "delete" link 執行

**HTTP**:
```
DELETE /modelRepository/models/{modelId}/contents/{contentId}
```

**Request Headers**:
```http
DELETE /modelRepository/models/{modelId}/contents/{contentId} HTTP/1.1
Authorization: Bearer {access_token}
```

**程式碼範例**:
```python
from sasctl._services.model_repository import ModelRepository as MR
from sasctl.core import delete

with sasctl.Session(...):
    model = MR.get_model("ChurnLogistic")
    contents = MR.get_model_contents(model)

    # 刪除指定名稱的檔案
    target = next(c for c in contents if c["name"] == "old_model.pkl")
    delete_link = next(lk for lk in target["links"] if lk["rel"] == "delete")
    delete(delete_link["href"])
    print("已刪除")
```

**純 HTTP**:
```python
# 先取 contentId（同 5.2 步驟 1）
requests.delete(
    f"{BASE}/modelRepository/models/{MODEL_ID}/contents/{content_id}",
    headers={"Authorization": f"Bearer {TOKEN}"},
).raise_for_status()
```

> **常見用途**：換版時先刪舊 pkl 再上傳新的（sasctl 的 `add_model_content` 409 衝突處理就是這個邏輯）。

---

### 5.4 下載 Files API 上傳的檔案

取回透過 `POST /files/files` 上傳的通用檔案（1.3 節只有 upload，這裡補 download）。

**函式**: `Files.get_file_content(file)`

**HTTP**:
```
GET /files/files/{fileId}/content
```

**Request Headers**:
```http
GET /files/files/{fileId}/content HTTP/1.1
Authorization: Bearer {access_token}
Accept: application/octet-stream        ← 二進位檔
```

**Response 行為**（`get_file_content` 依 Content-Type 自動切換）：
```
Content-Type: text/plain          → 回傳 str
Content-Type: application/json   → 回傳 dict
Content-Type: application/octet-stream → 回傳 bytes
```

**程式碼範例（sasctl）**:
```python
from sasctl._services.files import Files

with sasctl.Session(...):
    # get_file 先取 metadata（含 id）
    file_meta = Files.get_file("large_data.parquet")
    content = Files.get_file_content(file_meta)
    # content 是 bytes（octet-stream）
    with open("downloaded_data.parquet", "wb") as f:
        f.write(content)
```

**純 HTTP**:
```python
# 先取 fileId
list_resp = requests.get(
    f"{BASE}/files/files",
    headers={"Authorization": f"Bearer {TOKEN}"},
    params={"name": "large_data.parquet"},
)
file_id = list_resp.json()["items"][0]["id"]

# 下載
dl_resp = requests.get(
    f"{BASE}/files/files/{file_id}/content",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/octet-stream",
    },
    stream=True,
)
with open("downloaded_data.parquet", "wb") as f:
    for chunk in dl_resp.iter_content(chunk_size=1024 * 1024):
        f.write(chunk)
```

---

## 六、操作速查表

### 檔案上傳對比

| 操作 | HTTP Method | Endpoint | Content-Type | 適用場景 |
|---|---|---|---|---|
| 上傳單一檔案到模型 | `POST` | `/modelRepository/models/{id}/contents` | `multipart/form-data` | 分批上傳 pickle、score code 等 |
| 上傳 bytes 到模型 | `POST` | `/modelRepository/models/{id}/contents` | `application/octet-stream` | 二進位內容（自動判斷） |
| ZIP 匯入整包模型 | `POST` | `/modelRepository/models?type=ZIP&...` | `application/octet-stream` | 含所有內容的完整模型包 |
| SAS Files 通用上傳 | `POST` | `/files/files` | `multipart/form-data` | 非模型相關的通用檔案存放 |

### 下載 / 刪除對比（Section 5 補足）

| 操作 | HTTP Method | Endpoint | Accept | 說明 |
|---|---|---|---|---|
| 查詢可用 Repository | `GET` | `/modelRepository/repositories` | `application/vnd.sas.collection+json` | 建立 project 前取 repo UUID |
| 下載模型 content 檔案 | `GET` | `/modelRepository/models/{id}/contents/{contentId}` | `application/octet-stream` | 取回 pkl 等二進位檔 |
| 刪除模型單一 content | `DELETE` | `/modelRepository/models/{id}/contents/{contentId}` | — | 替換 pkl 時先刪舊的 |
| 下載 Files API 檔案 | `GET` | `/files/files/{fileId}/content` | `application/octet-stream` | 取回 Files 服務的通用檔案 |

### 版本管理對比

| 操作 | HTTP Method | Endpoint | Body | 說明 |
|---|---|---|---|---|
| 建立新版本 | `POST` | `/modelRepository/models/{id}/modelVersions` | `{"option":"major"}` | major / minor 版本 |
| 列出版本 | `GET` | `/modelRepository/models/{id}/modelVersions` | — | 取版本 id / name |
| 設為冠軍 | `PUT` | `/modelRepository/models/{id}` | `{...,"role":"champion"}` | 需帶 If-Match ETag |

### Header 組成矩陣

| 操作類型 | Authorization | Content-Type | If-Match | Accept |
|---|---|---|---|---|
| GET 查詢 | ✅ Bearer (自動) | — | — | — |
| POST 建立（JSON） | ✅ Bearer (自動) | `application/vnd.sas.models.*.json` | — | — |
| POST 上傳 multipart | ✅ Bearer (自動) | `multipart/form-data` (自動含 boundary) | — | — |
| POST 上傳 bytes | ✅ Bearer (自動) | `application/octet-stream` | — | — |
| PUT 更新 | ✅ Bearer (自動) | 沿用前次 GET 值 | ✅ ETag (自動) | — |
| DELETE 刪除 | ✅ Bearer (自動) | — | — | — |

### Content-Type 對照

| SAS Viya 資源類型 | Content-Type |
|---|---|
| 模型 JSON | `application/vnd.sas.models.model+json` |
| 專案 JSON | `application/vnd.sas.models.project+json` |
| 發佈請求 | `application/vnd.sas.models.publishing.request.asynchronous+json` |
| CAS 目的地 | `application/vnd.sas.models.publishing.destination.cas+json` |
| MAS 目的地 | `application/vnd.sas.models.publishing.destination.microAnalyticService+json` |
| 檔案上傳 | `multipart/form-data` 或 `application/octet-stream` |

---

## 七、Session 建立方式

所有以上操作均需在 `sasctl.Session` context manager 內執行：

```python
import sasctl
from sasctl._services.model_repository import ModelRepository

# 方式 A：username/password
with sasctl.Session(
    host="https://your-sas-viya-host",
    username="sas_user",
    password="sas_password",
    verify_ssl=False    # 若使用自簽憑證
):
    models = ModelRepository.list_models()

# 方式 B：直接使用 access_token
session = sasctl.Session(
    host="https://your-sas-viya-host",
    token="eyJhbGciOiJSU..."
)
with session:
    project = ModelRepository.get_project("ChurnPrediction")
```

> **Token 端點**：`POST /SASLogon/oauth/token`
> **Headers**: `Content-Type: application/x-www-form-urlencoded`, `Accept: application/json`

---

## 八、純 HTTP 呼叫：名稱→UUID 解析模式

> **純 HTTP 的核心問題**：sasctl 可以傳名稱字串（如 `"ChurnPrediction"`），內部會自動查找 UUID。
> 但純 HTTP 呼叫 `POST /modelRepository/models` 時，body 需要 `"projectId": "{uuid}"`，不能傳名稱。
> 以下列出每個資源的 name→UUID 查詢方式。

### 8.1 Filter 語法

SAS Viya 支援 OData-like filter 語法（`filter=` query param）：

| 語法 | 說明 | 範例 |
|---|---|---|
| `eq(field,"value")` | 精確匹配 | `filter=eq(name,"ChurnPrediction")` |
| `contains(field,"value")` | 模糊包含 | `filter=contains(name,"Churn")` |
| `in(field,"v1","v2")` | 多值 IN | `filter=in(projectId,"uuid1","uuid2")` |

> ⚠️ **[需實測] filter 語法普適性**：上述語法從 sasctl source 觀察到但未逐一驗證。待確認：(1) query param 名稱是 `filter` 還是 `$filter`；(2) `eq`/`contains`/`in` 是否對所有 list endpoint（repositories / projects / models）均有效；(3) 大小寫是否敏感。

### 8.2 各資源名稱→UUID 查詢

#### Repository UUID（建立 Project 前必須取得）

```python
resp = requests.get(
    f"{BASE}/modelRepository/repositories",
    headers={"Authorization": f"Bearer {TOKEN}"},
    params={"filter": 'eq(name,"Public")'},
)
repo_id = resp.json()["items"][0]["id"]
```

#### Project UUID（建立 Model 前必須取得）

```python
resp = requests.get(
    f"{BASE}/modelRepository/projects",
    headers={"Authorization": f"Bearer {TOKEN}"},
    params={"filter": 'eq(name,"ChurnPrediction")'},
)
project_id = resp.json()["items"][0]["id"]
```

#### Model UUID（上傳 Content 或版控前必須取得）

```python
resp = requests.get(
    f"{BASE}/modelRepository/models",
    headers={"Authorization": f"Bearer {TOKEN}"},
    params={"filter": 'eq(name,"LogisticChurn_v1")'},
)
model_id = resp.json()["items"][0]["id"]
```

#### Content ID（下載或刪除特定檔案前必須取得）

```python
resp = requests.get(
    f"{BASE}/modelRepository/models/{model_id}/contents",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
items = resp.json()
# contents 可能是 list 或 {"items": [...]}
items = items if isinstance(items, list) else items.get("items", [])
pkl_id = next(c["id"] for c in items if c["name"].endswith(".pkl"))
```

### 8.3 版控用途完整 ID 解析鏈

```python
import requests, base64

BASE = "https://your-viya-host"
TOKEN = "eyJhbGci..."   # 見附錄 E 取得方式

def get_id(path, filter_str):
    r = requests.get(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {TOKEN}"},
        params={"filter": filter_str},
    )
    r.raise_for_status()
    items = r.json()
    items = items if isinstance(items, list) else items.get("items", [])
    return items[0]["id"]

repo_id    = get_id("/modelRepository/repositories", 'eq(name,"Public")')
project_id = get_id("/modelRepository/projects",    'eq(name,"ChurnPrediction")')
model_id   = get_id("/modelRepository/models",      'eq(name,"LogisticChurn_v1")')
```

---

## 附錄 A：ZIP 封包格式規格

> **適用操作**：`ModelRepository.import_model_from_zip()`
> **來源**：`pzmm/zip_model.py`、`pzmm/write_json_files.py`（版本 1.11.7）

### A.1 ZIP 必要檔案清單

| 檔案名稱 | 必填 | Viya 版本 | 說明 |
|---|---|---|---|
| `fileMetadata.json` | ✅ 必填 | 3.5 + 4 | **最關鍵**：告訴 SAS Model Manager 各檔案的角色 |
| `inputVar.json` | ✅ 必填 | 3.5 + 4 | 模型輸入變數定義（名稱、型別、長度） |
| `outputVar.json` | ✅ 必填 | 3.5 + 4 | 模型輸出變數定義 |
| `ModelProperties.json` | ✅ 必填 | 3.5 + 4 | 模型後設資料（演算法、函數類型、目標變數等） |
| `score_{prefix}.py` | ✅ Viya 4 | 僅 Viya 4 | 評分程式碼；**Viya 3.5 不放入 ZIP**，改用 `add_model_content()` 另行上傳 |
| `{prefix}.pickle` | ✅ 擇一 | 3.5 + 4 | Python pickle 序列化模型 |
| `{prefix}.mojo` | ✅ 擇一 | 3.5 + 4 | H2O.ai MOJO 格式模型 |
| `{prefix}.h5` | ✅ 擇一 | 3.5 + 4 | TensorFlow/Keras HDF5 格式模型 |

> `{prefix}` = `model_prefix` 參數，也是 `import_model_from_zip()` 的 `name` 參數（空白會被替換為底線）。

**Source**: `pzmm/zip_model.py` `_filter_files()`:
```python
file_names.extend(sorted(Path(file_dir).glob("*.json")))   # 所有 JSON 檔案
if is_viya4:
    file_names.extend(sorted(Path(file_dir).glob("score_*.py")))  # Viya 4 才包含 score code
file_names.extend(sorted(Path(file_dir).glob("*.pickle")))
file_names.extend(sorted(Path(file_dir).glob("*.mojo")))
```

---

### A.2 `fileMetadata.json` — 檔案角色對應表

**這是最關鍵的檔案**，SAS Model Manager 根據此檔案識別哪個是 score code、哪個是模型二進位。

**標準格式（Python pickle + score code）**：
```json
[
  {"role": "inputVariables",  "name": "inputVar.json"},
  {"role": "outputVariables", "name": "outputVar.json"},
  {"role": "score",           "name": "score_MyModel.py"},
  {"role": "scoreResource",   "name": "MyModel.pickle"}
]
```

**H2O.ai MOJO 格式**（`role` 改為 `scoreResource` → `.mojo`）：
```json
[
  {"role": "inputVariables",  "name": "inputVar.json"},
  {"role": "outputVariables", "name": "outputVar.json"},
  {"role": "score",           "name": "score_MyModel.py"},
  {"role": "scoreResource",   "name": "MyModel.mojo"}
]
```

**有效的 role 值**：

| role 值 | 說明 |
|---|---|
| `"inputVariables"` | 輸入變數定義 JSON |
| `"outputVariables"` | 輸出變數定義 JSON |
| `"score"` | 評分程式碼（Python score code） |
| `"scoreResource"` | 評分所需的模型二進位（pickle / mojo / h5） |

> **注意**：`add_model_content()` 的 `role` 參數值與此不同！詳見 A.5。

**Source**: `pzmm/write_json_files.py` `write_file_metadata_json()`:
```python
dict_list = [
    {"role": "inputVariables", "name": INPUT},       # "inputVar.json"
    {"role": "outputVariables", "name": OUTPUT},     # "outputVar.json"
    {"role": "score", "name": f"score_{sanitized_prefix}.py"},
]
# 依模型類型追加:
{"role": "scoreResource", "name": sanitized_prefix + ".pickle"}  # 或 .mojo / .h5
```

---

### A.3 `inputVar.json` / `outputVar.json` — 變數定義格式

兩個檔案結構相同，都是**陣列格式**，每個元素代表一個變數：

**數值型變數（`level: "interval"`）**：
```json
[
  {"name": "age",    "level": "interval", "type": "decimal", "length": 8},
  {"name": "income", "level": "interval", "type": "decimal", "length": 8}
]
```

**類別型變數（`level: "nominal"`）**：
```json
[
  {"name": "gender",   "level": "nominal", "type": "string", "length": 6},
  {"name": "region",   "level": "nominal", "type": "string", "length": 10}
]
```

**混合型（常見的 inputVar.json 範例）**：
```json
[
  {"name": "age",      "level": "interval", "type": "decimal", "length": 8},
  {"name": "balance",  "level": "interval", "type": "decimal", "length": 8},
  {"name": "job",      "level": "nominal",  "type": "string",  "length": 25},
  {"name": "marital",  "level": "nominal",  "type": "string",  "length": 10}
]
```

**`outputVar.json` 範例（二元分類模型）**：
```json
[
  {"name": "P_churn1",   "level": "interval", "type": "decimal", "length": 8},
  {"name": "P_churn0",   "level": "interval", "type": "decimal", "length": 8},
  {"name": "EM_EVENTPROBABILITY", "level": "interval", "type": "decimal", "length": 8},
  {"name": "EM_CLASSIFICATION",  "level": "nominal",  "type": "string",  "length": 32}
]
```

**Source**: `pzmm/write_json_files.py` `generate_variable_properties()`:
```python
var_dict = {"name": name}
if is_str:
    var_dict.update({"level": "nominal", "type": "string",  "length": int(predict.str.len().max())})
else:
    var_dict.update({"level": "interval", "type": "decimal", "length": 8})
```

---

### A.4 `ModelProperties.json` — 模型後設資料格式

```json
{
  "name":            "ChurnLogistic",
  "description":     "Binary churn prediction model - Q1 2024",
  "scoreCodeType":   "python",
  "trainTable":      "",
  "trainCodeType":   "Python",
  "algorithm":       "Logistic Regression",
  "function":        "classification",
  "targetVariable":  "churn_flag",
  "targetEvent":     "1",
  "targetLevel":     "Binary",
  "eventProbVar":    "P_1",
  "modeler":         "data_scientist_name",
  "tool":            "Python 3",
  "toolVersion":     "3.10.12",
  "properties":      []
}
```

**`targetLevel` 可能值**（由 `target_values` 決定）：

| 情況 | `targetLevel` | `targetEvent` |
|---|---|---|
| `target_values=None` | `"Interval"` | `""` |
| `target_values=["1","0"]`（二元分類） | `"Binary"` | `"1"` |
| `target_values=["A","B","C"]`（多類別） | `"Nominal"` | `""` |

**Source**: `pzmm/write_json_files.py` `write_model_properties_json()`

---

### A.5 `add_model_content()` 的 `role` 參數值

與 `fileMetadata.json` 的 role 值**不同**，這是 SAS Viya API query param：

| role 參數值 | 說明 |
|---|---|
| `"Python pickle"` | pickle 序列化的模型檔案 |
| `"score"` | 評分用 Python script |
| `"scoreResource"` | 評分資源（model binary） |
| `None`（預設） | 一般附件，不指定角色 |

**Source**: `pzmm/_services/model_repository.py` docstring:
```
role : str
    Role of the model file, such as 'Python pickle'. Default value is None.
```

---

### A.6 完整 ZIP 建立範例（Python）

```python
import pickle
import json
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import sasctl
from sasctl._services.model_repository import ModelRepository

model_prefix = "ChurnLogistic"

# 1. 準備各 JSON 檔案內容
file_metadata = json.dumps([
    {"role": "inputVariables",  "name": "inputVar.json"},
    {"role": "outputVariables", "name": "outputVar.json"},
    {"role": "score",           "name": f"score_{model_prefix}.py"},
    {"role": "scoreResource",   "name": f"{model_prefix}.pickle"},
])

input_vars = json.dumps([
    {"name": "age",     "level": "interval", "type": "decimal", "length": 8},
    {"name": "balance", "level": "interval", "type": "decimal", "length": 8},
    {"name": "job",     "level": "nominal",  "type": "string",  "length": 20},
])

output_vars = json.dumps([
    {"name": "P_churn1", "level": "interval", "type": "decimal", "length": 8},
    {"name": "P_churn0", "level": "interval", "type": "decimal", "length": 8},
])

model_props = json.dumps({
    "name": model_prefix,
    "description": "Binary churn prediction",
    "scoreCodeType": "python",
    "algorithm": "Logistic Regression",
    "function": "classification",
    "targetVariable": "churn_flag",
    "targetEvent": "1",
    "targetLevel": "Binary",
    "eventProbVar": "P_1",
    "tool": "Python 3",
    "toolVersion": "3.10.12",
    "properties": [],
})

score_code = """
import pickle, os

with open(os.path.join(os.path.dirname(__file__), "ChurnLogistic.pickle"), "rb") as f:
    model = pickle.load(f)

def score(age, balance, job):
    proba = model.predict_proba([[age, balance, job]])[0]
    return proba[1], proba[0]
"""

# 2. 序列化 model（範例）
import pickle as pkl
model_bytes = pkl.dumps(trained_model)

# 3. 組裝 ZIP（in-memory）
buffer = BytesIO()
with ZipFile(buffer, "w", ZIP_DEFLATED, False) as zf:
    zf.writestr("fileMetadata.json", file_metadata)
    zf.writestr("inputVar.json",     input_vars)
    zf.writestr("outputVar.json",    output_vars)
    zf.writestr("ModelProperties.json", model_props)
    zf.writestr(f"score_{model_prefix}.py", score_code)
    zf.writestr(f"{model_prefix}.pickle",   model_bytes)

# 4. 上傳
with sasctl.Session(host="https://your-viya-host", username="user", password="pass"):
    model = ModelRepository.import_model_from_zip(
        name=model_prefix,
        project="ChurnPrediction",
        file=buffer,
        version="latest"
    )
    print(f"匯入成功，模型 ID: {model.id}")
```

---

### A.7 最小模型需求：只有 pkl 也可以嗎？

**結論：取決於使用哪條路徑。**

| 路徑 | `fileMetadata.json` | 其他 JSON | 最少需要的檔案 |
|---|---|---|---|
| `import_model_from_zip()` | ✅ **必要** | 建議含 inputVar / outputVar / ModelProperties | ≥ 1 JSON + 1 binary |
| `create_model()` + `add_model_content()` | ❌ **不需要** | ❌ 不需要 | **只有 pkl 也可以** |

**原因**：
- ZIP 匯入路徑：SAS 透過 `fileMetadata.json` 的 `role` 欄位才知道 ZIP 裡哪個是 score code、哪個是 model binary
- 步驟拆開路徑：`add_model_content()` 的 `role=` query parameter 直接指定角色，不需要 `fileMetadata.json`

**只有 pkl 的最小範例**：

```python
import sasctl
from sasctl._services.model_repository import ModelRepository

with sasctl.Session(host="https://your-viya-host", username="user", password="pass"):
    # 步驟 1：建立模型記錄（只是 metadata，無需任何檔案）
    model = ModelRepository.create_model(
        model="MinimalModel",
        project="MyProject",
        tool="Python 3",
        function="classification",
    )

    # 步驟 2：只上傳 pkl，不需要 fileMetadata / inputVar / outputVar
    with open("model.pkl", "rb") as f:
        ModelRepository.add_model_content(
            model=model,
            file=f.read(),
            name="model.pkl",
            role="Python pickle",
        )
    # 完成 — 模型已登錄，SAS Model Manager 中可見
```

> ⚠️ **功能限制**：沒有 score code（`role="score"`）的模型，SAS Model Manager 原生的 scoring 與 publishing 功能（如 MAS 部署）無法使用。若你的使用場景是**單純 artifact 版本管理**（儲存 pkl、追蹤版本、之後自行呼叫推論），只有 pkl 完全足夠。

---

## 附錄 B：Streaming 支援分析

> **來源**：直接閱讀 `sasctl/_services/files.py`、`sasctl/_services/model_repository.py` 原始碼

### B.1 `POST /files/files`（`Files.create_file()`）— ❌ 不支援 Streaming

**原始碼佐證**（`files.py` lines 69-72）：

```python
elif not isinstance(file, bytes):
    if filename is None:
        raise ValueError("`filename` must be specified if `file` is not a path.")
    file = file.read()   # ← 整個檔案內容讀入 Python 記憶體，再送出
```

**行為說明**：
- 輸入為 `str`/`Path` → 開啟後 `file.read()` 讀入 bytes
- 輸入為 file-like → **強制呼叫 `.read()`**，全部載入記憶體後才建立 multipart request
- `files={filename: file}` 傳出的是已完整在記憶體的 bytes
- **結論**：**完全不支援 streaming，所有檔案內容在送出前已全部在記憶體中**

---

### B.2 `POST /modelRepository/models?type=ZIP`（`import_model_from_zip()`）— ❌ 不支援 Streaming

**原始碼佐證**（`model_repository.py` lines 560-565）：

```python
if not isinstance(file, bytes):
    if file.seekable():
        file.seek(0)
    file = file.read()   # ← 整個 ZIP 讀入記憶體
```

**行為說明**：
- 非 bytes 輸入一律呼叫 `.read()`，全部載入記憶體
- 接著以 `data=file`（bytes）送出 `Content-Type: application/octet-stream`
- **結論**：**完全不支援 streaming**

---

### B.3 `POST /modelRepository/models/{id}/contents`（`add_model_content()`）— ⚠️ 部分支援

**原始碼**（`model_repository.py` lines 425-445）：

```python
# dict → 轉為 JSON string（記憶體）
elif isinstance(file, dict):
    file = json.dumps(file)

# 不論是 bytes、string 還是 file-like，都直接組 files tuple
files = {"files": (name, file, content_type)}

return cls.post("/models/{}/contents".format(id_), files=files, params=params)
```

```python
# 409 重試時的處理 —— 說明 file-like 需要 seek() 支援
if hasattr(files["files"][1], "seek"):
    files["files"][1].seek(0)
```

**行為說明**：

| 輸入型別 | sasctl 行為 | 記憶體佔用 |
|---|---|---|
| `bytes` | 直接組入 multipart，已在記憶體 | ❌ 全部在記憶體 |
| `dict` | `json.dumps()` → string → multipart | ❌ 全部在記憶體 |
| file-like（`io.BytesIO` 等） | **不呼叫 `.read()`**，直接傳給 requests | ⚠️ requests 準備 multipart body 時才讀取 |

**file-like 路徑的實際行為**：
- sasctl **不**在自己的程式碼中呼叫 `.read()`
- 但 `requests` 在 `PreparedRequest.prepare_body()` 準備 multipart 時仍會將整個 file-like 的內容讀入記憶體一次
- 因此仍**不是真正的 HTTP chunked streaming**，只是延後了讀取時機

**結論**：三種上傳方法均無法真正做到 HTTP streaming 上傳。

---

### B.4 大檔案上傳的建議做法

若需處理大型模型檔案（>500MB），sasctl 目前無原生 streaming 支援。建議：

1. **使用 pzmm 的 `ZipModel.zip_files()` 組裝 in-memory ZIP**，僅在 SAS Model Manager API 確認可接受大檔案時使用
2. **直接使用 `requests` 搭配 `requests-toolbelt` 的 `MultipartEncoder`** 做 streaming multipart upload：
   ```python
   from requests_toolbelt import MultipartEncoder
   import sasctl

   with sasctl.Session(host=...) as session:
       with open("large_model.pkl", "rb") as f:
           encoder = MultipartEncoder(
               fields={"files": ("large_model.pkl", f, "application/octet-stream")}
           )
           response = session.post(
               f"/modelRepository/models/{model_id}/contents",
               data=encoder,
               headers={
                   "Content-Type": encoder.content_type,  # 含 boundary
               },
               params="role=Python pickle"
           )
   ```
3. **分割大型模型**：若業務允許，考慮分割成較小的模型版本

---

## 附錄 C：純 HTTP 呼叫的大檔案處理策略

> **適用場景**：直接使用 `requests` / `httpx` 呼叫 SAS Viya 端點，不透過 sasctl。
> **核心原則**：`data=file_object` vs `files=file_object` 記憶體行為**完全不同**。

### C.1 關鍵差異：`data=` vs `files=`

**來源**：`requests.models.PreparedRequest.prepare_body()` + `urllib3.filepost.encode_multipart_formdata()`

```
data=open("file.pkl","rb")
  └─ prepare_body 偵測到 __iter__ → stream mode
     └─ super_len(f) → os.fstat → Content-Length（或 chunked 若無法取得大小）
        └─ socket 層逐塊傳輸（8KB/次）
           ✅ 記憶體：僅 socket 緩衝，不載入整個檔案

files={"key": open("file.pkl","rb")}
  └─ urllib3.encode_multipart_formdata()
     └─ body = BytesIO()
        for field in fields:
            body.write(field.data)   ← 整個 field.data 寫入記憶體
        return body.getvalue()       ← 回傳全部 bytes
           ❌ 記憶體：整個檔案一次載入
```

| 參數 | Content-Type | 記憶體行為 | 適合場景 |
|---|---|---|---|
| `data=file_object` | 由你指定 | ✅ 不緩衝（socket chunks） | 大檔案（推薦） |
| `data=generator()` | 由你指定 | ✅ 不緩衝（chunked encoding） | 不知大小時 |
| `files={k: file_object}` | multipart（自動） | ❌ 全部緩衝 | 小檔案 |
| `data=bytes` | 由你指定 | ❌ 全部在記憶體 | 小檔案 |

---

### C.2 策略一：`application/octet-stream` + `data=file_object`（最簡單）

適用端點：
- `POST /modelRepository/models/{id}/contents`（模型檔案上傳）
- `POST /modelRepository/models?type=ZIP&...`（ZIP 匯入）
- `POST /files/files`（通用上傳，docstring 明確支援 "raw request"）

```python
import requests

BASE_URL = "https://your-viya-host"
TOKEN = "eyJhbGci..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/octet-stream",
}

# ─── 上傳 pickle 到模型 ───────────────────────────────────────────
model_id = "a1b2c3d4-..."
with open("/path/to/large_model.pkl", "rb") as f:
    # data=f → requests 用 os.fstat 取得大小設 Content-Length
    # socket 層逐塊送出，不把整個檔案載入記憶體
    response = requests.post(
        f"{BASE_URL}/modelRepository/models/{model_id}/contents",
        data=f,
        headers=headers,
        params={"role": "Python pickle"},
        verify=False,  # 若自簽憑證
    )
response.raise_for_status()

# ─── ZIP 匯入整包模型 ─────────────────────────────────────────────
project_id = "proj-uuid-..."
with open("/path/to/model_package.zip", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/modelRepository/models",
        data=f,
        headers=headers,
        params={
            "name": "ChurnLogistic_v3",
            "type": "ZIP",
            "projectId": project_id,
            "versionOption": "latest",
        },
    )
response.raise_for_status()

# ─── 通用大檔案上傳（raw 模式）────────────────────────────────────
with open("/path/to/large_data.parquet", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/files/files",
        data=f,
        headers={
            **headers,
            "Slug": "large_data.parquet",  # SAS Files API 用 Slug header 指定檔名
        },
    )
response.raise_for_status()
```

> **`Slug` Header**：SAS Files API 的 raw upload 用 `Slug` header 傳檔案名稱，而非 multipart 的 `Content-Disposition: filename`。

---

### C.3 策略二：Chunked Transfer Encoding（不知檔案大小時）

當資料來源是動態產生的串流（例如壓縮中的資料、管道輸出），無法事先知道 Content-Length：

```python
import requests
from pathlib import Path

def zip_stream_generator(source_dir, chunk_size=1024 * 1024):
    """動態產生 ZIP 內容的 generator（示意）"""
    import zipfile, io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in Path(source_dir).glob("*"):
            zf.write(path, arcname=path.name)
    buffer.seek(0)
    while chunk := buffer.read(chunk_size):
        yield chunk

# requests 偵測到 generator（有 __iter__，無 Content-Length）
# → 自動設定 Transfer-Encoding: chunked
response = requests.post(
    f"{BASE_URL}/modelRepository/models",
    data=zip_stream_generator("./model_files"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/octet-stream",
    },
    params={"name": "DynamicModel", "type": "ZIP", "projectId": "proj-uuid"},
)
```

> ⚠️ **注意**：若遇到 `411 Length Required` 錯誤，代表該端點要求 Content-Length，改用策略一（`data=file_object` + 固定大小檔案）。

---

### C.4 策略三：Streaming Multipart（`requests-toolbelt`）

當端點必須使用 multipart，或需要同時帶多個 field：

```python
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import requests

# ─── 基本 streaming multipart ────────────────────────────────────
with open("/path/to/large_model.pkl", "rb") as f:
    encoder = MultipartEncoder(
        fields={"files": ("large_model.pkl", f, "application/octet-stream")}
    )
    response = requests.post(
        f"{BASE_URL}/modelRepository/models/{model_id}/contents",
        data=encoder,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": encoder.content_type,  # 含 boundary
        },
        params={"role": "Python pickle"},
    )

# ─── 加上進度監控 ─────────────────────────────────────────────────
def upload_progress(monitor):
    pct = monitor.bytes_read / monitor.len * 100
    print(f"\r上傳進度: {pct:.1f}%", end="", flush=True)

with open("/path/to/large_model.pkl", "rb") as f:
    encoder = MultipartEncoder(
        fields={"files": ("large_model.pkl", f, "application/octet-stream")}
    )
    monitor = MultipartEncoderMonitor(encoder, upload_progress)
    response = requests.post(
        f"{BASE_URL}/modelRepository/models/{model_id}/contents",
        data=monitor,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": monitor.content_type,
        },
        params={"role": "Python pickle"},
    )
print()
```

**安裝**：`uv add requests-toolbelt`

---

### C.5 策略四：`httpx` 非同步串流（FastAPI / async 環境）

```python
import httpx

async def upload_large_model(model_id: str, file_path: str, token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
        async def file_stream():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):  # 1MB chunks
                    yield chunk

        response = await client.post(
            f"https://your-viya-host/modelRepository/models/{model_id}/contents",
            content=file_stream(),
            headers=headers,
            params={"role": "Python pickle"},
        )
        response.raise_for_status()
        return response.json()
```

---

### C.6 各端點推薦策略速查

| SAS Viya 端點 | octet-stream | 推薦大檔案策略 |
|---|---|---|
| `POST /modelRepository/models/{id}/contents` | ✅ | **策略一**：`data=open_file` + `Content-Type: application/octet-stream` |
| `POST /modelRepository/models?type=ZIP` | ✅（唯一選項） | **策略一**：`data=open_file`，若動態產生用策略二 |
| `POST /files/files` | ✅（raw 模式） | **策略一**：`data=open_file` + `Slug: {filename}` header |

**檔案大小建議**：
- `< 50MB`：任何方式均可
- `50MB ~ 500MB`：策略一（`data=file_object`），避免 OOM
- `> 500MB`：策略一 + `timeout=600`，或策略二（chunked）+ 確認伺服器支援

---

## 附錄 D：版控專用工作流程（Model Registry 用途）

> **適用場景**：主管目標是把 SAS Model Manager 當作**模型版控系統**，不在 SAS Viya 上執行 predict / train / explain。

### D.1 「SAS 發佈」vs「版控登錄」差異

很多人混淆 SAS Model Manager 的「Publish」跟「版控」，這兩件事是完全獨立的。

| 操作 | SAS 術語 | 目的 | pkl only 可行？ | 需要 score code？ |
|---|---|---|---|---|
| 登錄模型 + 上傳 pkl | Register / Create Model | 存入 artifact | ✅ 是 | ❌ 不需要 |
| 建立新版本 | Create Version | 版本歷史追蹤 | ✅ 是 | ❌ 不需要 |
| 設為冠軍模型 | Set Champion | 標記當前生產版本 | ✅ 是 | ❌ 不需要 |
| 下載特定版本 pkl | Get Version Content | 取回模型檔案 | ✅ 是 | ❌ 不需要 |
| 發佈到 MAS | Publish to MAS | 部署為即時推論服務 | ❌ 否 | ✅ 必要（DS2 包裝） |
| 發佈到 CAS | Publish to CAS | 部署為批次推論表格 | ❌ 否 | ✅ 必要 |

**結論**：你的版控用途只需要上面前四項，**完全不需要 Publish**。

---

### D.2 版控最小操作集（sasctl 版本）

```python
import sasctl
from sasctl._services.model_repository import ModelRepository as MR

# ─── Session 建立 ─────────────────────────────────────────────────
with sasctl.Session(
    hostname="https://your-viya-host",
    username="user",
    password="pass",
    verify_ssl=False,
):
    # ── 1. 確保專案存在（建立或查詢）───────────────────────────────
    project = MR.get_project("ChurnModels")
    if project is None:
        project = MR.create_project(
            project="ChurnModels",
            repository="Public",   # 預設 repository 名稱
            function="classification",
            target_variable="churn_flag",
            target_level="Binary",
        )

    # ── 2. 登錄模型 v1.0（第一次）────────────────────────────────
    model = MR.create_model(
        model="ChurnLogistic_v1",
        project=project,
        tool="Python 3",
        tool_version="3.10",
        algorithm="Logistic Regression",
        function="classification",
        description="Churn prediction model - initial release",
        is_champion=True,          # 登錄即設為冠軍
    )

    # ── 3. 上傳 pkl ──────────────────────────────────────────────
    with open("churn_model_v1.pkl", "rb") as f:
        MR.add_model_content(
            model=model,
            file=f.read(),
            name="churn_model_v1.pkl",
            role="Python pickle",
        )
    print(f"模型登錄完成，ID: {model.id}")

    # ── 4. 建立新版本（當模型更新時）─────────────────────────────
    # major=True (預設)：v1.0 → v2.0
    # minor=True：v1.0 → v1.1
    model_v2 = MR.create_model_version(model=model, minor=False)  # → v2.0

    # ── 5. 上傳 v2 pkl ─────────────────────────────────────────
    with open("churn_model_v2.pkl", "rb") as f:
        MR.add_model_content(
            model=model_v2,
            file=f.read(),
            name="churn_model_v2.pkl",
            role="Python pickle",
        )

    # ── 6. 查詢版本歷史 ─────────────────────────────────────────
    versions = MR.list_model_versions(model=model)
    for v in versions:
        print(f"版本: {v.get('modelVersionName', v.id)}")

    # ── 7. 下載特定版本的 pkl ─────────────────────────────────────
    target_version_id = versions[0].id   # 取第一個歷史版本
    contents = MR.get_model_version_contents(model, target_version_id)
    pkl_item = next(c for c in contents if c["name"].endswith(".pkl"))
    pkl_data = MR.get_model_version_content(model, target_version_id, pkl_item.id)
    with open("downloaded_model.pkl", "wb") as f:
        f.write(pkl_data if isinstance(pkl_data, bytes) else pkl_data.encode())
```

---

### D.3 純 HTTP 端點對照（不依賴 sasctl）

版控所需的所有操作，純 HTTP 端點清單：

| 操作 | Method | 端點 | 重要 Header / Body |
|---|---|---|---|
| 建立專案 | `POST` | `/modelRepository/projects` | `Content-Type: application/vnd.sas.models.project+json` |
| 登錄模型 | `POST` | `/modelRepository/models` | `Content-Type: application/vnd.sas.models.model+json`，body 含 `"role":"champion"` |
| 上傳 pkl | `POST` | `/modelRepository/models/{id}/contents?role=Python%20pickle` | `Content-Type: application/octet-stream`，`data=open_file` |
| 建立新版本 | `POST` | `/modelRepository/models/{id}/modelVersions` | body: `{"option": "major"}` 或 `{"option": "minor"}` |
| 列出版本歷史 | `GET` | `/modelRepository/models/{id}/modelVersions` | `Accept: application/vnd.sas.collection+json` |
| 取版本內容清單 | `GET` | `/modelRepository/models/{id}/modelVersions/{versionId}/contents` | `Accept: application/vnd.sas.collection+json` |
| 下載版本中的 pkl | `GET` | `/modelRepository/models/{id}/modelVersions/{versionId}/contents/{contentId}` | `Accept: text/plain`（二進位檔也用此 header） |
| 設冠軍模型 | `PUT` | `/modelRepository/models/{id}` | `Content-Type: application/vnd.sas.models.model+json`，body: `{"role":"champion"}` |
| 查詢模型詳情 | `GET` | `/modelRepository/models/{id}` | `Authorization: Bearer {token}` |

**純 HTTP 版控範例（下載版本中的 pkl）**：

```python
import requests

TOKEN = "eyJhbGci..."
BASE = "https://your-viya-host"
MODEL_ID = "model-uuid"
VERSION_ID = "version-uuid"

# 1. 取版本內容清單
resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}/modelVersions/{VERSION_ID}/contents",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.sas.collection+json",
    },
)
contents = resp.json()["items"]

# 2. 找到 pkl（role == "Python pickle"）
pkl_item = next(c for c in contents if c.get("role") == "Python pickle")
content_id = pkl_item["id"]

# 3. 下載 pkl（stream=True 避免緩衝）
resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}/modelVersions/{VERSION_ID}/contents/{content_id}",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "text/plain",
    },
    stream=True,  # ← 大檔案時不緩衝回應體
)
with open("downloaded.pkl", "wb") as f:
    for chunk in resp.iter_content(chunk_size=1024 * 1024):
        f.write(chunk)
```

---

### D.4 版本狀態管理

SAS Model Manager 的版控核心是 **Project + Champion/Challenger** 機制：

```
Project（專案 = 模型家族）
  ├── Champion Model（當前生產版本，每個 project 只有一個）
  │     └── v2.0（最新 major 版本）
  │          ├── churn_model_v2.pkl   role=Python pickle
  │          └── （不需要 score code）
  └── Challenger Model（候選版本，可多個）
        └── v3.0-beta
             └── churn_model_v3beta.pkl
```

**設定/切換冠軍模型（純 HTTP）**：

```python
import requests

# 先取得目前模型的 ETag（更新必須帶 If-Match header 防並發衝突）
get_resp = requests.get(
    f"{BASE}/modelRepository/models/{MODEL_ID}",
    headers={"Authorization": f"Bearer {TOKEN}"},
)
etag = get_resp.headers["ETag"]
model_body = get_resp.json()

# 更新為冠軍
model_body["role"] = "champion"
put_resp = requests.put(
    f"{BASE}/modelRepository/models/{MODEL_ID}",
    json=model_body,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/vnd.sas.models.model+json",
        "If-Match": etag,          # ← SAS Viya PUT 必須帶 ETag
    },
)
put_resp.raise_for_status()
print(f"已設為冠軍: {put_resp.json()['name']}")
```

> **`role` 可選值**：`"champion"` / `"challenger"` / `""（清除角色）`

---

## 附錄 E：OAuth2 完整認證流程（純 HTTP 呼叫必看）

> **來源**：`sasctl/core.py` `Session._request_token_with_oauth()` 直接分析
> **目的**：讓你不靠 sasctl 也能取得 Bearer token，再自行帶入所有端點

### E.1 端點

```
POST /SASLogon/oauth/token
```

所有 grant type 都使用同一個端點，以 `#anchor` 作為命名標記（anchor 不帶入 HTTP）。

---

### E.2 共同 Headers

```http
POST /SASLogon/oauth/token HTTP/1.1
Host: {sas-viya-host}
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Authorization: Basic {base64(client_id:client_secret)}
```

**`Authorization: Basic` 說明**：

| 情況 | client_id | client_secret | Base64 字串 |
|---|---|---|---|
| 預設（大多數 Viya 部署） | `sas.ec` | `""` (空字串) | `base64("sas.ec:")` → `c2FzLmVjOg==` |
| 自訂 OAuth 應用程式 | 你的 client_id | 你的 client_secret | `base64("{id}:{secret}")` |

**Python 計算方式**：
```python
import base64
auth_header = "Basic " + base64.b64encode(b"sas.ec:").decode()
# → "Basic c2FzLmVjOg=="
```

---

### E.3 方式一：Password Grant（使用帳號密碼）

> ⚠️ **[需實測] `sas.ec` 通用性**：`sas.ec` 是 SAS Viya 的預設 OAuth 公開 client，空密鑰（`:`）在標準部署下有效，但部分組織會停用此 client 或要求使用自訂 `client_id`。若遇到 `401 invalid_client`，請向 SAS 管理員確認正確的 client_id / client_secret。

```http
POST /SASLogon/oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Authorization: Basic c2FzLmVjOg==

grant_type=password&username={sas_username}&password={sas_password}
```

**Python 範例**：
```python
import requests, base64

BASE = "https://your-viya-host"

def get_token(username, password):
    resp = requests.post(
        f"{BASE}/SASLogon/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": "Basic c2FzLmVjOg==",   # sas.ec: (空密鑰)
        },
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
        verify=False,  # 若自簽憑證
    )
    resp.raise_for_status()
    return resp.json()

token_data = get_token("sas_user", "sas_password")
ACCESS_TOKEN  = token_data["access_token"]
REFRESH_TOKEN = token_data["refresh_token"]   # 用於換新 token
EXPIRES_IN    = token_data["expires_in"]       # 秒數（通常 3600）
```

**Response**：
```json
{
  "access_token":  "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
  "token_type":    "bearer",
  "expires_in":    3600,
  "scope":         "openid",
  "jti":           "uuid",
  "refresh_token": "eyJhbGci..."
}
```

---

### E.4 方式二：Client Credentials Grant（服務帳號，無互動）

適用於機器對機器（M2M）情境，需要先在 SAS Viya 建立 OAuth Client。

```http
POST /SASLogon/oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Authorization: Basic {base64(client_id:client_secret)}

grant_type=client_credentials
```

**Python 範例**：
```python
client_id     = "my_service_client"
client_secret = "my_client_secret"

b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

resp = requests.post(
    f"{BASE}/SASLogon/oauth/token",
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {b64}",
    },
    data={"grant_type": "client_credentials"},
    verify=False,
)
ACCESS_TOKEN = resp.json()["access_token"]
# client_credentials 通常不含 refresh_token
```

---

### E.5 Token Refresh（避免重新登入）

```http
POST /SASLogon/oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Authorization: Basic c2FzLmVjOg==

grant_type=refresh_token&refresh_token={refresh_token_value}
```

**Python 範例**：
```python
def refresh_access_token(refresh_token):
    resp = requests.post(
        f"{BASE}/SASLogon/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": "Basic c2FzLmVjOg==",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]
```

---

### E.6 錯誤碼速查

| HTTP Status | error 值 | 說明 |
|---|---|---|
| `401` | `"unauthorized"` | 帳號/密碼錯誤，或 client_id/secret 錯誤 |
| `400` | `"invalid_grant"` | refresh_token 過期或已被撤銷 |
| `401` | `"invalid_client"` | client_id 不存在或 Unauthorized grant type |

---

### E.7 完整純 HTTP 呼叫最小範例（版控場景）

```python
import requests, base64

BASE = "https://your-viya-host"

# ── 1. 取得 token ─────────────────────────────────────────────────────────
resp = requests.post(
    f"{BASE}/SASLogon/oauth/token",
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": "Basic c2FzLmVjOg==",
    },
    data={"grant_type": "password", "username": "USER", "password": "PASS"},
    verify=False,
)
TOKEN = resp.json()["access_token"]
HDR = {"Authorization": f"Bearer {TOKEN}"}

# ── 2. 取得 repo/project/model UUID（見第 8 節）─────────────────────────────
def get_id(path, filter_str):
    r = requests.get(f"{BASE}{path}", headers=HDR, params={"filter": filter_str})
    items = r.json()
    items = items if isinstance(items, list) else items.get("items", [])
    return items[0]["id"]

repo_id = get_id("/modelRepository/repositories", 'eq(name,"Public")')

# ── 3. 建立 project（若不存在）──────────────────────────────────────────────
proj_resp = requests.post(
    f"{BASE}/modelRepository/projects",
    headers={**HDR, "Content-Type": "application/vnd.sas.models.project+json"},
    json={"name": "ChurnPrediction", "repositoryId": repo_id},
)
project_id = proj_resp.json()["id"]

# ── 4. 建立模型 ────────────────────────────────────────────────────────────
model_resp = requests.post(
    f"{BASE}/modelRepository/models",
    headers={**HDR, "Content-Type": "application/vnd.sas.models.model+json"},
    json={"name": "LogisticChurn_v1", "projectId": project_id, "tool": "Python 3"},
)
model_id = model_resp.json()["id"]

# ── 5. 上傳 pkl ────────────────────────────────────────────────────────────
with open("model.pkl", "rb") as f:
    requests.post(
        f"{BASE}/modelRepository/models/{model_id}/contents",
        headers={**HDR, "Content-Type": "application/octet-stream"},
        params={"name": "model.pkl", "role": "Python pickle"},
        data=f,   # stream mode，不全部載入記憶體
    ).raise_for_status()

# ── 6. 建立新版本 ──────────────────────────────────────────────────────────
requests.post(
    f"{BASE}/modelRepository/models/{model_id}/modelVersions",
    headers={**HDR, "Content-Type": "application/json"},
    json={"option": "major"},
).raise_for_status()

print("✅ 模型版控完成")
```

---

## 附錄 F：待實測項目清單

> **用途**：本節聚合所有 `[需實測]` 標記項目，供 implementation Agent 直接參考。
> **grep 指令**：`grep -n "\[需實測\]" SASCTL_MLOPS_OPERATIONS.md`
> **驗證方式**：每項建議以 integration test（對真實 SAS Viya 環境）驗證。

---

### F.1 `POST /modelRepository/models` 必填欄位

**文件位置**：Section 2.1
**端點**：`POST /modelRepository/models`
**不確定點**：`tool`、`function`、`scoreCodeType` 是否為 server 端必填？還是只有 `name` + `projectId` 必填？
**建議驗證**：
```python
# 最小 body 測試
resp = requests.post(f"{BASE}/modelRepository/models",
    headers={**HDR, "Content-Type": "application/vnd.sas.models.model+json"},
    json={"name": "MinimalTestModel", "projectId": project_id},
)
print(resp.status_code, resp.json())   # 期望 201；若 400 則看 error message
```

---

### F.2 `POST /modelRepository/projects` `folderId` 必填性

**文件位置**：Section 3.1
**端點**：`POST /modelRepository/projects`
**不確定點**：`folderId` 在純 HTTP 中是否必填？sasctl 會自動從 repository 取得再帶入，但若省略 SAS Viya 是否接受？
**建議驗證**：
```python
# 不帶 folderId
resp = requests.post(f"{BASE}/modelRepository/projects",
    headers={**HDR, "Content-Type": "application/vnd.sas.models.project+json"},
    json={"name": "TestProject_NoFolder", "repositoryId": repo_id},
)
print(resp.status_code)   # 201 = 不需要；400/422 = 必填
```

---

### F.3 `GET /modelRepository/models/{id}/contents` 回應格式

**文件位置**：Section 2.5、Section 5.2
**端點**：`GET /modelRepository/models/{modelId}/contents`
**不確定點**：頂層是 plain `[...]` 還是 `{"count":N,"items":[...]}`？
**建議驗證**：
```python
resp = requests.get(f"{BASE}/modelRepository/models/{model_id}/contents",
    headers=HDR)
body = resp.json()
print(type(body))         # list → plain array；dict → 有 items wrapper
if isinstance(body, dict):
    print(body.keys())    # 確認是否有 count, start, limit 等 pagination 欄位
```

---

### F.4 `GET /modelRepository/models/{id}/modelVersions` 回應 field names

**文件位置**：Section 2.7
**端點**：`GET /modelRepository/models/{modelId}/modelVersions`
**不確定點**：`modelVersionName`、`creationTimeStamp` 是否為正確欄位名稱？是否有 `versionName`、`createdAt` 等替代命名？
**建議驗證**：
```python
resp = requests.get(f"{BASE}/modelRepository/models/{model_id}/modelVersions",
    headers=HDR)
versions = resp.json()
versions = versions if isinstance(versions, list) else versions.get("items", [])
if versions:
    print(versions[0].keys())   # 印出完整 field list
    print(versions[0])          # 看實際值確認
```

---

### F.5 Filter 語法普適性

**文件位置**：Section 8.1
**適用端點**：`GET /modelRepository/repositories`、`/projects`、`/models`
**不確定點**：
- query param 是 `filter=` 還是 `$filter=`？
- `eq(name,"X")` 是否對所有端點有效（repositories、projects、models 分別測試）？
- 比對是否大小寫敏感？

**建議驗證**：
```python
for endpoint in ["repositories", "projects", "models"]:
    # 測 filter=
    r1 = requests.get(f"{BASE}/modelRepository/{endpoint}",
        headers=HDR, params={"filter": 'eq(name,"TestName")'})
    # 測 $filter=
    r2 = requests.get(f"{BASE}/modelRepository/{endpoint}",
        headers=HDR, params={"$filter": 'eq(name,"TestName")'})
    print(f"{endpoint}: filter={r1.status_code}, $filter={r2.status_code}")
```

---

### F.6 `sas.ec` client_id 通用性

**文件位置**：Appendix E.2、E.3
**端點**：`POST /SASLogon/oauth/token`
**不確定點**：`sas.ec` 是 SAS Viya 預設公開 client，但部分組織會停用或鎖定。
**已知錯誤碼**：
- `401 "Unauthorized grant type: password"` → 此 client 不允許 password grant，需要換 client_id
- `401 "Bad credentials"` → 帳號密碼錯誤（不是 client 問題）
- `401 "invalid_client"` → client_id 不存在或被停用

**建議驗證**：先用 `sas.ec` 嘗試，若遇到 `invalid_client` 錯誤，向 SAS 管理員詢問可用的 `client_id`：
```bash
curl -X POST "https://{host}/SASLogon/oauth/token" \
  -H "Authorization: Basic c2FzLmVjOg==" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=USER&password=PASS" \
  -k -v 2>&1 | grep -E "HTTP|error|access_token"
```

---

### F 快速查閱表

| # | 位置 | 端點 | 不確定點 | 優先級 |
|---|---|---|---|---|
| F.1 | Section 2.1 | `POST /modelRepository/models` | 必填欄位 | 🔴 高（build 前必知）|
| F.2 | Section 3.1 | `POST /modelRepository/projects` | `folderId` 必填性 | 🔴 高（build 前必知）|
| F.3 | Section 2.5/5.2 | `GET .../contents` | 回應頂層型別 | 🟠 中（已有防禦寫法）|
| F.4 | Section 2.7 | `GET .../modelVersions` | response field names | 🟠 中（版本管理用）|
| F.5 | Section 8.1 | 所有 list endpoints | filter 語法普適性 | 🟠 中（UUID 解析用）|
| F.6 | Appendix E.3 | `POST /SASLogon/oauth/token` | `sas.ec` 通用性 | 🔴 高（auth 入口）|

---

*文件由原始碼分析自動產生，sasctl 版本 1.11.7*
