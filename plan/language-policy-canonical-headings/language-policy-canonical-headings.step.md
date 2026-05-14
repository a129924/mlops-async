# Step Tracker — language-policy-canonical-headings

## Status

- **Topic status**: `review-ready`
- **Cycle**: 1

## Implementation Steps

- [x] Step 1: Create this step tracker file aligned to the plan's implementation steps.
- [x] Step 2: Update `.github/copilot-instructions.md` — keep Traditional Chinese as default for normal prose; explicitly allow strictly enumerated canonical English headings / terms to remain in English.
- [x] Step 3: Encode in `.github/copilot-instructions.md` that uncertain heading-like cases default to preserving canonical English, scoped only to candidate fixed headings / labels / workflow names / canonical terms, not general prose.
- [x] Step 4: Update `.github/CONTRIBUTING.md` so its contributor-facing wording does not contradict the same policy boundaries.
- [x] Step 5: Inspect whether another governance file directly states the same language policy. Result: **no additional governance file found**; no further action required through this plan.
- [x] Step 6: Re-read resulting wording to confirm: normal prose defaults to Traditional Chinese; strict enumeration bounds the English-heading exception; commit / PR / Issue title policy is untouched; no wording implies broad bilingual freedom.

## Acceptance Evidence

- `.github/copilot-instructions.md` `Language Requirement` section now distinguishes normal prose (繁體中文 default) from strictly enumerated canonical English headings / terms.
- Uncertain-case default rule encoded explicitly and scoped to heading-like items only.
- `.github/CONTRIBUTING.md` `Language policy` subsection added under `Git conventions` that mirrors and does not contradict `.github/copilot-instructions.md`.
- No other governance file found that directly states this policy; no plan repair needed.
