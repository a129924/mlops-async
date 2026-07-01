"""Readable request-contract tests for obtain_access_token."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.saslogon_token_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    SasLogonTokenContractHarness,
    _is_topic_scoped_pytest_run,
)

FIXTURE_ROOT = "tests/unit/request_contract/saslogon_token_request_gate/fixtures"
CLIENT_ID = "client-id-abc-123"
CLIENT_SECRET = "secret-value-xyz"


def test_obtain_access_token_client_credentials_request_shape(
    saslogon_token_contract: SasLogonTokenContractHarness,
) -> None:
    case_obtain_access_token_client_credentials = EndpointContractCase(
        name="saslogon_token.obtain_access_token.client_credentials_basic",
        invoke=lambda: saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body=(
                "grant_type=client_credentials"
                f"&client_id={CLIENT_ID}"
                f"&client_secret={CLIENT_SECRET}"
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
        source_observed=SourceObservedFixture(
            request_path=(
                f"{FIXTURE_ROOT}/obtain_access_token.request-flow.json"
                "#client_credentials_basic"
            ),
            response_path=(
                f"{FIXTURE_ROOT}/obtain_access_token.mock-responses.json"
                "#client_credentials_basic"
            ),
        ),
    )

    result = saslogon_token_contract.run(case_obtain_access_token_client_credentials)

    assert isinstance(result, SimpleNamespace)
    assert saslogon_token_contract.last_request is not None
    assert saslogon_token_contract.last_request["method"] == "POST"
    assert saslogon_token_contract.last_request["path"] == "/SASLogon/oauth/token"
    assert saslogon_token_contract.last_request["query"] == {}
    assert (
        saslogon_token_contract.last_request["body"]
        == "grant_type=client_credentials"
        f"&client_id={CLIENT_ID}"
        f"&client_secret={CLIENT_SECRET}"
    )


@pytest.mark.parametrize("client_id", [123, {"id": CLIENT_ID}])
def test_obtain_access_token_blocks_non_string_client_id_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    client_id: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty client_id string is allowed",
    ):
        saslogon_token_contract.client.obtain_access_token(
            client_id=client_id,
            client_secret=CLIENT_SECRET,
        )


@pytest.mark.parametrize("client_id", ["", "   "])
def test_obtain_access_token_blocks_blank_client_id_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    client_id: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty client_id string is allowed",
    ):
        saslogon_token_contract.client.obtain_access_token(
            client_id=client_id,
            client_secret=CLIENT_SECRET,
        )


@pytest.mark.parametrize("client_secret", [123, {"secret": CLIENT_SECRET}])
def test_obtain_access_token_blocks_non_string_client_secret_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    client_secret: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty client_secret string is allowed",
    ):
        saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=client_secret,
        )


@pytest.mark.parametrize("client_secret", ["", "   "])
def test_obtain_access_token_blocks_blank_client_secret_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    client_secret: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty client_secret string is allowed",
    ):
        saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=client_secret,
        )


@pytest.mark.parametrize(
    "grant_type",
    [
        "authorization_code",
        "refresh_token",
        123,
    ],
)
def test_obtain_access_token_blocks_wrong_grant_type_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    grant_type: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only grant_type='client_credentials' is allowed",
    ):
        saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            grant_type=grant_type,
        )


@pytest.mark.parametrize("scope", ["openid", "", ["openid"]])
def test_obtain_access_token_blocks_scope_variants(
    blocked_topic_scope_error: type[RuntimeError],
    saslogon_token_contract: SasLogonTokenContractHarness,
    scope: object,
) -> None:
    with pytest.raises(blocked_topic_scope_error, match="scope is blocked in this topic"):
        saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=scope,
        )


def test_obtain_access_token_percent_encodes_reserved_characters_in_form_body(
    saslogon_token_contract: SasLogonTokenContractHarness,
) -> None:
    reserved_client_id = "client/id?draft=yes"
    reserved_client_secret = "secret&value=1"

    case_obtain_access_token_reserved_characters = EndpointContractCase(
        name="saslogon_token.obtain_access_token.percent_encoded_form_body",
        invoke=lambda: saslogon_token_contract.client.obtain_access_token(
            client_id=reserved_client_id,
            client_secret=reserved_client_secret,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body=(
                "grant_type=client_credentials"
                "&client_id=client%2Fid%3Fdraft%3Dyes"
                "&client_secret=secret%26value%3D1"
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

    result = saslogon_token_contract.run(case_obtain_access_token_reserved_characters)

    assert isinstance(result, SimpleNamespace)
    assert saslogon_token_contract.last_request is not None
    assert (
        saslogon_token_contract.last_request["body"]
        == "grant_type=client_credentials"
        "&client_id=client%2Fid%3Fdraft%3Dyes"
        "&client_secret=secret%26value%3D1"
    )


def test_obtain_access_token_interceptor_fails_fast_on_unregistered_request(
    saslogon_token_contract: SasLogonTokenContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="saslogon_token.obtain_access_token.unregistered_request",
        invoke=lambda: saslogon_token_contract.client.obtain_access_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ),
        expected=RequestShape(
            method="POST",
            path="/SASLogon/oauth/token",
            query={},
            body="grant_type=client_credentials",
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
        saslogon_token_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/saslogon_token_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False
