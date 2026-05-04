# Version sources

## Current-state-first detection

Start by checking which version sources actually exist in the relevant release surface.

Examples:

- `pyproject.toml`
- `__version__.py`
- `package.json`

If no version files exist in the touched release surface, degrade to tag-only mode.

## Synchronization rule

If multiple sources exist, they must agree before release.

Examples:

- `pyproject.toml` = `1.4.0`
- `src/pkg/__version__.py` = `1.4.0`
- intended tag = `v1.4.0`

Any mismatch is a hard block.

## Multi-ecosystem releases

If one PR modifies both Python and Node release surfaces, keep those versions aligned as one coordinated release instead of treating one side as irrelevant.
