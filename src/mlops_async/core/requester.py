from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import random
from typing import Protocol, runtime_checkable

from mlops_async.core.auth import AuthException
from mlops_async.core.client import Client
from mlops_async.core.headers import json_request_headers
from mlops_async.core.http_request import Headers, HttpRequest, JsonBody
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.request_failure import RequestFailure
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse

__all__ = ["AuthorizationConflictException", "Requester"]

_SendOnce = Callable[[], Awaitable[RawClientResponse]]
_PrepareSend = Callable[[], Awaitable[tuple[_SendOnce, AccessToken | None]]]


@runtime_checkable
class _AuthHeadersProvider(Protocol):
    """Minimal auth collaborator accepted by the existing requester boundary."""

    async def get_auth_headers(self) -> Mapping[str, str]: ...


@runtime_checkable
class _AuthResilienceProvider(_AuthHeadersProvider, Protocol):
    """Private auth collaborator that can identify and conditionally refresh a token."""

    async def get_auth_headers_and_token(self) -> tuple[Mapping[str, str], AccessToken]: ...

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None: ...


class _RequesterResilienceContext:
    """Private typed callbacks required by the request-resilience decorator."""

    def __init__(
        self,
        refresh_if_current: Callable[[AccessToken], Awaitable[AccessToken | None]],
        failure_for: Callable[[BaseException], RequestFailure | None],
    ) -> None:
        self._refresh_if_current = refresh_if_current
        self._failure_for = failure_for

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None:
        """Request a conditional token refresh through the owning requester."""
        return await self._refresh_if_current(token)

    def failure_for(self, error: BaseException) -> RequestFailure | None:
        """Classify a failure through the owning requester transport."""
        return self._failure_for(error)


class AuthorizationConflictException(AuthException):
    """Caller supplied an Authorization header while auth is managed."""


