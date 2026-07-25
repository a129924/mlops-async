"""Direct access-token retrieval client."""

from __future__ import annotations

from mlops_async.core.auth import TokenEndpointClientProtocol
from mlops_async.core.token_storage import AccessToken


class AuthClient:
    """Expose direct access-token retrieval through an injected collaborator."""

    def __init__(self, token_endpoint_client: TokenEndpointClientProtocol) -> None:
        """Store the token-endpoint collaborator supplied by the application."""
        self._token_endpoint_client = token_endpoint_client

    async def get_access_token(self) -> AccessToken:
        """Return the access token fetched by the collaborator."""
        return await self._token_endpoint_client.fetch_access_token()
