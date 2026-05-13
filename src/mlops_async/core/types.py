from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias
from collections.abc import Iterable, Iterator

__all__ = ["HttpMethod", "JSONScalar", "JSONValue", "RawClientResponse", "ResponseHeaders"]

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class HttpMethod(str, Enum):
    """Common HTTP verbs used by the internal client contract."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ResponseHeaders:
    """Immutable case-insensitive header collection preserving duplicates and order."""

    __slots__ = ("_index", "_pairs")

    def __init__(self, pairs: Iterable[tuple[str, str]] = ()) -> None:
        """Store header pairs preserving original order, casing, and duplicates."""
        normalized_pairs: list[tuple[str, str]] = []
        index: dict[str, list[str]] = {}

        for name, value in pairs:
            normalized_pairs.append((name, value))
            index.setdefault(name.lower(), []).append(value)

        self._pairs = tuple(normalized_pairs)
        self._index = {name: tuple(values) for name, values in index.items()}

    def get(self, name: str) -> str | None:
        """Return the first value matching *name* (case-insensitive), or None."""
        values = self._index.get(name.lower())
        return values[0] if values else None

    def get_all(self, name: str) -> tuple[str, ...]:
        """Return all values matching *name* (case-insensitive) in original order."""
        return self._index.get(name.lower(), ())

    def pairs(self) -> tuple[tuple[str, str], ...]:
        """Return all header pairs preserving original casing and order."""
        return self._pairs

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)

    def __repr__(self) -> str:
        return f"ResponseHeaders({self._pairs!r})"


@dataclass(frozen=True, slots=True)
class RawClientResponse:
    """Minimal envelope for a raw HTTP response."""

    status_code: int
    headers: ResponseHeaders
    content: bytes
    method: HttpMethod
    url: str
