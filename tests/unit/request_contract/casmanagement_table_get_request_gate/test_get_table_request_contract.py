"""Readable request-contract tests for CASManagement get_table."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract import contract_case
from tests.unit.request_contract.casmanagement_table_get_request_gate import (
    conftest as get_table_conftest,
)
from tests.unit.request_contract.casmanagement_table_get_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    CASManagementTableGetContractHarness,
    _load_case_from_locator,
    _is_topic_scoped_pytest_run,
)

CASLIB = "CASUSER"
TABLE_NAME = "SCORING_INPUT"


def test_get_table_direct_identifiers_request_shape(
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    case_get_table_direct_identifiers = EndpointContractCase(
        name="casmanagement_tables.get_table.direct_identifiers",
        invoke=lambda: casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="GET",
            path=(
                "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
                f"{CASLIB}/tables/{TABLE_NAME}"
            ),
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"name": TABLE_NAME, "caslib": CASLIB, "state": "loaded"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path="get_table.request-flow.json#direct_identifiers",
            response_path="get_table.mock-responses.json#direct_identifiers",
        ),
    )

    result = casmanagement_table_get_contract.run(case_get_table_direct_identifiers)

    assert getattr(result, "name", None) == TABLE_NAME
    assert getattr(result, "caslib", None) == CASLIB
    assert casmanagement_table_get_contract.last_request is not None
    assert (
        casmanagement_table_get_contract.last_request["path"]
        == "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
        "CASUSER/tables/SCORING_INPUT"
    )
    assert casmanagement_table_get_contract.last_request["query"] == {}
    assert casmanagement_table_get_contract.last_request["body"] is None
    headers = casmanagement_table_get_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["Accept"] == "application/json"


@pytest.mark.parametrize("caslib", [123, {"name": CASLIB}])
def test_get_table_blocks_non_string_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
    caslib: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=caslib,
            table_name=TABLE_NAME,
        )


@pytest.mark.parametrize("caslib", ["", "   "])
def test_get_table_blocks_blank_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
    caslib: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=caslib,
            table_name=TABLE_NAME,
        )


@pytest.mark.parametrize("table_name", [123, {"name": TABLE_NAME}])
def test_get_table_blocks_non_string_table_name_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
    table_name: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty tableName string is allowed",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=table_name,
        )


@pytest.mark.parametrize("table_name", ["", "   "])
def test_get_table_blocks_blank_table_name_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
    table_name: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty tableName string is allowed",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=table_name,
        )


def test_get_table_blocks_query_params(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Query params are blocked in this topic",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            extra_query={"state": "loaded"},
        )


def test_get_table_blocks_request_body_presence(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body is blocked in this topic",
    ):
        casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            body={"unexpected": True},
        )


@pytest.mark.parametrize(
    ("endpoint_variant", "pattern"),
    [
        ("list_tables", "list_tables drift is blocked in this topic"),
        (
            "change_table_state",
            "change_table_state drift is blocked in this topic",
        ),
    ],
)
def test_get_table_blocks_endpoint_family_drift(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
    endpoint_variant: str,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            endpoint_variant=endpoint_variant,
        )


def test_get_table_percent_encodes_reserved_table_name_characters(
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    reserved_table_name = "INPUT/TABLE?draft=yes"
    encoded_table_name = "INPUT%2FTABLE%3Fdraft%3Dyes"

    case_get_table_reserved_table_name = EndpointContractCase(
        name="casmanagement_tables.get_table.percent_encoded_table_name",
        invoke=lambda: casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=reserved_table_name,
        ),
        expected=RequestShape(
            method="GET",
            path=(
                "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
                f"{CASLIB}/tables/{encoded_table_name}"
            ),
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"name": reserved_table_name},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    result = casmanagement_table_get_contract.run(case_get_table_reserved_table_name)

    assert isinstance(result, SimpleNamespace)
    assert casmanagement_table_get_contract.last_request is not None
    assert (
        casmanagement_table_get_contract.last_request["path"]
        == "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
        "CASUSER/tables/INPUT%2FTABLE%3Fdraft%3Dyes"
    )
    assert casmanagement_table_get_contract.last_request["query"] == {}


def test_get_table_interceptor_fails_fast_on_unregistered_request(
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="casmanagement_tables.get_table.unregistered_request",
        invoke=lambda: casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="GET",
            path="/casManagement/dataSources/cas~fs~cas-shared-default~fs~CASUSER/tables",
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"name": TABLE_NAME},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        casmanagement_table_get_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/casmanagement_table_get_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False


def test_load_case_from_locator_rejects_paths_outside_topic_fixture_root(
    tmp_path: Path,
) -> None:
    outside_fixture = tmp_path / "outside.json"
    outside_fixture.write_text(
        json.dumps(
            {
                "cases": {
                    "direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "GET",
                                    "path": "/unexpected",
                                    "query": {},
                                    "body": None,
                                }
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        AssertionError,
        match="Fixture locator must stay under the topic fixture root",
    ):
        _load_case_from_locator(f"{outside_fixture}#direct_identifiers")


def test_load_case_from_locator_rejects_multiple_cases_even_with_explicit_case_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    monkeypatch.setattr(get_table_conftest, "FIXTURE_DIR", fixture_root)

    multi_case_fixture = fixture_root / "get_table.request-flow.json"
    multi_case_fixture.write_text(
        json.dumps(
            {
                "cases": {
                    "direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "GET",
                                    "path": "/first",
                                    "query": {},
                                    "body": None,
                                }
                            }
                        ]
                    },
                    "second_case": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "GET",
                                    "path": "/second",
                                    "query": {},
                                    "body": None,
                                }
                            }
                        ]
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="must define exactly one case"):
        _load_case_from_locator("get_table.request-flow.json#direct_identifiers")


def test_get_table_source_observed_headers_must_match_fixture_subset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    casmanagement_table_get_contract: CASManagementTableGetContractHarness,
) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    monkeypatch.setattr(get_table_conftest, "FIXTURE_DIR", fixture_root)

    request_fixture = fixture_root / "get_table.request-flow.json"
    request_fixture.write_text(
        json.dumps(
            {
                "cases": {
                    "direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "purpose": "target-api",
                                "request": {
                                    "method": "GET",
                                    "path": (
                                        "/casManagement/dataSources/"
                                        "cas~fs~cas-shared-default~fs~"
                                        "CASUSER/tables/SCORING_INPUT"
                                    ),
                                    "required_header_subset": {
                                        "Authorization": "Bearer fake-token",
                                        "Accept": "application/problem+json",
                                    },
                                    "query": {},
                                    "body": None,
                                },
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    mismatched_source_case = contract_case.EndpointContractCase(
        name="casmanagement_tables.get_table.source_observed_header_drift",
        invoke=lambda: casmanagement_table_get_contract.client.get_table(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="GET",
            path=(
                "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
                f"{CASLIB}/tables/{TABLE_NAME}"
            ),
            query={},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"name": TABLE_NAME},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path="get_table.request-flow.json#direct_identifiers",
            response_path=None,
        ),
    )

    with pytest.raises(
        AssertionError,
        match="Observed request headers drifted from source evidence",
    ):
        casmanagement_table_get_contract.run(mismatched_source_case)
