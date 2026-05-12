# SAS Viya API Endpoint 文檔說明

> 本目錄整理 `sas-model-serving` 專案所需使用的所有 SAS Viya RESTful API 端點文檔
> **Git Branch**: `feature/sas-viya-endpoint-documentation`
> **來源**: Legacy `sas_api` 專案（`utils/_api/` 目錄，嚴格依照原始碼）

---

## 目錄結構

```
docs/api-endpoints/
├── swagger-spec/                        # OpenAPI 3.0 規範文件
│   ├── openapi-complete.yaml            # ✅ 完整合併版（所有端點）
│   ├── openapi-complete.json            # ✅ 完整合併版（JSON 格式）
│   ├── authentication-spec.yaml/.json   # 認證端點
│   ├── models-spec.yaml/.json           # 模型端點
│   ├── projects-spec.yaml/.json         # 專案端點
│   ├── tables-spec.yaml/.json           # CAS 資料表端點
│   └── jobs-spec.yaml/.json             # Job Execution 端點
│
└── markdown-reference/                  # Markdown 格式參考文件
    ├── ENDPOINTS_EXTRACTED.md           # 所有端點清單（含已知 Bug 說明）
    ├── SASCTL_ALIGNMENT.md              # sasctl 對齊分析報告
    └── README.md                        # 本文件
```

---

## 快速瀏覽所有端點

| # | Method | 路徑 | 功能 | Spec 檔案 |
|---|--------|------|------|-----------|
| 1 | `POST` | `/SASLogon/oauth/token` | Password Grant 取得 Token | `authentication-spec.yaml` |
| 2 | `POST` | `/SASLogon/oauth/token` | Refresh Token 更新 Token | `authentication-spec.yaml` |
| 3 | `GET` | `/modelRepository/models` | 取得所有模型清單 | `models-spec.yaml` |
| 4 | `GET` | `/modelRepository/models/{modelId}` | 取得單一模型詳情 | `models-spec.yaml` |
| 5 | `GET` | `/modelRepository/models/{modelId}/contents/{fileId}/content` | 下載模型檔案內容 | `models-spec.yaml` |
| 6 | `GET` | `/modelRepository/projects` | 取得所有專案清單 | `projects-spec.yaml` |
| 7 | `GET` | `/modelRepository/projects/{projectId}/champion` | 取得 Champion Model | `projects-spec.yaml` |
| 8 | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables` | CAS 資料表清單 ⚠️ | `tables-spec.yaml` |
| 9 | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}` | CAS 資料表詳情 ⚠️ | `tables-spec.yaml` |
| 10 | `PUT` | `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state` | 切換 CAS 表狀態 ⚠️ | `tables-spec.yaml` |
| 11 | `POST` | `/jobExecution/jobRequests/{jobRequestId}/jobs` | 啟動 Job 執行 ⚠️ | `jobs-spec.yaml` |
| 12 | `GET` | `/jobExecution/jobs/{jobId}` | 查詢 Job 詳情 ⚠️ | `jobs-spec.yaml` |
| 13 | `GET` | `/jobExecution/jobs/{jobId}/state` | 查詢 Job 狀態 ⚠️ | `jobs-spec.yaml` |

> ⚠️ = Legacy 程式碼有已知 Bug（詳見 `ENDPOINTS_EXTRACTED.md`）

---

## 如何使用 Swagger UI 檢視

### 方法一：線上 Swagger Editor

1. 開啟 [https://editor.swagger.io](https://editor.swagger.io)
2. 複製 `swagger-spec/openapi-complete.yaml` 內容貼入
3. 即可看到互動式 API 文件

### 方法二：本地 Docker（Swagger UI）

```bash
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/spec/openapi-complete.yaml \
  -v $(pwd)/docs/api-endpoints/swagger-spec:/spec \
  swaggerapi/swagger-ui
```

然後開啟 `http://localhost:8080`

### 方法三：FastAPI 整合

```python
from fastapi import FastAPI
import yaml

app = FastAPI()

# 直接使用 openapi-complete.json 作為 FastAPI 的 OpenAPI schema
with open("docs/api-endpoints/swagger-spec/openapi-complete.json") as f:
    import json
    custom_openapi = json.load(f)

app.openapi_schema = custom_openapi
```

---

## ⚠️ 重要：Legacy 程式碼已知問題

在使用或參考 Legacy `sas_api` 端點時，請注意以下兩個 Bug：

### Bug 1：`table.py` 缺少的 Header 函式
`utils/_api/table.py` 引用了 3 個在 `config/headers_variable.py` 中**不存在**的函式，
導致所有 CAS Table 相關端點（#8、#9、#10）在執行時拋出 `ImportError`。

詳見：[ENDPOINTS_EXTRACTED.md#已知問題](./ENDPOINTS_EXTRACTED.md#已知程式碼問題)

### Bug 2：`job_execution.py` 的錯誤參數
`utils/_api/job_execution.py` 呼叫 header 函式時傳入了不存在的 `is_text` 參數，
導致所有 Job 相關端點（#11、#12、#13）在執行時拋出 `TypeError`。

---

## sasctl 對齊摘要

`sasctl 1.11.7` 已涵蓋大部分 Legacy 端點的功能，以下是重點：

- ✅ **認證**：使用 `sasctl.Session` 完整取代
- ✅ **模型/專案查詢**：使用 `sasctl.ModelRepository` 服務
- ✅ **CAS 表管理**：使用 `sasctl.CASManagement` 服務（且無 Bug）
- ⚠️ **Champion Model**：`sasctl` 無直接對應，需保留 `GET /projects/{id}/champion`

詳見：[SASCTL_ALIGNMENT.md](./SASCTL_ALIGNMENT.md)
