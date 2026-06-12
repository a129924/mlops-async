# mlops-async agent discovery contract

## Governance source

- `AGENTS.md` is the repo-local governance source for discoverable agent skills in
  this repository.

## Discoverable skill surface

- Repo-local discoverable skills live under `.agents/skills/`.
- For the `codex-skill-projection` topic, the managed target set is limited to
  the frozen same-name skills materialized at `.agents/skills/<name>/`.

## Non-active surfaces

- `.codex/skills/` is not the active discovery surface for this repository in
  this topic.
- `.github/skills/` is not a source-of-truth or active discovery surface for
  this topic.

## Workflow agent boundary

- `.github/agents/*` remains outside the scope of skill discovery alignment in
  this topic.
