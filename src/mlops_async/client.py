from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType

import httpx

from mlops_async.core.auth import AuthProvider, TokenManager
from mlops_async.core.request_options import RequestTimeouts
from mlops_async.core.requester import Requester
from mlops_async.core.token_endpoint_client import TokenEndpointClient
from mlops_async.core.token_storage import InMemoryTokenStorage
from mlops_async.endpoints import TablesClient
from mlops_async.transport.http_client import HttpClient

__all__ = ["PackageLevelClient"]

_DEFAULT_TIMEOUTS = RequestTimeouts()


class PackageLevelClient:
    """Bounded public composition root for the tables runtime MVP."""

    def __init__(
        self,
        base_url: str | httpx.URL,
        *,
        client_id: str,
        client_secret: str,
        timeout: RequestTimeouts = _DEFAULT_TIMEOUTS,
        verify: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Wire shared transport, managed auth, and the tables family client."""
        self._http_client = HttpClient(
            base_url,
            timeout=timeout,
            verify=verify,
            transport=transport,
        )
        self._token_storage = InMemoryTokenStorage()
        self._token_endpoint_client = TokenEndpointClient(
            self._http_client,
            client_id=client_id,
            client_secret=client_secret,
        )
        self._token_manager = TokenManager(
            self._token_storage,
            self._token_endpoint_client,
        )
        self._auth_provider = AuthProvider(self._token_manager)
        self._requester = Requester(
            self._http_client,
            auth_provider=self._auth_provider,
            default_headers=default_headers,
        )

        self.tables = TablesClient(self._requester)

    async def aclose(self) -> None:
        """Close resources owned by the package-level client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> PackageLevelClient:
        """Return the wired client without prefetching tokens."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close owned transport resources when leaving the async context."""
        del exc_type, exc, traceback
        await self.aclose()
