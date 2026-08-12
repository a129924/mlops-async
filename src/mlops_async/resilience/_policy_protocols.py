"""Internal protocol contracts shared by resilience policies and executors."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from mlops_async.core.request_execution import (
    AuthRecoveryAttempt,
    RequestExecutor,
    RequestFailureClassifier,
    RequestInvocation,
)
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import RawClientResponse


class PolicyExecutionContext(Protocol):
    """Per-request services made available to a resilience policy."""

    classifier: RequestFailureClassifier
    last_auth_attempt: AuthRecoveryAttempt | None

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None: ...


@runtime_checkable
class ReplayableRequestExecutor(RequestExecutor, Protocol):
    """Internal capability for replaying through an inner policy pipeline."""

    async def replay(self, invocation: RequestInvocation) -> RawClientResponse: ...
