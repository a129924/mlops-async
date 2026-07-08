# tables-list-runtime-mvp Spec

## Acceptance Criteria

1. `PackageLevelClient` 透過 `client.tables` 對外暴露 `TablesClient`。
2. `TablesClient.list_tables(project_id)` 只透過 `Requester` 發出 `GET /modelRepository/projects/{project_id}/tables`。
3. 第一次 authenticated business request 才 lazy resolve token；constructor / wiring phase 不預取 token。
4. `TablesClient` 不直接依賴 `AuthClient`、`TokenManager`、`TokenStorage`、或 `TokenEndpointClient`。
5. `TablesClient` 不自行建立 `Authorization` header。
6. request shape 與既有 `projects_tables_link_request_gate` baseline 一致。
7. 最小 response boundary 可穩定承接本 endpoint MVP 所需欄位。

## Behavioral Scenarios

### Scenario 1: First authenticated business request

- **Given**: `PackageLevelClient` 已完成 wiring，但 token storage 尚無可用 token
- **When**: 呼叫 `await client.tables.list_tables("project-id-abc-123")`
- **Then**: runtime 先經 `Requester -> AuthProvider -> TokenManager` 取得 auth headers，再送出 `GET /modelRepository/projects/project-id-abc-123/tables`
- **And**: `PackageLevelClient.__init__` 與 `__aenter__` 未曾預先拿取真實 token

### Scenario 2: Reuse cached token

- **Given**: token storage 已有仍有效的 access token
- **When**: 再次呼叫 `await client.tables.list_tables("project-id-abc-123")`
- **Then**: request 直接重用既有 token，不重複 obtain
- **And**: `TablesClient` 本身不感知 token lifecycle decision

### Scenario 3: Endpoint boundary stays narrow

- **Given**: `TablesClient` 已建立
- **When**: 檢查其依賴與 outbound request construction
- **Then**: `TablesClient` 只持有 `Requester`
- **And**: family module 不接觸 `AuthClient`、`TokenManager`、`TokenStorage`、或 `TokenEndpointClient`

## Error / Edge Cases

- `project_id` 為非字串、空字串、或純空白時，family boundary 必須 fast-fail。
- `project_id` 含 reserved characters 時，path substitution 必須 percent-encode，且仍維持 fixed-path baseline。
- auth fetch / refresh failure 必須沿既有 runtime boundary 傳播；本 topic 不新增 retry/backoff。
- `asyncio.CancelledError` 不可被 family client 吞掉或轉譯成其他例外。
- topic 不涵蓋 HATEOAS rediscovery、CAS tables remap、pagination/filter expansion、或 broader AuthClient UX。
