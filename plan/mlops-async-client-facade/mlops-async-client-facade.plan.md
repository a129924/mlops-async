---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
d1_verdict: non-trivial
branch: feat/andrew/mlops-async-client-facade
worktree: D:\code\python\mlops-async.worktrees\agent-20260812-mlops-async-client-facade
---

# MlopsAsyncClient facade implementation plan

## Authoritative completion update (2026-08-13)

The prior `needs-rework -> creator-in-progress` record is historical. The
bounded Tach correction and facade-test rework were independently re-reviewed
and approved, as was independent code review. Final validation is also
complete: an isolated Linux-native ext4 detached checkout rebuilt the current
uncommitted snapshot from base `e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`,
hash-matching six tracked diffs and eight topic-untracked files. `uv sync
--frozen`, full non-E2E pytest (`694 passed, 9 skipped, 1 deselected`, 94.38%
coverage), Ruff, Pyright, Tach, and `git diff --check` all passed. The retained
transcript is `/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
(SHA-256 `2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`);
the disposable checkout and bare cache were deleted.

Current workflow status is `approved`. `publish` is the sole pending stage;
commit, push, draft PR, human review, merge, version, tag, and release have not
been performed or authorized by this artifact update.

> **Analysis-layer routing: strict mode.** `analysis/mlops-async-client-facade/technical-spec.md` 是 execution-facing source of truth；`requirements.md` 是 business-intent guardrail。本次只回填使用者新授權的 root seven-target Tach correction 與 re-review lifecycle。

## Goal / Outcome

保留 additive package-root `MlopsAsyncClient` 的已授權 provisional implementation，並以精確的 Tach composition-root boundary 消除 cycle，使此 public API 在獨立 review、final validation 與後續 publish gates 後可發布。

## Scope

### In-Scope

- `MlopsAsyncClient`、root export、facade tests、README、architecture/boundary docs 的既有 user-authorized provisional work；不回退它們。
- `tach.toml` 僅既有 `mlops_async` root `depends_on` list 與既有 `mlops_async.transport` `depends_on` list。
- six topic artifacts 的 material Tach rework、re-review lifecycle 與 acceptance shape。

### Out-Of-Scope

- `.users`、other grants、transport injection、retry/timeout/cancellation API、facade-specific exception、RequestExecutor/CAS migration。
- core/transport/clients production source、任何既有 endpoint behavior、VERSION/tag/release/release notes/live E2E。
- 除兩個明示 lists 之外的任何 Tach block、target、global flag、exclude、interface 或 config content。

## Locked Decisions

- Constructor 接受五個 required keyword-only `str` parameters；Facade 建立 `HttpClient`、password token client、`InMemoryTokenStorage()`、`TokenManager`、`AuthProvider` 和一個 raw `Requester`；五個 namespaces readonly 且 identity-stable。
- Constructor/context entry/property access 不作 I/O；first authenticated request 才 lazy token flow；Facade 是唯一 `HttpClient` close owner，`aclose()`/context exit idempotent，既有 errors/cancellation 原樣傳播。
- `tach.toml` 的 root list 必須恰為 `mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、`mlops_async.clients.models`、`mlops_async.clients.projects`；transport list 必須且僅為 `mlops_async.core`、`mlops_async.exceptions`。
- `tach.toml` 是 Modify，不是 Written；其他 Tach blocks、global flags、excludes、interfaces 與全部 production paths 都是 ReadOnly。
- 既有 facade/root export/tests/docs 與 scoped TDD/focused/full-validation evidence 是 provisional/historical evidence；不因 plan rework 重做或宣稱為新 gate 的完成證據。
- 此為 stable-library-affecting additive public API，但本 topic 不 bump VERSION、不建立 tag/release；README 的現有 public usage entry 在 publish gate 保留。

## Boundaries / Exclusions

### Written

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`

### Modify

- `src/mlops_async/__init__.py`
- `tests/unit/clients/test_auth_client.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `tach.toml`：僅兩個既有 `depends_on` lists。
- `analysis/mlops-async-client-facade/requirements.md`
- `analysis/mlops-async-client-facade/technical-spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.step.md`

### ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/transport/**`、`src/mlops_async/clients/**`。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`。
- 除 root seven-target list 與 transport exact two-target list 以外的所有 `tach.toml` content。

### Deleted

- 無。

## Status / Allowed Transitions

### Implementation-review rework record (2026-08-12)

**Current:** `creator-in-progress`。main workflow 與 restored Python companion 的 plan-review 均已獨立 `approved`，所以 `plan-review` 是完成的歷史 gate。後續 independent implementation review 的 verdict 為 `needs-rework`，本輪使用 canonical transition `needs-rework -> creator-in-progress`；先前的 `review-ready` 與 pending plan-review 宣稱均不適用。

