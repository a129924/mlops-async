from __future__ import annotations

import mlops_async.core.headers as headers_mod


def test_merge_headers_preserves_last_original_casing_case_insensitively() -> None:
    headers = headers_mod.merge_headers(
        {"X-Trace": "first"},
        {"x-trace": "second"},
        {"X-TRACE": "final"},
    )

    assert headers == {"X-TRACE": "final"}


def test_json_request_headers_applies_json_defaults_for_json_body() -> None:
    headers = headers_mod.json_request_headers(
        {"X-Default": "default"},
        {"X-Default": "caller", "X-Trace": "trace"},
        json_body={"name": "demo"},
    )

    assert headers == {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Default": "caller",
        "X-Trace": "trace",
    }


def test_json_request_headers_preserves_explicit_overrides() -> None:
    headers = headers_mod.json_request_headers(
        {"Accept": "application/custom+json"},
        {"Content-Type": "application/merge-patch+json"},
        json_body={"name": "demo"},
    )

    assert headers == {
        "Accept": "application/custom+json",
        "Content-Type": "application/merge-patch+json",
    }


def test_json_request_headers_omits_content_type_without_json_body() -> None:
    headers = headers_mod.json_request_headers({"X-Trace": "trace"})

    assert headers == {
        "Accept": "application/json",
        "X-Trace": "trace",
    }


def test_token_request_headers_emits_token_family_defaults_and_allows_overrides() -> None:
    headers = headers_mod.token_request_headers(
        {"Content-Type": "application/custom-token"},
        {"X-Trace": "trace"},
    )

    assert headers == {
        "Accept": "application/json",
        "Content-Type": "application/custom-token",
        "X-Trace": "trace",
    }
