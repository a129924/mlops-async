from __future__ import annotations

import mlops_async.core.headers as headers_mod
from mlops_async.core.http_request import Headers


def test_merge_headers_canonicalizes_lowercase_and_keeps_last_value_case_insensitively() -> None:
    headers = headers_mod.merge_headers(
        {"X-Trace": "first"},
        {"x-trace": "second"},
        {"X-TRACE": "final"},
    )

    assert headers == {"x-trace": "final"}


def test_json_request_headers_applies_json_defaults_for_json_body() -> None:
    headers = headers_mod.json_request_headers(
        {"X-Default": "default"},
        {"X-Default": "caller", "X-Trace": "trace"},
        json_body={"name": "demo"},
    )

    assert headers == {
        "accept": "application/json",
        "content-type": "application/json",
        "x-default": "caller",
        "x-trace": "trace",
    }


def test_json_request_headers_preserves_explicit_overrides() -> None:
    headers = headers_mod.json_request_headers(
        {"Accept": "application/custom+json"},
        {"Content-Type": "application/merge-patch+json"},
        json_body={"name": "demo"},
    )

    assert headers == {
        "accept": "application/custom+json",
        "content-type": "application/merge-patch+json",
    }


def test_json_request_headers_omits_content_type_without_json_body() -> None:
    headers = headers_mod.json_request_headers({"X-Trace": "trace"})

    assert headers == {
        "accept": "application/json",
        "x-trace": "trace",
    }


def test_token_request_headers_emits_token_family_defaults_and_allows_overrides() -> None:
    headers = headers_mod.token_request_headers(
        {"Content-Type": "application/custom-token"},
        {"X-Trace": "trace"},
    )

    assert headers == {
        "accept": "application/json",
        "content-type": "application/custom-token",
        "x-trace": "trace",
    }


def test_request_headers_value_object_has_no_case_variant_duplicates() -> None:
    headers = Headers.create(
        (("X-Request-ID", "first"), ("x-request-id", "final"), ("Accept", "application/json"))
    )

    assert headers.as_dict() == {
        "x-request-id": "final",
        "accept": "application/json",
    }
