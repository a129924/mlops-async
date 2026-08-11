from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import ModuleType

import mlops_async.exceptions as root_exceptions
import mlops_async.transport.exceptions as transport_exceptions
import pytest


def _exception_type(module: ModuleType, name: str) -> type[BaseException]:
    exception_type = getattr(module, name, None)
    assert isinstance(exception_type, type)
    return exception_type


def test_root_exceptions_module_exports_only_base_exception() -> None:
    assert root_exceptions.__all__ == ["MlopsAsyncBaseException"]
    assert hasattr(root_exceptions, "MlopsAsyncBaseException")
    assert not hasattr(root_exceptions, "HttpErrorContext")
    assert not hasattr(root_exceptions, "HttpTransportException")
    assert not hasattr(root_exceptions, "HTTPStatusException")
    assert not hasattr(root_exceptions, "InvalidJSONResponseException")


def test_transport_exceptions_module_defines_transport_error_contract() -> None:
    assert transport_exceptions.__all__ == [
        "HttpErrorContext",
        "HttpTransportException",
        "HTTPStatusException",
        "InvalidJSONResponseException",
    ]


def test_transport_exception_hierarchy_flows_through_transport_base() -> None:
    base_exception = _exception_type(root_exceptions, "MlopsAsyncBaseException")
    transport_exception = _exception_type(transport_exceptions, "HttpTransportException")
    http_status_exception = _exception_type(transport_exceptions, "HTTPStatusException")
    invalid_json_exception = _exception_type(transport_exceptions, "InvalidJSONResponseException")

    assert transport_exception.__bases__ == (base_exception,)
    assert http_status_exception.__bases__ == (transport_exception,)
    assert invalid_json_exception.__bases__ == (transport_exception,)


def test_http_error_context_is_frozen_and_truncates_body_snippet() -> None:
    context_type = getattr(transport_exceptions, "HttpErrorContext", None)
    assert context_type is not None

    context = context_type(
        status_code=500,
        method="POST",
        url="https://example.com/base/items",
        body=bytes([0xFF]) * 600,
    )

    with pytest.raises(FrozenInstanceError):
        context.url = "https://example.com/changed"

    assert context.body_snippet == "�" * 512


def test_http_status_exception_exposes_context_and_normalized_message() -> None:
    context_type = getattr(transport_exceptions, "HttpErrorContext", None)
    http_status_exception = _exception_type(transport_exceptions, "HTTPStatusException")
    assert context_type is not None

    context = context_type(
        status_code=418,
        method="PATCH",
        url="https://example.com/base/items/123/?verbose=true",
        body=b"problem details",
        request_id="req-42",
    )

    error = http_status_exception(context)

    assert error.context is context
    assert error.status_code == 418
    assert error.method == "PATCH"
    assert error.url == "https://example.com/base/items/123/?verbose=true"
    assert error.body_snippet == "problem details"
    assert error.request_id == "req-42"
    assert str(error) == "PATCH /base/items/123/ -> HTTP 418 [request_id=req-42]"


def test_invalid_json_response_exception_preserves_context_and_transport_inheritance() -> None:
    context_type = getattr(transport_exceptions, "HttpErrorContext", None)
    invalid_json_exception = _exception_type(transport_exceptions, "InvalidJSONResponseException")
    transport_exception = _exception_type(transport_exceptions, "HttpTransportException")
    assert context_type is not None

    context = context_type(
        status_code=200,
        method="GET",
        url="https://example.com/base/items/?page=1",
        body=b"not-json",
        request_id="req-json",
    )

    error = invalid_json_exception(context)

    assert isinstance(error, transport_exception)
    assert error.context is context
    assert error.status_code == 200
    assert error.method == "GET"
    assert error.url == "https://example.com/base/items/?page=1"
    assert error.body_snippet == "not-json"
    assert error.request_id == "req-json"
    assert str(error) == (
        "GET /base/items/ -> invalid JSON response (HTTP 200) [request_id=req-json]"
    )


def test_invalid_json_response_exception_handles_empty_success_body_mapping() -> None:
    context_type = getattr(transport_exceptions, "HttpErrorContext", None)
    invalid_json_exception = _exception_type(transport_exceptions, "InvalidJSONResponseException")
    assert context_type is not None

    context = context_type(
        status_code=200,
        method="GET",
        url="https://example.com/base/items",
        body=b"",
        request_id="req-empty",
    )

    error = invalid_json_exception(context)

    assert error.status_code == 200
    assert error.body_snippet == ""
    assert error.request_id == "req-empty"
    assert str(error) == (
        "GET /base/items -> invalid JSON response (HTTP 200) [request_id=req-empty]"
    )


def test_transport_failure_metadata_preserves_existing_exception_contract() -> None:
    context = transport_exceptions.HttpErrorContext(
        status_code=503,
        method="GET",
        url="https://example.test/items",
        body=b"busy",
        request_id="req-503",
    )
    error = transport_exceptions.HTTPStatusException(context)

    metadata = error.failure_metadata

    assert metadata.status_code == 503
    assert metadata.retry_after is None
    assert error.context is context
    assert error.status_code == 503
    assert error.method == "GET"
    assert error.url == "https://example.test/items"
    assert error.request_id == "req-503"
    assert str(error) == "GET /items -> HTTP 503 [request_id=req-503]"
