from __future__ import annotations

from base64 import b64decode
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import cast
from urllib.parse import parse_qsl, quote_plus, urlencode

import mlops_async.core.auth as auth
import mlops_async.core.token_endpoint.password as password_endpoint_mod
import mlops_async.core.token_storage as token_storage
import inspect
import pytest

from mlops_async.core.token_endpoint.password import PasswordTokenEndpointClient
from mlops_async.core.token_endpoint_client import TokenEndpointClientError
from mlops_async.core.types import HttpMethod, JSONValue

_USERNAME = "test-user-name"
_PASSWORD = "test-user-password"
_CLIENT_ID = "test-client-id"
_CLIENT_SECRET = "test-client-secret"
_RESERVED_USERNAME = "test/user?draft=yes"
_RESERVED_PASSWORD = "test&password=1"
_RESERVED_CLIENT_ID = "test/client"
_RESERVED_CLIENT_SECRET = "test&client-secret=1"
_SAS_EC_CLIENT_ID = "sas.ec"


def test_password_token_flow_remains_outside_json_requester_and_value_objects() -> None:
    source = inspect.getsource(password_endpoint_mod)

    assert "Requester" not in source
    assert "HttpRequest" not in source


def _valid_token_payload() -> JSONValue:
    return {
        "access_token": "test-access-token",
        "expires_in": 3600,
        "refresh_token": "test-refresh-token",
    }


def _token_payload_without_refresh_token() -> JSONValue:
    return {"access_token": "test-access-token", "expires_in": 3600}


def _invalid_token_payload() -> JSONValue:
    return {"access_token": "test-access-token", "expires_in": True}


def _expired_token() -> token_storage.AccessToken:
    return token_storage.AccessToken(
        value="test-expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        refresh_token="stored-refresh-token",
    )


def _legacy_expired_token() -> token_storage.AccessToken:
    return token_storage.AccessToken(
        value="legacy-expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
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
        expected_basic_credentials: tuple[str, str],
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
    expected_credentials: tuple[str, str],
) -> bool:
    if authorization is None:
        return False

    scheme, separator, encoded_credentials = authorization.partition(" ")
    if scheme != "Basic" or not separator or not encoded_credentials:
        return False

    try:
        decoded_credentials = b64decode(encoded_credentials, validate=True).decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return False

    return decoded_credentials == ":".join(
        quote_plus(credential) for credential in expected_credentials
    )


def _credential_values_are_absent(
    message: str,
    *,
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
) -> bool:
    return not any(
        value and value in message for value in (username, password, client_id, client_secret)
    )


def _password_transport(*, responses: list[JSONValue]) -> _FakeTransport:
    return _FakeTransport(
        responses,
        expected_form=(
            ("grant_type", "password"),
            ("username", _USERNAME),
            ("password", _PASSWORD),
        ),
        expected_basic_credentials=(_CLIENT_ID, _CLIENT_SECRET),
    )


def _password_client(transport: _FakeTransport) -> PasswordTokenEndpointClient:
    return PasswordTokenEndpointClient(
        transport,
        username=_USERNAME,
        password=_PASSWORD,
        client_id=_CLIENT_ID,
        client_secret=_CLIENT_SECRET,
    )


@pytest.mark.asyncio
async def test_password_client_posts_the_locked_password_grant_contract() -> None:
    transport = _password_transport(responses=[_valid_token_payload()])
    client = _password_client(transport)

    await client.fetch_access_token()

    record = transport.requests[0]
    assert record.method.value == "POST"
    assert record.path == "/SASLogon/oauth/token"
    assert record.header_names == frozenset({"accept", "content-type", "authorization"})
    assert record.authorization_scheme == "Basic"
    assert record.basic_contract_is_valid
    assert record.form_field_names == ("grant_type", "username", "password")
    assert record.form_contract_is_valid
    assert record.form_encoding_is_valid


