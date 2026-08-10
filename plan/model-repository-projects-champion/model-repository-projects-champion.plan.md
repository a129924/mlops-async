---
topic: model-repository-projects-champion
phase: pr-open
status: pr-open
pr: 65
---

# Model Repository Projects Champion

## Analysis Routing

- Analysis mode: strict with explicit human override.
- Source of truth: `analysis/model-repository-projects-champion/technical-spec.md`.
- Business guardrail: `analysis/model-repository-projects-champion/requirements.md`.
- Override applied: Projects and Models are peer endpoint families; all aggregate download scope is removed.

## Goal / Outcome

建立可獨立審查的 Projects family implementation contract：單頁 projects list、project get、repository-wide sequential exact-name lookup，以及 Champion metadata/file references；不包含任何跨 family content orchestration。

## Scope

- **Test collection correction**: add exactly `tests/unit/clients/projects/__init__.py` as an empty Projects-local package marker so the Projects `test_client.py` does not collide with the existing Models sibling during full pytest collection.

- **In scope**:
  - 五份 topic planning artifacts 的 corrected contract。
  - 未來 Projects family 的 list/get/exact lookup/champion metadata/file-reference implementation 與 family-local tests。
  - post-review `tach.toml` 的 bounded Projects module declarations。
  - peer-family isolation 的 static acceptance evidence。

- **Out of scope**:
  - content download/aggregate API 或 type、content mapping、Models injection/import/type-only dependency，以及任何 cross-family content orchestration。
  - retry、timeout、streaming、background work、server filter、parallel prefetch、mutation、tables、live Viya E2E。
  - 本 planning pass 的 source/test/Tach edits、metadata/release、worktree/PR/publish。

## Locked Decisions

- The sole test-package change is the empty `tests/unit/clients/projects/__init__.py` marker. It isolates Projects collection only and must not alter Models, parent test packages, runtime code, public APIs, or peer-family rules.

- `ProjectsClient` 只公開 `list_projects`、`get_project`、`get_project_by_name`、`get_champion`，constructor 只接收 caller-owned `Requester`。
- Human override（本次唯一新增 contract change）：`ChampionModel.score_code_type: str | None`。Champion response 的 `scoreCodeType` 缺失或 JSON `null` 解析為 `None`；只有字串可成為值，非字串且非 null 值必須拋出 `ProjectsResponseError`。
- `ChampionModel.files` 保留 `ChampionFile` tuple；file `id`/`name` 是 caller-observable references。Projects 不定義內容下載 result type。
- caller 在取得 champion 後，自己選擇是否呼叫 `ModelsClient.get_model_content(champion.id, file.id)`，並自行承擔 gather、failure/cancellation 與 result aggregation。Projects 不參與、包裝或測試這些 choices。
- `ProjectsResponseError` 與既有 transport/JSON error propagation contract 不變；不得新增 facade 或改動 root/transport exception architecture。
- `tach.toml` 已被 human 授權為 post-review bounded implementation path；只可新增 Projects package/client/value-objects declarations，並只使用 core/transport/root-exceptions direct boundaries。不得有 `mlops_async.clients.models` edge。
- feature-stage metadata 是 no-change。separately authorized post-merge minor release 僅在 re-verified baseline `v0.17.0` 時，才可規劃 candidate `v0.18.0`。

## Boundaries / Exclusions

Planning actor 只修改五份 topic artifacts。post-review Implementer 可變更列出的 Projects source/tests 與 `tach.toml`；independent Plan-Reviewer 只提供 verdict；Main Agent/human 擁有 implementation、publish 與 release routing。任何新增 peer import、public shortcut、transport/root-exception change、metadata change 或未列路徑都是停止並 re-plan 的條件。

## Status / Allowed Transitions

- **Current**: `pr-open`。PR #65 仍為 Ready for review；本機 human override 的 `ChampionModel.score_code_type: str | None` contract correction、對應 RED tests、implementation、independent `python-implementation-review` 與 independent `python-code-review` 均已完成。local workflow 為 `commit/push-ready`；topic comment-fix 尚未 commit 或 push，因此尚未成為 PR #65 的遠端內容。
- **Execution model**: 下一步由 Main Agent 對 topic comment-fix 依序 commit、push。GitHub review threads 仍未回覆且未 resolve；本更新不宣稱已處理任何遠端 comment。push 後仍須依 PR feedback routing 與 human review/merge boundary 行事，無 release action。
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Projects test package marker | `tests/unit/clients/projects/__init__.py` | Creator | Empty family-local marker that isolates Projects test module collection; no runtime or peer-family policy change |
| Requirements | `analysis/model-repository-projects-champion/requirements.md` | Plan-Creator | Corrected business/evidence boundary |
| Technical spec | `analysis/model-repository-projects-champion/technical-spec.md` | Plan-Creator | Corrected execution contract and Tach blocker record |
| Topic plan | `plan/model-repository-projects-champion/model-repository-projects-champion.plan.md` | Plan-Creator | Workflow and implementation handoff |
| Topic specification | `plan/model-repository-projects-champion/model-repository-projects-champion.spec.md` | Plan-Creator | Acceptance contract |
| Step tracker | `plan/model-repository-projects-champion/model-repository-projects-champion.step.md` | Plan-Creator | Re-reviewed workflow checkpoints |
| Projects family | `src/mlops_async/clients/projects/__init__.py` | Creator | Future family-local exports |
| Projects client | `src/mlops_async/clients/projects/client.py` | Creator | Future list/get/lookup/champion operations |
| Projects VOs | `src/mlops_async/clients/projects/value_objects.py` | Creator | Future semantic Project/Champion boundary |
| Client tests | `tests/unit/clients/projects/test_client.py` | Creator | Future request/pagination/peer-isolation tests |
| VO tests | `tests/unit/clients/projects/test_value_objects.py` | Creator | Future metadata/file-reference parsing and immutability tests |
| Tach configuration | `tach.toml` | Post-review Implementer | Exact bounded Projects dependency declarations; no peer-family edge |

