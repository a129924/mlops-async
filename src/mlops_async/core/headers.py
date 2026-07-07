from __future__ import annotations

from collections.abc import Mapping

from mlops_async.core.types import JSONValue

JSON_REQUEST_ACCEPT = "application/json"
JSON_REQUEST_CONTENT_TYPE = "application/json"
TOKEN_REQUEST_CONTENT_TYPE = "application/x-www-form-urlencoded"


def merge_headers(*mappings: Mapping[str, str] | None) -> dict[str, str]:
    """Merge headers case-insensitively while preserving the last original casing."""
    merged: dict[str, tuple[str, str]] = {}
    for mapping in mappings:
        if mapping is None:
            continue

        for name, value in mapping.items():
            merged[name.lower()] = (name, value)

    return dict(merged.values())


def json_request_headers(
    *mappings: Mapping[str, str] | None,
    json_body: JSONValue | None = None,
) -> dict[str, str]:
    """Return final headers for the JSON-domain request family."""
    headers = merge_headers({"Accept": JSON_REQUEST_ACCEPT}, *mappings)
    if json_body is not None and not any(name.lower() == "content-type" for name in headers):
        headers["Content-Type"] = JSON_REQUEST_CONTENT_TYPE
    return headers


def token_request_headers(*mappings: Mapping[str, str] | None) -> dict[str, str]:
    """Return final headers for the token-endpoint request family."""
    return merge_headers(
        {
            "Accept": JSON_REQUEST_ACCEPT,
            "Content-Type": TOKEN_REQUEST_CONTENT_TYPE,
        },
        *mappings,
    )
