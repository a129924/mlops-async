# http-client TLS trust 與使用者控制 Specification

## Acceptance Criteria

1. `HttpClient` 接受 `verify: bool | ssl.SSLContext = True`，合法值原樣傳遞，
   SSLContext identity不變。
2. Unsupported verify type在任何 `httpx.AsyncClient` 建立前raise
   `TypeError("verify must be bool or ssl.SSLContext")`。
3. E2E config required `VIYA_E2E_TLS_MODE` 並只接受 exact lowercase
   `system|insecure|ca_bundle`，不提供 default或fallback。
4. `system`解析為 `True`；`insecure`解析為 `False`並在每次 loader invocation發出一次
   `RuntimeWarning("Viya E2E is running with TLS verification explicitly disabled")`。
5. `ca_bundle`只在 non-blank `VIYA_E2E_CA_BUNDLE` 存在時呼叫
   `ssl.create_default_context(cafile=...)`；其他 mode的 non-blank CA value fail-fast。
6. Mode與CA errors使用 plan鎖定的固定 messages；CA load error保留 chaining但公開
   message不含 path、value或 raw cause。
7. Live password-token E2E使用 `config.verify`，並保留真實 HTTP 200、nonempty token、
   positive expiry與 hard-fail anti-fake-success contract。
8. Internal acceptance使用 explicit `insecure`，成功結論只能是
   `live password-token E2E passed with TLS verification explicitly disabled`。
9. Existing bool behavior、production transport exception、async lifecycle、其他 auth
   flows與 stable-library/release surfaces維持不變。

## Behavioral Scenarios

### Scenario 1: Framework caller保留安全預設

- **Given**：caller未提供 `verify`。
- **When**：`HttpClient` 建立底層 AsyncClient。
- **Then**：底層收到 exact `True`。

### Scenario 2: Framework caller明確停用驗證

- **Given**：caller提供 `verify=False`。
- **When**：`HttpClient` 建立底層 AsyncClient。
- **Then**：底層收到 exact `False`，library不阻擋、不改寫也不自行fallback。

### Scenario 3: Framework caller提供 SSLContext

- **Given**：caller建立 `ssl.SSLContext` 並傳給 `HttpClient`。
- **When**：底層 AsyncClient被建立。
- **Then**：收到相同 object identity；`HttpClient`不修改或關閉它。

### Scenario 4: Internal insecure E2E

- **Given**：ignored config設為 `VIYA_E2E_TLS_MODE=insecure` 且 process opt-in為
  `RUN_VIYA_E2E=1`。
- **When**：loader解析 config並執行 live password-token test。
- **Then**：發出固定 warning、使用 `verify=False`、真實驗證 HTTP 200/token/expiry；
  成功只回報限定 insecure結論。

### Scenario 5: Caller-provided CA bundle

- **Given**：mode為 `ca_bundle`且 config提供可載入的 PEM CA bundle。
- **When**：loader建立 `ViyaE2EConfig`。
- **Then**：以該 CA建立 SSLContext並由 live test傳給 `HttpClient`。

## Error / Edge Cases

- `str`、`Path`、`None`或其他 unsupported verify type在 client建立前得到固定
  `TypeError`。
- Missing或blank mode得到 `Viya E2E TLS mode is required`。
- 非 exact lowercase三值的 mode得到 `Viya E2E TLS mode is invalid`；不 trim或normalize。
- `ca_bundle`沒有 non-blank CA key得到 `Viya E2E CA bundle is required`。
- `system`或`insecure`提供 non-blank CA key得到
  `Viya E2E CA bundle is only valid in ca_bundle mode`；blank視為未提供。
- CA不存在、無法讀取或PEM invalid時得到 `Viya E2E CA bundle could not be loaded`並保留
  exception chaining；公開 message與evidence不得洩漏 path或raw cause。
- Loader不讀 `RUN_VIYA_E2E`，process opt-in ownership維持在 pytest hook。
- Live transport/config failure必須fail；不得 mock、fallback或skip。
- `verify=True`在公司內部自建環境失敗是允許的環境結果，不阻擋 explicit insecure topic
  completion，也不得觸發自動降級。
