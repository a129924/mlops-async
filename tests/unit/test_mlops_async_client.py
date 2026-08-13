from __future__ import annotations

import asyncio
import inspect
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

import mlops_async.mlops_async_client as facade
from mlops_async import MlopsAsyncClient
from mlops_async.clients.auth_client import AuthClient
from mlops_async.clients.cas_tables import CasTablesClient
from mlops_async.clients.job_execution import JobExecutionClient
from mlops_async.clients.models import ModelsClient
from mlops_async.clients.projects import ProjectsClient
from mlops_async.core.token_storage import AccessToken, InMemoryTokenStorage
from mlops_async.core.types import HttpMethod, RawClientResponse, ResponseHeaders


def _create_client(**overrides: object) -> MlopsAsyncClient:
    values: dict[str, object] = {
        "base_url": "https://viya.example.test",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "username": "user",
        "password": "password",
    }
    values.update(overrides)
    return MlopsAsyncClient(**values)  # type: ignore[arg-type]  # Intentional invalid runtime inputs.


def _access_token() -> AccessToken:
    return AccessToken(
        value="issued-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


def _models_page_response() -> RawClientResponse:
    return RawClientResponse(
        status_code=200,
        headers=ResponseHeaders(),
        content=b'{"count": 0, "start": 0, "limit": 20, "items": []}',
        method=HttpMethod.GET,
        url="https://viya.example.test/modelRepository/models",
    )


def test_package_root_export_has_the_frozen_keyword_only_constructor() -> None:
    assert MlopsAsyncClient is facade.MlopsAsyncClient

    parameters = inspect.signature(MlopsAsyncClient).parameters

    assert tuple(parameters) == (
        "base_url",
        "client_id",
        "client_secret",
        "username",
        "password",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values()
    )


def test_constructor_creates_one_shared_password_grant_runtime_without_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = AsyncMock()
    request_json = AsyncMock()
    monkeypatch.setattr(facade.HttpClient, "request", request)
    monkeypatch.setattr(facade.HttpClient, "request_json", request_json)

    client = _create_client()

    assert isinstance(client.auth, AuthClient)
    assert isinstance(client.models, ModelsClient)
    assert isinstance(client.projects, ProjectsClient)
    assert isinstance(client.cas_tables, CasTablesClient)
    assert isinstance(client.job_execution, JobExecutionClient)
    assert client.auth is client.auth
    assert client.models is client.models
    assert client.projects is client.projects
    assert client.cas_tables is client.cas_tables
    assert client.job_execution is client.job_execution
    assert isinstance(client._token_manager._storage, InMemoryTokenStorage)
    assert client.auth._token_endpoint_client is client._token_endpoint_client
    assert client._token_endpoint_client._transport is client._http_client
    assert client.models._requester is client._requester
    assert client.projects._requester is client._requester
    assert client.cas_tables._requester is client._requester
    assert client.job_execution._requester is client._requester
    request.assert_not_awaited()
    request_json.assert_not_awaited()


@pytest.mark.parametrize(
    "field,value",
    [
        ("base_url", "not an origin"),
        ("username", "   "),
        ("password", None),
        ("client_id", 1),
        ("client_secret", "\t"),
    ],
)
def test_constructor_uses_existing_validation_without_exposing_credentials(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError) as error_info:
        _create_client(**{field: value})

    assert str(value) not in str(error_info.value)


def test_invalid_credentials_fail_before_creating_the_http_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_constructed(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("HttpClient must not be created for invalid credentials")

    monkeypatch.setattr(facade, "HttpClient", fail_if_constructed)

    with pytest.raises(ValueError):
        _create_client(username="   ")


def test_namespace_properties_are_read_only() -> None:
    client = _create_client()

    with pytest.raises(AttributeError):
        client.models = client.models


@pytest.mark.asyncio
async def test_auth_client_preserves_token_endpoint_error_identity() -> None:
    client = _create_client()
    expected_error = RuntimeError("endpoint unavailable")

    async def raise_error() -> AccessToken:
        raise expected_error

    client._token_endpoint_client.fetch_access_token = raise_error

    with pytest.raises(RuntimeError) as error_info:
        await client.auth.get_access_token()

    assert error_info.value is expected_error


@pytest.mark.asyncio
async def test_auth_client_propagates_cancellation_identity() -> None:
    client = _create_client()
    cancellation = asyncio.CancelledError()

    async def raise_cancellation() -> AccessToken:
        raise cancellation

    client._token_endpoint_client.fetch_access_token = raise_cancellation

    with pytest.raises(asyncio.CancelledError) as error_info:
        await client.auth.get_access_token()

    assert error_info.value is cancellation


@pytest.mark.asyncio
async def test_aclose_closes_the_owned_http_client_once() -> None:
    client = _create_client()
    close = AsyncMock()
    client._http_client.aclose = close

    await client.aclose()
    await client.aclose()

    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_concurrent_aclose_calls_share_one_successful_close() -> None:
    client = _create_client()
    close_started = asyncio.Event()
    allow_close = asyncio.Event()

    async def blocking_close() -> None:
        close_started.set()
        await allow_close.wait()

    close = AsyncMock(side_effect=blocking_close)
    client._http_client.aclose = close

    first_close = asyncio.create_task(client.aclose())
    await close_started.wait()
    second_close = asyncio.create_task(client.aclose())
    await asyncio.sleep(0)
    allow_close.set()

    await asyncio.gather(first_close, second_close)
    await client.aclose()

    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_cancelling_one_aclose_waiter_does_not_cancel_the_shared_close() -> None:
    client = _create_client()
    close_started = asyncio.Event()
    allow_close = asyncio.Event()

    async def blocking_close() -> None:
        close_started.set()
        await allow_close.wait()

    close = AsyncMock(side_effect=blocking_close)
    client._http_client.aclose = close

    completing_waiter = asyncio.create_task(client.aclose())
    await close_started.wait()
    cancelled_waiter = asyncio.create_task(client.aclose())
    await asyncio.sleep(0)
    cancelled_waiter.cancel()

    with pytest.raises(asyncio.CancelledError):
        await cancelled_waiter

    assert client._close_task is not None
    assert not client._close_task.cancelled()

    allow_close.set()
    await completing_waiter

    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_aclose_failure_clears_state_for_a_later_retry() -> None:
    client = _create_client()
    expected_error = RuntimeError("close failed")
    close = AsyncMock(side_effect=(expected_error, None))
    client._http_client.aclose = close

    with pytest.raises(RuntimeError) as error_info:
        await client.aclose()

    assert error_info.value is expected_error
    assert client._close_task is None

    await client.aclose()

    assert close.await_count == 2


@pytest.mark.asyncio
async def test_aclose_cancellation_clears_state_for_a_later_retry() -> None:
    client = _create_client()
    close = AsyncMock(side_effect=(asyncio.CancelledError(), None))
    client._http_client.aclose = close

    with pytest.raises(asyncio.CancelledError):
        await client.aclose()

    assert client._close_task is None

    await client.aclose()

    assert close.await_count == 2


@pytest.mark.asyncio
async def test_namespace_properties_remain_readable_and_stable_after_aclose() -> None:
    client = _create_client()
    namespaces = (
        client.auth,
        client.models,
        client.projects,
        client.cas_tables,
        client.job_execution,
    )

    await client.aclose()

    assert (
        client.auth,
        client.models,
        client.projects,
        client.cas_tables,
        client.job_execution,
    ) == namespaces
    assert client.auth is namespaces[0]
    assert client.models is namespaces[1]
    assert client.projects is namespaces[2]
    assert client.cas_tables is namespaces[3]
    assert client.job_execution is namespaces[4]


@pytest.mark.asyncio
async def test_closed_domain_requester_io_propagates_httpx_closed_transport_error() -> None:
    client = _create_client()
    client._token_manager._storage.set_token(_access_token())

    await client.aclose()

    with pytest.raises(
        RuntimeError,
        match="Cannot send a request, as the client has been closed",
    ) as error_info:
        await client.models.list_models()

    assert error_info.value.__cause__ is None


@pytest.mark.asyncio
async def test_first_authenticated_domain_request_lazily_fetches_a_password_token() -> None:
    client = _create_client()
    issued_token = _access_token()
    fetch_access_token = AsyncMock(return_value=issued_token)
    request = AsyncMock(return_value=_models_page_response())
    client._token_endpoint_client.fetch_access_token = fetch_access_token
    client._http_client.request = request

    page = await client.models.list_models()

    assert page.count == 0
    fetch_access_token.assert_awaited_once_with()
    request.assert_awaited_once()
    args, kwargs = request.await_args
    assert args == (HttpMethod.GET, "/modelRepository/models")
    assert kwargs["headers"]["authorization"] == "Bearer issued-token"
    assert dict(kwargs["params"]) == {"start": "0", "limit": "20"}
    assert kwargs["json_body"] is None
    assert kwargs["content"] is None
    assert kwargs["options"] is None
    assert client._token_manager._storage.get_token() is issued_token


@pytest.mark.asyncio
async def test_async_context_manager_returns_self_and_closes_owned_http_client_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    close = AsyncMock()
    monkeypatch.setattr(facade.HttpClient, "aclose", close)

    async with _create_client() as client:
        assert isinstance(client, MlopsAsyncClient)

    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_context_manager_preserves_a_caller_exception() -> None:
    client = _create_client()
    close = AsyncMock()
    client._http_client.aclose = close
    expected_error = RuntimeError("caller failure")

    with pytest.raises(RuntimeError) as error_info:
        async with client:
            raise expected_error

    assert error_info.value is expected_error
    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_context_manager_propagates_a_close_failure() -> None:
    client = _create_client()
    expected_error = RuntimeError("close failed")
    close = AsyncMock(side_effect=expected_error)
    client._http_client.aclose = close

    with pytest.raises(RuntimeError) as error_info:
        async with client:
            pass

    assert error_info.value is expected_error
    assert client._close_task is None
    close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_context_manager_chains_a_caller_exception_after_close_failure() -> None:
    client = _create_client()
    caller_error = ValueError("caller failure")
    close_error = RuntimeError("close failed")
    close = AsyncMock(side_effect=close_error)
    client._http_client.aclose = close

    with pytest.raises(RuntimeError) as error_info:
        async with client:
            raise caller_error

    assert error_info.value is close_error
    assert close_error.__context__ is caller_error
    close.assert_awaited_once_with()
