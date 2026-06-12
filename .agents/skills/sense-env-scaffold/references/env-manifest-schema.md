# Env Manifest Schema

Defines the structure of `.codex/env-manifest.json` and
`.codex/env-manifest.snapshot.json` produced by `.codex/skills/sense-env-scaffold/scripts/sense_env.py`.
The canonical source lives under `skills/sense-env-scaffold/...`; the
`.codex/...` surfaces are platform projections.

## Purpose

The manifest is the single structured record of the repository's environment state
at the time of a `sense_env.py` run. It is designed to be:

- human-readable (stable JSON indentation)
- machine-parseable (fixed top-level keys, `snake_case` throughout)
- safe to commit only after human review (snapshot variant strips selected
  machine-local and secret-shaped data; see Snapshot filtering for v1 limits)

---

## Top-level schema

All five keys are required on every successful run. Their values may be empty
collections but the keys must be present.

```json
{
  "meta": { ... },
  "fingerprint": { ... },
  "facts": { ... },
  "assertions": [ ... ],
  "gaps": [ ... ]
}
```

| Key | Type | Description |
|---|---|---|
| `meta` | object | Run metadata: mode, timestamp, script version |
| `fingerprint` | object | Stable identity signals for the run environment |
| `facts` | object | Collected environment facts (tool versions, file presence, Git state) |
| `assertions` | array | Per-assertion evaluation records (acceptance mode only; empty in discovery) |
| `gaps` | array | Unmet items that require remediation |

---

## `meta` module

```json
"meta": {
  "schema_version": "1",
  "run_mode": "discovery",
  "timestamp_utc": "2026-04-22T06:00:00Z",
  "script_version": "1.0.0"
}
```

| Field | Type | Notes |
|---|---|---|
| `schema_version` | string | Fixed `"1"` for v1 |
| `run_mode` | string | `"discovery"` or `"acceptance"` |
| `timestamp_utc` | string | ISO 8601 UTC |
| `script_version` | string | Semver string from inside the script |

---

## `fingerprint` module

```json
"fingerprint": {
  "repo_root_marker": ".git",
  "python_version": "3.11.9",
  "platform": "darwin"
}
```

| Field | Type | Notes |
|---|---|---|
| `repo_root_marker` | string | `".git"` (directory or file); `null` when not in a repo |
| `python_version` | string | `sys.version_info` formatted as `"major.minor.patch"` |
| `platform` | string | `sys.platform` value |

Snapshot shaping replaces or removes any field that exposes machine-specific detail
beyond what is listed here.

---

## `facts` module

