"""Internal request-failure values shared by core resilience code."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RequestFailureKind = Literal["connection", "timeout", "response"]


@dataclass(frozen=True, slots=True)
class ResponseFailureMetadata:
    """Transport-neutral details of an HTTP response failure."""

    status_code: int | None
    retry_after: str | None


@dataclass(frozen=True, slots=True)
class RequestFailure:
    """Transport-neutral classification for private request resilience."""

    kind: RequestFailureKind
    metadata: ResponseFailureMetadata | None = None

    def __post_init__(self) -> None:
        if self.kind not in ("connection", "timeout", "response"):
            raise ValueError(f"Unsupported request failure kind: {self.kind}")
