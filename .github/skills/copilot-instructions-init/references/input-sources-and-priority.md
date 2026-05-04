# Input sources and priority

This skill uses a locked input order:

1. sensed facts
2. installed skills
3. plan / blueprint / retrofit contract
4. human intent

Lower-priority inputs may refine open choices, but they may not contradict a
higher-priority input without an explicit stop-and-ask handoff.

## Required fact categories

The minimum required fact categories are:
- toolchain
- installed skills
- project structure / entrypoints

If any required category is missing, generation or refresh must hard-block.
There is no downgrade template path.

## Human double-check rule

When human intent conflicts with current facts, stop and ask which source should
govern the next step.

Examples:
- the human says Poetry, but facts show uv
- the human says the file does not exist, but it is present
- the human requests a skill, command, or tool that is not installed

Do not resolve these conflicts by mixing both stories into the output.

## Three-fingerprint stale check

Facts are stale when any of these fingerprints changed since the last sensing
snapshot:
1. Git `HEAD`
2. `pyproject.toml` / `uv.lock`
3. `.github/skills/` summary

If one or more fingerprints changed, stop and require re-sensing before the skill
continues.

## Update-mode consistency policy

Greenfield first generation:
- requires current facts before writing
- does not require extra re-sensing after write

Update or retrofit refresh:
- requires current facts before writing
- must run a post-write semantic consistency check against current manifests and
  sensed facts after the file is updated
- uses a static semantic check, not a full acceptance rerun, unless some other
  workflow explicitly requires that later
