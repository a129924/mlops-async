from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from mlops_async.clients.cas_tables.value_objects import (
    CasTablesResponseError,
    TableDetail,
    TablesPage,
    TableState,
    parse_table_detail,
    parse_tables_page,
)
from mlops_async.core.types import JSONValue


def _detail_response(**overrides: JSONValue) -> dict[str, JSONValue]:
    response: dict[str, JSONValue] = {
        "name": "INPUT",
        "caslib": "CASUSER",
        "state": "loaded",
        "created": "2026-08-12T08:00:00Z",
        "lastModified": "not-an-ISO-8601-timestamp",
        "lastAccessed": "2026-08-12T09:00:00+08:00",
        "sourceLastModified": "raw source timestamp",
    }
    response.update(overrides)
    return response


def test_table_value_objects_are_frozen_slotted_semantic_types() -> None:
    detail = TableDetail(
        name="INPUT",
        caslib="CASUSER",
        state=TableState.LOADED,
        created="2026-08-12T08:00:00Z",
        last_modified="not-an-ISO-8601-timestamp",
        last_accessed=None,
        source_last_modified=None,
    )
    page = TablesPage(items=(detail,))

    assert is_dataclass(detail)
    assert is_dataclass(page)
    assert not hasattr(detail, "__dict__")
    assert not hasattr(page, "__dict__")
    assert {field.name for field in fields(detail)} == {
        "name",
        "caslib",
        "state",
        "created",
        "last_modified",
        "last_accessed",
        "source_last_modified",
    }
    assert {field.name for field in fields(page)} == {"items"}
    assert type(page.items) is tuple
    with pytest.raises(FrozenInstanceError):
        detail.name = "OTHER"  # type: ignore[misc]


def test_table_state_is_a_string_enum_with_only_loaded() -> None:
    assert issubclass(TableState, str)
    assert TableState.LOADED.value == "loaded"
    assert tuple(TableState) == (TableState.LOADED,)


def test_parse_table_detail_maps_and_preserves_full_metadata() -> None:
    detail = parse_table_detail(_detail_response())

    assert detail == TableDetail(
        name="INPUT",
        caslib="CASUSER",
        state=TableState.LOADED,
        created="2026-08-12T08:00:00Z",
        last_modified="not-an-ISO-8601-timestamp",
        last_accessed="2026-08-12T09:00:00+08:00",
        source_last_modified="raw source timestamp",
    )


def test_parse_tables_page_returns_an_immutable_tuple() -> None:
    page = parse_tables_page(
        {
            "items": [
                _detail_response(),
                _detail_response(name="OUTPUT", lastAccessed=None),
            ],
            "count": 2,
        }
    )

    assert page.items == (
        TableDetail(
            name="INPUT",
            caslib="CASUSER",
            state=TableState.LOADED,
            created="2026-08-12T08:00:00Z",
            last_modified="not-an-ISO-8601-timestamp",
            last_accessed="2026-08-12T09:00:00+08:00",
            source_last_modified="raw source timestamp",
        ),
        TableDetail(
            name="OUTPUT",
            caslib="CASUSER",
            state=TableState.LOADED,
            created="2026-08-12T08:00:00Z",
            last_modified="not-an-ISO-8601-timestamp",
            last_accessed=None,
            source_last_modified="raw source timestamp",
        ),
    )


@pytest.mark.parametrize("field", ("lastAccessed", "sourceLastModified"))
def test_parse_table_detail_maps_missing_optional_metadata_to_none(field: str) -> None:
    response = _detail_response()
    response.pop(field)

    detail = parse_table_detail(response)

    attribute_name = {
        "lastAccessed": "last_accessed",
        "sourceLastModified": "source_last_modified",
    }[field]
    assert getattr(detail, attribute_name) is None


def test_parse_table_detail_maps_null_optional_metadata_to_none() -> None:
    detail = parse_table_detail(_detail_response(lastAccessed=None, sourceLastModified=None))

    assert detail.last_accessed is None
    assert detail.source_last_modified is None


@pytest.mark.parametrize("field", ("created", "lastModified"))
@pytest.mark.parametrize("invalid_value", (None, "", 1, [], {}))
def test_parse_table_detail_rejects_malformed_required_metadata(
    field: str, invalid_value: JSONValue
) -> None:
    with pytest.raises(CasTablesResponseError):
        parse_table_detail(_detail_response(**{field: invalid_value}))


@pytest.mark.parametrize("field", ("created", "lastModified"))
def test_parse_table_detail_rejects_missing_required_metadata(field: str) -> None:
    response = _detail_response()
    response.pop(field)

    with pytest.raises(CasTablesResponseError):
        parse_table_detail(response)


@pytest.mark.parametrize("field", ("lastAccessed", "sourceLastModified"))
@pytest.mark.parametrize("invalid_value", ("", 1, [], {}))
def test_parse_table_detail_rejects_malformed_optional_metadata(
    field: str, invalid_value: JSONValue
) -> None:
    with pytest.raises(CasTablesResponseError):
        parse_table_detail(_detail_response(**{field: invalid_value}))


@pytest.mark.parametrize(
    "value",
    (
        None,
        [],
        {"items": None},
        {"items": {}},
        {"items": [{}]},
        {"items": [_detail_response(name=None)]},
        {"items": [_detail_response(caslib=1)]},
        {"items": [_detail_response(state="unloaded")]},
    ),
)
def test_parse_tables_page_rejects_semantic_mismatches(value: object) -> None:
    with pytest.raises(CasTablesResponseError):
        parse_tables_page(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    (
        None,
        [],
        {},
        _detail_response(name=""),
        _detail_response(caslib=""),
        _detail_response(state=None),
        _detail_response(state="unloaded"),
        _detail_response(ignored=True),
        _detail_response(caslibName="CASUSER"),
    ),
)
def test_parse_table_detail_rejects_semantic_mismatches(value: object) -> None:
    with pytest.raises(CasTablesResponseError):
        parse_table_detail(value)  # type: ignore[arg-type]
