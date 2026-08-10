# Model Repository Projects Champion Specification

## Acceptance Criteria

1. Projects family exposes exactly the frozen `ProjectsClient` list/get/exact-lookup/champion-metadata surface and semantic Project/Champion VOs, with no root or `clients` shortcut.
2. list/get honour the frozen GET request contracts; name lookup is sequential, exact-name-only, and invariant checked.
3. `ChampionModel.score_code_type` is `str | None`: missing or JSON-null `scoreCodeType` materializes `None`; only a JSON string materializes a value, and a non-string/non-null value raises `ProjectsResponseError`. `ChampionModel.files` exposes caller-observable `ChampionFile` references; missing raw `files` materializes an empty tuple, and no Projects content aggregate/result type exists.
4. Projects has no peer-family import, construction, injection, type-only dependency or hidden orchestration. The caller alone may choose later Models content calls and all concurrent/failure/result policy.
5. Feature-stage metadata remains unchanged; release metadata is a separately authorized gate.
6. Post-review Implementer modifies `tach.toml` only with the locked Projects declarations for existing core/transport/root-exceptions boundaries; no `mlops_async.clients.models` edge exists.
7. `tests/unit/clients/projects/__init__.py` is the sole empty, family-local test package marker. It prevents Projects and Models sibling `test_client.py` collection from sharing a module identity, without changing any public/runtime contract or peer-family rule.

## Behavioral Scenarios

### Scenario 1: Exact paged project search

- **Given**: pages with fixed count and matching start/limit metadata.
- **When**: `get_project_by_name` encounters a summary exactly equal to the name input.
- **Then**: it returns that summary and makes no further request.

### Scenario 2: Champion metadata and file references

- **Given**: a Champion response containing `id`, `name`, optional `scoreCodeType`, and optional `files`.
- **When**: `get_champion` is called.
- **Then**: a missing or JSON-null `scoreCodeType` returns `score_code_type is None`; a string returns that value; a non-string/non-null value raises `ProjectsResponseError`. Valid responses expose a tuple of caller-observable `ChampionFile` references; missing `files` returns an empty tuple.

### Scenario 3: Caller-owned cross-family orchestration

- **Given**: a caller has a `ChampionModel` returned by Projects.
- **When**: it chooses to fetch file content.
- **Then**: the caller chooses whether to call `ModelsClient.get_model_content(champion.id, file.id)`, and owns gather, failure/cancellation, lifecycle and result aggregation decisions; Projects has no API or private hook for that work.

### Scenario 4: Family-local test collection isolation

- **Given**: Models and Projects each contain a sibling `test_client.py`, while `tests` and `tests/unit` are already packages.
- **When**: pytest collects the full `tests/` tree after the empty `tests/unit/clients/projects/__init__.py` marker is present.
- **Then**: Projects receives a distinct family-local test module identity and collection completes without an import-file-mismatch error; no Models or parent-package file is added.

## Error / Edge Cases

- Count/start/limit/items-length mismatch raises `ProjectsResponseError`; only exhaust returns `None`.
- Missing `id`/`name`, a non-string/non-null `scoreCodeType`, or malformed present `files` structure raises `ProjectsResponseError`; missing or JSON-null `scoreCodeType` does not.
- Empty present files and missing raw files both expose an empty `ChampionModel.files` tuple; each valid parsed file reference remains observable.
- Later lookup request errors propagate unchanged and are never converted to `None`.
- Any requested Tach edge beyond the locked core/transport/root-exceptions route is a stop-and-re-plan condition, not an exception/public-API workaround.

## Test Matrix

- `tests/unit/clients/projects/__init__.py`: empty collection-isolation marker; the collection test case is `uv run pytest tests/ --collect-only`, which must discover both sibling `test_client.py` modules without an import-file-mismatch error.
- `tests/unit/clients/projects/test_client.py`: one-page request construction, dynamic encoding, input validation, sequential exact lookup, all page invariants, exhaustion, later request error, champion request/parsing including `scoreCodeType` missing/null/non-string cases, constructor/public-signature isolation and no peer-family collaborator.
- `tests/unit/clients/projects/test_value_objects.py`: frozen/slotted Project/Champion VOs, `ChampionModel.score_code_type: str | None`, `ChampionModel.files` tuple, `ChampionFile` id/name references, parser failures, and unknown-field exclusion.
- No cross-family content orchestration, content mapping or Models fake test target belongs in this topic.
