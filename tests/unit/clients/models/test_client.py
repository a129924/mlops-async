from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

import mlops_async
from mlops_async.clients.models import ModelContent, ModelsClient
from mlops_async.core.http_request import EndpointPath
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from mlops_async.clients.models.value_objects import (
    ModelDetail,
    ModelsPage,
    ModelsResponseError,
)
from mlops_async.transport.exceptions import (
    HTTPStatusException,
    HttpErrorContext,
    HttpTransportException,
    InvalidJSONResponseException,
)


@dataclass(frozen=True)
class _RecordedRequest:
    method: HttpMethod
    path: str
    headers: dict[str, str]
    params: dict[str, str]


class _FakeRequester:
    def __init__(self, outcomes: list[RawClientResponse | BaseException]) -> None:
        self._outcomes = outcomes
        self.requests: list[_RecordedRequest] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
    ) -> RawClientResponse:
        self.requests.append(
            _RecordedRequest(
                method=method,
                path=path,
                headers=dict(headers or {}),
                params=dict(params or {}),
            )
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _response(
    payload: bytes,
    *,
    status_code: int = 200,
    headers: ResponseHeaders | None = None,
) -> RawClientResponse:
    return RawClientResponse(
        status_code=status_code,
        headers=headers or ResponseHeaders(),
        content=payload,
        method=HttpMethod.GET,
        url="https://viya.example.test/modelRepository/models",
    )


def _error_context(status_code: int = 503) -> HttpErrorContext:
    return HttpErrorContext(
        status_code=status_code,
        method="GET",
        url="https://viya.example.test/modelRepository/models",
    )


@pytest.mark.asyncio
async def test_list_models_decodes_one_immutable_page_and_builds_the_default_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    literal_paths: list[str] = []
    original_literal = EndpointPath.literal

    def record_literal(_cls: type[EndpointPath], value: str) -> EndpointPath:
        literal_paths.append(value)
        return original_literal(value)

    monkeypatch.setattr(EndpointPath, "literal", classmethod(record_literal))
    requester = _FakeRequester(
        [
            _response(
                b'{"count": 3, "start": 0, "limit": 20, "items": ['
                b'{"id": "model-1", "name": "Credit", "projectId": "project-1", '
                b'"modelType": "analytic", "scoreCodeType": "python", "role": "champion", '
                b'"version": 2, "dataUris": ["secret"], "files": [{"name": "hidden"}]}]}'
            )
        ]
    )
    client = ModelsClient(requester)  # type: ignore[arg-type]

    page = await client.list_models()

    assert type(page) is ModelsPage
    assert page.count == 3
    assert page.start == 0
    assert page.limit == 20
    assert type(page.items) is tuple
    assert page.items[0].id == "model-1"
    assert page.items[0].name == "Credit"
    assert page.items[0].project_id == "project-1"
    assert page.items[0].model_type == "analytic"
    assert page.items[0].score_code_type == "python"
    assert page.items[0].role == "champion"
    assert page.items[0].version == 2
    assert not hasattr(page.items[0], "data_uris")
    assert not hasattr(page.items[0], "files")
    assert len(requester.requests) == 1
    request = requester.requests[0]
    assert request.method is HttpMethod.GET
    assert literal_paths == ["/modelRepository/models"]
    assert request.path == "/modelRepository/models"
    assert request.params == {"start": "0", "limit": "20"}


@pytest.mark.asyncio
async def test_list_models_preserves_server_page_metadata_and_uses_legacy_project_filter() -> None:
    requester = _FakeRequester(
        [
            _response(
                b'{"count": 99, "start": 20, "limit": 10, "items": '
                b'[{"id": "model-1", "name": "Credit"}]}'
            )
        ]
    )
    client = ModelsClient(requester)  # type: ignore[arg-type]

    page = await client.list_models(start=20, limit=10, project_id="proj-uuid")

    assert page.count == 99
    assert len(page.items) == 1
    assert requester.requests[0].method is HttpMethod.GET
    assert requester.requests[0].path == "/modelRepository/models"
    assert requester.requests[0].params == {
        "start": "20",
        "limit": "10",
        "filter": 'in(projectId,"proj-uuid")',
    }
    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_model_encodes_its_dynamic_identifier_and_returns_no_raw_payload() -> None:
    requester = _FakeRequester(
        [
            _response(
                b'{"id": "name with/slash", "name": "Credit", "modelType": "analytic", '
                b'"dataUris": ["secret"], "files": [{"name": "hidden"}]}'
            )
        ]
    )
    client = ModelsClient(requester)  # type: ignore[arg-type]

    detail = await client.get_model("name with/slash")

    assert type(detail) is ModelDetail
    assert detail.id == "name with/slash"
    assert detail.name == "Credit"
    assert detail.model_type == "analytic"
    assert not hasattr(detail, "data_uris")
    assert not hasattr(detail, "files")
    assert requester.requests[0].method is HttpMethod.GET
    assert requester.requests[0].path == "/modelRepository/models/name%20with%2Fslash"
    assert requester.requests[0].params == {}
    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_model_content_downloads_raw_bytes_and_present_metadata() -> None:
    requester = _FakeRequester(
        [
            _response(
                b"\x00model content\xff",
                headers=ResponseHeaders(
                    (
                        ("content-type", "application/octet-stream"),
                        ("ETag", '"model-content-v1"'),
                    )
                ),
            )
        ]
    )
    client = ModelsClient(requester)  # type: ignore[arg-type]

    content = await client.get_model_content("model id/slash", "content id/slash")

    assert type(content) is ModelContent
    assert content.content == b"\x00model content\xff"
    assert content.content_type == "application/octet-stream"
    assert content.etag == '"model-content-v1"'
    assert content.content_range is None
    assert len(requester.requests) == 1
    request = requester.requests[0]
    assert request.method is HttpMethod.GET
    assert request.path == (
        "/modelRepository/models/model%20id%2Fslash/contents/content%20id%2Fslash/content"
    )
    assert request.headers == {"Accept": "*/*"}
    assert "Authorization" not in request.headers
    assert "Access-Quarantine" not in request.headers
    assert request.params == {}


@pytest.mark.asyncio
async def test_get_model_content_sends_requested_range_headers_and_maps_partial_metadata() -> None:
    requester = _FakeRequester(
        [
            _response(
                b"partial",
                status_code=206,
                headers=ResponseHeaders(
                    (
                        ("CONTENT-TYPE", "application/octet-stream"),
                        ("etag", '"model-content-v1"'),
                        ("content-range", "bytes 0-6/14"),
                    )
                ),
            )
        ]
    )
    client = ModelsClient(requester)  # type: ignore[arg-type]

    content = await client.get_model_content(
        "model-1",
        "content-1",
        range_header="bytes=0-6",
        if_range='"model-content-v1"',
    )

    assert content.content == b"partial"
    assert content.content_type == "application/octet-stream"
    assert content.etag == '"model-content-v1"'
    assert content.content_range == "bytes 0-6/14"
    assert requester.requests == [
        _RecordedRequest(
            method=HttpMethod.GET,
            path="/modelRepository/models/model-1/contents/content-1/content",
            headers={
                "Accept": "*/*",
                "Range": "bytes=0-6",
                "If-Range": '"model-content-v1"',
            },
            params={},
        )
    ]


@pytest.mark.asyncio
async def test_get_model_content_maps_missing_metadata_headers_to_none() -> None:
    requester = _FakeRequester([_response(b"content")])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    content = await client.get_model_content("model-1", "content-1")

    assert content.content == b"content"
    assert content.content_type is None
    assert content.etag is None
    assert content.content_range is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"model_id": ""},
        {"model_id": "  "},
        {"model_id": 1},
        {"content_id": ""},
        {"content_id": "  "},
        {"content_id": 1},
        {"range_header": ""},
        {"range_header": "  "},
        {"range_header": 1},
        {"range_header": "bytes=0-6\r\nAuthorization: injected"},
        {"if_range": ""},
        {"if_range": "  "},
        {"if_range": 1},
        {"if_range": '"model-content-v1"\nAccess-Quarantine: injected'},
        {"if_range": '"model-content-v1"'},
    ),
)
async def test_get_model_content_rejects_invalid_input_before_requester_io(
    kwargs: dict[str, object],
) -> None:
    requester = _FakeRequester([])
    client = ModelsClient(requester)  # type: ignore[arg-type]
    model_id = kwargs.get("model_id", "model-1")
    content_id = kwargs.get("content_id", "content-1")
    header_kwargs = {
        name: value for name, value in kwargs.items() if name not in {"model_id", "content_id"}
    }

    with pytest.raises(ValueError, match=r".+"):
        await client.get_model_content(model_id, content_id, **header_kwargs)  # type: ignore[arg-type]

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", (201, 204))
async def test_get_model_content_rejects_unexpected_success_status_without_constructing_content(
    status_code: int,
) -> None:
    requester = _FakeRequester([_response(b"unexpected", status_code=status_code)])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ModelsResponseError, match="expected status 200 or 206"):
        await client.get_model_content("model-1", "content-1")

    assert len(requester.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception",
    (
        HTTPStatusException(_error_context(status_code=416)),
        HttpTransportException(_error_context()),
        asyncio.CancelledError(),
    ),
)
async def test_get_model_content_propagates_requester_exceptions_unchanged(
    exception: BaseException,
) -> None:
    requester = _FakeRequester([exception])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(type(exception)) as error_info:
        await client.get_model_content("model-1", "content-1")

    assert error_info.value is exception
    assert len(requester.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("kwargs", "description"),
    [
        ({"start": True}, "boolean start"),
        ({"start": -1}, "negative start"),
        ({"limit": True}, "boolean limit"),
        ({"limit": 0}, "zero limit"),
        ({"project_id": "  "}, "blank project id"),
    ],
)
async def test_list_models_rejects_invalid_input_before_requester_io(
    kwargs: dict[str, object], description: str
) -> None:
    requester = _FakeRequester([])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=r".+"):
        await client.list_models(**kwargs)  # type: ignore[arg-type]

    assert description
    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize("model_id", ("", "  ", 1))
