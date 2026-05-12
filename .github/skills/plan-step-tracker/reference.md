# Reference — plan-step-tracker

## Canonical file and marker rules

- The tracked file path is `plan/<topic>/<topic>.step.md`.
- The Python CLI parses only lines that match the regex `^\- \[(.)\](.*)`.
- Marker interpretation is fixed for accepted checkbox markers:
  - `[X]` = done
  - `[ ]` = pending
  - `[x]` = pending and warning-worthy
- Any other single character inside the brackets still matches the parser, emits a warning, and is treated as pending.
- This skill is read-only; it reports declared checkbox state and does not repair formatting.

## Python CLI contract

Use the local script from the repository root:

```bash
python .github/skills/plan-step-tracker/scripts/step_tracker.py <operation> <topic>
```

Supported operations:

| Operation | Result | Exit code |
| --- | --- | --- |
| `read_all` | prints all parsed checkbox lines | `0` |
| `read_not_run` | prints pending lines, including `[x]` | `0` |
| `read_success` | prints completed `[X]` lines | `0` |
| `check_all_succeeded` | prints success summary if all done; otherwise blocked summary plus pending lines | `0` when complete, `1` when pending |
| `check_impl_steps_succeeded` | reads only `## Implementation Steps`; prints implementation-only success summary if all done there, otherwise blocked summary plus pending implementation lines | `0` when all implementation steps are complete, `1` when any implementation step is pending |

Error contract:

- Missing file prints `錯誤：找不到檔案：plan/<topic>/<topic>.step.md` to stderr and returns exit code `1`.
- Lowercase `[x]` prints `警告：在第 N 行發現小寫 [x]；將視為待完成` to stderr.
- `check_impl_steps_succeeded` ignores later headings such as `## Workflow Stages` and evaluates only checkbox lines inside `## Implementation Steps`.

## Grep fallback guidance

Use grep only when the Python CLI cannot run.

Output format note:

- grep preserves the original leading `- ` prefix from the `.step.md` line
- the Python CLI normalizes matching lines to `[X] foo` / `[ ] foo` / `[x] foo`
- if a caller needs grep output to resemble the CLI contract, normalize it explicitly with `sed 's/^- //'`
- for implementation-only gates, grep must first isolate the `## Implementation Steps` section before counting or printing checkboxes

```bash
# all parsed checkbox lines
grep '^\- \[.\]' plan/<topic>/<topic>.step.md

# pending lines with a broad fallback that catches both [ ] and [x]
grep '^\- \[[ x]\]' plan/<topic>/<topic>.step.md

# completed lines
grep '^\- \[X\]' plan/<topic>/<topic>.step.md

# normalized fallback output that more closely matches the Python CLI format
grep '^\- \[.\]' plan/<topic>/<topic>.step.md | sed 's/^- //'
```

Blocking fallback example:

```bash
PENDING=$(grep -c '^\- \[[ x]\]' plan/<topic>/<topic>.step.md)
if [ "$PENDING" -eq 0 ]; then
  echo '成功：全部步驟都已完成'
  exit 0
else
  echo "阻擋：仍有 $PENDING 個步驟待完成"
  grep '^\- \[[ x]\]' plan/<topic>/<topic>.step.md
  exit 1
fi
```

Implementation-only fallback sketch:

```bash
awk '
  /^## Implementation Steps$/ { in_impl=1; next }
  in_impl && /^## / { exit }
  in_impl { print }
' plan/<topic>/<topic>.step.md | grep '^\- \[[ x]\]'
```

Fallback limitation:

- grep can approximate pending detection for `[x]`, but it does not emit the Python CLI warning automatically
- when using grep fallback, call out lowercase `[x]` manually if present
- section-scoped fallback is only an approximation of `check_impl_steps_succeeded`; the Python CLI remains the canonical gate
