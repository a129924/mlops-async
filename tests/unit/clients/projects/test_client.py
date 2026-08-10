from __future__ import annotations

import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

import mlops_async
from mlops_async.clients.projects import (
    ChampionFile,
    ChampionModel,
    ProjectDetail,
    ProjectsClient,
    ProjectsPage,
    ProjectsResponseError,
)
from mlops_async.core.requester import Requester
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders
from mlops_async.transport.exceptions import HttpErrorContext, HttpTransportException


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
            _RecordedRequest(method, path, dict(headers or {}), dict(params or {}))
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _response(payload: object) -> RawClientResponse:
    return RawClientResponse(
        status_code=200,
        headers=ResponseHeaders(),
        content=json.dumps(payload).encode(),
        method=HttpMethod.GET,
        url="https://viya.example.test/modelRepository/projects",
    )


def _page(
    *, count: int, start: int, limit: int, items: list[dict[str, object]]
) -> RawClientResponse:
    return _response({"count": count, "start": start, "limit": limit, "items": items})


def _context() -> HttpErrorContext:
    return HttpErrorContext(
        status_code=503,
        method="GET",
        url="https://viya.example.test/modelRepository/projects",
    )


@pytest.mark.asyncio
async def test_list_projects_builds_one_default_page_request_and_parses_semantic_items() -> None:
    requester = _FakeRequester(
        [_page(count=3, start=0, limit=20, items=[{"id": "p-1", "name": "Credit"}])]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    page = await client.list_projects()

    assert type(page) is ProjectsPage
    assert page.count == 3
    assert page.items[0].id == "p-1"
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/modelRepository/projects",
            {},
            {"start": "0", "limit": "20"},
        )
    ]


@pytest.mark.asyncio
async def test_get_project_encodes_identifier_and_discards_unmodeled_payload() -> None:
    requester = _FakeRequester(
        [_response({"id": "id/with space", "name": "Credit", "status": "development"})]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    project = await client.get_project("id/with space")

    assert type(project) is ProjectDetail
    assert project.id == "id/with space"
    assert project.name == "Credit"
    assert not hasattr(project, "status")
    assert requester.requests[0].path == "/modelRepository/projects/id%2Fwith%20space"
    assert requester.requests[0].params == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs", ({"start": True}, {"start": -1}, {"limit": True}, {"limit": 0}, {"limit": 1001})
)
async def test_list_projects_rejects_invalid_input_before_io(kwargs: dict[str, object]) -> None:
    requester = _FakeRequester([])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        await client.list_projects(**kwargs)  # type: ignore[arg-type]

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize("project_id", ("", "  ", 1))
async def test_project_operations_reject_blank_or_invalid_identifiers_before_io(
    project_id: object,
) -> None:
    requester = _FakeRequester([])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        await client.get_project(project_id)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        await client.get_champion(project_id)  # type: ignore[arg-type]

    assert requester.requests == []


@pytest.mark.asyncio
async def test_get_project_by_name_returns_first_page_exact_match_without_next_request() -> None:
    requester = _FakeRequester(
        [
            _page(
                count=3,
                start=0,
                limit=2,
                items=[{"id": "p-1", "name": "Credit"}, {"id": "p-2", "name": "other"}],
            )
        ]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    project = await client.get_project_by_name("Credit", page_size=2)

    assert project is not None and project.id == "p-1"
    assert [request.params for request in requester.requests] == [{"start": "0", "limit": "2"}]


@pytest.mark.asyncio
async def test_get_project_by_name_scans_sequential_pages_and_stops_at_exact_later_match() -> None:
    requester = _FakeRequester(
        [
            _page(
                count=3,
                start=0,
                limit=2,
                items=[{"id": "p-1", "name": "credit"}, {"id": "p-2", "name": "other"}],
            ),
            _page(count=3, start=2, limit=2, items=[{"id": "p-3", "name": "Credit"}]),
        ]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    project = await client.get_project_by_name("Credit", page_size=2)

    assert project is not None and project.id == "p-3"
    assert [request.params for request in requester.requests] == [
        {"start": "0", "limit": "2"},
        {"start": "2", "limit": "2"},
    ]


@pytest.mark.asyncio
async def test_get_project_by_name_returns_none_only_after_real_exhaustion() -> None:
    requester = _FakeRequester(
        [
            _page(
                count=3,
                start=0,
                limit=2,
                items=[{"id": "p-1", "name": "one"}, {"id": "p-2", "name": "two"}],
            ),
            _page(count=3, start=2, limit=2, items=[{"id": "p-3", "name": "three"}]),
        ]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    assert await client.get_project_by_name("missing", page_size=2) is None
    assert len(requester.requests) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "page_size"),
    (
        ("", 1000),
        ("  ", 1000),
        (1, 1000),
        ("Credit", True),
        ("Credit", 0),
        ("Credit", 1001),
    ),
)
async def test_get_project_by_name_rejects_invalid_input_before_requester_io(
    name: object, page_size: object
) -> None:
    requester = _FakeRequester([])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        await client.get_project_by_name(name, page_size=page_size)  # type: ignore[arg-type]

    assert requester.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    (
        {"count": 2, "start": 1, "limit": 2, "items": []},
        {"count": 2, "start": 0, "limit": 1, "items": []},
        {"count": -1, "start": 0, "limit": 2, "items": []},
        {
            "count": 2,
            "start": 0,
            "limit": 2,
            "items": [
                {"id": "a", "name": "a"},
                {"id": "b", "name": "b"},
                {"id": "c", "name": "c"},
            ],
        },
    ),
)
async def test_get_project_by_name_rejects_page_invariants(payload: dict[str, object]) -> None:
    requester = _FakeRequester([_response(payload)])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ProjectsResponseError):
        await client.get_project_by_name("missing", page_size=2)

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_project_by_name_rejects_short_non_final_page_without_next_request() -> None:
    requester = _FakeRequester([_page(count=3, start=0, limit=2, items=[{"id": "a", "name": "a"}])])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ProjectsResponseError):
        await client.get_project_by_name("missing", page_size=2)

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_lookup_rejects_item_count_overshoot_without_next_request() -> None:
    requester = _FakeRequester(
        [
            _page(
                count=1,
                start=0,
                limit=2,
                items=[{"id": "a", "name": "a"}, {"id": "b", "name": "b"}],
            )
        ]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ProjectsResponseError):
        await client.get_project_by_name("missing", page_size=2)

    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_project_by_name_rejects_count_changes_and_propagates_later_request_error() -> (
    None
):
    changed = _FakeRequester(
        [
            _page(
                count=3,
                start=0,
                limit=2,
                items=[{"id": "a", "name": "a"}, {"id": "b", "name": "b"}],
            ),
            _page(count=4, start=2, limit=2, items=[{"id": "c", "name": "c"}]),
        ]
    )
    client = ProjectsClient(changed)  # type: ignore[arg-type]
    with pytest.raises(ProjectsResponseError):
        await client.get_project_by_name("missing", page_size=2)

    transport_error = HttpTransportException(_context())
    failing = _FakeRequester(
        [
            _page(
                count=3,
                start=0,
                limit=2,
                items=[{"id": "a", "name": "a"}, {"id": "b", "name": "b"}],
            ),
            transport_error,
        ]
    )
    failing_client = ProjectsClient(failing)  # type: ignore[arg-type]
    with pytest.raises(HttpTransportException) as error_info:
        await failing_client.get_project_by_name("missing", page_size=2)
    assert error_info.value is transport_error


