from __future__ import annotations

from collections.abc import Mapping

from mlops_async.core.auth import AuthException, AuthProvider
from mlops_async.core.client import Client
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = ["AuthorizationConflictException", "Requester"]


class AuthorizationConflictException(AuthException):
    """Caller supplied an Authorization header while auth is managed."""


def _merge_headers(*mappings: Mapping[str, str] | None) -> dict[str, str]:
    merged: dict[str, tuple[str, str]] = {}
    for mapping in mappings:
        if mapping is None:
            continue

        for name, value in mapping.items():
            merged[name.lower()] = (name, value)

    return dict(merged.values())


class Requester:
    """Internal request-composition layer above the transport client."""

    def __init__(
        self,
        transport: Client,
        *,
        auth_provider: AuthProvider | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Store transport and optional auth/header composition defaults."""
        self._transport = transport
        self._auth_provider = auth_provider
        self._default_headers = dict(default_headers or {})

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        """Compose final request headers, then delegate to transport."""
        if (
            self._auth_provider is not None
            and headers is not None
            and any(name.lower() == "authorization" for name in headers)
        ):
            raise AuthorizationConflictException(
                "Authorization header is managed by AuthProvider when configured"
            )

        auth_headers = None
        if self._auth_provider is not None:
            auth_headers = await self._auth_provider.get_auth_headers()
        request_headers = _merge_headers(
            {"Accept": "application/json"},
            self._default_headers,
            auth_headers,
            headers,
        )
        if json_body is not None and not any(
            name.lower() == "content-type" for name in request_headers
        ):
            request_headers["Content-Type"] = "application/json"

        return await self._transport.request(
            method,
            path,
            headers=request_headers,
            params=params,
            json_body=json_body,
            content=content,
            options=options,
        )
