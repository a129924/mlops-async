---
topic: request-contract-non-authoritative-handling
phase: implementation-workflow
created: 2026-07-09
---

# request-contract-non-authoritative-handling Step Tracker

> **Executor**: Mark each stage and implementation step `[X]` when complete.
> This topic stops at `human-check`.

## Workflow Stages

- [X] create-worktree
- [X] plan-finalization
- [X] plan-review
- [X] plan-fix
- [X] final-gate
- [X] implementation
- [X] independent-review
- [ ] human-check

## Implementation Steps

- [X] 1. Freeze the topic-local planning artifacts.
- [X] 2. Update `request-contract-evidence-matrix.md`.
- [X] 3. Add `request-contract-non-authoritative-ledger.md`.
- [X] 4. Apply historical-only metadata and the collection guard to `projects_tables_link_request_gate`.
- [X] 5. Apply non-authoritative metadata to wrapper and custom-client shape-only topics.
- [X] 6. Run scoped pytest, `ruff check`, and `pyright` verification.
