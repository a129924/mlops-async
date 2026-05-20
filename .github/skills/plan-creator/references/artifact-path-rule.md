# Artifact Path Rule

Rules for declaring and maintaining the `Artifact Paths` section in a topic plan.

- Treat `Artifact Paths` as an executable contract, not a summary.
- Name concrete paths such as `.github/skills/<skill-name>/SKILL.md`, not vague phrases such as `docs` or `skill files`.
- Every artifact path must be role-labeled: state who owns the path and what role it plays in the topic.
- If later work appears outside the listed paths, that is a plan-alignment problem, not a harmless detail.
- Do not use broad directory references when individual file paths can be named.

## Correction / delta artifact paths

When a topic involves correction or delta artifacts, apply these additional rules:

- Label parent artifact paths as "current truth after accepted backfill" — not
  "old version", "baseline", or "pre-correction state".
- Label correction artifact paths as "historical truth" — they are the decision
  trail, not the active execution contract.
- Correction closure requires parent sync / backfill to be complete; state this
  explicitly in the plan. Do not declare closure while parent backfill is still
  pending.
- Include a `review-log` artifact path only if reviewer feedback controls routing
  or multi-round rework is required in this topic. If no `review-log` is listed,
  state why (e.g., "routing does not depend on multi-round rework").
- Do not use vague evidence labels such as "merged implementation",
  "backfilled baseline", or broad folder references like `plan/foo/` when
  individual file paths can be named.
