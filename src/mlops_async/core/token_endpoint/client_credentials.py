"""Client-credentials implementation for the token endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

from mlops_async.core.client import Client
from mlops_async.core.headers import token_request_headers
from mlops_async.core.token_endpoint._shared import (
    AuthTokenEndpoint,
    access_token_from_response,
    parse_token_response,
    require_non_empty_string,
)
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod


class TokenEndpointClient:
    """Concrete collaborator that obtains tokens with client credentials."""

    def __init__(
        self,
        transport: Client,
        *,
        client_id: str,
        client_secret: str,
        endpoint: AuthTokenEndpoint = AuthTokenEndpoint.OAUTH_TOKEN,
    ) -> None:
        """Store raw transport, credentials, and the token endpoint identifier."""
        self._transport = transport
        self._client_id = require_non_empty_string(client_id, field_name="client_id")
        self._client_secret = require_non_empty_string(client_secret, field_name="client_secret")
        self._endpoint = endpoint

    @property
    def endpoint(self) -> AuthTokenEndpoint:
        """Return the token-endpoint identifier used by this collaborator."""
        return self._endpoint

    async def fetch_access_token(self) -> AccessToken:
        """Obtain an access token through the canonical client-credentials path."""
        response = await self._transport.request_json(
            HttpMethod.POST,
            self._endpoint.value,
            headers=token_request_headers(),
            content=self._form_body_for_client_credentials(),
        )
        return access_token_from_response(
            parse_token_response(response),
            now=datetime.now(timezone.utc),
        )

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        """Renew a token using the MVP obtain path until refresh grant work exists."""
        del token
        return await self.fetch_access_token()

    def _form_body_for_client_credentials(self) -> bytes:
        return urlencode(
            (
                ("grant_type", "client_credentials"),
                ("client_id", self._client_id),
                ("client_secret", self._client_secret),
            )
        ).encode("utf-8")
