from __future__ import annotations

from base64 import b64decode
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast
from urllib.parse import parse_qsl, urlencode

import pytest

from mlops_async.core.token_endpoint._shared import (
    AuthTokenEndpoint,
    TokenEndpointClientError,
    TokenEndpointClientException,
)
from mlops_async.core.token_endpoint.client_credentials import TokenEndpointClient
from mlops_async.core.token_endpoint_client import (
    AuthTokenEndpoint as CompatibilityAuthTokenEndpoint,
)
from mlops_async.core.token_endpoint_client import (
    TokenEndpointClient as CompatibilityTokenEndpointClient,
)
from mlops_async.core.token_endpoint_client import (
    TokenEndpointClientError as CompatibilityTokenEndpointClientError,
)
from mlops_async.core.token_endpoint_client import (
    TokenEndpointClientException as CompatibilityTokenEndpointClientException,
)
from mlops_async.core.types import HttpMethod, JSONValue

_CLIENT_ID = "test-client-id"
_CLIENT_SECRET = "test-client-secret"
_RESERVED_CLIENT_ID = "test/client?draft=yes"
_SAS_EC_CLIENT_ID = "sas.ec"
_RESERVED_CLIENT_SECRET = "test-client&secret=1"


def _valid_token_payload() -> JSONValue:
    return {"access_token": "test-access-token", "expires_in": 3600}


def _invalid_token_payloads() -> tuple[JSONValue, ...]:
    return (
        ["unexpected"],
        {"expires_in": 3600},
        {"access_token": "", "expires_in": 3600},
        {"access_token": "test-access-token"},
        {"access_token": "test-access-token", "expires_in": 0},
        {"access_token": "test-access-token", "expires_in": -1},
        {"access_token": "test-access-token", "expires_in": "3600"},
        {"access_token": "test-access-token", "expires_in": True},
    )


@dataclass(frozen=True)
class _RecordedRequest:
    method: HttpMethod
    path: str
    header_names: frozenset[str]
    authorization_scheme: str | None
    form_field_names: tuple[str, ...]
    basic_contract_is_valid: bool
    form_contract_is_valid: bool
    form_encoding_is_valid: bool


class _FakeTransport:
    def __init__(
        self,
        responses: list[JSONValue],
        *,
        expected_form: tuple[tuple[str, str], ...],
        expected_basic_credentials: tuple[str, str] | None = None,
    ) -> None:
        self._responses = responses
        self._expected_form = expected_form
        self._expected_basic_credentials = expected_basic_credentials
        self.requests: list[_RecordedRequest] = []

    async def request_json(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: object | None = None,
    ) -> JSONValue:
        del params, json_body, options
        request_headers = {} if headers is None else headers
        authorization = next(
            (value for name, value in request_headers.items() if name.lower() == "authorization"),
            None,
        )
        form_content = b"" if content is None else content
        parsed_form = tuple(parse_qsl(form_content.decode("utf-8"), keep_blank_values=True))
        self.requests.append(
            _RecordedRequest(
                method=method,
                path=path,
                header_names=frozenset(request_headers),
                authorization_scheme=_authorization_scheme(authorization),
                form_field_names=tuple(name for name, _ in parsed_form),
                basic_contract_is_valid=_basic_credentials_match(
                    authorization,
                    self._expected_basic_credentials,
                ),
                form_contract_is_valid=parsed_form == self._expected_form,
                form_encoding_is_valid=(
                    form_content == urlencode(self._expected_form).encode("utf-8")
                ),
            )
        )
        if not self._responses:
            raise AssertionError("fake transport response was not configured")
        return self._responses.pop(0)


