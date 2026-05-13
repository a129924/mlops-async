from dataclasses import FrozenInstanceError

import pytest

from mlops_async.core.request_options import ClientRequestOptions, RequestTimeouts


def test_request_timeouts_accept_positive_values() -> None:
    timeouts = RequestTimeouts(total=30.0, connect=5.0, read=10.0, write=15.0)

    assert timeouts.total == 30.0
    assert timeouts.connect == 5.0
    assert timeouts.read == 10.0
    assert timeouts.write == 15.0


@pytest.mark.parametrize(
    ("kwargs", "field_name"),
    [
        ({"total": 0.0}, "total"),
        ({"connect": -1.0}, "connect"),
        ({"read": 0.0}, "read"),
        ({"write": -0.5}, "write"),
    ],
)
def test_request_timeouts_reject_non_positive_values(
    kwargs: dict[str, float], field_name: str
) -> None:
    with pytest.raises(ValueError, match=field_name):
        RequestTimeouts(**kwargs)


def test_request_timeouts_report_all_invalid_fields_in_one_error() -> None:
    with pytest.raises(ValueError, match=r"total=0\.0, connect=-1\.0"):
        RequestTimeouts(total=0.0, connect=-1.0)


def test_specific_timeouts_override_total() -> None:
    timeouts = RequestTimeouts(total=30.0, connect=5.0, read=10.0)

    assert timeouts.resolve("total") == 30.0
    assert timeouts.resolve("connect") == 5.0
    assert timeouts.resolve("read") == 10.0
    assert timeouts.resolve("write") == 30.0


def test_request_timeouts_preserve_none_values() -> None:
    timeouts = RequestTimeouts()

    assert timeouts.total is None
    assert timeouts.connect is None
    assert timeouts.read is None
    assert timeouts.write is None


def test_client_request_options_are_frozen_and_request_context_is_immutable() -> None:
    options = ClientRequestOptions(
        timeout=RequestTimeouts(total=3.0),
        request_context={"trace_id": "abc-123"},
    )

    with pytest.raises(FrozenInstanceError):
        options.timeout = RequestTimeouts(total=6.0)  # type: ignore[misc]

    with pytest.raises(TypeError):
        options.request_context["trace_id"] = "def-456"  # type: ignore[index]
