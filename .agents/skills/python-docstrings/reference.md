# Reference Overview

This folder provides comprehensive guidance on writing clear, contract-first docstrings using Google Style format. The reference is split into focused topic files to keep each file maintainable and portable.

## Reference Files

| File | Role |
|------|------|
| **google-style-template.md** | Google Style structure and format: one-liner, description, Args, Returns, Raises, Examples, Yields. Includes format examples and section guidelines. |
| **semantic-intent.md** | How to derive semantic intent from explicit code-adjacent signals. Includes fallback to contract-only wording when intent is not explicit. Contains good/bad examples showing when to document "why" and when to stay contract-focused. |
| **error-semantics.md** | Traditional `Raises:` (exception-based) vs business-return patterns (Result[T,E], Union[Success, Failure]). Explains how to document error cases for both patterns without prescribing which pattern to use. |
| **dataclass-patterns.md** | Field-level documentation for structured data: semantic role, optional/required status, domain constraints. Shows the contract-vs-validation boundary and when to document field intent. |

## When to Use Each File

- **Starting with Google Style?** → Read **google-style-template.md** first
- **Unsure whether to document "why"?** → **semantic-intent.md** clarifies when to document semantic intent vs stay contract-focused
- **Handling errors?** → **error-semantics.md** covers both exception and Result patterns
- **Documenting dataclass fields?** → **dataclass-patterns.md** shows field-level contracts and domain semantics

## Quick Navigation

1. Review the **SKILL.md** Purpose and Process sections for workflow
2. Check SKILL.md Examples for quick positive/negative patterns
3. Dive into specific reference files for deeper context and edge cases
4. Use **examples.md** for detailed representative scenarios including anti-patterns
