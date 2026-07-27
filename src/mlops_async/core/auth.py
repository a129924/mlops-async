from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import timedelta
from typing import Protocol, runtime_checkable

from mlops_async.core.token_endpoint_client import TokenEndpointClient
from mlops_async.core.token_storage import AccessToken, DEFAULT_EXPIRY_SKEW, TokenStorage

__all__ = [
    "AuthException",
    "AuthProvider",
    "TokenEndpointClient",
    "TokenFetchException",
    "TokenManager",
]


class AuthException(Exception):  # noqa: N818
    """Base exception for auth-layer failures.

    The established ``AuthException`` class name is retained for callers that
    observe exception names in logs, tracebacks, or serialized error records.
    """


class TokenFetchException(AuthException):
    """Token endpoint fetch/refresh failure."""


@runtime_checkable
class TokenEndpointClientProtocol(Protocol):
    """Internal collaborator that fetches or refreshes tokens via raw transport."""

    async def fetch_access_token(self) -> AccessToken: ...

    async def refresh_access_token(self, token: AccessToken) -> AccessToken: ...


def _token_fetch_exception_message(exc: Exception) -> str:
    details = str(exc)
    if details:
        return f"{type(exc).__name__}: {details}"
    return f"{type(exc).__name__} during token fetch/refresh"


class TokenManager:
    """Own token lifecycle decisions and in-process refresh coordination."""

    def __init__(
        self,
        storage: TokenStorage,
        fetcher: TokenEndpointClientProtocol,
        expiry_skew: timedelta = DEFAULT_EXPIRY_SKEW,
    ) -> None:
        """Store collaborators and the shared refresh policy."""
        self._storage = storage
        self._fetcher = fetcher
        self._expiry_skew = expiry_skew
        self._refresh_lock = asyncio.Lock()

    async def get_access_token(self) -> AccessToken:
        """Return a valid token, fetching or refreshing only when needed."""
        cached_token = self._storage.get_token()
        if cached_token is not None and not cached_token.is_expired(skew=self._expiry_skew):
            return cached_token

        async with self._refresh_lock:
            cached_token = self._storage.get_token()
            if cached_token is not None and not cached_token.is_expired(skew=self._expiry_skew):
                return cached_token

            return await self._resolve_token(cached_token)

    async def _resolve_token(self, cached_token: AccessToken | None) -> AccessToken:
        try:
            if cached_token is None:
                resolved_token = await self._fetcher.fetch_access_token()
            else:
                resolved_token = await self._fetcher.refresh_access_token(cached_token)
        except asyncio.CancelledError:
            raise
        except AuthException:
            raise
        except Exception as exc:
            raise TokenFetchException(_token_fetch_exception_message(exc)) from exc

        self._storage.set_token(resolved_token)
        return resolved_token


class AuthProvider:
    """Thin adapter that turns a managed access token into request headers."""

    def __init__(self, token_manager: TokenManager) -> None:
        """Store the token manager used to resolve managed auth headers."""
        self._token_manager = token_manager

    async def get_auth_headers(self) -> Mapping[str, str]:
        """Return authorization headers for a domain request."""
        access_token = await self._token_manager.get_access_token()
        return {"Authorization": f"Bearer {access_token.value}"}