- **Required rework**: root Tach list 的精確順序必須是 `mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、`mlops_async.clients.models`、`mlops_async.clients.projects`；補加既定 tests，涵蓋 close 後 properties 仍可讀且 identity 不變、close 後 domain requester I/O 的既有 closed-transport failure、以及首個 authenticated domain request 經 TokenManager/AuthProvider lazy password-token flow。
- **Next**: Implementer 完成上述 scope-preserving rework、Tach correction 與可重作的驗證後，再送 independent implementation review；通過後才是 code review，最後才可能 `approved -> publish-in-progress`。
- Allowed transitions: `planned -> creator-in-progress -> review-ready -> reviewer-in-progress -> approved|needs-rework`; `needs-rework -> creator-in-progress`; `approved -> creator-in-progress|publish-in-progress`; `publish-in-progress -> pr-open|merged`; `pr-open -> needs-rework|merged`; `merged -> terminal`。
- 不包含 commit、push、PR、merge 或 release 的完成/授權。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements | `analysis/mlops-async-client-facade/requirements.md` | Plan-Creator | Business boundary、exact Tach shape、rework route |
| Technical spec | `analysis/mlops-async-client-facade/technical-spec.md` | Plan-Creator | Execution contract、runtime/lifecycle、exact Tach shape |
| Topic plan | `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md` | Plan-Creator | Workflow contract |
| Python plan | `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md` | Plan-Creator | Python execution handoff |
| Specification | `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md` | Plan-Creator | Acceptance contract |
| Step tracker | `plan/mlops-async-client-facade/mlops-async-client-facade.step.md` | Plan-Creator | Historical evidence and pending gates |
| Boundary config | `tach.toml` | Implementer after approval | Only two locked existing lists |

Drift outside these paths blocks execution and requires a new topic or human authorization.

## Stable library metadata

- `README row`: preserve existing `MlopsAsyncClient` public root usage entry; do not expose actual credentials.
- `VERSION bump`: no-bump.
- `timing`: only after approved Tach correction, final validation, independent implementation review and independent code review, at `publish-in-progress`.
- `tag/release`: no.
- `rationale`: additive root API requires documentation but does not itself authorize a version/release event.

## Implementation Steps

1. 保留已完成的 independent plan-review historical approval；不重新執行 plan review，除非發現 scope conflict。
2. Implementer 只修正兩個既有 `tach.toml` `depends_on` lists，令 root seven targets 依 Locked Decisions 的精確順序排列，並保持 transport exact two-target list；不得改其他 config 或 production files。
3. Implementer 在 `tests/unit/test_mlops_async_client.py` 補足既定 close-after-properties identity、closed-transport propagation、first authenticated domain request lazy password-token flow tests；不得擴張 public contract 或改動 ReadOnly production paths。
4. Implementer 以 exact Tach config diff/shape inspection 和 `tach check` 驗證 correction，並重跑 required validations；full non-E2E WSL 的 linked-worktree `.git` pointer guard nonzero 必須記為 environment exception，full validation 不得勾選完成。
5. Independent implementation reviewer 重新檢查完成的 rework；通過後 independent code reviewer 才可驗證品質，兩者均不可擴張 scope。
5. Only after all gates are green may the Main Agent move to `publish-in-progress` for topic commit, push, draft PR, and human review; VERSION/tag/release remain excluded.

## Validation / Acceptance Checks

- Shape inspection/config diff proves root has exactly the seven listed targets and transport has exactly `mlops_async.core`, `mlops_async.exceptions`; no other Tach blocks/flags/excludes/interfaces differ.
- `tach check` passes without cycle.
- Final full non-E2E pytest, Ruff, Pyright, `git diff --check`, independent implementation review, and independent code review are completed after the Tach correction, not inferred from earlier provisional evidence.
- No source/tests/docs are changed by the Tach correction itself; current provisional work remains retained.

## Reviewer Handoff

### Completed reviewer verdict

```json
{"verdict":"needs-rework","blocking_issues":["root Tach seven-target order is not the locked order","three existing-planned facade lifecycle/lazy-auth tests are missing","full WSL validation remains nonzero only because of linked-worktree .git Windows-pointer guard"],"copilot_feedback_triage":{"ADDRESS":["restore exact root target order","add the three bounded facade tests"],"DISCUSS":[],"SKIP":[]}}
```

The implementation-review verdict applies to this exact artifact state and routes work to `creator-in-progress`; it does not reopen plan-review or authorize downstream gates.

```json
{"verdict":"needs-rework|approved","blocking_issues":[],"copilot_feedback_triage":{"ADDRESS":[],"DISCUSS":[],"SKIP":[]}}
```

Re-reviewer must issue an independent implementation verdict after the bounded rework. `approved` is not pre-filled; plan-review approval remains historical and complete.

## Post-merge / release actions

沒有 VERSION bump、tag、release 或 release notes。Draft PR 的下一站是 human review；merge 後的 cleanup/release 需要另行授權。

## Open Questions / Unresolved Items

無；exact Tach target set、transport preservation、scope boundary與 re-review routing 均由使用者明確授權。
