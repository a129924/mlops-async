from __future__ import annotations

from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from mlops_async.clients.projects import (
    ChampionFile,
    ChampionModel,
    ProjectDetail,
    ProjectsPage,
    ProjectsResponseError,
    ProjectSummary,
)
from mlops_async.clients.projects.value_objects import (
    parse_champion_model,
    parse_project_detail,
    parse_projects_page,
)
from mlops_async.core.types import JSONValue


_Parser = Callable[[JSONValue], object]


def test_projects_value_objects_are_frozen_slotted_semantic_types() -> None:
    summary = ProjectSummary(id="project-1", name="Credit risk")
    detail = ProjectDetail(id="project-1", name="Credit risk")
    file = ChampionFile(id="content-1", name="score.sas")
    champion = ChampionModel(
        id="model-1",
        name="Champion",
        score_code_type="dataStep",
        files=(file,),
    )
    page = ProjectsPage(count=1, start=0, limit=20, items=(summary,))

    for value in (summary, detail, file, champion, page):
        assert is_dataclass(value)
        assert not hasattr(value, "__dict__")
    assert {field.name for field in fields(summary)} == {
        "id",
        "name",
        "created_by",
        "modified_by",
        "creation_timestamp",
        "modified_timestamp",
    }
    assert {field.name for field in fields(detail)} == {
        "id",
        "name",
        "created_by",
        "modified_by",
        "creation_timestamp",
        "modified_timestamp",
    }
    assert {field.name for field in fields(file)} == {"id", "name"}
    assert {field.name for field in fields(champion)} == {
        "id",
        "name",
        "score_code_type",
        "files",
    }
    assert {field.name for field in fields(page)} == {"count", "start", "limit", "items"}
    assert type(page.items) is tuple
    assert type(champion.files) is tuple

    with pytest.raises(FrozenInstanceError):
        summary.name = "changed"  # type: ignore[misc]


def test_project_value_objects_expose_optional_audit_metadata_with_none_defaults() -> None:
    summary = ProjectSummary(id="project-1", name="Credit risk")
    detail = ProjectDetail(id="project-1", name="Credit risk")

    for value in (summary, detail):
        assert [field.name for field in fields(value)] == [
            "id",
            "name",
            "created_by",
            "modified_by",
            "creation_timestamp",
            "modified_timestamp",
        ]
        assert value.created_by is None
        assert value.modified_by is None
        assert value.creation_timestamp is None
        assert value.modified_timestamp is None


def test_project_parsers_map_complete_raw_audit_metadata_for_list_and_detail() -> None:
    audit_metadata = {
        "createdBy": "creator",
        "modifiedBy": "editor",
        "creationTimeStamp": "2026-08-13T00:00:00Z",
        "modifiedTimeStamp": "not-normalized",
    }
    page = parse_projects_page(
        {
            "count": 1,
            "start": 0,
            "limit": 20,
            "items": [{"id": "project-1", "name": "Credit risk", **audit_metadata}],
        }
    )
    detail = parse_project_detail({"id": "project-1", "name": "Credit risk", **audit_metadata})

    for project in (page.items[0], detail):
        assert project.created_by == "creator"
        assert project.modified_by == "editor"
        assert project.creation_timestamp == "2026-08-13T00:00:00Z"
        assert project.modified_timestamp == "not-normalized"


def test_project_parsers_materialize_missing_audit_metadata_as_none() -> None:
    page = parse_projects_page(
        {
            "count": 1,
            "start": 0,
            "limit": 20,
            "items": [{"id": "project-1", "name": "Credit risk"}],
        }
    )
    detail = parse_project_detail({"id": "project-1", "name": "Credit risk"})

    for project in (page.items[0], detail):
        assert project.created_by is None
        assert project.modified_by is None
        assert project.creation_timestamp is None
        assert project.modified_timestamp is None