```json
"facts": {
  "repo_present": true,
  "git_available": true,
  "current_branch": "feat/andrew/sense-env-scaffold",
  "workspace_clean": false,
  "key_paths": {
    "README.md": true,
    ".codex/": true,
    "pyproject.toml": false,
    "tests/": false,
    "scripts/": true,
    ".codex/copilot-instructions.md": true
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `repo_present` | boolean | `true` when `.git` marker found |
| `git_available` | boolean | `true` when `git` command runs without error |
| `current_branch` | string or null | Branch name; `null` when Git unavailable or detached HEAD |
| `workspace_clean` | boolean or null | `true` when `git status --porcelain` returns empty; `null` when Git unavailable |
| `key_paths` | object | Map of well-known relative paths to boolean presence values |

`key_paths` values are repo-relative. The v1 set is fixed; do not add arbitrary paths
without a separate planning topic.

---

## `assertions` module

Populated in acceptance mode only. Empty array `[]` in discovery mode.

Each assertion record:

```json
{
  "id": "path_exists/0",
  "kind": "path_exists",
  "target": ".codex/skills/sense-env-scaffold/scripts/sense_env.py",
  "state": "PASS",
  "expected": true,
  "observed": true,
  "remediation_type": null
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Kind-prefixed hierarchical identifier: `"<kind>/<index>"` (e.g., `"path_exists/0"`, `"command_available/0"`); index resets per kind |
| `kind` | string | One of the v1 supported kinds (see below) |
| `target` | string | The subject of the assertion |
| `state` | string | `"PASS"` or `"FAIL"` |
| `expected` | any | Expected value as parsed from the contract |
| `observed` | any | Observed value at run time |
| `remediation_type` | string or null | Semantic hint for how to resolve a FAIL; `null` when state is PASS |

### V1 supported assertion kinds

| Kind | Target meaning | Expected value |
|---|---|---|
| `path_exists` | Repo-relative path | `true` / `false` |
| `path_type` | Repo-relative path | `"file"` / `"directory"` |
| `command_available` | Executable name | `true` / `false` |

Any assertion kind outside this list in acceptance mode causes exit `30` (contract
error). The script does not claim general YAML support; only the v1 narrow subset is
evaluated.

---

## `gaps` module

Records items that require attention: assertion failures, contract errors,
or missing optional components found in discovery mode.

```json
{
  "id": "path_exists/0",
  "kind": "path_exists",
  "target": "pyproject.toml",
  "state": "UNRESOLVED",
  "detail": "path_exists: expected True, got False",
  "remediation_type": "MISSING"
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Kind-prefixed hierarchical identifier: `"<kind>/<index>"` (e.g., `"path_exists/0"`, `"CONTRACT_MISSING/0"`); index resets per kind |
| `kind` | string | Mirrors the assertion `kind` for assertion failures; or a contract-level kind (see below) |
| `target` | string | The subject that has the gap |
| `state` | string | Always `"UNRESOLVED"` in v1 |
| `detail` | string | Human-readable explanation |
| `remediation_type` | string or null | Semantic hint for how to resolve the gap (see below) |

### Assertion-failure gap kinds

Gap `kind` mirrors the assertion `kind` (e.g., `"path_exists"`, `"path_type"`, `"command_available"`).

### Contract-level gap kinds

| Kind | Meaning |
|---|---|
| `CONTRACT_MISSING` | Contract file not found or not readable |
| `CONTRACT_MALFORMED` | Fenced block absent or block parse failed |
| `CONTRACT_ERROR` | Evaluation error (e.g., unknown assertion kind) |

### Remediation types

| Value | Meaning | When used |
|---|---|---|
| `MISSING` | Required thing does not exist | `path_exists` expected true / `path_type` target absent / `command_available` expected true / contract file not found |
| `MISMATCH` | Thing exists but has wrong type or value | `path_type` target exists with wrong type |
| `DEPRECATED` | Thing exists but should be removed | `path_exists` expected false / `command_available` expected false |
| `MALFORMED` | Thing exists but is structurally invalid | Contract block absent, malformed block, or unsupported assertion kind |

---

## Example: discovery-mode manifest

```json
{
  "meta": {
    "schema_version": "1",
    "run_mode": "discovery",
    "timestamp_utc": "2026-04-22T06:00:00Z",
    "script_version": "1.0.0"
  },
  "fingerprint": {
    "repo_root_marker": ".git",
    "python_version": "3.11.9",
    "platform": "darwin"
  },
  "facts": {
    "repo_present": true,
    "git_available": true,
    "current_branch": "feat/andrew/sense-env-scaffold",
    "workspace_clean": false,
    "key_paths": {
      "README.md": true,
      ".codex/": true,
      "pyproject.toml": false,
      "tests/": false,
      "scripts/": true,
      ".codex/copilot-instructions.md": true
    }
  },
  "assertions": [],
  "gaps": []
}
```

---

## Example: acceptance-mode manifest (one failure)

```json
{
  "meta": {
    "schema_version": "1",
    "run_mode": "acceptance",
    "timestamp_utc": "2026-04-22T06:01:00Z",
    "script_version": "1.0.0"
  },
  "fingerprint": {
    "repo_root_marker": ".git",
    "python_version": "3.11.9",
    "platform": "darwin"
  },
  "facts": {
    "repo_present": true,
    "git_available": true,
    "current_branch": "feat/andrew/sense-env-scaffold",
    "workspace_clean": false,
    "key_paths": {
      "README.md": true,
      ".codex/": true,
      "pyproject.toml": false,
      "tests/": false,
      "scripts/": true,
      ".codex/copilot-instructions.md": true
    }
  },
  "assertions": [
    {
      "id": "path_exists/0",
      "kind": "path_exists",
      "target": "pyproject.toml",
      "state": "FAIL",
      "expected": true,
      "observed": false,
      "remediation_type": "MISSING"
    },
    {
      "id": "command_available/0",
      "kind": "command_available",
      "target": "python3",
      "state": "PASS",
      "expected": true,
      "observed": true,
      "remediation_type": null
    }
  ],
  "gaps": [
    {
      "id": "path_exists/0",
      "kind": "path_exists",
      "target": "pyproject.toml",
      "state": "UNRESOLVED",
      "detail": "path_exists: expected True, got False",
      "remediation_type": "MISSING"
    }
  ]
}
```

---

## Snapshot filtering and promotion

When `--snapshot` is used, the script writes a second file:
`.codex/env-manifest.snapshot.json`

Snapshot shaping rules in v1 (applied before writing):

| Data category | Treatment in v1 |
|---|---|
| Selected fingerprint fields that are machine-local | Removed (only `repo_root_marker`, `python_version`, `platform` are kept) |
| Facts fields whose keys match secret-related patterns | Removed |
| Absolute local paths inside `key_paths` | Replaced with `null` |
| Usernames in paths | Not specifically scrubbed in v1 |
| Machine-specific identifiers (hostname, UID) | Not broadly guaranteed to be removed in v1 |
| Secret-shaped values (tokens, keys, passwords) | Not inspected by value in v1; only key-pattern matching is applied |
| Branch names | Kept; may expose usernames if the branch follows a `user/topic` naming convention — callers should assess before committing |
| Platform string | Kept |
| Python version | Kept |

The v1 snapshot is only partially sanitized. It should not be treated as a complete
scrub of usernames, host identifiers, or secret-like values based on their content.

The snapshot is written only when the run exits `0`. If the run exits `10`, `20`, or
`30`, no snapshot is written. This is enforced by the script; callers should not
attempt to promote partial or error-state manifests.

Snapshot promotion to a permanent record (for example, committing to the repo) is
a workflow-level human decision outside the script's responsibility.
