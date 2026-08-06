"""Direct access-token retrieval client."""

from __future__ import annotations

import asyncio

from mlops_async.core.auth import (
    AuthException,
    TokenEndpointClientProtocol,
    TokenEndpointFetchClientProtocol,
)
from mlops_async.core.token_storage import AccessToken


class AuthClientRefreshTokenError(AuthException):
    """Raised when an access token cannot be refreshed through AuthClient."""


class AuthClient:
    """Expose direct access-token retrieval through an injected collaborator."""

    def __init__(self, token_endpoint_client: TokenEndpointFetchClientProtocol) -> None:
        """Store the token-endpoint collaborator supplied by the application."""
        self._token_endpoint_client = token_endpoint_client

    async def get_access_token(self) -> AccessToken:
        """Return the access token fetched by the collaborator."""
        return await self._token_endpoint_client.fetch_access_token()

    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        """Return a refreshed access token or fetch one when no refresh token exists."""
        if token.refresh_token is None:
            return await self._token_endpoint_client.fetch_access_token()

        if not isinstance(self._token_endpoint_client, TokenEndpointClientProtocol):
            raise AuthClientRefreshTokenError(
                "The configured token endpoint client cannot refresh access tokens"
            )

        try:
            return await self._token_endpoint_client.refresh_access_token(token)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise AuthClientRefreshTokenError(
                "Unable to refresh the access token through the configured token endpoint client"
            ) from exc
