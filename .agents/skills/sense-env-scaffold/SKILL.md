---
name: sense-env-scaffold
description: Run the sense_env.py scaffold to discover or assert facts about the repository environment. Use this when you need a structured JSON snapshot of the current environment state, or when you need to evaluate a contract's sensing assertions.
complexity: medium
risk_profile:
  - external_tooling
use_when:
  - "you need a structured JSON record of environment facts before beginning implementation work"
  - "you need to verify that the repository satisfies a set of `sensing-assertions` defined in a `blueprint.md` or `retrofit-plan.md`"
  - "you want a portable, secret-free snapshot of the current environment for handoff or archival purposes"
do_not_use_when:
  - "the task only needs a single shell command such as `python --version` or `git status`"
  - "you need deep static analysis, linting, or architecture commentary"
  - "you need to install dependencies, create virtual environments, or start services"
  - "the repository does not have `.github/skills/sense-env-scaffold/scripts/sense_env.py` present"
inputs:
  - "the run mode: `discovery` (fact collection) or `acceptance` (contract assertion)"
  - "optionally, a contract file path containing a `yaml [sensing-assertions]` fenced block"
  - "optionally, a custom output path for the live manifest"
  - "whether a snapshot export is required (`--snapshot` flag)"
outputs:
  - "`.github/env-manifest.json` live manifest with five top-level modules: meta, fingerprint, facts, assertions, gaps"
  - "`.github/env-manifest.snapshot.json` filtered secret-free snapshot when `--snapshot` is used and the run exits `0`"
  - "non-zero exit code and a JSON manifest describing the failure when errors occur"
---

# Purpose
Invoke `.github/skills/sense-env-scaffold/scripts/sense_env.py` to produce a structured, machine-readable manifest of
the repository environment, or to evaluate sensing assertions defined in a contract
document.
The canonical source lives under `skills/sense-env-scaffold/...`; any
`.codex/skills/sense-env-scaffold/...` path is a platform projection of that
canonical source.

# Trigger / When to use
Use this skill when:
- you need a structured JSON record of environment facts (Python version, Git state,
  key file presence) before beginning implementation work
- you need to verify that the repository satisfies a set of `sensing-assertions` defined
  in a `blueprint.md` or `retrofit-plan.md`
- you want a portable, secret-free snapshot of the current environment for handoff or
  archival purposes

Do not use this skill when:
- the task only needs a single shell command such as `python --version` or `git status`
- you need deep static analysis, linting, or architecture commentary
- you need to install dependencies, create virtual environments, or start services
- the repository does not have `.github/skills/sense-env-scaffold/scripts/sense_env.py` present

# Inputs
- the run mode: `discovery` (fact collection) or `acceptance` (contract assertion)
- optionally, a contract file path containing a `yaml [sensing-assertions]` fenced block
- optionally, a custom output path for the live manifest
- whether a snapshot export is required (`--snapshot` flag)

# Process
1. Confirm `.github/skills/sense-env-scaffold/scripts/sense_env.py` is present in the skill folder.
2. Choose the mode:
   - `discovery` for a harmless fact-collection run; no contract required
   - `acceptance` to evaluate assertions from a contract file
3. Construct the command using the locked CLI contract (see `references/sense-env-cli-contract.md`).
4. Run the command from the repository working directory.
5. Read the exit code:
   - `0` — success; manifest written
   - `10` — operational error (I/O failure); check the JSON for details
   - `20` — acceptance failure; assertions failed; read `gaps` in the manifest
   - `30` — contract error; contract file missing or fenced block absent
6. If the run succeeds and a snapshot is needed, re-run with `--snapshot` or confirm
   it was included in the original invocation.
7. Interpret the manifest structure using `references/env-manifest-schema.md`.

# Examples
- **Positive**: Run `python3 .github/skills/sense-env-scaffold/scripts/sense_env.py --mode discovery` to collect environment
  facts before a retrofit; read the resulting `.github/env-manifest.json` to understand
  what is present.
- **Negative**: Run `python3 .github/skills/sense-env-scaffold/scripts/sense_env.py --mode acceptance` without a contract
  file and expect it to succeed — acceptance mode always requires a readable contract
  with a `yaml [sensing-assertions]` block; exit `30` is returned when none is found.

# Outputs
- `.github/env-manifest.json` — live manifest with five top-level modules:
  `meta`, `fingerprint`, `facts`, `assertions`, `gaps`
- `.github/env-manifest.snapshot.json` — filtered, secret-free snapshot (when
  `--snapshot` is used and the run exits `0`)
- non-zero exit code and a JSON manifest describing the failure when errors occur

# Boundaries
- Do not modify `.github/skills/sense-env-scaffold/scripts/sense_env.py` or its local
  runtime package as part of invoking this skill; treat them as fixed prototype tooling.
- If related documentation elsewhere uses `.<platform>` as an abstract compatibility
  label, do not copy it into runnable CLI paths; this scaffold's executable defaults
  remain `.github/env-manifest.json` and `.github/env-manifest.snapshot.json` unless
  `--output` overrides them.
- Do not interpret exit `20` as a fatal environment error; it means assertions failed
  and the `gaps` section describes what is missing.
- Do not promote a snapshot unless the run exited `0`; the script enforces this but
  callers should also respect it.
- Do not broaden the assertion kinds beyond the v1 supported subset
  (`path_exists`, `path_type`, `command_available`) without a separate planning topic.
- Do not claim this prototype represents a stable repository-wide tool policy.

# Validation

## Required Checks
- PASS: `.github/skills/sense-env-scaffold/scripts/sense_env.py` is present before any invocation
- PASS for discovery mode: no contract file required; proceed directly
- BLOCKED for acceptance mode: contract file must exist and contain a `yaml [sensing-assertions]` block; if absent, exit `30` is expected — do not retry without a valid contract

## On Soft Fail
- exit `20` is a soft fail, not a fatal error; acceptance assertions failed; read `gaps` and report what must change
- exit `10` is an operational error; read the JSON manifest for I/O failure details before retrying
- do not promote or share a snapshot unless the run exited `0`

# Failure Handling

## Missing Context
- BLOCKED — if `sense_env.py` is not present in the skill folder, stop and report the missing file before any invocation attempt

## Ambiguous Requirement
- if the run mode is not specified, default to `discovery` rather than guessing; do not invoke `acceptance` without explicit intent to evaluate assertions
- if the contract file path is provided but the file does not contain a `yaml [sensing-assertions]` block, report exit `30` as expected behavior rather than an error

## Execution Limitation
- if exit code `10` (operational error) is returned, read the manifest for I/O details and report them; do not retry without understanding the root cause
- if exit code `20` (assertion failure) is returned, report all `gaps` from the manifest; do not reinterpret the result as a pass
- do not broaden assertion kinds or modify `sense_env.py` as part of invoking this skill

# Local references
- `references/env-manifest-schema.md`: stable top-level manifest schema, module
  definitions, gap and assertion record shapes, and snapshot filtering rules
- `references/sense-env-cli-contract.md`: CLI synopsis, flag semantics, mode
  semantics, exit-code table, path-resolution rules, and invocation examples
- `scripts/sense_env.py`: thin CLI entrypoint for discovery and acceptance sensing runs
- `scripts/sense_env_runtime/`: local internal package that holds the manifest models,
  contract parsing, assertion evaluation, snapshot shaping, and run-mode logic used by
  the CLI entrypoint
