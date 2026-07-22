"""Readable request-contract tests for refresh_access_token."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.saslogon_refresh_token_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    SasLogonRefreshTokenContractHarness,
    _is_topic_scoped_pytest_run,
)

FIXTURE_ROOT = "tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures"
REFRESH_TOKEN = "refresh-token-abc-123"


def test_refresh_access_token_request_shape(
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
) -> None:
    case_refresh_access_token = EndpointContractCase(
        name="saslogon_token.refresh_access_token.refresh_token_basic",
        invoke=lambda: saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body=f"grant_type=refresh_token&refresh_token={REFRESH_TOKEN}",
            required_headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=(
                f"{FIXTURE_ROOT}/refresh_access_token.request-flow.json#refresh_token_basic"
            ),
            response_path=(
                f"{FIXTURE_ROOT}/refresh_access_token.mock-responses.json#refresh_token_basic"
            ),
        ),
    )

    result = saslogon_refresh_token_contract.run(case_refresh_access_token)

    assert isinstance(result, SimpleNamespace)
    assert saslogon_refresh_token_contract.last_request is not None
    assert saslogon_refresh_token_contract.last_request["method"] == "POST"
    assert saslogon_refresh_token_contract.last_request["path"] == "/SASLogon/oauth/token"
    assert saslogon_refresh_token_contract.last_request["query"] == {}
    assert (
        saslogon_refresh_token_contract.last_request["body"]
        == f"grant_type=refresh_token&refresh_token={REFRESH_TOKEN}"
    )


@pytest.mark.parametrize("refresh_token", [123, {"token": REFRESH_TOKEN}])
def test_refresh_access_token_blocks_non_string_refresh_token_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
    refresh_token: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty refresh_token string is allowed",
    ):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=refresh_token,
        )


@pytest.mark.parametrize("refresh_token", ["", "   "])
def test_refresh_access_token_blocks_blank_refresh_token_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
    refresh_token: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty refresh_token string is allowed",
    ):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=refresh_token,
        )


@pytest.mark.parametrize("grant_type", ["client_credentials", "authorization_code", 123])
def test_refresh_access_token_blocks_wrong_grant_type_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
    grant_type: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only grant_type='refresh_token' is allowed",
    ):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
            grant_type=grant_type,
        )


@pytest.mark.parametrize("scope", ["openid", "", ["openid"]])
def test_refresh_access_token_blocks_scope_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
    scope: object,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match="scope is blocked in this topic"):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
            scope=scope,
        )


def test_refresh_access_token_blocks_client_id_drift(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match="client_id is blocked in this topic"):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
            client_id="client-id-abc-123",
        )


def test_refresh_access_token_blocks_client_secret_drift(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match="client_secret is blocked in this topic"):
        saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
            client_secret="secret-value-xyz",
        )


def test_refresh_access_token_percent_encodes_reserved_characters_in_form_body(
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
) -> None:
    reserved_refresh_token = "refresh/token?draft=yes&retry=1"

    case_refresh_access_token_reserved_characters = EndpointContractCase(
        name="saslogon_token.refresh_access_token.percent_encoded_form_body",
        invoke=lambda: saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=reserved_refresh_token,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body=(
                "grant_type=refresh_token&refresh_token=refresh%2Ftoken%3Fdraft%3Dyes%26retry%3D1"
            ),
            required_headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    result = saslogon_refresh_token_contract.run(case_refresh_access_token_reserved_characters)

    assert isinstance(result, SimpleNamespace)
    assert saslogon_refresh_token_contract.last_request is not None
    assert (
        saslogon_refresh_token_contract.last_request["body"] == "grant_type=refresh_token"
        "&refresh_token=refresh%2Ftoken%3Fdraft%3Dyes%26retry%3D1"
    )


def test_refresh_access_token_interceptor_fails_fast_on_unregistered_request(
    saslogon_refresh_token_contract: SasLogonRefreshTokenContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="saslogon_token.refresh_access_token.unregistered_request",
        invoke=lambda: saslogon_refresh_token_contract.client.refresh_access_token(
            refresh_token=REFRESH_TOKEN,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body="grant_type=refresh_token",
            required_headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ),
        response=FakeResponse(
            status_code=200,
            json_body={},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        saslogon_refresh_token_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/saslogon_refresh_token_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False
