from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import get_type_hints

import mlops_async
import mlops_async.core.auth as auth
import mlops_async.core.token_storage as token_storage


def test_internal_auth_contracts_are_not_promoted_to_package_root() -> None:
    assert not hasattr(mlops_async, "AuthProvider")
    assert not hasattr(mlops_async, "TokenManager")
    assert not hasattr(mlops_async, "TokenFetcher")
    assert not hasattr(mlops_async, "TokenStorage")
    assert not hasattr(mlops_async, "AccessToken")
    assert not hasattr(mlops_async, "Requester")


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


def test_token_fetcher_contract_supports_fetch_and_refresh_paths() -> None:
    fetch_access_token = auth.TokenFetcher.fetch_access_token
    assert inspect.iscoroutinefunction(fetch_access_token)
    assert get_type_hints(fetch_access_token)["return"] is token_storage.AccessToken

    refresh_access_token = auth.TokenFetcher.refresh_access_token
    assert inspect.iscoroutinefunction(refresh_access_token)
    refresh_hints = get_type_hints(refresh_access_token)
    assert refresh_hints["token"] is token_storage.AccessToken
    assert refresh_hints["return"] is token_storage.AccessToken
