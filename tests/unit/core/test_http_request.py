from __future__ import annotations

import inspect

import pytest

import mlops_async.core.http_request as http_request
from mlops_async.core.http_request import (
    BaseUrl,
    EndpointPath,
    Headers,
    HttpRequest,
    JsonBody,
    QueryParams,
    RawBody,
)
from mlops_async.core.types import HttpMethod


class _UserEndpoints:
    """Minimal local endpoint-family fixture; this is not a production catalog."""

    @staticmethod
    def list() -> EndpointPath:
        return EndpointPath.literal("/api/v1/users")

    @staticmethod
    def detail(user_id: str) -> EndpointPath:
        return EndpointPath.from_segments("api", "v1", "users", user_id)


def _request(*, body: JsonBody | RawBody | None = None) -> HttpRequest:
    return HttpRequest(
        method=HttpMethod.POST,
        base_url=BaseUrl.create("https://api.example.test"),
        endpoint_path=EndpointPath.literal("/api/v1/items"),
        query=QueryParams.create((("tag", "one"), ("tag", "two"))),
        headers=Headers.create((("X-Trace", "request"),)),
        body=body,
        options=None,
    )


def test_request_value_objects_are_repo_owned_immutable_and_http_library_free() -> None:
    payload = {"items": ["before"]}
    body = JsonBody(payload)
    payload["items"].append("after")

    request = _request(body=body)

    assert request.json_body == {"items": ["before"]}
    assert request.url == "https://api.example.test/api/v1/items?tag=one&tag=two"
    with pytest.raises((AttributeError, TypeError)):
        request.body = None  # type: ignore[misc]
    assert "httpx" not in inspect.getsource(http_request)


@pytest.mark.parametrize(
    "invalid_origin",
    (
        "ftp://api.example.test",
        "https://api.example.test/api/v1",
        "https://user@api.example.test",
        "https://api.example.test?draft=yes",
        "https://api.example.test#fragment",
    ),
)
def test_base_url_is_origin_only(invalid_origin: str) -> None:
    with pytest.raises(ValueError):
        BaseUrl.create(invalid_origin)


def test_direct_construction_matches_named_invariants() -> None:
    assert BaseUrl("https://api.example.test:8443") == BaseUrl.create(
        "https://api.example.test:8443"
    )
    assert EndpointPath("/api/v1/%E5%8F%B0") == EndpointPath.literal("/api/v1/%E5%8F%B0")
    assert QueryParams((("tag", "one"),)) == QueryParams.create((("tag", "one"),))
    assert Headers((("X-Trace", "first"), ("x-trace", "final"))).as_dict() == {"x-trace": "final"}
    assert Headers((("X-Trace", "first"), ("x-trace", "final"))).as_dict() == (
        Headers.create((("X-Trace", "first"), ("x-trace", "final"))).as_dict()
    )

    with pytest.raises(ValueError):
        BaseUrl("https://api example.test")
    with pytest.raises(ValueError):
        EndpointPath("api/v1/items")
    with pytest.raises(ValueError):
        QueryParams((("", "not-allowed"),))
    with pytest.raises(ValueError):
        Headers((("X-Bad\nName", "value"),))


def test_direct_query_params_mapping_matches_create_and_canonical_output() -> None:
    direct = QueryParams({"ab": "value"})  # type: ignore[arg-type]
    created = QueryParams.create({"ab": "value"})

    assert direct == created
    assert direct.render() == "ab=value"


def test_direct_headers_mapping_matches_create_and_canonical_output() -> None:
    direct = Headers({"ab": "value"})  # type: ignore[arg-type]
    created = Headers.create({"ab": "value"})

    assert direct == created
    assert direct.as_dict() == {"ab": "value"}


def test_endpoint_path_literal_rejects_noncanonical_static_paths() -> None:
    literal = EndpointPath.literal("/api/v1/%E5%8F%B0")

    assert literal.value == "/api/v1/%E5%8F%B0"
    for noncanonical_path in (
        "/api/v1/name with space",
        "/api/v1/台北",
        "/api/v1/\x1f",
    ):
        with pytest.raises(ValueError):
            EndpointPath.literal(noncanonical_path)


def test_base_url_rejects_invalid_authority_characters() -> None:
    valid_origin = "https://api.example.test:8443"
    assert BaseUrl(valid_origin) == BaseUrl.create(valid_origin)

    for invalid_origin in (
        "https://api example.test",
        "https://api\\example.test",
        "https://api%00example.test",
    ):
        with pytest.raises(ValueError):
            BaseUrl(invalid_origin)
        with pytest.raises(ValueError):
            BaseUrl.create(invalid_origin)


