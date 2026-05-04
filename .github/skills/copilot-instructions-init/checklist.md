# Copilot Instructions Init Checklist

Use this checklist when reviewing or self-checking this higher-risk skill draft.

- [ ] The skill stays single-responsibility: generate or refresh only the target project's `.github/copilot-instructions.md`.
- [ ] `SKILL.md` includes concise positive and negative examples.
- [ ] `examples.md` covers:
  - [ ] greenfield placeholder -> formal instructions
  - [ ] retrofit follow-up refresh
  - [ ] human-intent conflict with facts or capabilities
  - [ ] stale-facts hard block
  - [ ] materially different existing instructions
  - [ ] missing-facts hard block
- [ ] The fixed input priority is explicit: facts -> installed skills -> plan contract -> human intent.
- [ ] Human-intent conflict requires a double-check stop rather than silent override.
- [ ] Missing facts are a hard block; no downgrade template path exists.
- [ ] Stale detection uses all three fingerprints:
  - [ ] Git `HEAD`
  - [ ] `pyproject.toml` / `uv.lock`
  - [ ] `.github/skills/` summary
- [ ] The output contract requires all three sections:
  - [ ] `## Project Truth`
  - [ ] `## Governance`
  - [ ] `## Implementation Rules`
- [ ] The merge policy forbids silent merge of materially different existing instructions.
- [ ] Non-managed-block detection is explicit and tied to agent block markers.
- [ ] The overwrite choice set is exactly: full overwrite, keep current content, manual merge by the human.
- [ ] Greenfield first generation does not require extra re-sensing after write.
- [ ] Update or retrofit refresh requires a post-write semantic consistency check.
- [ ] `Local references` names every local file and gives each one a clear role.
