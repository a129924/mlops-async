"""Transport-backed defaults for request-resilience policy wiring."""

from __future__ import annotations

from typing import final

from mlops_async.core.request_execution import RequestFailureClassifier
from mlops_async.core.request_failure import RequestFailure, ResponseFailureMetadata

__all__ = ["TransportRequestFailureClassifier"]


@final
class TransportRequestFailureClassifier(RequestFailureClassifier):
    """Classify private metadata attached by the transport exception boundary."""

    def classify(self, error: BaseException) -> RequestFailure | None:
        """Return a resilience failure only for supported transport metadata."""
        kind = getattr(error, "failure_kind", None)
        metadata = getattr(error, "failure_metadata", None)
        if kind not in ("connection", "timeout", "response"):
            return None
        if metadata is not None and not isinstance(metadata, ResponseFailureMetadata):
            return None
        return RequestFailure(kind=kind, metadata=metadata)
