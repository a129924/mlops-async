from mlops_async.core.types import ResponseHeaders


def test_get_returns_first_case_insensitive_match() -> None:
    headers = ResponseHeaders(
        (
            ("X-Request-ID", "req-1"),
            ("x-request-id", "req-2"),
            ("Content-Type", "application/json"),
        )
    )

    assert headers.get("x-request-id") == "req-1"
    assert headers.get("X-REQUEST-ID") == "req-1"


def test_get_all_preserves_duplicates_and_original_order() -> None:
    headers = ResponseHeaders(
        (
            ("X-Trace", "first"),
            ("Content-Type", "application/json"),
            ("x-trace", "second"),
            ("X-Trace", "third"),
        )
    )

    assert headers.get_all("x-trace") == ("first", "second", "third")


def test_pairs_preserve_original_casing_and_order() -> None:
    pairs = (
        ("X-Trace", "first"),
        ("content-type", "application/json"),
        ("x-trace", "second"),
    )

    headers = ResponseHeaders(pairs)

    assert headers.pairs() == pairs


def test_missing_headers_return_empty_results() -> None:
    headers = ResponseHeaders((("Content-Type", "application/json"),))

    assert headers.get("x-request-id") is None
    assert headers.get_all("x-request-id") == ()
