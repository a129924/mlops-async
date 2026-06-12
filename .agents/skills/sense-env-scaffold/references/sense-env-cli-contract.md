# Sense-Env CLI Contract

Defines the complete CLI surface of `.codex/skills/sense-env-scaffold/scripts/sense_env.py` v1.
The canonical source lives under `skills/sense-env-scaffold/...`; any
`.codex/skills/sense-env-scaffold/...` path is a platform projection.

---

## Synopsis

```
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py [OPTIONS]
```

Must be invoked from within the repository (any subdirectory). The script
resolves the repository root upward from the current working directory.

---

## Flags

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--mode` | string | yes | — | Run mode: `discovery` or `acceptance` |
| `--contract-file` | path | no | implicit lookup | Path to contract document containing `yaml [sensing-assertions]` block |
| `--output` | path | no | `<repo_root>/.codex/env-manifest.json` | Output path for the live manifest |
| `--snapshot` | boolean flag | no | off | When present, also write a filtered snapshot to the fixed snapshot path |

### `--mode`

| Value | Behaviour |
|---|---|
| `discovery` | Collect environment facts. Tolerant: missing optional tools produce `null` values, not errors. Always exits `0` when sensing completes, regardless of optional-tool availability. |
| `acceptance` | Load contract, extract assertions, evaluate each one. Fails hard when one or more assertions do not pass. |

### `--contract-file`

- Accepted in acceptance mode only.
- If absolute: used as-is.
- If relative: resolved against `repo_root`.
- If omitted in acceptance mode: implicit lookup proceeds (see Contract lookup order).
- If the file is not readable: exit `30`.

### `--output`

- Overrides the live manifest destination only.
- If relative: resolved against `repo_root`.
- Parent directory is created unconditionally (`parents=True, exist_ok=True`).
- If parent-directory creation or file write fails: exit `10`.

### `--snapshot`

- Boolean flag (no value argument).
- Does not replace live-manifest writing; the live manifest is always written first.
- When enabled and the run would exit `0`: writes filtered snapshot to the fixed path.
- When the run exits `10`, `20`, or `30`: snapshot is NOT written.
- If live-manifest write succeeds but snapshot write fails: keep the live manifest
  and exit `10`.
- v1 does not support a custom snapshot output path.

---

## Repo-root detection

The script searches upward from the current working directory for a `.git` marker.

- A `.git` **directory** is a valid repo-root marker.
- A `.git` **file** (worktree case) is also a valid repo-root marker.
- The first directory containing either form is the `repo_root`.
- If no marker is found after reaching the filesystem root: `repo_root` falls back
  to the current working directory.

All relative paths in the script are resolved against `repo_root`.

---

## Contract lookup order

In acceptance mode, the contract file is resolved in this priority order:

1. `--contract-file` (explicit, if provided)
2. `<repo_root>/retrofit-plan.md`
3. `<repo_root>/blueprint.md`

If none of the above is readable: exit `30`.

---

## Fenced block extraction

The script extracts assertions from a fenced block with this exact tag:

````
```yaml [sensing-assertions]
```
````

- A regex-based extractor is used.
- Minor surrounding noise (BOM, extra blank lines) is tolerated; Windows `\r\n` line
  endings inside the fenced block are normalized, but general `\r\n` tolerance across
  the whole file is not guaranteed in v1.
- In acceptance mode, absence of this block in the contract file is a contract error:
  exit `30`.
- The parser supports only the v1 narrow YAML-like subset (see Assertion format below).

---

## Assertion format (v1 narrow subset)

The fenced block must contain a top-level sequence of assertion records.

```yaml
- kind: path_exists
  target: .codex/skills/sense-env-scaffold/scripts/sense_env.py
  expected: "true"

- kind: path_type
  target: .<platform>
  expected: directory

- kind: command_available
  target: python3
  expected: "true"
```

Supported constraints:

- Top-level sequence only (list of mappings)
- Scalar keys and scalar values only
- No nested mappings
- No anchors
- No multiline strings
- No flow-style collections (`{...}` or `[...]`)

The parser does **not** claim general YAML compatibility. Input that falls outside
this narrow subset produces a contract error: exit `30`.

---

## Supported assertion kinds (v1)

| Kind | Target | Expected values |
|---|---|---|
| `path_exists` | Repo-relative path string | `"true"` / `"false"` |
| `path_type` | Repo-relative path string | `"file"` / `"directory"` |
| `command_available` | Executable name | `"true"` / `"false"` |

Any other `kind` value in acceptance mode causes exit `30` (contract error). The
script treats unknown kinds as a contract problem — it does not silently skip or
record them. Add new kinds by extending the script in a separate planning topic.

---

## Output paths

| Path | Description |
|---|---|
| `<repo_root>/.codex/env-manifest.json` | Default live manifest path |
| `<repo_root>/.codex/env-manifest.snapshot.json` | Fixed snapshot path (v1, not overridable) |

When `--output` is provided, it overrides the live manifest path only. The snapshot
path is always fixed.

`.codex/` is created automatically if it does not exist and the write target is
under `<repo_root>/.codex/`.

---

## Exit codes

| Code | Meaning | JSON emitted |
|---|---|---|
| `0` | Success; manifest written | Yes, to output path |
| `10` | Operational error (I/O failure writing manifest) | Attempted to output path; falls back to stderr |
| `20` | Acceptance failure; one or more assertions evaluated as FAIL | Yes, to output path |
| `30` | Contract error: file not found, not readable, block absent, block malformed, or unknown assertion kind | Yes (attempted); falls back to stderr on write failure |

All exit paths attempt to emit a JSON manifest to the output path. On I/O failure
(exit `10`), or if the output write fails during a contract-error path, the manifest
is emitted to stderr as a fallback.

---

## Invocation examples

### Discovery (default output path)

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode discovery
# Writes: .codex/env-manifest.json
# Exit:   0 (always, unless I/O fails)
```

### Discovery with custom output path

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode discovery --output /tmp/my-manifest.json
# Writes: /tmp/my-manifest.json
# Exit:   0
```

### Discovery with snapshot export

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode discovery --snapshot
# Writes: .codex/env-manifest.json
# Writes: .codex/env-manifest.snapshot.json  (only when exit is 0)
# Exit:   0
```

### Acceptance with explicit contract file

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode acceptance --contract-file plan/my-blueprint.md
# Loads assertions from plan/my-blueprint.md
# Exit:   0 (all assertions pass) / 20 (any FAIL) / 30 (contract error)
```

### Acceptance with implicit contract lookup

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode acceptance
# Looks for: retrofit-plan.md, then blueprint.md in repo root
# Exit:   0 / 20 / 30
```

### Acceptance with snapshot export

```bash
python3 .codex/skills/sense-env-scaffold/scripts/sense_env.py --mode acceptance --contract-file blueprint.md --snapshot
# Snapshot is written only when exit would be 0
```

---

## Error scenarios

| Scenario | Exit |
|---|---|
| `--mode acceptance` with no contract file anywhere | `30` |
| Contract file found but no `yaml [sensing-assertions]` block | `30` |
| Fenced block present but content is outside the narrow supported subset | `30` |
| `.codex/` parent-dir creation fails | `10` |
| Manifest file write fails | `10` |
| Snapshot write fails after live manifest write succeeds | `10` (live manifest kept) |
| Required assertion fails | `20` |
| Optional tool missing in discovery mode | `0` (fact recorded as `null`) |
