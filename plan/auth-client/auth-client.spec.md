# AuthClient architecture correction specification

## Goal

以 `src/mlops_async/clients/auth_client.py` 的 direct-import AuthClient 取代 root AuthClient，同時修正 core 的反向 root dependency，建立可驗證的單向 Tach graph；本 topic 不實作 future facade 或任何 release。

## Non-Goal

- 不實作 `MLOpsAsyncClient`、`.auth` wiring、transport ownership 或 close。
- 不加入 grant selection、refresh、cache、lifecycle、exception translation、retry 或 timeout。
- 不遷移 transport/exceptions；不執行 `tach sync`。
- 不執行 release metadata、tag、push、PR、merge、release 或 live E2E。

## In-Scope

- concrete endpoint-family AuthClient 的 flat clients layout、root removal、core reverse-dependency removal、Tach configuration 與 replacement tests。
- `tests/unit/clients/test_auth_client.py` 的 RED/validation coverage，及 `tests/unit/core/test_auth_contract.py` 的 root non-export assertion。

## Out-Of-Scope

- `src/mlops_async/mlops_async_client.py` 或其他 facade source。
- TokenManager fetch/refresh policy、transport/exceptions hierarchy 與 shared contracts module creation。

## ReadOnly

- `plan/auth-client/auth-client.tdd-test-authoring.yaml` 於 Plan-Creator 階段必須保持唯讀；它是 superseded，僅可由 approval 後的 Tester 重寫。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`docs/ARCHITECTURE.md`、
  `docs/standards/http-client-auth-boundary.md` 是 superseded release-prep
  evidence，維持 ReadOnly 且沒有本 topic write target。沒有 materialized 的
  separate reviewer verdict/evidence artifact。

### Superseded evidence inventory

| Evidence | Exact repository-relative path | Exists | Classification |
| --- | --- | --- | --- |
| Old root implementation | `src/mlops_async/auth_client.py` | Yes | old root semantic is superseded and not a gate/authorization source; Implementer delete target after approval |
| Old package-root export | `src/mlops_async/__init__.py` | Yes | old root-export semantic is superseded and not a gate/authorization source; Implementer update target after approval |
| Old root-import tests | `tests/unit/core/test_auth_client.py` | Yes | old root-import assertions are superseded and not a gate/authorization source; Implementer delete target after approval |
| Old supporting contract-test change | `tests/unit/core/test_auth_contract.py` | Yes | old supporting assertions/evidence are superseded and not a gate/authorization source; Implementer update target after approval |
| Old TDD/reviewer-phase evidence | `plan/auth-client/auth-client.tdd-test-authoring.yaml` | Yes | superseded; ReadOnly; Tester rewrites only after new plan approval; not a gate or authorization source |
| Old release-prep README text | `README.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep version file | `VERSION` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep project metadata | `pyproject.toml` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep lock metadata | `uv.lock` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep architecture text | `docs/ARCHITECTURE.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Old release-prep auth-boundary text | `docs/standards/http-client-auth-boundary.md` | Yes | superseded; ReadOnly; not a gate or authorization source |
| Separate reviewer verdict/evidence artifact | None under `plan/auth-client/` | No | no materialized reviewer verdict, implementation-review evidence, code-review evidence, or review-log exists; it cannot be used as a gate or authorization source |

The `0.14.0` authorization recorded by the listed release-prep artifacts is
superseded and cannot be reused.

## Written

- Planning actor：`plan/auth-client/auth-client.plan.md`、`plan/auth-client/auth-client.spec.md`、`plan/auth-client/auth-client.step.md`。
- Approval 後 Tester rewrites `plan/auth-client/auth-client.tdd-test-authoring.yaml`
  與 `tests/unit/clients/test_auth_client.py`; Implementer writes
  `src/mlops_async/clients/auth_client.py`, updates
  `src/mlops_async/core/auth.py`, `src/mlops_async/__init__.py`,
  `tests/unit/core/test_auth_contract.py`, and `tach.toml`.

## Deleted

- Approval 後 Implementer deletes `src/mlops_async/auth_client.py` 與
  `tests/unit/core/test_auth_client.py`。
- `src/mlops_async/__init__.py` 本身不刪除；其 old AuthClient export 是
  Implementer update target，而非 ReadOnly path。

## TestCase

1. canonical direct import：從 `mlops_async.clients.auth_client` import AuthClient 成功、為 concrete endpoint-family client；`mlops_async` 沒有 AuthClient。
2. exactly once delegation：每次 call 只 await 一次 `fetch_access_token()`，回傳同一 AccessToken。
3. errors/cancellation：collaborator error 與 `asyncio.CancelledError` 原樣傳播，沒有 wrapping 或 cleanup。
4. prohibited behavior：無 refresh/grant/cache/lifecycle/context/close/timeout/retry，且不使用 TokenManager。
5. Tach：static graph 加上 `uv run tach check` 的真實 verdict；WDAC 阻擋即 validation blocker，不得 skip/fake success。

