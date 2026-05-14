> **Analysis-layer routing: INCOMPLETE LAYER**
>
> - Available business guardrail: `analysis/language-policy-canonical-headings/requirements.md`
> - Missing companion artifact: `analysis/language-policy-canonical-headings/technical-spec.md`
> - No human `override` instruction changes the analysis-layer priority for this topic.
> - This topic plan may proceed, but creator work must not invent technical-spec-level scope expansion beyond the frozen requirements baseline.

## Goal / Outcome

- Produce the repo-visible execution contract for `language-policy-canonical-headings` so future creator work can align the repository language policy around canonical English headings without widening the repository into broad bilingual usage.
- When this topic is complete, `.github/copilot-instructions.md` and `.github/CONTRIBUTING.md` will express a non-conflicting policy where Traditional Chinese remains the default for normal prose and strictly enumerated canonical headings / terms may remain in English.

## Scope

- **In scope**:
  - Maintain the planning artifacts for this topic under `plan/language-policy-canonical-headings/`.
  - Use `analysis/language-policy-canonical-headings/requirements.md` as the frozen business baseline for creator and reviewer work.
  - Update `.github/copilot-instructions.md` to encode:
    - Traditional Chinese as the default for non-fixed prose
    - strict enumeration for canonical English headings / terms
    - preserve-canonical-English behavior for uncertain heading-like cases
  - Update `.github/CONTRIBUTING.md` so its contributor-facing guidance does not conflict with the policy encoded in `.github/copilot-instructions.md`.
  - Inspect whether any additional governance document directly states this same language policy; if one is found outside the exact artifact paths below, stop and repair this plan before modifying it.

- **Out of scope**:
  - Commit, PR, or Issue title language policy changes
  - Retroactive cleanup of existing repository documents
  - Broad bilingual policy changes for general prose
  - `technical-spec.md` authoring for this topic
  - README updates, VERSION bumps, release notes, tag/release work, or stable-library publication tasks

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**. It does not modify `README.md`, `VERSION`, release notes, or release timing metadata.
- The frozen business baseline is `analysis/language-policy-canonical-headings/requirements.md`; chat-time intent does not override that baseline.
- Traditional Chinese remains the default language for normal prose in repo-owned governance, analysis, and planning documents.
- Canonical English may remain only under **strict enumeration**:
  - canonical section headings
  - plan / step tracker fixed section names
  - fixed labels
  - workflow names
  - necessary canonical terms
- If an agent cannot confidently classify a heading-like item, the default is to preserve the existing canonical English form rather than translate it automatically.
- `.github/copilot-instructions.md` and `.github/CONTRIBUTING.md` are both formal policy sources for this topic and must not conflict when the topic is complete.
- This topic must not expand into a generic mixed-language or all-English-heading policy.

## Boundaries / Exclusions

- Planning actor owns this plan and the requirements baseline only.
- Creator owns drafting the allowed policy wording changes within the exact artifact paths listed below.
- Reviewer owns the independent verdict and must not perform creator work as part of review.
- Main Agent owns publish routing, PR flow, merge follow-up, and any later worktree cleanup; those actions are not creator scope.
- If work appears to require editing an additional governance file that directly states this policy, stop and repair this plan with exact artifact paths before continuing.
- If implementation drifts toward commit / PR / Issue title policy, retroactive document cleanup, or broad bilingual governance, stop and split that into a separate topic.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops at `merged` and does not declare a release action.
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

- Use the standard Phase 4.5 planner-alignment rule before publish.
- Because the analysis layer is incomplete, creator work must stay bounded to the frozen requirements baseline and may not invent extra policy surfaces.
- STOP POINT 1 still applies before commit / push / PR creation.
- STOP POINT 2 still applies after merge handoff; post-merge local sync requires a new explicit human resume message.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/language-policy-canonical-headings/language-policy-canonical-headings.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/language-policy-canonical-headings/language-policy-canonical-headings.step.md` | Planning actor -> Creator | Machine-readable tracking for the locked creator steps |
| Requirements baseline | `analysis/language-policy-canonical-headings/requirements.md` | Planning actor | Frozen business guardrail for this policy topic |
| AI policy source | `.github/copilot-instructions.md` | Creator | Primary AI-facing language policy source that must encode the strict-enumeration exception |
| Contributor policy source | `.github/CONTRIBUTING.md` | Creator | Contributor-facing guidance that must remain non-conflicting with the AI-facing policy source |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: modified in this topic.
- If later work drifts outside these exact paths, stop and update this plan before continuing.
- If inspection finds another file that directly states the same language policy, do not edit it under this plan until the plan is repaired with an exact path entry.

## Implementation Steps

1. Create `plan/language-policy-canonical-headings/language-policy-canonical-headings.step.md` with creator-facing implementation checkboxes aligned to the steps below and the canonical workflow contract.
2. Update `.github/copilot-instructions.md` so the `Language Requirement` section keeps Traditional Chinese as the default for normal prose while explicitly allowing strictly enumerated canonical English headings / terms to remain in English.
3. In `.github/copilot-instructions.md`, encode that uncertain heading-like cases default to preserving canonical English only for candidate fixed headings / labels / workflow names / canonical terms, not for general prose.
4. Update `.github/CONTRIBUTING.md` so its contributor-facing wording does not contradict the same policy boundaries, and make the non-conflicting scope explicit without broadening the repository language policy.
5. Inspect whether another governance file directly states the same language policy. If none exists, record no further action through the normal review evidence. If one exists outside the artifact list, stop and repair this topic plan before editing it.
6. Re-read the resulting wording across `.github/copilot-instructions.md` and `.github/CONTRIBUTING.md` to confirm:
   - normal prose still defaults to Traditional Chinese
   - strict enumeration bounds the English-heading exception
   - commit / PR / Issue title policy remains untouched
   - no wording implies broad bilingual freedom

## Validation / Acceptance Checks

- The modified files stay inside the exact artifact paths listed above, or the plan is repaired before continuing.
- `analysis/language-policy-canonical-headings/requirements.md` remains the business guardrail for creator and reviewer decisions.
- `.github/copilot-instructions.md` explicitly distinguishes normal prose from strictly enumerated canonical English headings / terms.
- `.github/CONTRIBUTING.md` does not contradict `.github/copilot-instructions.md` on this topic.
- The final wording preserves these locked decisions:
  - Traditional Chinese remains the default for normal prose
  - only the enumerated canonical categories may remain in English
  - uncertain heading-like cases default to preserving canonical English
  - commit / PR / Issue title policy is unchanged
- Reviewer verifies that no wording expands the policy into broad mixed-language permission.

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

- After merge, Main Agent may perform the normal local sync flow only after an explicit human resume message.
- No README update, VERSION bump, release-note work, tag creation, or repository release action belongs to this topic.
- This topic is terminal at `merged`.

## Open Questions / Unresolved Items

- `analysis/language-policy-canonical-headings/technical-spec.md` is intentionally absent in this flow; if later work needs technical translation rather than direct policy editing, stop and create that artifact before widening implementation scope.
