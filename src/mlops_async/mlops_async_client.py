"""Package-root facade for the supported password-grant client runtime."""

from __future__ import annotations

import asyncio
from types import TracebackType

from mlops_async.clients.auth_client import AuthClient
from mlops_async.clients.cas_tables import CasTablesClient
from mlops_async.clients.job_execution import JobExecutionClient
from mlops_async.clients.models import ModelsClient
from mlops_async.clients.projects import ProjectsClient
from mlops_async.core.auth import AuthProvider, TokenManager
from mlops_async.core.http_request import BaseUrl
from mlops_async.core.requester import Requester
from mlops_async.core.token_endpoint._shared import (
    require_non_empty_string,
    require_password_client_secret,
)
from mlops_async.core.token_endpoint.password import PasswordTokenEndpointClient
from mlops_async.core.token_storage import InMemoryTokenStorage
from mlops_async.transport.http_client import HttpClient

__all__ = ["MlopsAsyncClient"]


class MlopsAsyncClient:
    """Own one password-grant HTTP/auth runtime and its supported client families."""

    def __init__(
        self,
        *,
        base_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ) -> None:
        """Wire the owned runtime without performing HTTP or token I/O."""
        BaseUrl.create(base_url)
        resolved_username = require_non_empty_string(username, field_name="username")
        resolved_password = require_non_empty_string(password, field_name="password")
        resolved_client_id = require_non_empty_string(client_id, field_name="client_id")
        resolved_client_secret = require_password_client_secret(
            client_secret,
            client_id=resolved_client_id,
        )

        self._http_client = HttpClient(base_url)
        self._token_endpoint_client = PasswordTokenEndpointClient(
            self._http_client,
            username=resolved_username,
            password=resolved_password,
            client_id=resolved_client_id,
            client_secret=resolved_client_secret,
        )
        self._token_manager = TokenManager(
            InMemoryTokenStorage(),
            self._token_endpoint_client,
        )
        self._requester = Requester(
            self._http_client,
            auth_provider=AuthProvider(self._token_manager),
        )
        self._auth = AuthClient(self._token_endpoint_client)
        self._models = ModelsClient(self._requester)
        self._projects = ProjectsClient(self._requester)
        self._cas_tables = CasTablesClient(self._requester)
        self._job_execution = JobExecutionClient(self._requester)
        self._closed = False
        self._close_task: asyncio.Task[None] | None = None

    @property
    def auth(self) -> AuthClient:
        """Return the stable direct password-token client."""
        return self._auth

    @property
    def models(self) -> ModelsClient:
        """Return the stable Models client sharing this runtime."""
        return self._models

    @property
    def projects(self) -> ProjectsClient:
        """Return the stable Projects client sharing this runtime."""
        return self._projects

    @property
    def cas_tables(self) -> CasTablesClient:
        """Return the stable CAS Tables client sharing this runtime."""
        return self._cas_tables

    @property
    def job_execution(self) -> JobExecutionClient:
        """Return the stable Job Execution client sharing this runtime."""
        return self._job_execution

    async def aclose(self) -> None:
        """Close the facade-owned HTTP client once after a successful close."""
        if self._closed:
            return

        if self._close_task is None:
            self._close_task = asyncio.create_task(self._close_owned_http_client())

        await asyncio.shield(self._close_task)

    async def _close_owned_http_client(self) -> None:
        """Close the owned HTTP client and retain retryability on failure."""
        try:
            await self._http_client.aclose()
        except BaseException:
            self._close_task = None
            raise
        else:
            self._closed = True
            self._close_task = None

    async def __aenter__(self) -> MlopsAsyncClient:
        """Return this already-wired facade without performing I/O."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the owned HTTP client while preserving context exceptions."""
        del exc_type, exc, traceback
        await self.aclose()
