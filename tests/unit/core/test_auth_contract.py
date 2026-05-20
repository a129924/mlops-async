from __future__ import annotations

import importlib
import inspect
from collections.abc import Mapping
from typing import get_type_hints

import mlops_async
import pytest


def _auth_module():
    try:
        return importlib.import_module("mlops_async.core.auth")
    except ModuleNotFoundError as exc:
        pytest.fail(
            f"Internal auth contracts must live at mlops_async.core.auth; import failed: {exc}"
        )


def _token_storage_module():
    try:
        return importlib.import_module("mlops_async.core.token_storage")
    except ModuleNotFoundError as exc:
        pytest.fail(
            "Token storage contracts must live at mlops_async.core.token_storage; "
            f"import failed: {exc}"
        )


def test_internal_auth_contracts_are_not_promoted_to_package_root() -> None:
    assert not hasattr(mlops_async, "AuthProvider")
    assert not hasattr(mlops_async, "TokenManager")
    assert not hasattr(mlops_async, "TokenFetcher")
    assert not hasattr(mlops_async, "TokenStorage")
    assert not hasattr(mlops_async, "AccessToken")
    assert not hasattr(mlops_async, "Requester")


def test_token_manager_surface_is_async_and_returns_access_token() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()

    token_manager = auth_module.TokenManager
    signature = inspect.signature(token_manager)
    assert tuple(signature.parameters) == ("storage", "fetcher", "expiry_skew")

    get_access_token = token_manager.get_access_token
    assert inspect.iscoroutinefunction(get_access_token)
    assert get_type_hints(get_access_token)["return"] is token_storage_module.AccessToken


def test_auth_provider_surface_is_async_and_returns_header_mapping() -> None:
    auth_module = _auth_module()

    auth_provider = auth_module.AuthProvider
    signature = inspect.signature(auth_provider)
    assert tuple(signature.parameters) == ("token_manager",)

    get_auth_headers = auth_provider.get_auth_headers
    assert inspect.iscoroutinefunction(get_auth_headers)
    assert get_type_hints(get_auth_headers)["return"] == Mapping[str, str]


def test_token_fetcher_contract_supports_fetch_and_refresh_paths() -> None:
    auth_module = _auth_module()
    token_storage_module = _token_storage_module()

    fetch_access_token = auth_module.TokenFetcher.fetch_access_token
    assert inspect.iscoroutinefunction(fetch_access_token)
    assert get_type_hints(fetch_access_token)["return"] is token_storage_module.AccessToken

    refresh_access_token = auth_module.TokenFetcher.refresh_access_token
    assert inspect.iscoroutinefunction(refresh_access_token)
    refresh_hints = get_type_hints(refresh_access_token)
    assert refresh_hints["token"] is token_storage_module.AccessToken
    assert refresh_hints["return"] is token_storage_module.AccessToken
