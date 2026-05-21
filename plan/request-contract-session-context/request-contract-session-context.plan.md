Analysis-layer routing: **incomplete mode** — `analysis/request-contract-session-context/requirements.md` exists, but companion `analysis/request-contract-session-context/technical-spec.md` is absent. This plan uses the requirements baseline as the business guardrail. If a future `technical-spec.md` is created and conflicts with this plan, stop and realign instead of silently overriding it.

## Goal / Outcome

建立一個 repo-visible 的 request-contract session-context topic plan，讓後續 creator 可以在
不改動 runtime behavior 的前提下，更新既有 request-contract standards doc，並新增一份可直接
注入新 session 的 prompt artifact。

Topic 完成時，repo 應同時具備：

1. 一份完整的 request-contract testing source-of-truth 文件
2. 一份可供 Main Agent 或 human operator 在新 session 中直接注入的入口 prompt

## Scope

- **In scope**:
  - `analysis/request-contract-session-context/requirements.md`
  - `plan/request-contract-session-context/request-contract-session-context.plan.md`
  - `docs/standards/request-contract-testing.md`
  - `.github/prompts/request-contract-testing-context.prompt.md`

- **Out of scope**:
  - `analysis/request-contract-session-context/technical-spec.md`
  - `src/mlops_async/**`
  - `tests/**`
  - `README.md`、`VERSION`、release-note 或其他 stable-library surfaces
  - request-contract harness / DSL 重寫
  - sasctl / legacy source 行為變更

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**.
- This topic is a **docs / prompt context topic**, not a Python implementation topic; it does **not** use `python-implementation-workflow`, and it does not require `*.spec.md` / `*.step.md` to proceed.
- `docs/standards/request-contract-testing.md` remains the source of truth for this domain.
- `.github/prompts/request-contract-testing-context.prompt.md` is an injection entry artifact only; it may summarize and route, but it must not redefine the contract independently.
- If the prompt and standards doc drift, Agent must stop for human review rather than silently preferring one over the other.
- The prompt must support both actors, but Main Agent is the primary consumer.
- Topic success requires both:
  - single-injection startup for a new session
  - Agent can restate the four core testing semantics plus gate rules after reading the artifacts
- No correction/delta artifact path is used in this topic.
- No `review-log` artifact is required because routing does not depend on reviewer-controlled multi-round rework.
- No round cap is declared for this topic.

## Boundaries / Exclusions

- Planning actor 只建立 repo-visible requirements 與 topic plan；不進入文件 / prompt 實作。
- Creator 不得把這個 topic 擴張成 request-contract harness 重構、auth integration 設計、或 API porting implementation。
- Reviewer 只能依據 requirements baseline、topic plan、與 exact artifact paths 審查；不得在 review 時把 scope 擴張到 `src/**`、`tests/**`、README、VERSION 或 release workflow。
- Executor scope ends at local file changes plus validation summary; `git commit / push / PR` remain Main Agent operations under the canonical repo lifecycle and are not part of creator execution for this topic.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops before release and does not declare stable-library promotion.
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

- Analysis-layer incomplete mode applies for this topic because `technical-spec.md` is absent.
- Shared-file coordination warning: `docs/standards/request-contract-testing.md` and `.github/prompts/` are shared governance surfaces; if parallel worktrees touch them, treat any drift as a human-coordination issue before implementation continues.
- Creator handoff boundary for this topic is review-ready local changes only; publish routing begins only when Main Agent later resumes canonical `publish-in-progress`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/request-contract-session-context/requirements.md` | Planning actor | Business baseline and business guardrail for this topic |
| Topic plan | `plan/request-contract-session-context/request-contract-session-context.plan.md` | Planning actor | Repo-visible execution contract for creator/reviewer workflow |
| Request-contract standards doc | `docs/standards/request-contract-testing.md` | Creator | Source-of-truth standards document for request-contract testing |
| Request-contract injection prompt | `.github/prompts/request-contract-testing-context.prompt.md` | Creator | Directly injectable session-entry artifact for Main Agent / human operator |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or `.github/copilot-instructions.md`.
- Listed paths are an executable contract; if later work drifts outside them, stop and realign the plan before implementation continues.
- The prompt path is subordinate to the standards doc path; if the prompt starts carrying contract meaning not backed by the standards doc, stop and realign.
- No correction or delta artifact family is used here.
- No `review-log` path is listed because reviewer feedback does not control routing across mandatory multi-round rework in this topic.

## Implementation Steps

1. Update `docs/standards/request-contract-testing.md` so it explicitly supports session reuse: identify it as the source of truth for request-contract testing topics and make the four core testing semantics and gate rules easy for a new session to recover.
2. Create `.github/prompts/request-contract-testing-context.prompt.md` as a directly injectable prompt that routes a new session to the standards doc, restates the minimal four-part mental model, and requires stop-on-drift behavior.
3. Keep both artifacts aligned: if either artifact implies behavior not backed by the other, stop and fix the mismatch rather than choosing one silently.

## Validation / Acceptance Checks

- `analysis/request-contract-session-context/requirements.md` exists and this plan stays inside its actor, success-signal, and source-of-truth decisions.
- `docs/standards/request-contract-testing.md` remains the complete standard rather than becoming a partial pointer doc.
- `.github/prompts/request-contract-testing-context.prompt.md` exists and clearly points to the standards doc as source of truth.
- Manual inspection confirms a new session could recover:
  - request shape / contract
  - auth steps and mock-response handling
  - preflight
  - target-api / intercepted flow capture
  - the request-contract gate core rules
- No files under `src/` or `tests/` are modified by this topic.
- Validation commands remain bounded to this topic's scope:
  - `rg -n "request-contract|prompt|source of truth|Agent first-read|preflight|target-api" docs/standards/request-contract-testing.md .github/prompts/request-contract-testing-context.prompt.md`

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

- After merge, no repository release action is required for this topic.
- No README row, VERSION bump, or release-note action is expected.

## Open Questions / Unresolved Items

- None.
