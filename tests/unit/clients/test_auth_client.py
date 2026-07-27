from __future__ import annotations

import ast
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import mlops_async
import mlops_async.core.auth as core_auth
from mlops_async.clients.auth_client import AuthClient
from mlops_async.core.token_storage import AccessToken


class _CollaboratorError(Exception):
    pass


class _FetchOnlyTokenEndpointClient:
    def __init__(self, outcomes: list[AccessToken | BaseException]) -> None:
        self._outcomes = outcomes
        self.fetch_calls = 0

    async def fetch_access_token(self) -> AccessToken:
        self.fetch_calls += 1
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class _FullTokenEndpointClient(_FetchOnlyTokenEndpointClient):
    async def refresh_access_token(self, token: AccessToken) -> AccessToken:
        return token


def _access_token(value: str) -> AccessToken:
    return AccessToken(
        value=value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


def test_auth_client_is_available_only_from_canonical_family_module() -> None:
    assert AuthClient.__module__ == "mlops_async.clients.auth_client"
    assert not hasattr(mlops_async, "AuthClient")
    assert not Path(mlops_async.__file__).with_name("mlops_async_client.py").exists()


def test_auth_client_accepts_a_fetch_only_protocol_collaborator() -> None:
    fetch_only_collaborator: core_auth.TokenEndpointFetchClientProtocol = (
        _FetchOnlyTokenEndpointClient([_access_token("issued-token")])
    )
    auth_client: AuthClient = AuthClient(fetch_only_collaborator)

    assert isinstance(fetch_only_collaborator, core_auth.TokenEndpointFetchClientProtocol)
    assert not isinstance(fetch_only_collaborator, core_auth.TokenEndpointClientProtocol)
    assert isinstance(auth_client, AuthClient)


def test_auth_client_remains_compatible_with_the_full_token_endpoint_protocol() -> None:
    full_collaborator: core_auth.TokenEndpointClientProtocol = _FullTokenEndpointClient(
        [_access_token("issued-token")]
    )
    fetch_only_collaborator: core_auth.TokenEndpointFetchClientProtocol = full_collaborator
    auth_client: AuthClient = AuthClient(full_collaborator)

    assert isinstance(fetch_only_collaborator, core_auth.TokenEndpointFetchClientProtocol)
    assert isinstance(full_collaborator, core_auth.TokenEndpointClientProtocol)
    assert isinstance(auth_client, AuthClient)


@pytest.mark.asyncio
async def test_get_access_token_awaits_fetch_once_and_returns_the_same_token() -> None:
    expected_token = _access_token("issued-token")
    token_endpoint_client = _FetchOnlyTokenEndpointClient([expected_token])
    auth_client = AuthClient(token_endpoint_client)

    actual_token = await auth_client.get_access_token()

    assert actual_token is expected_token
    assert token_endpoint_client.fetch_calls == 1


@pytest.mark.asyncio
async def test_get_access_token_preserves_collaborator_errors_without_translation() -> None:
    expected_error = _CollaboratorError("endpoint failed")
    token_endpoint_client = _FetchOnlyTokenEndpointClient([expected_error])
    auth_client = AuthClient(token_endpoint_client)

    with pytest.raises(_CollaboratorError) as error_info:
        await auth_client.get_access_token()

    assert error_info.value is expected_error
    assert token_endpoint_client.fetch_calls == 1


@pytest.mark.asyncio
async def test_get_access_token_propagates_cancellation_without_cleanup() -> None:
    cancellation = asyncio.CancelledError()
    token_endpoint_client = _FetchOnlyTokenEndpointClient([cancellation])
    auth_client = AuthClient(token_endpoint_client)

    with pytest.raises(asyncio.CancelledError) as error_info:
        await auth_client.get_access_token()

    assert error_info.value is cancellation
    assert token_endpoint_client.fetch_calls == 1


@pytest.mark.asyncio
async def test_auth_client_has_no_cache_or_lifecycle_and_uses_fetch_only_collaborator() -> None:
    first_token = _access_token("first-token")
    second_token = _access_token("second-token")
    token_endpoint_client = _FetchOnlyTokenEndpointClient([first_token, second_token])
    auth_client = AuthClient(token_endpoint_client)

    assert await auth_client.get_access_token() is first_token
    assert await auth_client.get_access_token() is second_token

    assert token_endpoint_client.fetch_calls == 2
    assert not hasattr(auth_client, "close")
    assert not hasattr(auth_client, "__aenter__")
    assert not hasattr(auth_client, "__aexit__")


def test_core_auth_does_not_import_package_root_or_higher_layers() -> None:
    tree = ast.parse(Path(core_auth.__file__).read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert AuthClient.__module__ == "mlops_async.clients.auth_client"
    assert all(
        module == "mlops_async.exceptions"
        or module == "mlops_async.core"
        or module.startswith("mlops_async.core.")
        for module in imported_modules
        if module == "mlops_async" or module.startswith("mlops_async.")
    )
