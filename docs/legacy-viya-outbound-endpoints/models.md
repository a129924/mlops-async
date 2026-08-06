# Models handoff

## Legacy observation

- Legacy 觀察到 `GET /modelRepository/models` 與
  `GET /modelRepository/models/{model_id}`，使用 Bearer 與 model JSON Accept header。

## Upstream/evidence

- `docs/api-endpoints/swagger-spec/upstream/modelRepository-openapi.yml` 是 upstream
  source；repo-local mapping 為 `docs/api-endpoints/swagger-spec/models-spec.yaml`。
- evidence matrix 的 `models_request_gate` 是 `sasctl-direct` /
  `upstream-aligned`，可作 request implementation-truth，不是 runtime 或 response proof。

## Current repo evidence

- `tests/unit/request_contract/models_request_gate/` 已有 list/get semantic request gates。
- 目前沒有 production models endpoint client。

## Difference

- legacy observation 與 request shape 已對齊，但 response model、error translation、
  pagination 與 session lifecycle 都未凍結。

## Disposition

- 優先的 read-only MVP candidate；list/get 可作同一 family 的規劃單位。

## Human decision required

- 核准 response/error contract 的資料來源、pagination 行為與公開 client surface 後才實作。

## Target mapping