def _authorization_scheme(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    return authorization.partition(" ")[0]


def _basic_credentials_match(
    authorization: str | None,
    expected_credentials: tuple[str, str] | None,
) -> bool:
    if expected_credentials is None:
        return authorization is None
    if authorization is None:
        return False

    scheme, separator, encoded_credentials = authorization.partition(" ")
    if scheme != "Basic" or not separator or not encoded_credentials:
        return False

    try:
        decoded_credentials = b64decode(encoded_credentials, validate=True).decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return False

    return decoded_credentials == ":".join(expected_credentials)


def _client_credentials_transport(*, responses: list[JSONValue]) -> _FakeTransport:
    return _FakeTransport(
        responses,
        expected_form=(
            ("grant_type", "client_credentials"),
            ("client_id", _CLIENT_ID),
            ("client_secret", _CLIENT_SECRET),
        ),
    )


def test_compatibility_module_reexports_the_migrated_client_credentials_contract() -> None:
    assert CompatibilityAuthTokenEndpoint is AuthTokenEndpoint
    assert CompatibilityTokenEndpointClient is TokenEndpointClient
    assert CompatibilityTokenEndpointClientError is TokenEndpointClientError
    assert CompatibilityTokenEndpointClientException is TokenEndpointClientException


@pytest.mark.asyncio
async def test_client_credentials_client_preserves_existing_request_contract() -> None:
    transport = _client_credentials_transport(responses=[_valid_token_payload()])
    client = TokenEndpointClient(
        transport,
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET,
    )

    await client.fetch_access_token()

    assert client.endpoint is CompatibilityAuthTokenEndpoint.OAUTH_TOKEN
    assert transport.requests == [
        _RecordedRequest(
            method=HttpMethod.POST,
            path="/SASLogon/oauth/token",
            header_names=frozenset({"Accept", "Content-Type"}),
            authorization_scheme=None,
            form_field_names=("grant_type", "client_id", "client_secret"),
            basic_contract_is_valid=True,
            form_contract_is_valid=True,
            form_encoding_is_valid=True,
        )
    ]


@pytest.mark.asyncio
async def test_client_credentials_client_percent_encodes_reserved_characters() -> None:
    expected_form = (
        ("grant_type", "client_credentials"),
        ("client_id", _RESERVED_CLIENT_ID),
        ("client_secret", _RESERVED_CLIENT_SECRET),
    )
    transport = _FakeTransport(
        [_valid_token_payload()],
        expected_form=expected_form,
    )
    client = TokenEndpointClient(
        transport,
        client_id=expected_form[1][1],
        client_secret=expected_form[2][1],
    )

    await client.fetch_access_token()

    assert transport.requests[0].form_contract_is_valid
    assert transport.requests[0].form_encoding_is_valid


@pytest.mark.asyncio
async def test_client_credentials_refresh_reuses_mvp_obtain_path() -> None:
    transport = _client_credentials_transport(
        responses=[_valid_token_payload(), _valid_token_payload()]
    )
    client = TokenEndpointClient(
        transport,
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET,
    )

    initial_token = await client.fetch_access_token()
    refreshed_token = await client.refresh_access_token(initial_token)

    assert refreshed_token is not initial_token
    assert len(transport.requests) == 2
    assert all(record.form_contract_is_valid for record in transport.requests)


@pytest.mark.asyncio
async def test_client_credentials_client_rejects_invalid_token_payloads() -> None:
    for payload in _invalid_token_payloads():
        transport = _client_credentials_transport(responses=[payload])
        client = TokenEndpointClient(
            transport,
            client_id=_CLIENT_ID,
            client_secret=_CLIENT_SECRET,
        )

        with pytest.raises(CompatibilityTokenEndpointClientError):
            await client.fetch_access_token()


def test_client_credentials_client_rejects_blank_credentials() -> None:
    cases = (
        ("", _CLIENT_SECRET, "client_id"),
        ("  ", _CLIENT_SECRET, "client_id"),
        (_CLIENT_ID, "", "client_secret"),
        (_CLIENT_ID, "  ", "client_secret"),
    )

    for client_id, client_secret, field_name in cases:
        transport = _client_credentials_transport(responses=[])
        with pytest.raises(CompatibilityTokenEndpointClientError, match=field_name):
            TokenEndpointClient(
                transport,
                client_id=client_id,
                client_secret=client_secret,
            )


@pytest.mark.parametrize("client_secret", ("", " ", "  "))
def test_client_credentials_client_rejects_sas_ec_without_a_non_empty_secret(
    client_secret: str,
) -> None:
    transport = _client_credentials_transport(responses=[])

    with pytest.raises(CompatibilityTokenEndpointClientError, match="client_secret"):
        TokenEndpointClient(
            transport,
            client_id=_SAS_EC_CLIENT_ID,
            client_secret=client_secret,
        )


def test_client_credentials_client_rejects_non_string_credentials() -> None:
    cases = (
        (cast(str, 123), _CLIENT_SECRET, "client_id"),
        (_CLIENT_ID, cast(str, None), "client_secret"),
    )

    for client_id, client_secret, field_name in cases:
        transport = _client_credentials_transport(responses=[])

        with pytest.raises(CompatibilityTokenEndpointClientError) as exc_info:
            TokenEndpointClient(
                transport,
                client_id=client_id,
                client_secret=client_secret,
            )

        assert str(exc_info.value) == f"{field_name} must be a non-empty string"