@pytest.mark.asyncio
async def test_get_champion_accepts_present_empty_and_missing_files() -> None:
    requester = _FakeRequester(
        [
            _response(
                {
                    "id": "model-1",
                    "name": "Champion",
                    "scoreCodeType": "dataStep",
                    "files": [],
                }
            ),
            _response({"id": "model-2", "name": "Champion", "scoreCodeType": "dataStep"}),
        ]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    champion = await client.get_champion("project-1")
    missing_files = await client.get_champion("project-2")

    assert champion.files == ()
    assert missing_files.files == ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    (
        {"id": "model-1", "name": "Champion"},
        {"id": "model-1", "name": "Champion", "scoreCodeType": None},
    ),
)
async def test_get_champion_maps_missing_or_null_score_code_type_to_none(
    payload: dict[str, object],
) -> None:
    requester = _FakeRequester([_response(payload)])
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    champion = await client.get_champion("project-1")

    assert champion.score_code_type is None
    assert len(requester.requests) == 1


@pytest.mark.asyncio
async def test_get_champion_propagates_invalid_score_code_type_as_response_error() -> None:
    requester = _FakeRequester(
        [_response({"id": "model-1", "name": "Champion", "scoreCodeType": 1})]
    )
    client = ProjectsClient(requester)  # type: ignore[arg-type]

    with pytest.raises(ProjectsResponseError):
        await client.get_champion("project-1")

    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/modelRepository/projects/project-1/champion",
            {},
            {},
        )
    ]


@pytest.mark.asyncio
async def test_get_champion_retains_caller_observable_file_references() -> None:
    requester = _FakeRequester(
        [
            _response(
                {
                    "id": "model-1",
                    "name": "Champion",
                    "scoreCodeType": "dataStep",
                    "files": [{"id": "content-1", "name": "score.sas"}],
                }
            )
        ]
    )

    champion = await ProjectsClient(requester).get_champion("project-1")  # type: ignore[arg-type]

    assert champion == ChampionModel(
        id="model-1",
        name="Champion",
        score_code_type="dataStep",
        files=(ChampionFile(id="content-1", name="score.sas"),),
    )
    assert requester.requests == [
        _RecordedRequest(
            HttpMethod.GET,
            "/modelRepository/projects/project-1/champion",
            {},
            {},
        )
    ]


def test_projects_client_has_only_the_frozen_family_local_public_surface() -> None:
    signature = inspect.signature(ProjectsClient)
    assert list(signature.parameters) == ["requester"]
    assert list(inspect.signature(ProjectsClient.list_projects).parameters) == [
        "self",
        "start",
        "limit",
    ]
    assert list(inspect.signature(ProjectsClient.get_project_by_name).parameters) == [
        "self",
        "name",
        "page_size",
    ]
    assert (
        inspect.signature(ProjectsClient.get_project_by_name).parameters["page_size"].default
        == 1000
    )
    assert not hasattr(mlops_async, "ProjectsClient")
    assert not hasattr(ProjectsClient, "close")
    assert (
        inspect.signature(ProjectsClient).parameters["requester"].annotation == Requester.__name__
    )
    assert not hasattr(ProjectsClient, "get_champion_contents")