@pytest.mark.asyncio
async def test_password_client_encodes_reserved_user_credentials_without_form_client_credentials() -> (  # noqa: E501
    None
):
    expected_form = (
        ("grant_type", "password"),
        ("username", _RESERVED_USERNAME),
        ("password", _RESERVED_PASSWORD),
    )
    transport = _FakeTransport(
        [_valid_token_payload()],
        expected_form=expected_form,
        expected_basic_credentials=(_RESERVED_CLIENT_ID, _RESERVED_CLIENT_SECRET),
    )
    client = PasswordTokenEndpointClient(
        transport,
        username=expected_form[1][1],
        password=expected_form[2][1],
        client_id=_RESERVED_CLIENT_ID,
        client_secret=_RESERVED_CLIENT_SECRET,
    )

    await client.fetch_access_token()

    record = transport.requests[0]
    assert record.basic_contract_is_valid
    assert record.form_contract_is_valid
    assert record.form_encoding_is_valid
    assert record.form_field_names == ("grant_type", "username", "password")


@pytest.mark.asyncio
async def test_password_client_encodes_reserved_basic_credentials_per_rfc6749() -> None:
    transport = _FakeTransport(
        [_valid_token_payload()],
        expected_form=(
            ("grant_type", "password"),
            ("username", _USERNAME),
            ("password", _PASSWORD),
        ),
        expected_basic_credentials=(_RESERVED_CLIENT_ID, _RESERVED_CLIENT_SECRET),
    )
    client = PasswordTokenEndpointClient(
        transport,
        username=_USERNAME,
        password=_PASSWORD,
        client_id=_RESERVED_CLIENT_ID,
        client_secret=_RESERVED_CLIENT_SECRET,
    )

    await client.fetch_access_token()

    record = transport.requests[0]
    assert record.authorization_scheme == "Basic"
    assert record.basic_contract_is_valid


def test_password_client_rejects_blank_credentials_without_echoing_values() -> None:
    cases = (
        ("", _PASSWORD, _CLIENT_ID, _CLIENT_SECRET, "username"),
        ("  ", _PASSWORD, _CLIENT_ID, _CLIENT_SECRET, "username"),
        (_USERNAME, "", _CLIENT_ID, _CLIENT_SECRET, "password"),
        (_USERNAME, "  ", _CLIENT_ID, _CLIENT_SECRET, "password"),
        (_USERNAME, _PASSWORD, "", _CLIENT_SECRET, "client_id"),
        (_USERNAME, _PASSWORD, "  ", _CLIENT_SECRET, "client_id"),
        (_USERNAME, _PASSWORD, _CLIENT_ID, "", "client_secret"),
        (_USERNAME, _PASSWORD, _CLIENT_ID, "  ", "client_secret"),
    )

    for username, password, client_id, client_secret, field_name in cases:
        transport = _password_transport(responses=[])
        with pytest.raises(TokenEndpointClientError, match=field_name) as exc_info:
            PasswordTokenEndpointClient(
                transport,
                username=username,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
            )

        if not _credential_values_are_absent(
            str(exc_info.value),
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        ):
            pytest.fail("credential validation error exposed a secret")


@pytest.mark.asyncio
async def test_password_client_accepts_sas_ec_with_an_empty_secret() -> None:
    """Preserve sasctl's ``sas.ec`` plus empty-secret password-grant default."""
    transport = _FakeTransport(
        [_token_payload_without_refresh_token()],
        expected_form=(
            ("grant_type", "password"),
            ("username", _USERNAME),
            ("password", _PASSWORD),
        ),
        expected_basic_credentials=(_SAS_EC_CLIENT_ID, ""),
    )
    client = PasswordTokenEndpointClient(
        transport,
        username=_USERNAME,
        password=_PASSWORD,
        client_id=_SAS_EC_CLIENT_ID,
        client_secret="",
    )

    token = await client.fetch_access_token()

    record = transport.requests[0]
    assert record.authorization_scheme == "Basic"
    assert record.basic_contract_is_valid
    assert record.form_contract_is_valid
    assert token.refresh_token is None


