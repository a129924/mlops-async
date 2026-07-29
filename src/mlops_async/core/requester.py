from __future__ import annotations

from collections.abc import Mapping

from mlops_async.core.auth import AuthException, AuthProvider
from mlops_async.core.client import Client
from mlops_async.core.headers import json_request_headers
from mlops_async.core.http_request import Headers, HttpRequest, JsonBody
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = ["AuthorizationConflictException", "Requester"]


class AuthorizationConflictException(AuthException):
    """Caller supplied an Authorization header while auth is managed."""


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
        request_headers = json_request_headers(
            self._default_headers,
            auth_headers,
            headers,
            json_body=json_body,
        )

        return await self._transport.request(
            method,
            path,
            headers=request_headers,
            params=params,
            json_body=json_body,
            content=content,
            options=options,
        )

    async def execute(self, request: HttpRequest) -> RawClientResponse:
        """Compose immutable JSON-domain headers, then execute a canonical request."""
        if request.body is not None and not isinstance(request.body, JsonBody):
            raise ValueError("Requester.execute accepts JSON-domain requests only")
        if (
            self._auth_provider is not None
            and "authorization" in request.headers.as_dict()
        ):
            raise AuthorizationConflictException(
                "Authorization header is managed by AuthProvider when configured"
            )

        auth_headers = None
        if self._auth_provider is not None:
            auth_headers = await self._auth_provider.get_auth_headers()
        header_policy_body = request.json_body
        if isinstance(request.body, JsonBody) and header_policy_body is None:
            header_policy_body = {}
        request_headers = json_request_headers(
            self._default_headers,
            auth_headers,
            request.headers.as_dict(),
            json_body=header_policy_body,
        )
        composed_request = HttpRequest(
            method=request.method,
            base_url=request.base_url,
            endpoint_path=request.endpoint_path,
            query=request.query,
            headers=Headers.create(request_headers),
            body=request.body,
            options=request.options,
        )
        return await self._transport.execute(composed_request)
