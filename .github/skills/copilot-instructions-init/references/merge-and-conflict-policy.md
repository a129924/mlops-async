# Merge and conflict policy

This skill is not allowed to silently blend materially different instruction
content.

## Managed versus non-managed content

Agent-managed regions should use explicit block markers such as:
- `<!-- START AGENT BLOCK -->`
- `<!-- END AGENT BLOCK -->`

Managed blocks may be refreshed when the current inputs still justify them.
Non-managed content is any content outside those markers.

## Non-managed-block detection

Treat the existing target-project `.github/copilot-instructions.md` as materially
different when either condition is true:
- non-managed content outside agent block markers is non-empty
- core rules inside managed regions were manually changed in a way that no longer
  matches the generated contract

Material difference is a hard stop, not a warning.

## Required overwrite choice set

When the file is materially different, present exactly these choices:
1. full overwrite
2. keep current content
3. manual merge by the human

Do not add a hidden fourth path such as silent synthesis or automatic partial
merge.

## When to stop and ask

Stop and ask instead of merging when:
- non-managed content exists outside the managed blocks
- the current file already expresses a different toolchain, structure, or
  governance policy than current facts support
- the requested update would overwrite manual editorial content that the skill
  does not own
- human intent asks for a merge strategy that would require heuristic rewriting

## Safe refresh boundary

A refresh is safe only when:
- the file is fully agent-managed, or the human explicitly chose overwrite or
  manual merge
- current facts are fresh and complete
- the generated sections remain semantically aligned with the current manifests
  and structure

If any of those conditions fail, stop rather than improvise.
