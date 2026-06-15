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

## Boundaries

- The parent Codex session remains responsible for sequencing and tool execution.
- This skill is descriptive guidance for that session, not a standalone orchestrator.
- Git commit, push, and pull request actions stay outside this workflow skill.