`README.md`、`VERSION`、`pyproject.toml` 是 feature-stage no-change，且不是 implementation artifact paths。`tach.toml` 只能於 post-review implementation 依 locked exact declaration 修改；任何其他 drift 均為 plan-alignment blocker。

## Stable library metadata

- `README row`: 本 feature topic 無變更。
- `VERSION bump`: 本 feature topic 無 bump。
- `timing`: metadata promotion 延後至 separately authorized post-merge minor-release topic。
- `rationale`: additive endpoint family 不構成 release authorization；release topic 必須重新確認 baseline。
- Release notes: 本 feature topic 無變更。

## Implementation Steps

0. Before authoring or collecting Projects tests, confirm the existing empty `tests/unit/clients/projects/__init__.py` marker remains the sole family-local collection-isolation repair. Do not add a Models marker, alter a parent test package, or modify runtime/public contract code.

下列 steps 屬於 post-review Implementer；舊 aggregate steps 一律不保留為完成狀態。

1. 在 `tests/unit/clients/projects/test_value_objects.py` 與 `tests/unit/clients/projects/test_client.py` 作者 RED tests：VO/parser、request construction、pre-I/O validation、全部 lookup invariants、exact match/exhaustion/later error、Champion metadata/file references、`scoreCodeType` missing/null/non-string parser matrix，以及 Projects 無 peer-family imports/construction/injection/type-only dependency。
2. 建立 `src/mlops_async/clients/projects/value_objects.py` 的 frozen/slotted Project、Champion、`ProjectsResponseError` 與 parser；`ChampionModel.score_code_type` 必須為 `str | None`，只將 missing/null materialize 為 `None`，將 non-string/non-null `scoreCodeType` 翻譯為 `ProjectsResponseError`；保留 `ChampionModel.files`/`ChampionFile` references，不加入 content result object。
3. 建立 `src/mlops_async/clients/projects/client.py` 的 single-page list、encoded get、sequential name lookup 與 champion metadata request/parsing；constructor 只持有 `Requester`。
4. 建立 family-local `src/mlops_async/clients/projects/__init__.py` exports，且不改 Models/core/transport public contract。
5. 在 `tach.toml` 新增 locked exact Projects package/client/value-objects declarations：value objects 只依賴 core/root exceptions，client 只依賴 Projects value objects/core/transport，package 只依賴其 child modules；不得建立 `clients.models` edge 或 architecture escape hatch。
6. 執行 authorized implementation 的 WSL validation，確認僅列出路徑變動、peer-family isolation 及 Tach legal dependencies；若需要另一個 path 或 public error change，停止並 re-plan。

## Validation / Acceptance Checks

- Collection-isolation acceptance: after the marker exists, run full test collection with `uv run pytest tests/ --collect-only`; it must collect the Projects and Models sibling `test_client.py` files without an import-file-mismatch error. This validates test discovery only and does not change public/runtime or peer-family contracts.

- 靜態 planning acceptance：五份 artifacts 不含 cross-family aggregate API/type；public signatures 只含 `Requester`；future test matrix 明確涵蓋 `ChampionModel.score_code_type: str | None` 與 `scoreCodeType` missing/null/non-string，且只保留 family-local metadata/file-reference targets。
- 靜態 boundary acceptance：`tach.toml` 的 post-review exact declaration 與 allowed core/transport/root-exceptions edges 被記錄；不得建立 `clients.models` edge 或提出新 facade。
- Post-review Implementer acceptance：request/path encoding、pre-I/O validation、所有 pagination invariants、exact search/exhaustion/later transport error、Champion `scoreCodeType` missing/null -> `None` 與 non-string/non-null -> `ProjectsResponseError`、metadata/file-reference parsing/immutability、no Models import/injection/type-only dependency，以及 Tach check。
- Latest local validation evidence：Projects targeted suite `46 passed`；full suite `554 passed`，coverage `95.35%`。此 evidence 驗證 local correction；independent implementation review 與 code review 已完成，但不能取代尚未完成的 commit、push 或 GitHub review-thread 回覆／resolve。
- 本 planning pass 僅執行 artifact shape/search 與 `git diff --check`；不執行 tests、lint、type check、Tach check、commit、push 或 PR。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release action is authorized for this feature topic. A separately authorized post-merge minor-release topic must inspect the then-current `VERSION` and `pyproject.toml`; only if baseline remains `v0.17.0` may it plan README/VERSION/pyproject alignment and candidate `v0.18.0`, otherwise it stops for a new version decision.

## Open Questions / Unresolved Items

None. The post-review `tach.toml` declaration form and ownership are locked.

## Workflow state

- current_step: `commit-push-ready`
- next_step: `topic comment-fix commit -> push`
- status: `IN_PROGRESS`
