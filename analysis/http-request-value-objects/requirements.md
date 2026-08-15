# HTTP Request Value Objects Requirements

## Status

- **Topic**: `http-request-value-objects`
- **Status**: frozen for technical translation and independent plan review
- **Scope**: internal JSON-domain request contract

## Problem Statement

目前 JSON-domain request 以 primitive `path`、`params`、`headers`、`json_body` 與
`content` 跨越 composition/transport boundary，無法將 URL、body、query 與 header
canonicalization 固定為單一可測模型。

## Requirements

1. 所有 request-side value objects 必須 repo-owned、immutable、comparable、無 I/O，且不
   依賴 HTTP library。
2. `BaseUrl` 是 origin-only：只接受 `http`／`https`、host、optional port；拒絕
   path-prefix、user-info、query、fragment。`/api/vN` 必須由 `EndpointPath` 表示。
3. `EndpointPath.literal()` 只表示靜態 path；`EndpointPath.from_segments()` 只接受 raw
   dynamic segments、逐段 percent-encode 一次，並拒絕預編碼 dynamic ID。
4. `QueryParams` 是 ordered duplicate pairs；值限 `str | int | float | bool | None`。空
   key 拒絕，empty string value render 為 `key=`，None omission，bool 小寫，UTF-8
   percent-encoding，space 為 `%20`，不用 `+`，不排序，不 double-encode。
5. `Headers` 是 request-side lowercase canonical model：case-insensitive、last wins、不
   支援 duplicates；現有 `merge_headers()`、`json_request_headers()`、
   `token_request_headers()` precedence 保持，最終輸出為 lowercase names。
6. body 的唯一 construction variant 是 `HttpRequest.body: JsonBody | RawBody | None`；
   不得有 `json_body`／`content` construction fields，不得建立 XOR、implicit priority、
   library default 或 override semantics。
7. `JsonBody` 只 validation/snapshot JSON-compatible input，不 serialize。`RawBody` 是
   immutable bytes，且不自動加入或覆寫 `Content-Type`。`HttpRequest` 可提供 readonly
   compatibility `json_body`／`content` properties，但它們不得是 construction inputs。
8. `HttpRequest.url` 是唯一 canonical final URL。`Requester` 只進行 immutable
   JSON-domain composition；`HttpClient` 只執行 canonical request。
9. `<EndpointFamily>Endpoints` 只凍結回傳 `EndpointPath` 的 contract；本 topic 不 port
   concrete endpoint family。
10. primitive surface 只作 JSON-domain compatibility adapter；primitive cleanup 是後續
    topic。TokenEndpointClient/password token/token-form 本批維持 raw primitive path，且不進
    JSON-domain Requester。

## Success Signals

- URL、body variant、query encoding、headers canonicalization 均由 unit tests 鎖定。
- Requester 不 mutate input，HttpClient 不作第二套 URL/body construction。
- token/password-token regression 證明其仍走 raw primitive path，且未經 Requester。
- 無 README、VERSION、release、package-root export 或 concrete endpoint port 變更。

## Non-Goals

- 不遷移 token/form、password grant 或 client-credentials payload。
- 不重設 header merge precedence、retry、timeout、auth lifecycle、response model 或 facade。
- 不清理 primitive compatibility adapter。
- 不建立 concrete endpoint catalog。

## Human Decisions Recorded

| ID | Status | Decision |
| --- | --- | --- |
| HD-01 | accepted | BaseUrl origin-only；API prefix 歸 EndpointPath |
| HD-02 | accepted | Token/password token 不遷移；維持 raw primitive path |
