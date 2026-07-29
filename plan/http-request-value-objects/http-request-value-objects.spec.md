# HTTP Request Value Objects Specification

## Acceptance Criteria

1. request-side value objects immutable/comparable/no-I-O/no-HTTP-library。
2. BaseUrl 僅為 origin；EndpointPath.literal/from_segments 分別處理 static/raw dynamic path。
3. QueryParams 保留 ordered duplicate pairs 並滿足 empty/UTF-8/%20/no-plus/no-sort/no-double-encode contract。
4. Headers canonical lowercase、case-insensitive、last-wins、no duplicates；merge precedence 保持且輸出 lowercase。
5. HttpRequest 僅以 `body: JsonBody | RawBody | None` construction；JsonBody snapshot 不 serialize，RawBody bytes 不注入 Content-Type，compat properties readonly。
6. Requester immutable JSON-domain only；HttpClient execution-only canonical URL/body。
7. Token/password token 維持 raw primitive 且不經 Requester；endpoint family 僅 contract，無 concrete port。
8. JSON-domain GET request 在 body 為 `None` 時不帶 `Content-Type`，且 authorization/accept
   assertions 使用 lowercase canonical lookup。

## Behavioral Scenarios

### Scenario 1: Canonical JSON request
- **Given**: origin BaseUrl、`/api/v1/users` EndpointPath、duplicate query pairs 與 JSON body。
- **When**: Requester composition 後交 HttpClient execution。
- **Then**: input 不變、headers lowercased per precedence、transport 只使用 canonical URL/body。

### Scenario 2: Single body variant and compatibility reads
- **Given**: HttpRequest 的 body 是 JsonBody 或 RawBody。
- **When**: 讀取 json_body/content compatibility property。
- **Then**: 只反映對應 variant；constructor 沒有 json_body/content，沒有 XOR/priority/default/override。

### Scenario 3: Query and endpoint edge rules
- **Given**: duplicate keys、empty value、UTF-8 space，及 raw dynamic segment。
- **When**: render query 或從 segments 建 path。
- **Then**: query 為 `%20` 且不排序/double encode；pre-encoded ID 被拒絕。

### Scenario 4: Token exclusion
- **Given**: TokenEndpointClient 或 password-token form request。
- **When**: JSON-domain flow 存在。
- **Then**: token request 保持 raw primitive，且未呼叫 Requester。

### Scenario 5: JSON-domain GET request shape
- **Given**: job execution GET request 由 JSON-domain Requester 組成且 body 為 `None`。
- **When**: request-contract fixture 檢查最終 request headers/body。
- **Then**: 不存在 `Content-Type`，且以 `authorization`／`accept` lowercase names 取得 canonical values。

## Error / Edge Cases

- BaseUrl 含 path-prefix/user-info/query/fragment 時拒絕。
- Query empty key 拒絕；empty value 保留等號；None omit。
- Header case collision 僅保留最後值及 lowercase name；不保留 duplicates。
- RawBody 不自動加 Content-Type；JsonBody 不 serialize。
- EndpointPath.from_segments 收到 pre-encoded dynamic ID 時拒絕。
- GET request 無 body 時不得因 JSON-domain default 產生 `Content-Type`。
