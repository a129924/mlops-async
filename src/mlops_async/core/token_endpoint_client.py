from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from urllib.parse import urlencode

from mlops_async.core.client import Client
from mlops_async.core.headers import token_request_headers
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod, JSONValue

__all__ = [
    "AuthTokenEndpoint",
    "TokenEndpointClient",
    "TokenEndpointClientError",
    "TokenEndpointClientException",
]


class TokenEndpointClientError(ValueError):
    """Raised when token endpoint inputs or outputs are invalid."""


TokenEndpointClientException = TokenEndpointClientError


class AuthTokenEndpoint(str, Enum):
    """Token collaborator-local endpoint identifiers."""

    OAUTH_TOKEN = "/SASLogon/oauth/token"


@dataclass(frozen=True, slots=True)
class _TokenResponse:
    access_token: str
    expires_in: int


class TokenEndpointClient:
    """Concrete collaborator that talks to the token endpoint via raw transport."""

    def __init__(
        self,
        transport: Client,
        *,
        client_id: str,
        client_secret: str,
        endpoint: AuthTokenEndpoint = AuthTokenEndpoint.OAUTH_TOKEN,
    ) -> None:
        """Store raw transport, credentials, and the shared token endpoint identifier."""
        self._transport = transport
        self._client_id = _require_non_empty_string(client_id, field_name="client_id")
        self._client_secret = _require_non_empty_string(client_secret, field_name="client_secret")
        self._endpoint = endpoint

    @property
    def endpoint(self) -> AuthTokenEndpoint:
        """Return the shared token-endpoint identifier used by this collaborator."""
        return self._endpoint

    async def fetch_access_token(self) -> AccessToken:
        """Obtain an access token through the canonical client-credentials path."""
        response = await self._transport.request_json(
            HttpMethod.POST,
            self._endpoint.value,
            headers=token_request_headers(),
            content=self._form_body_for_client_credentials(),
        )
        token_response = _parse_token_response(response)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response.expires_in)
        return AccessToken(value=token_response.access_token, expires_at=expires_at)

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


def _require_non_empty_string(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TokenEndpointClientError(f"{field_name} must be a non-empty string")
    return value


def _parse_token_response(payload: JSONValue) -> _TokenResponse:
    if not isinstance(payload, dict):
        raise TokenEndpointClientError("token response must be a JSON object")

    access_token = payload.get("access_token")
    expires_in = payload.get("expires_in")

    if not isinstance(access_token, str) or not access_token:
        raise TokenEndpointClientError("token response must include a non-empty access_token")
    if not isinstance(expires_in, int) or isinstance(expires_in, bool) or expires_in <= 0:
        raise TokenEndpointClientError(
            "token response must include a positive expires_in integer"
        )

    return _TokenResponse(access_token=access_token, expires_in=expires_in)
