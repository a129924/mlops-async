> **Analysis layer — strict mode**
>
> `analysis/custom-agent-codex-compat/requirements.md` and
> `analysis/custom-agent-codex-compat/technical-spec.md` exist. This plan uses
> the technical spec as the execution-facing source of truth and converts this
> topic to an implementation baseline for downstream work.

## Goal / Outcome

建立一份 repo-visible implementation baseline，讓後續 creator 可以把 legacy
`.github/agents/python-implementation-workflow.agent.md` 轉成官方 repo-local
discovery artifacts：

- `./.codex/agents/python-implementation-workflow.toml`
- `./.agents/skills/python-implementation-workflow/SKILL.md`
- `./.agents/skills/python-implementation-workflow/agents/openai.yaml`

本輪只交付 planning artifacts ready for downstream implementation，不建立上述實作檔。

## Scope

- **In scope**:
  - `analysis/custom-agent-codex-compat/requirements.md`
  - `analysis/custom-agent-codex-compat/technical-spec.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.spec.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md`
  - `.github/agents/python-implementation-workflow.agent.md` as read-only source evidence
  - `./.codex/agents/python-implementation-workflow.toml` as downstream implementation target only
  - `./.agents/skills/python-implementation-workflow/SKILL.md` as downstream implementation target only
  - `./.agents/skills/python-implementation-workflow/agents/openai.yaml` as downstream implementation target only

- **Out of scope**:
  - any artifact under `./codex/**`
  - `./agents/openai.yaml`
  - direct edits to `.github/agents/python-implementation-workflow.agent.md`
  - implementation artifact creation in this round
  - `./tests/test_codex_custom_agent_baseline.py`

## Locked Decisions

- The legacy source remains `.github/agents/python-implementation-workflow.agent.md`, but it is read-only evidence only.
- Official repo-local discovery paths are mandatory:
  - `./.codex/agents/*.toml`
  - `./.agents/skills/<skill-name>/SKILL.md`
  - `./.agents/skills/<skill-name>/agents/openai.yaml`
- The wrapper skill is a boundary wrapper, not an alternate implementation surface.
- `SKILL.md` must not absorb or replace core custom-agent workflow semantics that belong in `./.codex/agents/python-implementation-workflow.toml`.
- No legacy path aliasing, adapter surface, or non-official path may be used to satisfy this topic.
- This round ends with planning artifacts ready for downstream implementation; all implementation artifacts remain pending.

## Boundaries / Exclusions

- This round is planning-artifacts-only.
- Do not create `./.codex/agents/*.toml` in this round.
- Do not create `./.agents/skills/*` in this round.
- Do not create test artifacts in this round.
- Any artifact under `./codex/**` is forbidden.
- `./agents/openai.yaml` is forbidden.
- `.github/agents/*.agent.md` files are legacy reference / provenance only and are not target contracts for this topic.

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: plan/spec/step/checklist are implementation-oriented now, but Phase 3 artifact creation has not started in this round.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- This plan is no longer a paused draft baseline.
- Phase 3 remains pending because this round does not create implementation artifacts.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/custom-agent-codex-compat/requirements.md` | Planning actor | Frozen implementation-planning requirements |
| Topic technical specification | `analysis/custom-agent-codex-compat/technical-spec.md` | Planning actor | Execution-facing technical contract |
| Topic plan | `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md` | Planning actor | Repo-visible implementation baseline |
| Topic specification | `plan/custom-agent-codex-compat/custom-agent-codex-compat.spec.md` | Planning actor | Phase 2 behavior contract for artifact family, paths, and boundaries |
| Topic step tracker | `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md` | Planning actor | Canonical Phase 3 completion gate source |
| Topic checklist | `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md` | Planning actor | Planning-round validation of implementation readiness |
| Legacy source evidence | `.github/agents/python-implementation-workflow.agent.md` | Creator | Read-only source semantics for migration |
| Custom agent entry | `./.codex/agents/python-implementation-workflow.toml` | Future creator | Downstream custom-agent implementation target |
| Wrapper skill entry | `./.agents/skills/python-implementation-workflow/SKILL.md` | Future creator | Downstream wrapper skill implementation target |
| Wrapper skill agent config | `./.agents/skills/python-implementation-workflow/agents/openai.yaml` | Future creator | Downstream wrapper-to-agent binding target |

Artifact path notes:

- The three repo-local discovery targets are required together as one implementation family.
- `./.codex/agents/python-implementation-workflow.toml` is the only allowed agent discovery target in this topic.
- `./.agents/skills/python-implementation-workflow/SKILL.md` and `./.agents/skills/python-implementation-workflow/agents/openai.yaml` are wrapper-layer targets only.

## Implementation Steps

1. Create `./.codex/agents/python-implementation-workflow.toml` by translating the legacy phase order, active gates, and workflow boundaries from `.github/agents/python-implementation-workflow.agent.md` into the repo-local custom-agent surface.
2. Create `./.agents/skills/python-implementation-workflow/SKILL.md` as a wrapper skill that explains invocation scope, handoff contract, and the fact that the custom agent remains the owner of workflow orchestration semantics.
3. Create `./.agents/skills/python-implementation-workflow/agents/openai.yaml` so the wrapper skill binds to the custom agent through the official repo-local path contract.
4. Verify all cross-references inside the three downstream artifacts use only official repo-local discovery paths and do not reference `./codex/...` or `./agents/openai.yaml`.
5. Verify the legacy dependency boundary remains intact: `.github/agents/python-implementation-workflow.agent.md` stays read-only and serves only as source evidence.
6. Verify the wrapper skill boundary remains intact: wrapper artifacts route to the custom agent but do not replace or duplicate the custom agent's core workflow logic.
7. Update `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md` so every downstream implementation step is marked complete before Phase 3 gate execution.

## Validation / Acceptance Checks

- `analysis/custom-agent-codex-compat/requirements.md`, `analysis/custom-agent-codex-compat/technical-spec.md`, `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`, `plan/custom-agent-codex-compat/custom-agent-codex-compat.spec.md`, `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`, and `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md` all exist.
- `plan.md`, `technical-spec.md`, and `checklist.md` all use the same official repo-local discovery paths.
- The implementation artifact family is complete only when all three downstream targets are present.
- The plan forbids `./codex/**` and `./agents/openai.yaml`.
- The plan preserves the legacy dependency boundary and wrapper skill boundary.
- This round's planning completion does not imply Phase 3 implementation completion.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- This topic is planning-only.
- No release action is required after merge.
- No `VERSION`, `README`, or release-notes change is required.
- Downstream implementation artifacts belong only to the next implementation phase and are not part of this round's deliverables.

## Open Questions / Unresolved Items

- Reviewer should verify whether the eventual `./.codex/agents/python-implementation-workflow.toml` needs any repo-specific metadata keys beyond those implied by the legacy source.
- Reviewer should verify whether wrapper skill wording needs additional guardrails to prevent orchestration drift into `SKILL.md`.
