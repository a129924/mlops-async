"""Raw auth and header composition for domain requests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from mlops_async.core.auth import AuthException
from mlops_async.core.client import Client
from mlops_async.core.headers import json_request_headers
from mlops_async.core.http_request import Headers, HttpRequest, JsonBody
from mlops_async.core.request_execution import (
    AuthRecoveryAttempt,
    AuthRecoveryExecutor,
    RequestInvocation,
)
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = ["AuthorizationConflictException", "Requester"]


@runtime_checkable
class _AuthHeadersProvider(Protocol):
    """Minimal auth collaborator accepted by the requester boundary."""

    async def get_auth_headers(self) -> Mapping[str, str]: ...


@runtime_checkable
class _AuthRecoveryProvider(_AuthHeadersProvider, Protocol):
    """Auth collaborator that can identify and conditionally refresh a token."""

    async def get_auth_headers_and_token(self) -> tuple[Mapping[str, str], AccessToken]: ...

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None: ...


class AuthorizationConflictException(AuthException):
    """Caller supplied an Authorization header while auth is managed."""


class Requester(AuthRecoveryExecutor):
    """Raw request-composition executor with no implicitly installed policies."""

    def __init__(
        self,
        transport: Client,
        *,
        auth_provider: _AuthHeadersProvider | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Store the raw transport and optional auth/header collaborators."""
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
        """Compose one raw request and send it exactly once."""
        invocation = RequestInvocation(
            method=method,
            path=path,
            headers=headers,
            params=params,
            json_body=json_body,
            content=content,
            options=options,
        )
        attempt = await self.prepare_auth_recovery_attempt(invocation)
        return await attempt.send()

    async def prepare_auth_recovery_attempt(
        self, invocation: RequestInvocation
    ) -> AuthRecoveryAttempt:
        """Prepare one independent raw send with its exact observed token."""
        self._assert_no_authorization_conflict(invocation.headers)
        auth_headers, observed_token = await self._auth_headers_and_token()
        request_headers = json_request_headers(
            self._default_headers,
            auth_headers,
            invocation.headers,
            json_body=invocation.json_body,
        )

        async def send() -> RawClientResponse:
            return await self._transport.request(
                invocation.method,
                invocation.path,
                headers=request_headers,
                params=invocation.params,
                json_body=invocation.json_body,
                content=invocation.content,
                options=invocation.options,
            )

        return AuthRecoveryAttempt(token=observed_token, send=send)

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None:
        """Request a conditional refresh from an auth provider when available."""
        if not isinstance(self._auth_provider, _AuthRecoveryProvider):
            return None
        return await self._auth_provider.refresh_if_current(token)

    async def execute(self, request: HttpRequest) -> RawClientResponse:
        """Compose immutable JSON-domain headers, then send the canonical request."""
        if request.body is not None and not isinstance(request.body, JsonBody):
            raise ValueError("Requester.execute accepts JSON-domain requests only")
        self._assert_no_authorization_conflict(request.headers.as_dict())
        auth_headers, _ = await self._auth_headers_and_token()
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

    def _assert_no_authorization_conflict(self, headers: Mapping[str, str] | None) -> None:
        if (
            self._auth_provider is not None
            and headers is not None
            and any(name.lower() == "authorization" for name in headers)
        ):
            raise AuthorizationConflictException(
                "Authorization header is managed by AuthProvider when configured"
            )

    async def _auth_headers_and_token(
        self,
    ) -> tuple[Mapping[str, str] | None, AccessToken | None]:
        if self._auth_provider is None:
            return None, None
        if isinstance(self._auth_provider, _AuthRecoveryProvider):
            return await self._auth_provider.get_auth_headers_and_token()
        return await self._auth_provider.get_auth_headers(), None
