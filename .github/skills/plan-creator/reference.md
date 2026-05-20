# Plan Creator Reference

Overview of the stable rules that keep topic-plan authoring aligned with the repository workflow. Detailed rules for each topic are split into the `references/` files listed below.

- **Required section meaning**: what each mandatory topic-plan section means and what it must contain. See `references/required-section-meaning.md`.
- **Stable-library rule**: when and how to declare stable-library intent, `## Stable library metadata`, release timing, and VERSION/README decisions. See `references/stable-library-rule.md`.
- **Artifact path rule**: how to declare exact, role-labeled, executable artifact paths instead of vague descriptions. See `references/artifact-path-rule.md`.
- **Role boundary rule**: how to keep planning actor, creator, reviewer, and main-agent responsibilities distinct. See `references/role-boundary-rule.md`.
- **Stop-and-ask triggers**: conditions that require stopping and asking before drafting or continuing. See `references/stop-and-ask-triggers.md`.
- **Template usage rule**: how to use and complete `templates/topic-plan-template.md` without leaving scaffolding in the final plan. See `references/template-usage-rule.md`.
- **Correction / delta lifecycle rule**: when a topic uses correction or delta artifacts, apply these minimum rules:
  - parent artifacts become current truth only after accepted backfill is complete — not before;
  - correction artifacts are historical truth and must not replace parent artifacts, be promoted to active contract, or be deleted at closure;
  - correction closure requires parent sync / backfill to be complete first;
  - a `review-log` or equivalent repo-visible handoff is required only when reviewer feedback controls routing or the topic uses multi-round rework — not universally;
  - any round cap is topic-scoped policy only; it must not imply a repository-wide invariant;
  - detailed correction artifact schema and long examples belong in reference / example surfaces, not in the workflow body;
  - correction lifecycle refresh updates existing workflow / planning surfaces only; creating a standalone correction skill requires a separate topic with explicit justification.
  - For path contract details see `references/artifact-path-rule.md`. For role boundary details see `references/role-boundary-rule.md`.
