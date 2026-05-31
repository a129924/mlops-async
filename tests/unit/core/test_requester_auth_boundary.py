from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import mlops_async.core.auth as auth
import mlops_async.core.requester as requester_mod
import pytest

from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders


@dataclass
class _RecordedRequest:
    method: HttpMethod
    path: str
    headers: Mapping[str, str] | None
    params: Mapping[str, str] | None
    json_body: object | None
    content: bytes | None
    options: ClientRequestOptions | None


class _FakeHttpClient:
    def __init__(self) -> None:
        self.requests: list[_RecordedRequest] = []

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: object | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        self.requests.append(
            _RecordedRequest(
                method=method,
                path=path,
                headers=headers,
                params=params,
                json_body=json_body,
                content=content,
                options=options,
            )
        )
        return RawClientResponse(
            status_code=204,
            headers=ResponseHeaders(),
            content=b"",
            method=method,
            url=f"https://example.test{path}",
        )

    async def request_json(self, *args: object, **kwargs: object) -> object:
        raise AssertionError("Requester tests should call request(), not request_json()")

    async def aclose(self) -> None:
        return None

    async def __aenter__(self) -> _FakeHttpClient:
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class _StaticAuthProvider:
    def __init__(self, headers: Mapping[str, str]) -> None:
        self.headers = dict(headers)
        self.calls = 0

    async def get_auth_headers(self) -> Mapping[str, str]:
        self.calls += 1
        return dict(self.headers)


class _FailingAuthProvider:
    def __init__(self, exc: BaseException) -> None:
        self.exc = exc

    async def get_auth_headers(self) -> Mapping[str, str]:
        raise self.exc


@pytest.mark.asyncio
async def test_requester_merges_defaults_auth_and_caller_headers_before_transport() -> None:
    transport = _FakeHttpClient()
    auth_provider = _StaticAuthProvider({"Authorization": "Bearer managed-token"})
    requester = requester_mod.Requester(
        transport,
        auth_provider=auth_provider,
        default_headers={"X-Mode": "default"},
    )

    response = await requester.request(
        HttpMethod.POST,
        "/items",
        headers={"X-Mode": "caller", "X-Trace": "present"},
        json_body={"name": "demo"},
    )

    assert response.status_code == 204
    assert auth_provider.calls == 1
    sent_request = transport.requests[0]
    assert sent_request.headers == {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer managed-token",
        "X-Mode": "caller",
        "X-Trace": "present",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("header_name", ["Authorization", "authorization", "AUTHORIZATION"])
async def test_requester_rejects_caller_authorization_when_auth_provider_is_configured(
    header_name: str,
) -> None:
    transport = _FakeHttpClient()
    requester = requester_mod.Requester(
        transport,
        auth_provider=_StaticAuthProvider({"Authorization": "Bearer managed-token"}),
    )

    with pytest.raises(requester_mod.AuthorizationConflictException, match="Authorization"):
        await requester.request(
            HttpMethod.GET,
            "/items",
            headers={header_name: "Bearer caller-token"},
        )

    assert transport.requests == []


@pytest.mark.asyncio
async def test_requester_allows_caller_authorization_without_auth_provider() -> None:
    transport = _FakeHttpClient()
    requester = requester_mod.Requester(transport)

    await requester.request(
        HttpMethod.GET,
        "/items",
        headers={"Authorization": "Bearer caller-token"},
    )

    sent_request = transport.requests[0]
    assert sent_request.headers == {
        "Accept": "application/json",
        "Authorization": "Bearer caller-token",
    }


@pytest.mark.asyncio
async def test_requester_does_not_call_transport_after_auth_layer_failure() -> None:
    transport = _FakeHttpClient()
    requester = requester_mod.Requester(
        transport,
        auth_provider=_FailingAuthProvider(auth.AuthException("token endpoint unavailable")),
    )

    with pytest.raises(auth.AuthException, match="token endpoint unavailable"):
        await requester.request(HttpMethod.GET, "/items")

    assert transport.requests == []