@pytest.mark.parametrize(
    ("client_id", "client_secret"),
    (
        (_SAS_EC_CLIENT_ID, " "),
        (_SAS_EC_CLIENT_ID, "  "),
        (_CLIENT_ID, ""),
        (_CLIENT_ID, " "),
        (_CLIENT_ID, "  "),
    ),
)
def test_password_client_rejects_disallowed_empty_or_whitespace_secrets_without_echoing_values(
    client_id: str,
    client_secret: str,
) -> None:
    transport = _password_transport(responses=[])

    with pytest.raises(TokenEndpointClientError, match="client_secret") as exc_info:
        PasswordTokenEndpointClient(
            transport,
            username=_USERNAME,
            password=_PASSWORD,
            client_id=client_id,
            client_secret=client_secret,
        )

    assert str(exc_info.value) == "client_secret must be a non-empty string"


def test_password_client_rejects_non_string_credentials_without_echoing_values() -> None:
    cases = (
        (cast(str, 123), _PASSWORD, _CLIENT_ID, _CLIENT_SECRET, "username"),
        (_USERNAME, cast(str, None), _CLIENT_ID, _CLIENT_SECRET, "password"),
        (_USERNAME, _PASSWORD, cast(str, 456), _CLIENT_SECRET, "client_id"),
        (_USERNAME, _PASSWORD, _CLIENT_ID, cast(str, None), "client_secret"),
    )

    for username, password, client_id, client_secret, field_name in cases:
        transport = _password_transport(responses=[])

        with pytest.raises(TokenEndpointClientError) as exc_info:
            PasswordTokenEndpointClient(
                transport,
                username=username,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
            )

        assert str(exc_info.value) == f"{field_name} must be a non-empty string"


@pytest.mark.asyncio
async def test_password_client_rejects_invalid_token_payload() -> None:
    transport = _password_transport(responses=[_invalid_token_payload()])
    client = _password_client(transport)

    with pytest.raises(TokenEndpointClientError):
        await client.fetch_access_token()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    (
        {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "refresh_token": None,
        },
        {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "refresh_token": "",
        },
        {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "refresh_token": "   ",
        },
        {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "refresh_token": 123,
        },
    ),
)
async def test_password_client_rejects_present_malformed_obtain_refresh_token(
    payload: JSONValue,
) -> None:
    transport = _password_transport(responses=[payload])
    client = _password_client(transport)

    with pytest.raises(TokenEndpointClientError, match="refresh_token"):
        await client.fetch_access_token()


@pytest.mark.asyncio
async def test_password_client_allows_an_omitted_obtain_refresh_token() -> None:
    transport = _password_transport(responses=[_token_payload_without_refresh_token()])
    client = _password_client(transport)

    token = await client.fetch_access_token()

    assert token.value == "test-access-token"
    assert token.refresh_token is None


@pytest.mark.asyncio
async def test_password_client_refreshes_with_refresh_grant_and_existing_auth_headers() -> None:
    transport = _FakeTransport(
        [_valid_token_payload()],
        expected_form=(
            ("grant_type", "refresh_token"),
            ("refresh_token", "stored-refresh-token"),
        ),
        expected_basic_credentials=(_CLIENT_ID, _CLIENT_SECRET),
    )
    client = _password_client(transport)
    previous_token = _expired_token()

    refreshed_token = await client.refresh_access_token(previous_token)

    assert refreshed_token.value == "test-access-token"
    assert refreshed_token.refresh_token == "test-refresh-token"
    assert len(transport.requests) == 1
    record = transport.requests[0]
    assert record.header_names == frozenset({"accept", "content-type", "authorization"})
    assert record.authorization_scheme == "Basic"
    assert record.basic_contract_is_valid
    assert record.form_field_names == ("grant_type", "refresh_token")
    assert record.form_contract_is_valid
    assert record.form_encoding_is_valid


