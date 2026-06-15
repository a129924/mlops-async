---
name: python-implementation-workflow
description: Wrapper workflow recipe for parent Codex sessions that need to coordinate Python topic delivery with repo-local planner, implementer, and reviewer agents while preserving shared artifact-contract boundaries.
---

# Python Implementation Workflow

Use this skill when a parent Codex session needs the repo-local Python implementation workflow for a single topic with plan, implementation, and review handoffs.

Read [reference.md](./reference.md) before acting.

## Role

This skill is a wrapper recipe for the parent Codex session.

- It does not replace runtime orchestration with its own engine.
- It does not redefine the core workflow contract that belongs in custom agents.
- It does not create a runtime dependency on legacy `.github/agents/*.agent.md` files.

## Required Inputs

- A single active topic with its plan artifacts
- Repo-local custom agents:
  - `planner`
  - `implementer`
  - `reviewer`
- The shared `workflow-artifact-contract` skill when workflow artifacts are being created or reviewed

## Wrapper Handoff Recipe

1. Use `planner` to confirm or refine the topic execution plan from current repo artifacts.
2. Use `implementer` to make scoped repository changes that satisfy the approved plan.
3. Use `reviewer` to check correctness, path compliance, contract boundaries, and validation coverage.
4. Keep all workflow artifacts on official repo-local paths only.

## Required Returned Artifacts

- `planner` must return a concrete execution plan for the single active topic, including scoped steps, assumptions, constraints, and the repo-local artifact paths it expects the workflow to use.
- `implementer` must return the applied repository change set, a concise implementation summary, and the validation results needed to show the approved plan was executed.
- `reviewer` must return review findings, residual risks or open questions, and an explicit pass/fail recommendation for whether the topic is ready to leave review.
- Returned artifacts must be grounded in current repo-local workflow outputs and must not depend on legacy `.github/agents/*.agent.md` files at runtime.
- Legacy `.github/agents/*.agent.md` files remain frozen provenance only and are not a required runtime artifact source for this wrapper skill.

## Required Gates

- Planning gate: `planner` must produce or confirm a usable topic plan before `implementer` begins scoped repository changes.
- Implementation gate: `implementer` must stay within the approved topic scope and return the applied change summary plus validation evidence before handoff to `reviewer`.
- Review gate: `reviewer` must verify correctness, path compliance, artifact-contract boundaries, and validation coverage before the parent Codex session treats the topic as review-complete.
- Path gate: all workflow artifacts must stay on official repo-local paths; this wrapper skill must not redirect runtime artifacts to legacy `.github/agents/*.agent.md` files or repo-root `agents/openai.yaml`.
- Workflow boundary gate: git commit, push, and pull request actions remain outside this workflow and are not part of satisfying these gates.

## Human-Review Stop Boundary

- The parent Codex session must stop for human review once `reviewer` has returned findings and a final pass/fail recommendation for the scoped topic.
- The wrapper skill coordinates `planner`, `implementer`, and `reviewer`, but it must not present itself as an autonomous runtime orchestration engine that self-approves release or merge decisions.
- If `reviewer` reports blocking findings, unresolved risks, or insufficient validation, the workflow must return to the parent Codex session for explicit human-directed next steps.
- Even when review passes, commit, push, and pull request decisions remain outside this workflow boundary and require separate human-directed handling.

## Boundaries

- The parent Codex session remains responsible for sequencing and tool execution.
- This skill is descriptive guidance for that session, not a standalone orchestrator.
- Git commit, push, and pull request actions stay outside this workflow skill.