@pytest.mark.parametrize(
    "invalid_origin",
    (
        "https://api.example.test\r",
        "https://api.example.test\n",
        "https://api.example.test\t",
        "https://api.example.test\x1f",
    ),
    ids=("carriage-return", "line-feed", "tab", "c0-unit-separator"),
)
def test_base_url_rejects_raw_control_characters_before_url_parsing(
    monkeypatch: pytest.MonkeyPatch,
    invalid_origin: str,
) -> None:
    def fail_urlsplit(_value: str) -> None:
        raise AssertionError("control characters must not reach urlsplit")

    monkeypatch.setattr(http_request, "urlsplit", fail_urlsplit)

    with pytest.raises(ValueError):
        BaseUrl.create(invalid_origin)


def test_endpoint_path_distinguishes_literal_static_path_from_encoded_raw_segments() -> None:
    literal = EndpointPath.literal("/api/v1/users")
    dynamic = EndpointPath.from_segments("api", "v1", "users", "name with/slash")

    assert literal.value == "/api/v1/users"
    assert dynamic.value == "/api/v1/users/name%20with%2Fslash"

    with pytest.raises(ValueError):
        EndpointPath.from_segments("already%2Fencoded")


def test_endpoint_path_encodes_a_raw_percent_but_rejects_only_preencoded_percent_triplets() -> None:
    raw_percent = EndpointPath.from_segments("50% complete")

    assert raw_percent.value == "/50%25%20complete"

    with pytest.raises(ValueError):
        EndpointPath.from_segments("already%2Fencoded")


def test_query_params_preserve_duplicate_order_and_exact_percent_encoding() -> None:
    query = QueryParams.create(
        (
            ("tag", "first"),
            ("tag", "second"),
            ("empty", ""),
            ("skip", None),
            ("enabled", True),
            ("city", "台 北"),
        )
    )

    assert query.render() == ("tag=first&tag=second&empty=&enabled=true&city=%E5%8F%B0%20%E5%8C%97")
    with pytest.raises(ValueError):
        QueryParams.create((("", "not-allowed"),))


def test_query_params_render_float_false_and_raw_percent_once() -> None:
    query = QueryParams.create((("ratio", 1.25), ("enabled", False), ("progress", "50% complete")))

    assert query.render() == "ratio=1.25&enabled=false&progress=50%25%20complete"


def test_headers_lowercase_case_insensitively_and_keep_only_last_value() -> None:
    headers = Headers.create(
        (("X-Trace", "first"), ("x-trace", "final"), ("Accept", "application/json"))
    )

    assert headers.as_dict() == {
        "x-trace": "final",
        "accept": "application/json",
    }


def test_http_request_has_one_body_construction_variant_and_readonly_compatibility_reads() -> None:
    signature = inspect.signature(HttpRequest)
    json_request = _request(body=JsonBody({"name": "demo"}))
    raw_request = _request(body=RawBody(b"grant_type=client_credentials"))

    assert "body" in signature.parameters
    assert "json_body" not in signature.parameters
    assert "content" not in signature.parameters
    assert json_request.json_body == {"name": "demo"}
    assert json_request.content is None
    assert raw_request.json_body is None
    assert raw_request.content == b"grant_type=client_credentials"

    with pytest.raises((AttributeError, TypeError)):
        raw_request.content = b"replacement"  # type: ignore[misc]


def test_raw_body_never_injects_content_type() -> None:
    request = _request(body=RawBody(b"raw payload"))

    assert "content-type" not in request.headers.as_dict()


def test_raw_body_snapshots_mutable_bytes_as_immutable_content() -> None:
    source = bytearray(b"first")
    body = RawBody(source)
    source[:] = b"other"

    assert type(body.content) is bytes
    assert body.content == b"first"


@pytest.mark.parametrize("invalid_content", ("text", 1, object()))
def test_raw_body_rejects_non_bytes_content(invalid_content: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        RawBody(invalid_content)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid_body", (b"raw", {"json": "primitive"}, object()))
def test_http_request_rejects_body_variants_other_than_json_raw_or_none(
    invalid_body: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _request(body=invalid_body)  # type: ignore[arg-type]


def test_endpoint_family_contract_returns_endpoint_paths_without_a_concrete_catalog() -> None:
    listed = _UserEndpoints.list()
    detailed = _UserEndpoints.detail("name with/slash")

    assert type(listed) is EndpointPath
    assert listed.value == "/api/v1/users"
    assert type(detailed) is EndpointPath
    assert detailed.value == "/api/v1/users/name%20with%2Fslash"