@pytest.mark.asyncio
async def test_password_client_preserves_refresh_token_when_response_omits_it() -> None:
    transport = _FakeTransport(
        [{"access_token": "replacement-access-token", "expires_in": 1800}],
        expected_form=(
            ("grant_type", "refresh_token"),
            ("refresh_token", "stored-refresh-token"),
        ),
        expected_basic_credentials=(_CLIENT_ID, _CLIENT_SECRET),
    )
    client = _password_client(transport)

    refreshed_token = await client.refresh_access_token(_expired_token())

    assert refreshed_token.value == "replacement-access-token"
    assert refreshed_token.refresh_token == "stored-refresh-token"


@pytest.mark.asyncio
async def test_password_client_reobtains_with_password_grant_when_legacy_token_has_no_refresh_token() -> (  # noqa: E501
    None
):
    transport = _password_transport(responses=[_valid_token_payload()])
    client = _password_client(transport)

    refreshed_token = await client.refresh_access_token(_legacy_expired_token())

    assert refreshed_token.value == "test-access-token"
    assert refreshed_token.refresh_token == "test-refresh-token"
    assert len(transport.requests) == 1
    assert transport.requests[0].form_contract_is_valid
    assert transport.requests[0].form_field_names == ("grant_type", "username", "password")


@pytest.mark.asyncio
@pytest.mark.parametrize("refresh_token", ("   ", 123))
async def test_password_client_rejects_malformed_refresh_response_refresh_token(
    refresh_token: JSONValue,
) -> None:
    transport = _FakeTransport(
        [
            {
                "access_token": "replacement-access-token",
                "expires_in": 1800,
                "refresh_token": refresh_token,
            }
        ],
        expected_form=(
            ("grant_type", "refresh_token"),
            ("refresh_token", "stored-refresh-token"),
        ),
        expected_basic_credentials=(_CLIENT_ID, _CLIENT_SECRET),
    )
    client = _password_client(transport)

    with pytest.raises(TokenEndpointClientError, match="refresh_token"):
        await client.refresh_access_token(_expired_token())


@pytest.mark.asyncio
async def test_password_client_structurally_conforms_to_token_endpoint_protocol() -> None:
    transport = _password_transport(responses=[_valid_token_payload()])
    client = _password_client(transport)

    assert isinstance(client, auth.TokenEndpointClientProtocol)


@pytest.mark.asyncio
async def test_token_manager_refreshes_expired_token_through_password_client_protocol() -> None:
    transport = _FakeTransport(
        [_valid_token_payload()],
        expected_form=(
            ("grant_type", "refresh_token"),
            ("refresh_token", "stored-refresh-token"),
        ),
        expected_basic_credentials=(_CLIENT_ID, _CLIENT_SECRET),
    )
    client = _password_client(transport)
    expired_token = _expired_token()
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(expired_token)
    manager = auth.TokenManager(storage, client)

    resolved = await manager.get_access_token()

    assert resolved is storage.get_token()
    assert resolved is not expired_token
    assert resolved.refresh_token == "test-refresh-token"
    assert len(transport.requests) == 1
    assert transport.requests[0].form_contract_is_valid


@pytest.mark.asyncio
async def test_token_manager_fetches_when_legacy_expired_token_has_no_refresh_token() -> None:
    transport = _password_transport(responses=[_valid_token_payload()])
    client = _password_client(transport)
    storage = token_storage.InMemoryTokenStorage()
    storage.set_token(_legacy_expired_token())
    manager = auth.TokenManager(storage, client)

    resolved = await manager.get_access_token()

    assert resolved is storage.get_token()
    assert resolved.value == "test-access-token"
    assert resolved.refresh_token == "test-refresh-token"
    assert len(transport.requests) == 1
    assert transport.requests[0].form_contract_is_valid
    assert transport.requests[0].form_field_names == ("grant_type", "username", "password")
