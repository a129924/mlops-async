# Request Contract Testing Technical Spec

## Source Requirements

This technical spec implements:

- `analysis/request-contract-testing/requirements.md`

## Objective

把「Fully Intercepted Baseline Capture -> Contract Fixture -> Target Request Test」落成 repo-visible 標準與 topic plan，供後續 implementation topic 使用。

## Allowed File Scope

This phase may create or update only:

- `analysis/request-contract-testing/requirements.md`
- `analysis/request-contract-testing/technical-spec.md`
- `plan/request-contract-testing/request-contract-testing.plan.md`
- `plan/request-contract-testing/request-contract-testing.step.md`
- `plan/agent-handoff-workflow.md`
- `docs/standards/request-contract-testing.md`

This phase must not modify:

- `src/mlops_async/**`
- `tests/**`
- runtime dependency configuration

## Artifact Responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結業務基線：capture gate、auth divergence、stop boundary、可量測 acceptance |
| `technical-spec.md` | 將需求映射成可實作檔案範圍、規則責任與驗證方式 |
| `request-contract-testing.plan.md` | 後續 implementation topic 的執行合約 |
| `request-contract-testing.step.md` | implementation-only completion gate |
| `plan/agent-handoff-workflow.md` | 定義 agent handoff workflow 的跨主題 handoff 合約，防止 analysis 與 plan 在執行交接時語意漂移 |
| `docs/standards/request-contract-testing.md` | normative standard；skills 只引用並執行，不重複定義整份規範 |

## Technical requirements mapping

1. **Gate contract**
   - Define gate pass as `capture -> fixture -> derived request-contract test`.
   - Fail-fast on real-network escape or unregistered requests.

2. **Capture outputs**
   - Persist `full_observed_flow` request-flow snapshot.
   - Persist separate mock-response answer artifact.
   - Keep traceable linkage between two artifacts.

3. **Purpose classification**
   - Require step-level purpose tags (`auth`, `preflight`, `target-api`, optional others).
   - Require ordered flow output.

4. **Comparison policy**
   - Enforce semantic comparison for method/path/required header subset/query semantics/body shape.
   - Explicitly avoid brittle checks: query order, transport-generated headers, host, content-length, connection headers.

5. **Auth divergence policy**
   - Keep captured auth steps in fixture.
   - Allow target equivalence comparison to exclude those auth steps only with explicit `intentionally_changed` record and rationale.
   - Any capture-vs-review baseline conflict must block for human decision.

6. **Stop conditions**
   - Encode first-version stop/escalation list from requirements as normative rule.

## Validation

This phase is documentation and planning only.

Required checks:

1. All six artifacts exist at expected paths.
2. Standard doc includes:
   - interception rule
   - full observed flow requirement
   - split request/answer artifacts
   - auth divergence handling
   - stop conditions
3. Plan file explicitly references analysis inputs.

Suggested commands:

```bash
test -f analysis/request-contract-testing/requirements.md
test -f analysis/request-contract-testing/technical-spec.md
test -f plan/request-contract-testing/request-contract-testing.plan.md
test -f plan/request-contract-testing/request-contract-testing.step.md
test -f plan/agent-handoff-workflow.md
test -f docs/standards/request-contract-testing.md
```

## Stop conditions

Stop and request human review if:

- requested changes need `src/mlops_async/**` or `tests/**` in this phase
- capture-vs-source-review conflict cannot be reconciled without changing baseline semantics
- standard wording drifts into implementation design that belongs to a separate execution topic
