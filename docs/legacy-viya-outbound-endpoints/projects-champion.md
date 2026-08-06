# Projects and champion handoff

## Legacy observation

- Legacy list projects 使用 `GET /modelRepository/projects?limit={limit}`；以名稱 lookup
  是先 list 後篩選，並非獨立 Viya endpoint；champion 為
  `GET /modelRepository/projects/{project_id}/champion`。

## Upstream/evidence

- `modelRepository-openapi.yml` 是 projects/champion source；repo-local mapping 為
  `projects-spec.yaml`。
- matrix 中 projects 與 champion 均為 `sasctl-direct` / `upstream-aligned`；champion
  僅可讀作 generic-path prepared-request capture，不能擴張成 legacy helper truth。

## Current repo evidence

- `tests/unit/request_contract/projects_request_gate/` 有 list/get/champion request gates；
  沒有 production endpoint client。

## Difference

- lookup-by-name 是 target-side orchestration 選擇，不是 endpoint；champion contents
  的多 request 與 `gather()` 編排不屬於 thin wrapper。

## Disposition

- 在 models read-only 穩定後，projects list 與 champion 分別建立 topic，不帶入
  name lookup 或 contents orchestration。

## Human decision required

- 確認 projects 的 pagination/response policy，及 champion 是否需要獨立 public surface。

## Target mapping