class Requester:
    """Internal request-composition layer above the transport client."""

    def __init__(
        self,
        transport: Client,
        *,
        auth_provider: _AuthHeadersProvider | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        """Store transport and optional auth/header composition defaults."""
        self._transport = transport
        self._auth_provider = auth_provider
        self._default_headers = dict(default_headers or {})
        self._resilience = _RequesterResilienceDecorator(
            _RequesterResilienceContext(
                self._refresh_if_current,
                self._failure_for,
            )
        )

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

        async def prepare_send() -> tuple[_SendOnce, AccessToken | None]:
            auth_headers, observed_token = await self._auth_headers_and_token()
            request_headers = json_request_headers(
                self._default_headers,
                auth_headers,
                headers,
                json_body=json_body,
            )

            async def send_once() -> RawClientResponse:
                return await self._transport.request(
                    method,
                    path,
                    headers=request_headers,
                    params=params,
                    json_body=json_body,
                    content=content,
                    options=options,
                )

            return send_once, observed_token

        send_once, observed_token = await prepare_send()
        return await self._resilience.send(method, send_once, observed_token, prepare_send)

    async def execute(self, request: HttpRequest) -> RawClientResponse:
        """Compose immutable JSON-domain headers, then execute a canonical request."""
        if request.body is not None and not isinstance(request.body, JsonBody):
            raise ValueError("Requester.execute accepts JSON-domain requests only")
        if self._auth_provider is not None and "authorization" in request.headers.as_dict():
            raise AuthorizationConflictException(
                "Authorization header is managed by AuthProvider when configured"
            )

        async def prepare_send() -> tuple[_SendOnce, AccessToken | None]:
            auth_headers, observed_token = await self._auth_headers_and_token()
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

            async def send_once() -> RawClientResponse:
                return await self._transport.execute(composed_request)

            return send_once, observed_token

        send_once, observed_token = await prepare_send()
        return await self._resilience.send(
            request.method,
            send_once,
            observed_token,
            prepare_send,
        )

    async def _auth_headers_and_token(
        self,
    ) -> tuple[Mapping[str, str] | None, AccessToken | None]:
        if self._auth_provider is None:
            return None, None
        if isinstance(self._auth_provider, _AuthResilienceProvider):
            return await self._auth_provider.get_auth_headers_and_token()
        return await self._auth_provider.get_auth_headers(), None

    async def _refresh_if_current(self, token: AccessToken) -> AccessToken | None:
        if not isinstance(self._auth_provider, _AuthResilienceProvider):
            return None
        return await self._auth_provider.refresh_if_current(token)

    def _failure_for(self, error: BaseException) -> RequestFailure | None:
        return self._transport.failure_for(error)


class _RequesterResilienceDecorator:
    """Private bounded retry and one-replay policy for managed safe requests."""

    _MAX_SENDS = 3
    _BACKOFF_BASE_SECONDS = 0.25
    _BACKOFF_CAP_SECONDS = 2.0
    _RETRY_AFTER_CAP_SECONDS = 30.0

    def __init__(self, context: _RequesterResilienceContext) -> None:
        self._context = context

    async def send(
        self,
        method: HttpMethod,
        send_once: _SendOnce,
        observed_token: AccessToken | None,
        prepare_replay: _PrepareSend,
    ) -> RawClientResponse:
        """Send an eligible request, optionally refreshing once after initial 401."""
        if not self._is_eligible_method(method):
            return await send_once()

        try:
            return await self._send_with_retries(send_once)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            if not self._is_unauthorized(self._failure_for(error)):
                raise

            if observed_token is None:
                raise
            current_token = await self._context.refresh_if_current(observed_token)
            if current_token is None:
                raise
            replay_send_once, _ = await prepare_replay()
            return await self._send_with_retries(replay_send_once)

    async def _send_with_retries(
        self,
        send_once: Callable[[], Awaitable[RawClientResponse]],
    ) -> RawClientResponse:
        for attempt in range(self._MAX_SENDS):
            try:
                return await send_once()
            except asyncio.CancelledError:
                raise
            except Exception as error:
                failure = self._failure_for(error)
                if (
                    failure is None
                    or not self._is_retryable(failure)
                    or attempt == self._MAX_SENDS - 1
                ):
                    raise
                await asyncio.sleep(self._delay_for(failure, attempt))

        raise AssertionError("bounded retry loop must return or raise")

    @staticmethod
    def _is_eligible_method(method: HttpMethod) -> bool:
        match method:
            case HttpMethod.GET | HttpMethod.HEAD:
                return True
            case _:
                return False

    def _failure_for(self, error: BaseException) -> RequestFailure | None:
        return self._context.failure_for(error)

    @staticmethod
    def _is_unauthorized(failure: RequestFailure | None) -> bool:
        return (
            failure is not None
            and failure.metadata is not None
            and failure.metadata.status_code == 401
        )

    def _is_retryable(self, failure: RequestFailure | None) -> bool:
        if failure is None:
            return False
        match failure.kind:
            case "connection" | "timeout":
                return True
            case "response":
                if failure.metadata is None:
                    return False
                match failure.metadata.status_code:
                    case 429 | 502 | 503 | 504:
                        return True
                    case _:
                        return False

    def _delay_for(self, failure: RequestFailure, attempt: int) -> float:
        retry_after = failure.metadata.retry_after if failure.metadata is not None else None
        parsed_retry_after = self._parse_retry_after(retry_after)
        if parsed_retry_after is not None:
            return parsed_retry_after
        exponential_delay = min(
            self._BACKOFF_CAP_SECONDS,
            self._BACKOFF_BASE_SECONDS * (2**attempt),
        )
        return random.uniform(0.0, exponential_delay)

    def _parse_retry_after(self, retry_after: str | None) -> float | None:
        if retry_after is None:
            return None
        try:
            return min(self._RETRY_AFTER_CAP_SECONDS, max(0.0, float(retry_after)))
        except ValueError:
            pass
        try:
            retry_at = parsedate_to_datetime(retry_after)
        except (TypeError, ValueError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
        return min(self._RETRY_AFTER_CAP_SECONDS, max(0.0, delay))
