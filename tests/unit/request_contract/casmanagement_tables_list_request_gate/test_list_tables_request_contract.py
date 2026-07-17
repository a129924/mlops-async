"""Readable request-contract tests for CASManagement list_tables."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.casmanagement_tables_list_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    CASManagementTablesListContractHarness,
    _is_topic_scoped_pytest_run,
)

FIXTURE_ROOT = "tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures"
CASLIB = "CASUSER"


def test_list_tables_limit_1000_start_0_request_shape(
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    case_list_tables_limit_1000_start_0 = EndpointContractCase(
        name="casmanagement_tables.list_tables.limit_1000_start_0",
        invoke=lambda: casmanagement_tables_list_contract.client.list_tables(caslib=CASLIB),
        expected=RequestShape(
            method="GET",
            path=(f"/casManagement/dataSources/cas~fs~cas-shared-default~fs~{CASLIB}/tables"),
            query={"limit": "1000", "start": "0"},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=(f"{FIXTURE_ROOT}/list_tables.request-flow.json#limit_1000_start_0"),
            response_path=(f"{FIXTURE_ROOT}/list_tables.mock-responses.json#limit_1000_start_0"),
        ),
    )

    result = casmanagement_tables_list_contract.run(case_list_tables_limit_1000_start_0)

    assert getattr(result, "items", None) == []
    assert casmanagement_tables_list_contract.last_request is not None
    assert (
        casmanagement_tables_list_contract.last_request["path"]
        == "/casManagement/dataSources/cas~fs~cas-shared-default~fs~CASUSER/tables"
    )
    assert casmanagement_tables_list_contract.last_request["query"] == {
        "limit": "1000",
        "start": "0",
    }
    assert casmanagement_tables_list_contract.last_request["body"] is None
    headers = casmanagement_tables_list_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["Accept"] == "application/json"


@pytest.mark.parametrize("caslib", [123, {"name": CASLIB}])
def test_list_tables_blocks_non_string_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
    caslib: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_tables_list_contract.client.list_tables(caslib=caslib)


@pytest.mark.parametrize("caslib", ["", "   "])
def test_list_tables_blocks_blank_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
    caslib: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_tables_list_contract.client.list_tables(caslib=caslib)


def test_list_tables_blocks_bare_get_without_limit_start(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Bare GET without limit/start is blocked in this topic",
    ):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            include_default_query=False,
        )


@pytest.mark.parametrize(
    ("limit", "pattern"),
    [
        (500, "Only limit=1000 is allowed in this topic"),
        ("1000", "Only limit=1000 is allowed in this topic"),
    ],
)
def test_list_tables_blocks_non_canonical_limit(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
    limit: object,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            limit=limit,
        )


@pytest.mark.parametrize(
    ("start", "pattern"),
    [
        (10, "Only start=0 is allowed in this topic"),
        ("0", "Only start=0 is allowed in this topic"),
    ],
)
def test_list_tables_blocks_non_canonical_start(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
    start: object,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            start=start,
        )


def test_list_tables_blocks_extra_query_params(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Extra query params are blocked in this topic",
    ):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            extra_query={"filter": "loaded"},
        )


def test_list_tables_blocks_request_body_presence(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body is blocked in this topic",
    ):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            body={"unexpected": True},
        )


@pytest.mark.parametrize(
    ("endpoint_variant", "pattern"),
    [
        ("get_table", "get_table drift is blocked in this topic"),
        (
            "change_table_state",
            "change_table_state drift is blocked in this topic",
        ),
    ],
)
def test_list_tables_blocks_endpoint_family_drift(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
    endpoint_variant: str,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_tables_list_contract.client.list_tables(
            caslib=CASLIB,
            endpoint_variant=endpoint_variant,
        )


def test_list_tables_percent_encodes_reserved_caslib_characters(
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    reserved_caslib = "CAS/USER?draft=yes"
    encoded_caslib = "CAS%2FUSER%3Fdraft%3Dyes"

    case_list_tables_reserved_caslib = EndpointContractCase(
        name="casmanagement_tables.list_tables.percent_encoded_caslib",
        invoke=lambda: casmanagement_tables_list_contract.client.list_tables(
            caslib=reserved_caslib
        ),
        expected=RequestShape(
            method="GET",
            path=(
                f"/casManagement/dataSources/cas~fs~cas-shared-default~fs~{encoded_caslib}/tables"
            ),
            query={"limit": "1000", "start": "0"},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    result = casmanagement_tables_list_contract.run(case_list_tables_reserved_caslib)

    assert isinstance(result, SimpleNamespace)
    assert casmanagement_tables_list_contract.last_request is not None
    assert (
        casmanagement_tables_list_contract.last_request["path"]
        == "/casManagement/dataSources/cas~fs~cas-shared-default~fs~"
        "CAS%2FUSER%3Fdraft%3Dyes/tables"
    )
    assert casmanagement_tables_list_contract.last_request["query"] == {
        "limit": "1000",
        "start": "0",
    }


def test_list_tables_interceptor_fails_fast_on_unregistered_request(
    casmanagement_tables_list_contract: CASManagementTablesListContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="casmanagement_tables.list_tables.unregistered_request",
        invoke=lambda: casmanagement_tables_list_contract.client.list_tables(caslib=CASLIB),
        expected=RequestShape(
            method="GET",
            path="/casManagement/dataSources/cas~fs~cas-shared-default~fs~CASUSER/tables",
            query={"limit": "1000"},
            body=None,
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        casmanagement_tables_list_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/casmanagement_tables_list_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False