async def test_get_model_rejects_invalid_identifier_before_requester_io(model_id: object) -> None:
    requester = _FakeRequester([])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=r".+"):
        await client.get_model(model_id)  # type: ignore[arg-type]

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    (
        b"[]",
        b'{"count": 1, "start": 0, "limit": 20, "items": [{"id": "model-1", '
        b'"unmodeled": "do-not-echo-this-raw-payload"}]}',
        b'{"id": "model-1"}',
    ),
)
async def test_successful_but_malformed_responses_raise_safe_models_response_error(
    payload: bytes,
) -> None:
    raw_secret = "do-not-echo-this-raw-payload"
    requester = _FakeRequester([_response(payload)])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ModelsResponseError) as error_info:
        await client.list_models()

    assert raw_secret not in str(error_info.value)
    assert requester.requests and len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_model_missing_required_semantic_field_raises_models_response_error() -> None:
    requester = _FakeRequester([_response(b'{"id": "model-1"}')])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ModelsResponseError):
        await client.get_model("model-1")

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_invalid_json_response_uses_the_existing_transport_exception_type() -> None:
    requester = _FakeRequester([_response(b"this is not JSON")])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(InvalidJSONResponseException) as error_info:
        await client.list_models()

    assert isinstance(error_info.value.context, HttpErrorContext)
    assert len(requester.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception",
    (
        HTTPStatusException(_error_context()),
        HttpTransportException(_error_context()),
        InvalidJSONResponseException(_error_context()),
    ),
)
async def test_requester_transport_exceptions_propagate_as_the_same_instance(
    exception: BaseException,
) -> None:
    requester = _FakeRequester([exception])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(type(exception)) as error_info:
        await client.list_models()

    assert error_info.value is exception
    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_requester_cancellation_propagates_unchanged_without_follow_up_work() -> None:
    cancellation = asyncio.CancelledError()
    requester = _FakeRequester([cancellation])
    client = ModelsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(asyncio.CancelledError) as error_info:
        await client.list_models()

    assert error_info.value is cancellation
    assert len(requester.requests) == 1


