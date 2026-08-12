"""Ordered decorator pipeline for request-resilience policies."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeGuard

from mlops_async.core.request_execution import (
    AuthRecoveryAttempt,
    AuthRecoveryExecutor,
    RequestExecutor,
    RequestFailureClassifier,
    RequestInvocation,
)
from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import HttpMethod, JSONValue, RawClientResponse
from mlops_async.resilience.classifier import TransportRequestFailureClassifier
from mlops_async.resilience.policies import (
    RequestPolicy,
    TransientRetryPolicy,
    UnauthorizedRecoveryPolicy,
    forward_request,
)

__all__ = ["PolicyRequestExecutor"]


class PolicyRequestExecutor(RequestExecutor):
    """Apply policies in supplied left-to-right, outermost-to-innermost order."""

    def __init__(
        self,
        raw: RequestExecutor,
        policies: list[RequestPolicy],
        *,
        classifier: RequestFailureClassifier | None = None,
    ) -> None:
        """Store explicit policy wiring after validating its bounded invariants."""
        self._raw = raw
        self._classifier = TransportRequestFailureClassifier() if classifier is None else classifier
        self._policies = tuple(self._validate_pipeline(policies))

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        """Run one invocation through the configured policy pipeline."""
        invocation = RequestInvocation(method, path, headers, params, json_body, content, options)
        return await self._request_with_auth_attempt_callback(invocation)

    async def _request_with_auth_attempt_callback(
        self,
        invocation: RequestInvocation,
        on_auth_attempt: Callable[[AuthRecoveryAttempt], None] | None = None,
    ) -> RawClientResponse:
        """Run a nested pipeline while forwarding its leaf auth attempt to its caller."""
        context = _PolicyExecutionContext(
            self._raw,
            self._classifier,
            self._policies,
            auth_executor=self._find_auth_recovery_executor(self._raw),
            on_auth_attempt=on_auth_attempt,
        )
        return await context.run_from(0, invocation)

    def _validate_pipeline(self, policies: list[RequestPolicy]) -> list[RequestPolicy]:
        """Return a concrete typed policy list after runtime invariant checks."""
        validated: list[RequestPolicy] = []
        for policy in policies:
            if not _is_request_policy(policy):
                raise TypeError("each pipeline item must be a RequestPolicy")
            if (
                isinstance(policy, UnauthorizedRecoveryPolicy)
                and self._find_auth_recovery_executor(self._raw) is None
            ):
                raise TypeError("UnauthorizedRecoveryPolicy requires auth recovery capability")
            validated.append(policy)

        families = (
            *self._builtin_policy_families(validated),
            *self._builtin_policy_families(self._raw),
        )
        if len(families) != len(set(families)):
            raise ValueError("duplicate built-in request policy")
        if (
            UnauthorizedRecoveryPolicy in families
            and TransientRetryPolicy in families
            and families.index(TransientRetryPolicy) < families.index(UnauthorizedRecoveryPolicy)
        ):
            raise ValueError("UnauthorizedRecoveryPolicy must be outermost to TransientRetryPolicy")
        return validated

    @staticmethod
    def _find_auth_recovery_executor(
        executor: RequestExecutor,
    ) -> AuthRecoveryExecutor | None:
        """Find a forwarded auth capability without treating every nested wrapper as one."""
        if isinstance(executor, PolicyRequestExecutor):
            return PolicyRequestExecutor._find_auth_recovery_executor(executor._raw)
        if isinstance(executor, AuthRecoveryExecutor):
            return executor
        return None

    @staticmethod
    def _builtin_policy_families(
        policies_or_executor: list[RequestPolicy] | RequestExecutor,
    ) -> tuple[type[UnauthorizedRecoveryPolicy] | type[TransientRetryPolicy], ...]:
        """Collect canonical built-in policy families in effective outer-to-inner order."""
        if isinstance(policies_or_executor, list):
            families: list[type[UnauthorizedRecoveryPolicy] | type[TransientRetryPolicy]] = []
            for policy in policies_or_executor:
                family = _builtin_policy_family(policy)
                if family is not None:
                    families.append(family)
            return tuple(families)

        executor = policies_or_executor
        if not isinstance(executor, PolicyRequestExecutor):
            return ()
        return (
            *PolicyRequestExecutor._builtin_policy_families(list(executor._policies)),
            *PolicyRequestExecutor._builtin_policy_families(executor._raw),
        )


def _is_request_policy(value: object) -> TypeGuard[RequestPolicy]:
    """Narrow untrusted runtime configuration without weakening the API type."""
    return isinstance(value, RequestPolicy)


def _builtin_policy_family(
    policy: RequestPolicy,
) -> type[UnauthorizedRecoveryPolicy] | type[TransientRetryPolicy] | None:
    """Return the canonical built-in family, including subclasses of a policy."""
    if isinstance(policy, UnauthorizedRecoveryPolicy):
        return UnauthorizedRecoveryPolicy
    if isinstance(policy, TransientRetryPolicy):
        return TransientRetryPolicy
    return None


class _PolicyExecutionContext:
    """Per-request policy state; never shared across concurrent executions."""

    def __init__(
        self,
        raw: RequestExecutor,
        classifier: RequestFailureClassifier,
        policies: tuple[RequestPolicy, ...],
        *,
        auth_executor: AuthRecoveryExecutor | None,
        on_auth_attempt: Callable[[AuthRecoveryAttempt], None] | None,
    ) -> None:
        self._raw = raw
        self.classifier = classifier
        self._policies = policies
        self._auth_executor = auth_executor
        self._on_auth_attempt = on_auth_attempt
        self.last_auth_attempt: AuthRecoveryAttempt | None = None

    async def run_from(self, policy_index: int, invocation: RequestInvocation) -> RawClientResponse:
        """Run policies from the selected index through the raw executor."""
        if policy_index == len(self._policies):
            return await self._send_raw(invocation)
        policy = self._policies[policy_index]
        downstream = _PipelineTail(self, policy_index + 1)
        return await policy.execute(invocation, downstream, self)

    async def _send_raw(self, invocation: RequestInvocation) -> RawClientResponse:
        if isinstance(self._raw, PolicyRequestExecutor):
            return await self._raw._request_with_auth_attempt_callback(  # pyright: ignore[reportPrivateUsage]
                invocation,
                self._record_auth_attempt,
            )
        if self._auth_executor is not None:
            attempt = await self._auth_executor.prepare_auth_recovery_attempt(invocation)
            self._record_auth_attempt(attempt)
            return await attempt.send()
        return await forward_request(self._raw, invocation)

    def _record_auth_attempt(self, attempt: AuthRecoveryAttempt) -> None:
        """Remember the leaf attempt locally and expose it to an outer wrapper."""
        self.last_auth_attempt = attempt
        if self._on_auth_attempt is not None:
            self._on_auth_attempt(attempt)

    async def replay_from(
        self, policy_index: int, invocation: RequestInvocation
    ) -> RawClientResponse:
        """Replay through the remaining, inner policy pipeline."""
        return await self.run_from(policy_index, invocation)

    async def refresh_if_current(self, token: AccessToken) -> AccessToken | None:
        """Conditionally refresh through the raw auth-capable executor."""
        if self._auth_executor is None:
            return None
        return await self._auth_executor.refresh_if_current(token)


class _PipelineTail(RequestExecutor):
    """A request executor representing the remaining inner pipeline."""

    def __init__(self, context: _PolicyExecutionContext, policy_index: int) -> None:
        self._context = context
        self._policy_index = policy_index

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json_body: JSONValue | None = None,
        content: bytes | None = None,
        options: ClientRequestOptions | None = None,
    ) -> RawClientResponse:
        """Forward one invocation into the remaining inner policies."""
        return await self._context.run_from(
            self._policy_index,
            RequestInvocation(method, path, headers, params, json_body, content, options),
        )

    async def replay(self, invocation: RequestInvocation) -> RawClientResponse:
        """Replay through the same remaining inner policies."""
        return await self._context.replay_from(self._policy_index, invocation)
