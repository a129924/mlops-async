"""Policy contracts and built-in request-resilience policies."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import random
from typing import TYPE_CHECKING, TypedDict

from mlops_async.core.request_execution import RequestExecutor, RequestInvocation
from mlops_async.core.request_failure import RequestFailure
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse
from mlops_async.resilience._policy_protocols import (
    PolicyExecutionContext,
    ReplayableRequestExecutor,
)

if TYPE_CHECKING:
    from mlops_async.resilience.classifier import TransportRequestFailureClassifier
    from mlops_async.resilience.executor import PolicyRequestExecutor

__all__ = [
    "PolicyRequestExecutor",
    "RequestPolicy",
    "TransientRetryPolicy",
    "TransportRequestFailureClassifier",
    "UnauthorizedRecoveryPolicy",
]


class RequestPolicy:
    """Base type for a caller-injected request-execution policy."""

    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        context: PolicyExecutionContext,
    ) -> RawClientResponse:
        """Apply the policy around one downstream request execution."""
        raise NotImplementedError


class _RequestKwargs(TypedDict, total=False):
    """The optional fields that can be forwarded to a request executor."""

    headers: Mapping[str, str]
    params: Mapping[str, str]
    json_body: JSONValue
    content: bytes
    options: ClientRequestOptions


class UnauthorizedRecoveryPolicy(RequestPolicy):
    """Refresh once after an authenticated safe-method 401, then replay inner policies."""

    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        context: PolicyExecutionContext,
    ) -> RawClientResponse:
        """Recover a classified 401 only when the raw attempt used a managed token."""
        if not _is_eligible_method(invocation.method):
            return await forward_request(downstream, invocation)
        try:
            return await forward_request(downstream, invocation)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            failure = context.classifier.classify(error)
            if not _is_unauthorized(failure):
                raise
            attempt = context.last_auth_attempt
            if attempt is None or attempt.token is None:
                raise
            current = await context.refresh_if_current(attempt.token)
            if current is None:
                raise
            if not isinstance(downstream, ReplayableRequestExecutor):
                raise TypeError(
                    "UnauthorizedRecoveryPolicy requires a policy pipeline downstream"
                ) from error
            return await downstream.replay(invocation)


class TransientRetryPolicy(RequestPolicy):
    """Bounded retry for safe methods and explicitly transient failures."""

    _MAX_SENDS = 3
    _BACKOFF_BASE_SECONDS = 0.25
    _BACKOFF_CAP_SECONDS = 2.0
    _RETRY_AFTER_CAP_SECONDS = 30.0

    async def execute(
        self,
        invocation: RequestInvocation,
        downstream: RequestExecutor,
        context: PolicyExecutionContext,
    ) -> RawClientResponse:
        """Retry classified transient failures within this policy invocation's budget."""
        if not _is_eligible_method(invocation.method):
            return await forward_request(downstream, invocation)
        for attempt in range(self._MAX_SENDS):
            try:
                return await forward_request(downstream, invocation)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                failure = context.classifier.classify(error)
                if (
                    failure is None
                    or not self._is_retryable(failure)
                    or attempt == self._MAX_SENDS - 1
                ):
                    raise
                await asyncio.sleep(self._delay_for(failure, attempt))
        raise AssertionError("bounded retry loop must return or raise")

    @staticmethod
    def _is_retryable(failure: RequestFailure) -> bool:
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


def _is_eligible_method(method: HttpMethod) -> bool:
    match method:
        case HttpMethod.GET | HttpMethod.HEAD:
            return True
        case _:
            return False


def _is_unauthorized(failure: RequestFailure | None) -> bool:
    return (
        failure is not None
        and failure.metadata is not None
        and failure.metadata.status_code == 401
    )


async def forward_request(
    downstream: RequestExecutor, invocation: RequestInvocation
) -> RawClientResponse:
    request_kwargs: _RequestKwargs = {}
    if invocation.headers is not None:
        request_kwargs["headers"] = invocation.headers
    if invocation.params is not None:
        request_kwargs["params"] = invocation.params
    if invocation.json_body is not None:
        request_kwargs["json_body"] = invocation.json_body
    if invocation.content is not None:
        request_kwargs["content"] = invocation.content
    if invocation.options is not None:
        request_kwargs["options"] = invocation.options
    return await downstream.request(
        invocation.method,
        invocation.path,
        **request_kwargs,
    )


def __getattr__(name: str) -> object:
    """Lazily retain legacy policy-module imports without an import cycle."""
    if name == "PolicyRequestExecutor":
        from mlops_async.resilience.executor import PolicyRequestExecutor

        return PolicyRequestExecutor
    if name == "TransportRequestFailureClassifier":
        from mlops_async.resilience.classifier import TransportRequestFailureClassifier

        return TransportRequestFailureClassifier
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
