# request-header-policy-normalization Specification

## Acceptance Criteria

1. `src/mlops_async/core/headers.py` 成為 request-side header policy source of
   truth，且不新增 mutable `Headers` class。
2. `Requester` 與 `HttpClient` 仍維持既有 JSON domain request 行為：
   預設 `Accept: application/json`，且僅在 `json_body` 存在時補
   `Content-Type: application/json`。
3. `TokenEndpointClient` 仍維持 token family request 行為：
   `Accept: application/json` 與
   `Content-Type: application/x-www-form-urlencoded`。
4. 既有 public API、error boundary、merge order、與 caller override semantics
   不回歸。
5. `docs/ARCHITECTURE.md`、`docs/standards/http-client-auth-boundary.md`、
   `README.md` 與 release surfaces 的描述能對齊最終 implementation reality。

## Behavioral Scenarios

### Scenario 1: JSON domain request consumes centralized defaults

- **Given**:
  - `Requester` 收到一般 JSON domain request
  - caller 未自行提供 `Accept` 或 `Content-Type`
- **When**:
  - `Requester` 透過 policy helper 組裝 request headers
- **Then**:
  - final headers 包含 `Accept: application/json`
  - 僅在 `json_body` 存在時才補 `Content-Type: application/json`
  - 與既有 merge order 一致

### Scenario 2: Token request stays isolated from JSON domain policy

- **Given**:
  - `TokenEndpointClient` 建立 `/SASLogon/oauth/token` request
- **When**:
  - request headers 改由 centralized policy helper 提供
- **Then**:
  - headers 仍為 `Accept: application/json`
  - headers 仍為 `Content-Type: application/x-www-form-urlencoded`
  - 不會被 JSON domain policy 補成其他 content type

### Scenario 3: Family-specific Accept override remains possible

- **Given**:
  - repo-visible evidence 顯示 `jobExecution/jobs/state` 擁有 family-specific
    `Accept`
- **When**:
  - reviewer 檢查 request-header policy plan 與 runtime changes
- **Then**:
  - plan 能說明此類 override 的位置與邊界
  - implementation 不需藉由散落 hardcoded literals 繞過 policy surface

### Scenario 4: Release surfaces align with delivered topic truth

- **Given**:
  - topic merge 完成且進入 release step
- **When**:
  - Main Agent 處理 release surfaces
- **Then**:
  - `VERSION`、`pyproject.toml`、`uv.lock`、`README.md` 同步
  - README/docs 不會留下與實際 header behavior 不一致的描述

## Error / Edge Cases

- caller 已自行提供 header 時，merge order 與 override semantics 必須維持不變。
- `json_body is None` 的 path 不得被誤補 `Content-Type: application/json`。
- policy helper 不得把 auth lifecycle、timeout、或 cancellation 責任偷偷搬入
  `core/headers.py`。
- request-contract fixture JSON 與 source-observed harness 必須保持 evidence 身分，
  不因 normalization 而被抽象化改寫。
