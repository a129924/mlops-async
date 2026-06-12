# Version bump guidance

Use commit semantics to recommend the bump direction.

## Priority

1. breaking change -> major
2. feature -> minor
3. fix/perf/refactor/docs/chore/style/test/build/ci -> patch unless repo policy says otherwise

## Mixed history

If several commit classes exist in one release range, choose the highest required bump.

- breaking + fix -> major
- feat + fix -> minor
- docs + chore -> patch

## Do not infer beyond the evidence

If commit history is too noisy or inconsistent to support a reliable bump, say so and ask for human confirmation instead of pretending the recommendation is certain.
