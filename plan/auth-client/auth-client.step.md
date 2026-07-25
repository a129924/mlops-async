---
topic: auth-client
phase: plan-review
created: 2026-07-26
---

# auth-client Step Tracking

> **Executor**：僅在所屬 phase 完成後將項目標為 `[X]`。
> 全部 Implementation Steps 完成前，不得交給 implementation review。
> 本 tracker 是更正後唯一有效的 workflow state；舊 root-AuthClient tracker
> interpretation、TDD YAML、tests、review evidence 與 release-prep evidence
> 全部為 **superseded**，不得用作 gate 或 authorization。

## Superseded evidence inventory

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

## Filesystem dispositions

- **ReadOnly before approval**: `plan/auth-client/auth-client.tdd-test-authoring.yaml`
  is Tester-only until plan approval; `README.md`, `VERSION`, `pyproject.toml`,
  `uv.lock`, `docs/ARCHITECTURE.md`, and
  `docs/standards/http-client-auth-boundary.md` have no write target in this
  topic.
- **Written or updated after approval**: Tester rewrites
  `plan/auth-client/auth-client.tdd-test-authoring.yaml` and
  `tests/unit/clients/test_auth_client.py`; Implementer writes
  `src/mlops_async/clients/auth_client.py`, updates
  `src/mlops_async/core/auth.py`, `src/mlops_async/__init__.py`,
  `tests/unit/core/test_auth_contract.py`, and `tach.toml`.
- **Deleted after approval**: Implementer deletes
  `src/mlops_async/auth_client.py` and `tests/unit/core/test_auth_client.py`.

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review（等待獨立 Plan-Reviewer）
- [ ] tdd-test-authoring（只在 plan approval 後由 Tester 重寫 YAML/RED tests）
- [ ] implementation
- [ ] tester-validation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. Tester 於 plan approval 後重寫 `plan/auth-client/auth-client.tdd-test-authoring.yaml`，並在 `tests/unit/clients/test_auth_client.py` 建立 canonical direct-import、exactly-once delegation、errors/cancellation 原樣傳播與禁止 lifecycle/policy 的 RED tests。
- [X] 2. Implementer 建立 `src/mlops_async/clients/auth_client.py`；AuthClient 是 concrete endpoint-family client，僅直接 await `fetch_access_token()`，且不得建立或繼承 EndpointFamilyClient base、Protocol 或 module。
- [X] 3. Implementer 刪除 `src/mlops_async/auth_client.py` 與 `tests/unit/core/test_auth_client.py`，移除 `src/mlops_async/__init__.py` 的 AuthClient export，並更新 `tests/unit/core/test_auth_contract.py` 保護 root non-export。
- [X] 4. Implementer 更正 `src/mlops_async/core/auth.py`，移除 core-to-root import/root-exception inheritance，保留 core token contracts，且不遷移 transport/exceptions 或改變 TokenManager policy。
- [X] 5. Implementer 更新 `tach.toml` 為 core 無 root dependency、clients 僅依賴 core、root 不新增 direct core dependency；不得執行 `tach sync`。
- [X] 6. Tester 依 spec 執行 pytest、pyright、ruff、`uv run tach check` 與 diff check。WDAC 阻擋 Tach 時記錄 validation blocker，不能 skip 或 fake success。
