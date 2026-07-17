"""Readable request-contract tests for CASManagement change_table_state."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.unit.request_contract import contract_case
from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.casmanagement_table_state_change_request_gate import (
    conftest as change_table_state_conftest,
)
from tests.unit.request_contract.casmanagement_table_state_change_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    CASManagementTableStateChangeContractHarness,
    _is_topic_scoped_pytest_run,
    _load_case_from_locator,
)

CASLIB = "CASUSER"
TABLE_NAME = "SCORING_INPUT"


def test_change_table_state_loaded_direct_identifiers_request_shape(
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    case_change_table_state_loaded = EndpointContractCase(
        name="casmanagement_tables.change_table_state.loaded_direct_identifiers",
        invoke=lambda: casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="PUT",
            path=(
                "/casManagement/servers/cas-shared-default/caslibs/"
                f"{CASLIB}/tables/{TABLE_NAME}/state"
            ),
            query={"value": "loaded"},
            body={
                "outputCaslibName": CASLIB,
                "outputTableName": TABLE_NAME,
            },
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "loaded"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path="change_table_state.request-flow.json#loaded_direct_identifiers",
            response_path="change_table_state.mock-responses.json#loaded_direct_identifiers",
        ),
    )

    result = casmanagement_table_state_change_contract.run(case_change_table_state_loaded)

    assert getattr(result, "state", None) == "loaded"
    assert casmanagement_table_state_change_contract.last_request is not None
    assert (
        casmanagement_table_state_change_contract.last_request["path"]
        == "/casManagement/servers/cas-shared-default/caslibs/"
        "CASUSER/tables/SCORING_INPUT/state"
    )
    assert casmanagement_table_state_change_contract.last_request["query"] == {"value": "loaded"}
    assert casmanagement_table_state_change_contract.last_request["body"] == {
        "outputCaslibName": CASLIB,
        "outputTableName": TABLE_NAME,
    }
    headers = casmanagement_table_state_change_contract.last_request["headers"]
    assert isinstance(headers, dict)
    assert str(headers["Authorization"]).startswith("Bearer ")
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("caslib", [123, {"name": CASLIB}])
def test_change_table_state_blocks_non_string_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    caslib: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=caslib,
            table_name=TABLE_NAME,
        )


@pytest.mark.parametrize("caslib", ["", "   "])
def test_change_table_state_blocks_blank_caslib_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    caslib: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty caslib string is allowed",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=caslib,
            table_name=TABLE_NAME,
        )


@pytest.mark.parametrize("table_name", [123, {"name": TABLE_NAME}])
def test_change_table_state_blocks_non_string_table_name_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    table_name: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty tableName string is allowed",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=table_name,
        )


@pytest.mark.parametrize("table_name", ["", "   "])
def test_change_table_state_blocks_blank_table_name_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    table_name: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty tableName string is allowed",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=table_name,
        )


def test_change_table_state_blocks_missing_value_query(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Missing value query is blocked in this topic",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            include_state_query=False,
        )


@pytest.mark.parametrize(
    ("state", "pattern"),
    [
        ("unloaded", "value=unloaded is blocked in this topic"),
        ("loading", "Only value=loaded is allowed in this topic"),
        (1, "Only value=loaded is allowed in this topic"),
    ],
)
def test_change_table_state_blocks_non_canonical_state_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    state: object,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            state=state,
        )


def test_change_table_state_blocks_extra_query_params(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Extra query params are blocked in this topic",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            extra_query={"x": "1"},
        )


def test_change_table_state_blocks_missing_body(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body is required in this topic",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            body_override=None,
        )


@pytest.mark.parametrize("body_override", ["invalid", 123, ["x"]])
def test_change_table_state_blocks_non_object_body_variants(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    body_override: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body must be a JSON object in this topic",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            body_override=body_override,
        )


def test_change_table_state_blocks_output_caslib_mismatch(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body outputCaslibName must match the path caslib",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            body_override={
                "outputCaslibName": "OTHER",
                "outputTableName": TABLE_NAME,
            },
        )


def test_change_table_state_blocks_output_table_name_mismatch(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Request body outputTableName must match the path tableName",
    ):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            body_override={
                "outputCaslibName": CASLIB,
                "outputTableName": "OTHER",
            },
        )


@pytest.mark.parametrize(
    ("endpoint_variant", "pattern"),
    [
        ("list_tables", "list_tables drift is blocked in this topic"),
        ("get_table", "get_table drift is blocked in this topic"),
    ],
)
def test_change_table_state_blocks_endpoint_family_drift(
    blocked_topic_scope_error: type[RuntimeError],
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
    endpoint_variant: str,
    pattern: str,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match=pattern):
        casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
            endpoint_variant=endpoint_variant,
        )


def test_change_table_state_percent_encodes_reserved_identifier_characters(
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    reserved_caslib = "CAS/USER?draft=yes"
    reserved_table_name = "INPUT/TABLE?draft=yes"
    encoded_caslib = "CAS%2FUSER%3Fdraft%3Dyes"
    encoded_table_name = "INPUT%2FTABLE%3Fdraft%3Dyes"

    case_change_table_state_reserved_identifiers = EndpointContractCase(
        name="casmanagement_tables.change_table_state.percent_encoded_identifiers",
        invoke=lambda: casmanagement_table_state_change_contract.client.change_table_state(
            caslib=reserved_caslib,
            table_name=reserved_table_name,
        ),
        expected=RequestShape(
            method="PUT",
            path=(
                "/casManagement/servers/cas-shared-default/caslibs/"
                f"{encoded_caslib}/tables/{encoded_table_name}/state"
            ),
            query={"value": "loaded"},
            body={
                "outputCaslibName": reserved_caslib,
                "outputTableName": reserved_table_name,
            },
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "loaded"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    result = casmanagement_table_state_change_contract.run(
        case_change_table_state_reserved_identifiers
    )

    assert isinstance(result, SimpleNamespace)
    assert casmanagement_table_state_change_contract.last_request is not None
    assert (
        casmanagement_table_state_change_contract.last_request["path"]
        == "/casManagement/servers/cas-shared-default/caslibs/"
        "CAS%2FUSER%3Fdraft%3Dyes/tables/INPUT%2FTABLE%3Fdraft%3Dyes/state"
    )
    assert casmanagement_table_state_change_contract.last_request["query"] == {"value": "loaded"}
    assert casmanagement_table_state_change_contract.last_request["body"] == {
        "outputCaslibName": reserved_caslib,
        "outputTableName": reserved_table_name,
    }


def test_change_table_state_interceptor_fails_fast_on_unregistered_request(
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="casmanagement_tables.change_table_state.unregistered_request",
        invoke=lambda: casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="PUT",
            path="/casManagement/servers/cas-shared-default/caslibs/CASUSER/tables",
            query={"value": "loaded"},
            body={
                "outputCaslibName": CASLIB,
                "outputTableName": TABLE_NAME,
            },
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "loaded"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        casmanagement_table_state_change_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/casmanagement_table_state_change_request_gate"],
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
                    "loaded_direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "PUT",
                                    "path": "/unexpected",
                                    "query": {"value": "loaded"},
                                    "body": {
                                        "outputCaslibName": CASLIB,
                                        "outputTableName": TABLE_NAME,
                                    },
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
        _load_case_from_locator(f"{outside_fixture}#loaded_direct_identifiers")


def test_load_case_from_locator_rejects_multiple_cases_even_with_explicit_case_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    monkeypatch.setattr(change_table_state_conftest, "FIXTURE_DIR", fixture_root)

    multi_case_fixture = fixture_root / "change_table_state.request-flow.json"
    multi_case_fixture.write_text(
        json.dumps(
            {
                "cases": {
                    "loaded_direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "PUT",
                                    "path": "/first",
                                    "query": {"value": "loaded"},
                                    "body": {
                                        "outputCaslibName": CASLIB,
                                        "outputTableName": TABLE_NAME,
                                    },
                                }
                            }
                        ]
                    },
                    "second_case": {
                        "full_observed_flow": [
                            {
                                "request": {
                                    "method": "PUT",
                                    "path": "/second",
                                    "query": {"value": "loaded"},
                                    "body": {
                                        "outputCaslibName": CASLIB,
                                        "outputTableName": TABLE_NAME,
                                    },
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
        _load_case_from_locator("change_table_state.request-flow.json#loaded_direct_identifiers")


def test_change_table_state_source_observed_headers_must_match_fixture_subset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    casmanagement_table_state_change_contract: CASManagementTableStateChangeContractHarness,
) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    monkeypatch.setattr(change_table_state_conftest, "FIXTURE_DIR", fixture_root)

    request_fixture = fixture_root / "change_table_state.request-flow.json"
    request_fixture.write_text(
        json.dumps(
            {
                "cases": {
                    "loaded_direct_identifiers": {
                        "full_observed_flow": [
                            {
                                "purpose": "target-api",
                                "request": {
                                    "method": "PUT",
                                    "path": (
                                        "/casManagement/servers/cas-shared-default/"
                                        "caslibs/CASUSER/tables/SCORING_INPUT/state"
                                    ),
                                    "required_header_subset": {
                                        "Authorization": "Bearer fake-token",
                                        "Accept": "application/problem+json",
                                        "Content-Type": "application/json",
                                    },
                                    "query": {"value": "loaded"},
                                    "body": {
                                        "outputCaslibName": CASLIB,
                                        "outputTableName": TABLE_NAME,
                                    },
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
        name="casmanagement_tables.change_table_state.source_observed_header_drift",
        invoke=lambda: casmanagement_table_state_change_contract.client.change_table_state(
            caslib=CASLIB,
            table_name=TABLE_NAME,
        ),
        expected=RequestShape(
            method="PUT",
            path=(
                "/casManagement/servers/cas-shared-default/caslibs/"
                f"{CASLIB}/tables/{TABLE_NAME}/state"
            ),
            query={"value": "loaded"},
            body={
                "outputCaslibName": CASLIB,
                "outputTableName": TABLE_NAME,
            },
            required_headers={
                "Authorization": "Bearer ",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"state": "loaded"},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=("change_table_state.request-flow.json#loaded_direct_identifiers"),
            response_path=None,
        ),
    )

    with pytest.raises(
        AssertionError,
        match="Observed request headers drifted from source evidence",
    ):
        casmanagement_table_state_change_contract.run(mismatched_source_case)
