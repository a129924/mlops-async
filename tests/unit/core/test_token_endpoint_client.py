from __future__ import annotations

from dataclasses import dataclass

import pytest

import mlops_async.core.headers as headers_mod
from mlops_async.core.token_endpoint_client import (
    AuthTokenEndpoint,
    TokenEndpointClient,
    TokenEndpointClientError,
)
from mlops_async.core.types import HttpMethod


@dataclass
class _RecordedRequest:
    method: HttpMethod
    path: str
    headers: dict[str, str] | None
    content: bytes | None


class _FakeTransport:
    def __init__(self, response: object) -> None:
        self.response = response
        self.requests: list[_RecordedRequest] = []

    async def request_json(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json_body: object | None = None,
        content: bytes | None = None,
        options: object | None = None,
    ) -> object:
        del params, json_body, options
        self.requests.append(
            _RecordedRequest(
                method=method,
                path=path,
                headers=dict(headers) if headers is not None else None,
                content=content,
            )
        )
        return self.response


@pytest.mark.asyncio
async def test_token_endpoint_client_emits_obtain_request_matching_request_gate_baseline() -> None:
    transport = _FakeTransport({"access_token": "managed-token", "expires_in": 3600})
    client = TokenEndpointClient(
        transport,
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
    )

    access_token = await client.fetch_access_token()

    assert access_token.value == "managed-token"
    assert client.endpoint is AuthTokenEndpoint.OAUTH_TOKEN
    assert transport.requests == [
        _RecordedRequest(
            method=HttpMethod.POST,
            path="/SASLogon/oauth/token",
            headers=headers_mod.token_request_headers(),
            content=(
                b"grant_type=client_credentials"
                b"&client_id=client-id-abc-123"
                b"&client_secret=secret-value-xyz"
            ),
        )
    ]


@pytest.mark.asyncio
async def test_token_endpoint_client_percent_encodes_reserved_characters() -> None:
    transport = _FakeTransport({"access_token": "managed-token", "expires_in": 3600})
    client = TokenEndpointClient(
        transport,
        client_id="client/id?draft=yes",
        client_secret="secret&value=1",
    )

    await client.fetch_access_token()

    assert transport.requests[0].content == (
        b"grant_type=client_credentials"
        b"&client_id=client%2Fid%3Fdraft%3Dyes"
        b"&client_secret=secret%26value%3D1"
    )


@pytest.mark.asyncio
async def test_token_endpoint_client_refresh_path_reuses_mvp_obtain_path() -> None:
    transport = _FakeTransport({"access_token": "managed-token", "expires_in": 3600})
    client = TokenEndpointClient(
        transport,
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
    )

    initial_token = await client.fetch_access_token()
    refreshed_token = await client.refresh_access_token(initial_token)

    assert refreshed_token.value == "managed-token"
    assert len(transport.requests) == 2
    assert {request.path for request in transport.requests} == {"/SASLogon/oauth/token"}


@pytest.mark.asyncio
async def test_token_endpoint_client_rejects_non_object_response() -> None:
    transport = _FakeTransport(["unexpected"])
    client = TokenEndpointClient(
        transport,
        client_id="client-id-abc-123",
        client_secret="secret-value-xyz",
    )

    with pytest.raises(TokenEndpointClientError, match="JSON object"):
        await client.fetch_access_token()


@pytest.mark.asyncio
async def test_token_endpoint_client_rejects_missing_or_invalid_required_fields() -> None:
    invalid_responses = [
        {"expires_in": 3600},
        {"access_token": "", "expires_in": 3600},
        {"access_token": "managed-token"},
        {"access_token": "managed-token", "expires_in": 0},
    ]

    for payload in invalid_responses:
        transport = _FakeTransport(payload)
        client = TokenEndpointClient(
            transport,
            client_id="client-id-abc-123",
            client_secret="secret-value-xyz",
        )

        with pytest.raises(TokenEndpointClientError):
            await client.fetch_access_token()


def test_token_endpoint_client_rejects_blank_credentials_at_construction_time() -> None:
    transport = _FakeTransport({"access_token": "managed-token", "expires_in": 3600})

    with pytest.raises(TokenEndpointClientError, match="client_id"):
        TokenEndpointClient(transport, client_id="", client_secret="secret")

    with pytest.raises(TokenEndpointClientError, match="client_secret"):
        TokenEndpointClient(transport, client_id="client", client_secret=" ")
