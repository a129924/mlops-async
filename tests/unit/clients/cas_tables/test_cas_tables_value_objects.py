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


def test_table_value_objects_are_frozen_slotted_semantic_types() -> None:
    detail = TableDetail(name="INPUT", caslib="CASUSER", state=TableState.LOADED)
    page = TablesPage(items=(detail,))

    assert is_dataclass(detail)
    assert is_dataclass(page)
    assert not hasattr(detail, "__dict__")
    assert not hasattr(page, "__dict__")
    assert {field.name for field in fields(detail)} == {"name", "caslib", "state"}
    assert {field.name for field in fields(page)} == {"items"}
    assert type(page.items) is tuple
    with pytest.raises(FrozenInstanceError):
        detail.name = "OTHER"  # type: ignore[misc]


def test_table_state_is_a_string_enum_with_only_loaded() -> None:
    assert issubclass(TableState, str)
    assert TableState.LOADED.value == "loaded"
    assert tuple(TableState) == (TableState.LOADED,)


def test_parse_table_detail_returns_the_strict_contract() -> None:
    detail = parse_table_detail({"name": "INPUT", "caslib": "CASUSER", "state": "loaded"})

    assert detail == TableDetail(name="INPUT", caslib="CASUSER", state=TableState.LOADED)


def test_parse_tables_page_returns_an_immutable_tuple() -> None:
    page = parse_tables_page(
        {
            "items": [
                {"name": "INPUT", "caslib": "CASUSER", "state": "loaded"},
                {"name": "OUTPUT", "caslib": "CASUSER", "state": "loaded"},
            ],
            "count": 2,
        }
    )

    assert page.items == (
        TableDetail(name="INPUT", caslib="CASUSER", state=TableState.LOADED),
        TableDetail(name="OUTPUT", caslib="CASUSER", state=TableState.LOADED),
    )


@pytest.mark.parametrize(
    "value",
    (
        None,
        [],
        {"items": None},
        {"items": {}},
        {"items": [{}]},
        {"items": [{"name": None, "caslib": "CASUSER", "state": "loaded"}]},
        {"items": [{"name": "INPUT", "caslib": 1, "state": "loaded"}]},
        {"items": [{"name": "INPUT", "caslib": "CASUSER", "state": "unloaded"}]},
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
        {"name": "", "caslib": "CASUSER", "state": "loaded"},
        {"name": "INPUT", "caslib": "", "state": "loaded"},
        {"name": "INPUT", "caslib": "CASUSER", "state": None},
        {"name": "INPUT", "caslib": "CASUSER", "state": "unloaded"},
        {"name": "INPUT", "caslib": "CASUSER", "state": "loaded", "ignored": True},
    ),
)
def test_parse_table_detail_rejects_semantic_mismatches(value: object) -> None:
    with pytest.raises(CasTablesResponseError):
        parse_table_detail(value)  # type: ignore[arg-type]
