---
topic: password-token-endpoint-client
phase: plan-review
created: 2026-07-13
updated: 2026-07-13
---

# PasswordTokenEndpointClient Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/password-token-endpoint-client/password-token-endpoint-client.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [X] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. Update the TDD YAML and create RED cases in the two target test modules without modifying production code.
- [X] 2. Create `_shared.py` and move endpoint/error/validation/parser/expiry pure logic.
- [X] 3. Create `client_credentials.py` and move TokenEndpointClient without changing its request contract.
- [X] 4. Create `password.py` with locked password grant and refresh-as-reobtain behavior.
- [X] 5. Create family initializer and replace `token_endpoint_client.py` with four-symbol compatibility re-export.
- [X] 6. Update both target test modules, run scoped and full validation, and update the corresponding implementation steps only after those checks succeed.
- [ ] 7. After reopened Plan-Reviewer approval, first add/run the corrective tests: PasswordTokenEndpointClient accepts exact `sas.ec` plus `""` with redacted Basic `sas.ec:` structural verification; rejects all non-`sas.ec` empty/whitespace-only secrets and `sas.ec` whitespace-only secret; TokenEndpointClient rejects `sas.ec` plus `""`. Do not modify or rerun the historical TDD YAML. Then minimally update `_shared.py` and `password.py`, run scoped/full validation, and complete implementation-review and code-review.

## P1 Rework Routing

`tdd-test-authoring` remains `[X]` because its YAML is historical evidence for the initial strict-non-empty contract. P1 reopens only `plan-review`, `implementation`, `implementation-review`, and `code-review`; no correction-specific workflow stage is created.

P1 scope guards：TDD YAML 為 immutable ReadOnly evidence，禁止 rewrite 或 rerun。`client_credentials.py` 是 ReadOnly 且 diff-free；它維持 `require_non_empty_string()`，僅 `test_token_endpoint_client.py` 可修改 strict regression。`sas.ec` exception helper 僅能由 `password.py` 使用；P1 production diff 僅限 `_shared.py` 與 `password.py`。
