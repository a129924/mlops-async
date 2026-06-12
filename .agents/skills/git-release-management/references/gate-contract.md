# Release gate contract

A release or PR is green only when all required signals are present.

## Normal path

The normal path is green only when all of these are true:

- at least one reviewer approval
- CI green
- base tests passing
- strict type checks passing
- lint passing
- relevant documentation updated
- versions synchronized across existing release sources
- clean workspace
- target tag does not already exist

## Emergency path

The emergency path may bypass exactly one normal-path condition:

- missing pre-release reviewer approval

The emergency path still requires all of these:

- CI green
- base tests passing
- strict type checks passing
- lint passing
- relevant documentation updated
- versions synchronized across existing release sources
- clean workspace
- target tag does not already exist
- explicit emergency marker
- recorded human confirmation
- release-note or equivalent anomaly record

## Skill-signature rule

Treat upstream skills as explicit gate signals.

- `python-testing-pytest`: PASS means test expectations are satisfied for release gating
- `python-type-hints-strict`: PASS means strict typing is satisfied for release gating

Do not substitute intuition or partial logs for those outcomes when the workflow already exposes them.

## Failure reporting

When the gate fails, name each failed condition directly and give the shortest useful repair path.
