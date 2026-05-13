from dataclasses import FrozenInstanceError

import pytest

from mlops_async.exceptions import CustomException, HttpErrorContext


def test_http_error_context_is_frozen() -> None:
    context = HttpErrorContext(status_code=500, method="GET", url="https://example.com/base/items")

    with pytest.raises(FrozenInstanceError):
        context.url = "https://example.com/changed"  # type: ignore[misc]


def test_body_snippet_uses_first_512_bytes_with_utf8_replace() -> None:
    context = HttpErrorContext(
        status_code=500,
        method="POST",
        url="https://example.com/base/items",
        body=bytes([0xFF]) * 600,
    )

    assert context.body_snippet == "�" * 512


def test_custom_exception_forwards_context_fields() -> None:
    context = HttpErrorContext(
        status_code=418,
        method="PATCH",
        url="https://example.com/base/items/123/?verbose=true",
        body=b"problem details",
        request_id="req-42",
    )

    error = CustomException(context)

    assert error.context is context
    assert error.status_code == 418
    assert error.method == "PATCH"
    assert error.url == "https://example.com/base/items/123/?verbose=true"
    assert error.body_snippet == "problem details"
    assert error.request_id == "req-42"


def test_custom_exception_message_uses_normalized_path_and_request_id() -> None:
    error = CustomException(
        HttpErrorContext(
            status_code=404,
            method="GET",
            url="https://example.com/base/v1/items/?page=1",
            body=b"not found",
            request_id="req-404",
        )
    )

    assert str(error) == "GET /base/v1/items/ -> HTTP 404 [request_id=req-404]"


def test_custom_exception_message_omits_query_string_and_request_id_suffix_when_absent() -> None:
    error = CustomException(
        HttpErrorContext(
            status_code=502,
            method="DELETE",
            url="https://example.com/base/items?debug=true",
            body=b"bad gateway",
        )
    )

    assert str(error) == "DELETE /base/items -> HTTP 502"
