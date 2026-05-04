---
name: copilot-instructions-init
description: Generate or refresh a target project's `.github/copilot-instructions.md` from current sensed facts, installed skills, and plan contracts, with hard stops for stale facts, missing facts, and materially different existing instructions.
---

# Purpose
Generate or refresh exactly one target-project file: `.github/copilot-instructions.md`.

# Trigger / When to use
Use this skill when:
- a target project already has current sensed facts and needs formal `.github/copilot-instructions.md` content
- a greenfield project has moved past the placeholder stage and facts now exist
- a retrofit or structural refresh changed project truth and the instructions file must be updated
- the task is to align target-project instructions with current facts, installed skills, and plan contracts without inventing unsupported tooling

Do not use this skill when:
- required facts are missing, stale, or still being sensed
- the task is to scaffold a greenfield baseline, retrofit structure, or modify sensing scripts
- the task is to edit this repository's own `.github/copilot-instructions.md`, `README.md`, or `VERSION`
- an existing target-project instructions file is materially different and the human has not chosen overwrite, keep, or manual merge

# Inputs
- the target repository root
- a current sensed-facts snapshot for toolchain, installed skills, and project structure / entrypoints
- stale-check fingerprints for Git `HEAD`, `pyproject.toml` / `uv.lock`, and `.github/skills/` summary
- installed skill inventory for the target project
- any applicable plan, blueprint, or retrofit contract
- the human request or intent description
- the current target `.github/copilot-instructions.md`, if present
- explicit human direction when overwrite or manual merge is required

# Process
1. Confirm the job is limited to generating or refreshing the target project's `.github/copilot-instructions.md`.
2. Validate the inputs in this fixed priority order:
   1. sensed facts
   2. installed skills
   3. plan / blueprint / retrofit contract
   4. human intent
3. Hard-block if required fact categories are missing.
   - Required categories include toolchain, installed skills, and project structure / entrypoints.
   - Do not fall back to a generic downgrade template.
4. Run the stale-fact gate before drafting.
   - Compare the last sensing snapshot against all three fingerprints: Git `HEAD`, `pyproject.toml` / `uv.lock`, and `.github/skills/` summary.
   - If any fingerprint changed, stop and require re-sensing before generation or update continues.
5. Compare human intent against sensed facts.
   - If intent conflicts with facts or installed capabilities, stop and ask the human which source should govern.
   - Use the same stop-and-ask behavior for claims such as Poetry vs uv, missing file vs present file, or unavailable requested skills.
6. Build the target instructions from the highest-priority valid inputs only.
   - `## Project Truth`: facts about toolchain, layout, entrypoints, and other observed project reality.
   - `## Governance`: installed skills and plan-level constraints that should govern agent behavior.
   - `## Implementation Rules`: concrete execution rules that remain consistent with facts and governance.
7. Handle an existing `.github/copilot-instructions.md` safely.
   - Treat agent-managed regions as blocks marked with comments such as `<!-- START AGENT BLOCK -->` and `<!-- END AGENT BLOCK -->`.
   - If non-managed content outside those blocks is non-empty, or the existing core rules are materially different, stop and present exactly these choices: full overwrite, keep current content, or manual merge by the human.
   - Do not silently merge materially different instructions.
8. Write the refreshed or first generated file only after all gates pass.
   - Greenfield flow may replace a placeholder once facts exist.
   - Retrofit flow refreshes the same file after structure changes.
9. Run the required post-write check for update paths.
   - Greenfield first generation does not require extra re-sensing after write.
   - Update or retrofit refresh must perform a post-write semantic consistency check against current manifests and sensed facts.
10. Return the result, any hard-stop reason, and any required human follow-up without claiming approval beyond the generated instructions.

# Examples
- Positive: After sensing confirms uv, installed skills, and current entrypoints, replace a greenfield placeholder with `.github/copilot-instructions.md` containing `## Project Truth`, `## Governance`, and `## Implementation Rules`, then run the post-write semantic consistency check only for update or retrofit mode.
- Negative: Guess a generic instructions file when toolchain facts are missing, merge materially different manual content without asking, or honor a human request for Poetry when sensed facts still show uv.

# Outputs
- one generated or refreshed target-project `.github/copilot-instructions.md`
- a hard-stop result when facts are stale, missing, conflicting, or unsupported
- an explicit overwrite / keep / manual-merge choice request when existing instructions are materially different
- an update-mode semantic consistency result when the task is refresh rather than first greenfield generation

# Verification
- confirm the fixed input priority stays explicit and facts are never downgraded below human intent
- confirm missing facts and stale fingerprints cause hard stops rather than warnings
- confirm the generated file always contains `## Project Truth`, `## Governance`, and `## Implementation Rules`
- confirm generated rules mention only toolchains, skills, and layouts supported by current facts
- confirm materially different existing instructions trigger overwrite / keep / manual-merge choices instead of silent synthesis
- confirm update or retrofit mode runs a post-write semantic consistency check, while greenfield first generation does not add extra re-sensing

# Red Flags
- a request to "just write a sensible default" before facts exist
- a request to merge human-authored instructions and generated content without a diff-oriented choice
- a claim that a stale sensing snapshot is close enough because only one fingerprint changed
- a request to refresh instructions after retrofit without checking current manifests or facts
- a request to modify adjacent files such as `README.md`, `VERSION`, or this repository's own policy file

# Common Rationalizations
- "The toolchain probably did not really change, so skip the stale check."
- "Human intent is more recent, so facts can be ignored this time."
- "The existing instructions mostly look compatible, so silent merge is safer than asking."
- "If facts are missing, a placeholder is better than blocking."
- "Update mode already wrote the file, so semantic consistency does not matter anymore."

# Boundaries
- Do not generate or update files other than the target project's `.github/copilot-instructions.md`.
- Do not modify this repository's own `.github/copilot-instructions.md`.
- Do not implement greenfield scaffolding, retrofit restructuring, or sensing-script changes.
- Do not invent unsupported tools, skills, commands, layouts, or entrypoints.
- Do not silently merge materially different existing instructions.
- Do not bypass the human double-check gate when intent conflicts with sensed facts.

# Local references
- `examples.md`: branching scenarios for greenfield, retrofit refresh, stale facts, overwrite conflicts, and missing-fact hard blocks
- `references/instruction-layering.md`: section contract for `## Project Truth`, `## Governance`, and `## Implementation Rules`
- `references/merge-and-conflict-policy.md`: managed-block handling, materially-different detection, and overwrite decision rules
- `references/input-sources-and-priority.md`: fact-first ordering, required-fact categories, stale fingerprints, and update-mode consistency policy
- `checklist.md`: repeatable higher-risk validation checklist for hard stops, overwrite safety, and output-shape checks
