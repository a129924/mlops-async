# Copilot Instructions Init Examples

Use these examples when the concise `SKILL.md` examples are not enough.

## Scenario 1: Greenfield placeholder becomes formal instructions

**Starting point**
- the target repository already has a placeholder `.github/copilot-instructions.md`
- sensing now confirms uv, installed skills, package layout, and entrypoints
- no materially different manual instruction content exists

**Expected behavior**
1. verify the sensed facts are fresh against Git `HEAD`, `pyproject.toml` / `uv.lock`, and `.github/skills/` summary
2. derive the instructions in this order: facts -> installed skills -> plan contract -> human intent
3. replace the placeholder with formal content containing:
   - `## Project Truth`
   - `## Governance`
   - `## Implementation Rules`
4. finish without extra re-sensing because this is first-generation greenfield output

**Anti-pattern**
- keep the placeholder because it is "good enough"
- write generic rules before required facts exist

## Scenario 2: Retrofit follow-up refresh after structure changes

**Starting point**
- `python-project-retrofit` already changed layout or entrypoints
- a sensing delta or refreshed fact snapshot exists
- the target project already has `.github/copilot-instructions.md`

**Expected behavior**
1. treat the refreshed facts as the highest-priority input
2. update `## Project Truth` and any dependent governance or implementation rules that changed semantically
3. preserve only safe agent-managed content
4. run the post-write semantic consistency check against current manifests and facts

**Anti-pattern**
- skip the semantic consistency check because the refresh already completed
- reuse old structure claims that no longer match the repository

## Scenario 3: Human intent conflicts with facts or installed capabilities

**Starting point**
- the human asks for Poetry commands
- sensed facts show uv and no Poetry support

**Expected behavior**
1. stop before writing
2. explain the conflict clearly
3. ask the human which source should govern the next step
4. resume only after explicit direction

**Anti-pattern**
- treat the human request as an override and emit Poetry rules anyway
- partially mention both toolchains to avoid asking

## Scenario 4: Stale-facts hard block

**Starting point**
- the last sensing snapshot was taken on one Git `HEAD`
- current `HEAD` or `pyproject.toml` / `uv.lock` or `.github/skills/` summary has changed since then

**Expected behavior**
1. stop immediately
2. report which fingerprint changed
3. require re-sensing before generation or refresh continues

**Anti-pattern**
- continue because only one fingerprint moved
- attempt a best-effort refresh from stale facts

## Scenario 5: Materially different existing instructions

**Starting point**
- `.github/copilot-instructions.md` already exists
- content outside agent-managed block markers is non-empty, or core rules were manually changed

**Expected behavior**
1. classify the file as materially different
2. present exactly these choices:
   - full overwrite
   - keep current content
   - manual merge by the human
3. stop until the human chooses one path

**Anti-pattern**
- silently mix generated rules into the manual content
- delete non-managed content because the new draft seems better

## Scenario 6: Missing-facts hard block

**Starting point**
- installed skills were sensed, but toolchain or entrypoint facts are missing

**Expected behavior**
1. stop before generating any final instructions
2. name the missing fact category or categories
3. require a new sensing pass or fact collection step
4. do not emit a downgrade placeholder template

**Anti-pattern**
- generate a generic `.github/copilot-instructions.md` with vague guidance
- guess project structure from folder names alone
