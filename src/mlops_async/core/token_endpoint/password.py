"""Password-grant implementation for the token endpoint."""

from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timezone
from urllib.parse import quote_plus, urlencode

from mlops_async.core.client import Client
from mlops_async.core.headers import token_request_headers
from mlops_async.core.token_endpoint._shared import (
    AuthTokenEndpoint,
    access_token_from_response,
    parse_token_response,
    require_non_empty_string,
    require_password_client_secret,
)
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod


class PasswordTokenEndpointClient:
    """Concrete collaborator that obtains tokens with the password grant."""

    def __init__(
        self,
        transport: Client,
        *,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        endpoint: AuthTokenEndpoint = AuthTokenEndpoint.OAUTH_TOKEN,
    ) -> None:
        """Store injected transport and password-grant credentials."""
        self._transport = transport
        self._username = require_non_empty_string(username, field_name="username")
        self._password = require_non_empty_string(password, field_name="password")
        self._client_id = require_non_empty_string(client_id, field_name="client_id")
        self._client_secret = require_password_client_secret(
            client_secret,
            client_id=self._client_id,
        )
        self._endpoint = endpoint

    @property
    def endpoint(self) -> AuthTokenEndpoint:
        """Return the token-endpoint identifier used by this collaborator."""
        return self._endpoint

    async def fetch_access_token(self) -> AccessToken:
        """Obtain an access token through the OAuth password grant."""
        response = await self._transport.request_json(
            HttpMethod.POST,
            self._endpoint.value,
            headers=token_request_headers({"Authorization": self._basic_authorization()}),
            content=self._form_body_for_password_grant(),
        )
        return access_token_from_response(
            parse_token_response(response),
            now=datetime.now(timezone.utc),
        )

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        """Renew a token by repeating the password obtain path for this MVP."""
        del token
        return await self.fetch_access_token()

    def _basic_authorization(self) -> str:
        credentials = (
            f"{quote_plus(self._client_id)}:{quote_plus(self._client_secret)}"
        ).encode("ascii")
        return f"Basic {b64encode(credentials).decode('ascii')}"

    def _form_body_for_password_grant(self) -> bytes:
        return urlencode(
            (
                ("grant_type", "password"),
                ("username", self._username),
                ("password", self._password),
            )
        ).encode("utf-8")