@pytest.mark.parametrize("malformed_value", (None, 0, True, [], {}))
def test_project_parsers_reject_present_non_string_audit_metadata(
    malformed_value: JSONValue,
) -> None:
    page_payload: JSONValue = {
        "count": 1,
        "start": 0,
        "limit": 20,
        "items": [
            {
                "id": "project-1",
                "name": "Credit risk",
                "createdBy": malformed_value,
            }
        ],
    }
    detail_payload: JSONValue = {
        "id": "project-1",
        "name": "Credit risk",
        "modifiedTimeStamp": malformed_value,
    }

    with pytest.raises(ProjectsResponseError):
        parse_projects_page(page_payload)
    with pytest.raises(ProjectsResponseError):
        parse_project_detail(detail_payload)


@pytest.mark.parametrize(
    ("parser", "payload"),
    (
        (
            parse_projects_page,
            {"count": True, "start": 0, "limit": 20, "items": []},
        ),
        (
            parse_projects_page,
            {
                "count": 1,
                "start": 0,
                "limit": 20,
                "items": [{"id": 1, "name": "Credit"}],
            },
        ),
        (parse_project_detail, {"id": "project-1", "name": ""}),
        (
            parse_champion_model,
            {"id": "model-1", "name": "Champion", "scoreCodeType": 0},
        ),
        (
            parse_champion_model,
            {
                "id": "model-1",
                "name": "Champion",
                "scoreCodeType": "dataStep",
                "files": [{"id": 1}],
            },
        ),
    ),
)
def test_projects_parsers_translate_malformed_required_fields_to_response_error(
    parser: _Parser,
    payload: JSONValue,
) -> None:
    with pytest.raises(ProjectsResponseError):
        parser(payload)


@pytest.mark.parametrize(
    "payload",
    (
        {"id": "model-1", "name": "Champion"},
        {"id": "model-1", "name": "Champion", "scoreCodeType": None},
    ),
)
def test_champion_parser_materializes_missing_or_null_score_code_type_as_none(
    payload: JSONValue,
) -> None:
    champion = parse_champion_model(payload)

    assert champion.score_code_type is None


@pytest.mark.parametrize("score_code_type", (0, True, [], {}))
def test_champion_parser_rejects_non_string_non_null_score_code_type(
    score_code_type: JSONValue,
) -> None:
    with pytest.raises(ProjectsResponseError):
        parse_champion_model(
            {
                "id": "model-1",
                "name": "Champion",
                "scoreCodeType": score_code_type,
            }
        )


def test_projects_parsers_exclude_unknown_response_fields_from_semantic_objects() -> None:
    page = parse_projects_page(
        {
            "count": 1,
            "start": 0,
            "limit": 20,
            "items": [{"id": "project-1", "name": "Credit", "status": "development"}],
            "links": [{"rel": "self"}],
        }
    )
    detail = parse_project_detail({"id": "project-1", "name": "Credit", "owner": "risk-team"})

    assert page == ProjectsPage(
        count=1,
        start=0,
        limit=20,
        items=(ProjectSummary(id="project-1", name="Credit"),),
    )
    assert detail == ProjectDetail(id="project-1", name="Credit")
    assert not hasattr(page, "links")
    assert not hasattr(page.items[0], "status")
    assert not hasattr(detail, "owner")


def test_champion_parser_excludes_unknown_response_fields_from_semantic_objects() -> None:
    champion = parse_champion_model(
        {
            "id": "model-1",
            "name": "Champion",
            "scoreCodeType": "dataStep",
            "description": "Selected by governance",
            "files": [
                {
                    "id": "content-1",
                    "name": "score.sas",
                    "contentType": "text/x-sas",
                }
            ],
        }
    )

    assert champion == ChampionModel(
        id="model-1",
        name="Champion",
        score_code_type="dataStep",
        files=(ChampionFile(id="content-1", name="score.sas"),),
    )
    assert not hasattr(champion, "description")
    assert not hasattr(champion.files[0], "contentType")
