from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import get_type_hints

import pytest

import mlops_async
import mlops_async.core.auth as auth
import mlops_async.core.token_storage as token_storage
from mlops_async.exceptions import MlopsAsyncBaseException


def test_internal_auth_contracts_are_not_promoted_to_package_root() -> None:
    assert not hasattr(mlops_async, "AuthClient")
    assert not hasattr(mlops_async, "AuthProvider")
    assert not hasattr(mlops_async, "TokenManager")
    assert not hasattr(mlops_async, "TokenEndpointClient")
    assert not hasattr(mlops_async, "TokenEndpointClientProtocol")
    assert not hasattr(mlops_async, "TokenStorage")
    assert not hasattr(mlops_async, "AccessToken")
    assert not hasattr(mlops_async, "Requester")


def test_auth_exception_retains_its_public_class_identity() -> None:
    exception = auth.AuthException("token endpoint failed")

    assert auth.AuthException.__name__ == "AuthException"
    assert type(exception) is auth.AuthException
    assert repr(exception).startswith("AuthException(")


def test_auth_exception_is_caught_by_the_shared_library_base_exception() -> None:
    with pytest.raises(MlopsAsyncBaseException):
        raise auth.AuthException("token endpoint failed")


def test_token_manager_surface_is_async_and_returns_access_token() -> None:
    token_manager = auth.TokenManager
    signature = inspect.signature(token_manager)
    assert tuple(signature.parameters) == ("storage", "fetcher", "expiry_skew")

    get_access_token = token_manager.get_access_token
    assert inspect.iscoroutinefunction(get_access_token)
    assert get_type_hints(get_access_token)["return"] is token_storage.AccessToken


def test_auth_provider_surface_is_async_and_returns_header_mapping() -> None:
    auth_provider = auth.AuthProvider
    signature = inspect.signature(auth_provider)
    assert tuple(signature.parameters) == ("token_manager",)

    get_auth_headers = auth_provider.get_auth_headers
    assert inspect.iscoroutinefunction(get_auth_headers)
    assert get_type_hints(get_auth_headers)["return"] == Mapping[str, str]


def test_token_endpoint_client_surface_supports_fetch_and_refresh_paths() -> None:
    token_endpoint_client = auth.TokenEndpointClient
    signature = inspect.signature(token_endpoint_client)
    assert tuple(signature.parameters) == ("transport", "client_id", "client_secret", "endpoint")

    fetch_access_token = token_endpoint_client.fetch_access_token
    assert inspect.iscoroutinefunction(fetch_access_token)
    assert get_type_hints(fetch_access_token)["return"] is token_storage.AccessToken

    refresh_access_token = token_endpoint_client.refresh_access_token
    assert inspect.iscoroutinefunction(refresh_access_token)
    refresh_hints = get_type_hints(refresh_access_token)
    assert refresh_hints["token"] is token_storage.AccessToken
    assert refresh_hints["return"] is token_storage.AccessToken
