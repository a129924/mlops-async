from __future__ import annotations

import math
from dataclasses import dataclass, field
from collections.abc import Mapping
from types import MappingProxyType
from typing import Literal

__all__ = ["ClientRequestOptions", "RequestTimeouts"]

TimeoutPhase = Literal["total", "connect", "read", "write"]


@dataclass(frozen=True, slots=True)
class RequestTimeouts:
    """Immutable per-request timeout configuration."""

    total: float | None = None
    connect: float | None = None
    read: float | None = None
    write: float | None = None

    def __post_init__(self) -> None:
        invalid_fields = tuple(
            (field_name, value)
            for field_name in ("total", "connect", "read", "write")
            if (value := getattr(self, field_name)) is not None
            and (not math.isfinite(value) or value <= 0)
        )
        if invalid_fields:
            field_list = ", ".join(f"{field_name}={value}" for field_name, value in invalid_fields)
            raise ValueError(f"timeout values must be > 0 when provided: {field_list}")

    def resolve(self, phase: TimeoutPhase) -> float | None:
        """Return the field-specific timeout, falling back to total."""
        if phase == "total":
            return self.total

        specific_value = getattr(self, phase)
        return specific_value if specific_value is not None else self.total


@dataclass(frozen=True, slots=True)
class ClientRequestOptions:
    """Per-request extension carrying timeouts and request context."""

    timeout: RequestTimeouts = field(default_factory=RequestTimeouts)
    request_context: Mapping[str, str] = field(default_factory=dict[str, str])

    def __post_init__(self) -> None:
        immutable_context = MappingProxyType(dict(self.request_context))
        object.__setattr__(self, "request_context", immutable_context)