## Acceptance Criteria

1. `src/mlops_async/clients/auth_client.py` 定義 concrete endpoint-family AuthClient；`clients/` 使用 flat `<endpoint_family>_client.py` layout。`EndpointFamilyClient` 僅是 architectural classification，絕不建立或繼承 concrete base class、Protocol 或 module。
2. AuthClient accepts `TokenEndpointClientProtocol` from core，且唯一 public async operation 只直接 await `fetch_access_token()`；每次呼叫 exactly once。
3. AuthClient 不實作 grant selection、refresh、cache、stateful lifecycle/close/context，亦不做 exception translation、timeout 或 retry。
4. `from mlops_async.clients.auth_client import AuthClient` 為 canonical import；`from mlops_async import AuthClient` 不可用，且 root package 不新增 core dependency。
5. `TokenEndpointClientProtocol` 與 `AccessToken` 留在 core；`core/auth.py` 不再 import package root 或繼承 root exception。transport/exceptions hierarchy 不遷移。
6. Tach 中 `mlops_async.core` 不依賴 root，`mlops_async.clients` 僅依賴 core，root 不被允許直接依賴 core；不得執行 `tach sync`。
7. future-only facade contract 被記錄但未實作：`MLOpsAsyncClient(token_endpoint_client: TokenEndpointClientProtocol)` 未來位於 `src/mlops_async/mlops_async_client.py`、建立 `.auth`、不擁有或 close transport，並以 root import 公開。
8. 舊 root implementation、root tests、TDD YAML、review evidence、release-prep evidence 均 superseded；舊 `0.14.0` 授權不得重用。

## Async contradiction log

- Trigger：`get_access_token()` 是直接 await token-endpoint I/O 的 public async boundary，需原樣處理 cancellation 與 collaborator failures。
- Contradiction：舊 root import/implementation、既有 TDD/review/release-prep evidence 與 clients direct import/future facade only correction 相衝突。
- Classification：blocking；本 spec/plan/step 取代舊 evidence 的 gate/authorization 功能。Tester 必須 approval 後重寫 TDD YAML，任何後續 stage 不得引用舊 `0.14.0` authorization。

## Behavioral Scenarios

### Scenario 1: Direct family-client delegation

- **Given**：concrete token endpoint client 已由 caller 設定並符合 core protocol。
- **When**：caller await canonical AuthClient 的 `get_access_token()`。
- **Then**：只呼叫一次 fetch，回傳相同 token；client 不做其他 policy。

### Scenario 2: Failure and cancellation boundary

- **Given**：collaborator raises a token/transport exception 或 `asyncio.CancelledError`。
- **When**：caller awaits AuthClient。
- **Then**：相同 failure 原樣離開；沒有 conversion、retry、timeout、close 或 cleanup。

### Scenario 3: Root removal and graph direction

- **Given**：package root、core 與 clients 已依 correction implementation。
- **When**：run direct-import/root-non-export tests 和 Tach validation。
- **Then**：root lacks AuthClient，core does not depend on root，clients only depends on core；沒有 root-to-core allowance 或 cycle。

### Scenario 4: Future facade is absent

- **Given**：AuthClient correction 已完成。
- **When**：review implementation artifacts。
- **Then**：沒有 `mlops_async_client.py`、`.auth` wiring 或 transport lifecycle code；future composition contract 只存在於 plan/spec。

## Validation Commands

```powershell
uv run pytest --no-cov tests/unit/clients/test_auth_client.py tests/unit/core/test_auth_contract.py
uv run pyright --pythonpath .\.venv\Scripts\python.exe
uv run ruff check src/mlops_async/clients/auth_client.py src/mlops_async/core/auth.py src/mlops_async/__init__.py tests/unit/clients/test_auth_client.py tests/unit/core/test_auth_contract.py
uv run tach check
git diff --check
```

`uv run tach check` 是 Tester validation gate。若 WDAC 阻擋 native extension，記錄實際 blocker 並停止該 gate；不得執行 `tach sync`、skip，或宣稱成功。

## Risks and Stop Conditions

- 若 core 無法移除 root dependency，停止並要求 human shared-contracts decision；不得以建立 EndpointFamilyClient base、Protocol 或 module 作為替代。
- 若 Tach/pytest/typing/lint 顯示觸及未列 path，停止並回到 plan correction。
- 未取得各自獨立 human gate 前，release metadata、tag、push、PR、merge、release 均 pending。