def test_models_client_has_the_frozen_public_surface_with_content_download() -> None:
    signature = inspect.signature(ModelsClient)
    list_signature = inspect.signature(ModelsClient.list_models)
    get_signature = inspect.signature(ModelsClient.get_model)
    content_signature = inspect.signature(ModelsClient.get_model_content)

    assert ModelsClient.__module__ == "mlops_async.clients.models.client"
    assert list(signature.parameters) == ["requester"]
    assert list(list_signature.parameters) == ["self", "start", "limit", "project_id"]
    assert list_signature.parameters["start"].default == 0
    assert list_signature.parameters["limit"].default == 20
    assert list_signature.parameters["project_id"].default is None
    assert list_signature.parameters["start"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_signature.parameters["model_id"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert list(content_signature.parameters) == [
        "self",
        "model_id",
        "content_id",
        "range_header",
        "if_range",
    ]
    content_id_parameter = content_signature.parameters["content_id"]
    assert content_id_parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert content_signature.parameters["range_header"].default is None
    assert content_signature.parameters["range_header"].kind is inspect.Parameter.KEYWORD_ONLY
    assert content_signature.parameters["if_range"].default is None
    assert content_signature.parameters["if_range"].kind is inspect.Parameter.KEYWORD_ONLY
    assert not hasattr(ModelsClient, "close")
    assert not hasattr(ModelsClient, "aclose")
    assert not hasattr(ModelsClient, "__aenter__")
    assert not hasattr(ModelsClient, "__aexit__")
    assert not hasattr(mlops_async, "ModelsClient")


def test_models_client_constructor_accepts_the_caller_owned_requester() -> None:
    signature = inspect.signature(ModelsClient)

    assert signature.parameters["requester"].annotation == Requester.__name__
