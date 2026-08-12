from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect

from mlops_async.core import request_failure
from mlops_async.core.request_failure import RequestFailure, ResponseFailureMetadata
import pytest


def test_failure_carriers_are_internal_immutable_value_objects() -> None:
    metadata = ResponseFailureMetadata(status_code=503, retry_after="2")
    failure = RequestFailure(kind="response", metadata=metadata)

    assert metadata.status_code == 503
    assert metadata.retry_after == "2"
    assert failure.kind == "response"
    assert failure.metadata is metadata
    with pytest.raises(FrozenInstanceError):
        metadata.status_code = 429
    with pytest.raises(FrozenInstanceError):
        failure.kind = "timeout"


@pytest.mark.parametrize("kind", ("connection", "timeout", "response"))
def test_request_failure_accepts_only_the_locked_failure_kinds(kind: str) -> None:
    failure = RequestFailure(kind=kind)

    assert failure.kind == kind


def test_request_failure_rejects_unknown_kind_and_keeps_core_transport_agnostic() -> None:
    with pytest.raises(ValueError):
        RequestFailure(kind="dns")

    source = inspect.getsource(request_failure)
    assert "mlops_async.transport" not in source
    assert "import httpx" not in source
