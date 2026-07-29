from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from math import isfinite
from typing import TypeAlias, cast
from urllib.parse import quote, urlsplit

from collections.abc import Iterable, Mapping

from mlops_async.core.request_options import ClientRequestOptions
from mlops_async.core.types import HttpMethod, JSONValue

__all__ = [
    "BaseUrl",
    "EndpointPath",
    "Headers",
    "HttpRequest",
    "JsonBody",
    "QueryParams",
    "RawBody",
]

_QueryValue: TypeAlias = str | int | float | bool | None


def _is_json_value(value: object) -> bool:
    if value is None or isinstance(value, str | bool | int):
        return True
    if isinstance(value, float):
        return isfinite(value)
    if isinstance(value, list):
        list_value = cast(list[object], value)
        return all(_is_json_value(item) for item in list_value)
    if isinstance(value, dict):
        dict_value = cast(dict[object, object], value)
        return all(
            isinstance(key, str) and _is_json_value(item) for key, item in dict_value.items()
        )
    return False


def _query_pair(key: object, value: object) -> tuple[str, _QueryValue] | None:
    if not isinstance(key, str) or not key:
        raise ValueError("Query parameter names must be non-empty strings")
    if not isinstance(value, str | int | float | bool | type(None)):
        raise ValueError("Query parameter values must be JSON scalar values")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Query parameter floats must be finite")
    return (key, value) if value is not None else None


def _header_pair(name: object, value: object) -> tuple[str, str]:
    if (
        not isinstance(name, str)
        or not name
        or any(character in name for character in "\r\n:")
    ):
        raise ValueError("Header names must be non-empty field names")
    if not isinstance(value, str) or "\r" in value or "\n" in value:
        raise ValueError("Header values must be strings without line breaks")
    return name.lower(), value


@dataclass(frozen=True, slots=True)
class BaseUrl:
    """An HTTP(S) origin without a path prefix or URL decorations."""

    value: str

    @classmethod
    def create(cls, value: str) -> BaseUrl:
        parts = urlsplit(value)
        try:
            port = parts.port
        except ValueError as exc:
            raise ValueError("BaseUrl must contain a valid origin") from exc
        if (
            parts.scheme not in {"http", "https"}
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
        ):
            raise ValueError("BaseUrl must be an http(s) origin only")
        authority = parts.hostname
        if ":" in authority and not authority.startswith("["):
            authority = f"[{authority}]"
        if port is not None:
            authority = f"{authority}:{port}"
        return cls(f"{parts.scheme}://{authority}")


@dataclass(frozen=True, slots=True)
class EndpointPath:
    """A validated static path or a path composed from raw dynamic segments."""

    value: str

    @classmethod
    def literal(cls, value: str) -> EndpointPath:
        if not value.startswith("/") or "?" in value or "#" in value:
            raise ValueError(
                "EndpointPath.literal must be an absolute path without query or fragment"
            )
        return cls(value)

    @classmethod
    def from_segments(cls, *segments: str) -> EndpointPath:
        if not segments:
            raise ValueError("EndpointPath.from_segments requires at least one segment")
        resolved_segments: list[str] = []
        for segment in segments:
            if not segment or any(
                segment[index] == "%"
                and index + 2 < len(segment)
                and all(
                    character in "0123456789abcdefABCDEF"
                    for character in segment[index + 1 : index + 3]
                )
                for index in range(len(segment))
            ):
                raise ValueError("EndpointPath dynamic segments must be non-empty raw strings")
            resolved_segments.append(quote(segment, safe=""))
        return cls("/" + "/".join(resolved_segments))


@dataclass(frozen=True, slots=True)
class QueryParams:
    """Ordered query pairs with exact RFC 3986 percent encoding."""

    _pairs: tuple[tuple[str, _QueryValue], ...]

    @classmethod
    def create(
        cls,
        pairs: Mapping[str, _QueryValue] | Iterable[tuple[str, _QueryValue]],
    ) -> QueryParams:
        source = (
            cast(Iterable[tuple[str, _QueryValue]], pairs.items())
            if isinstance(pairs, Mapping)
            else pairs
        )
        resolved_pairs: list[tuple[str, _QueryValue]] = []
        for key, value in source:
            resolved_pair = _query_pair(key, value)
            if resolved_pair is not None:
                resolved_pairs.append(resolved_pair)
        return cls(tuple(resolved_pairs))

    def render(self) -> str:
        def render_value(value: _QueryValue) -> str:
            if isinstance(value, bool):
                return "true" if value else "false"
            return str(value)

        return "&".join(
            f"{quote(key, safe='')}={quote(render_value(value), safe='')}"
            for key, value in self._pairs
        )


@dataclass(frozen=True, slots=True)
class Headers:
    """Immutable, case-insensitive request headers with lowercase output."""

    _items: tuple[tuple[str, str], ...]

    @classmethod
    def create(
        cls,
        pairs: Mapping[str, str] | Iterable[tuple[str, str]],
    ) -> Headers:
        source = (
            cast(Iterable[tuple[str, str]], pairs.items())
            if isinstance(pairs, Mapping)
            else pairs
        )
        resolved: dict[str, str] = {}
        for name, value in source:
            normalized_name, normalized_value = _header_pair(name, value)
            resolved[normalized_name] = normalized_value
        return cls(tuple(resolved.items()))

    def as_dict(self) -> dict[str, str]:
        return dict(self._items)


@dataclass(frozen=True, slots=True, init=False)
class JsonBody:
    """A validated snapshot of a JSON-domain request body."""

    _value: JSONValue = field(repr=False)

    def __init__(self, value: JSONValue) -> None:
        """Validate and snapshot the JSON value at construction time."""
        snapshot = deepcopy(value)
        if not _is_json_value(snapshot):
            raise ValueError("JsonBody must contain a finite JSON value")
        object.__setattr__(self, "_value", snapshot)

    @property
    def value(self) -> JSONValue:
        return deepcopy(self._value)


@dataclass(frozen=True, slots=True, init=False)
class RawBody:
    """Immutable raw request content with no implied media type."""

    content: bytes

    def __init__(self, content: object) -> None:
        """Validate and snapshot raw request content at construction time."""
        if not isinstance(content, bytes | bytearray):
            raise ValueError("RawBody content must be bytes or bytearray")
        object.__setattr__(self, "content", bytes(content))


@dataclass(frozen=True, slots=True)
class HttpRequest:
    """Canonical internal request data consumed by the transport boundary."""

    method: HttpMethod
    base_url: BaseUrl
    endpoint_path: EndpointPath
    query: QueryParams
    headers: Headers
    body: JsonBody | RawBody | None
    options: ClientRequestOptions | None

    def __post_init__(self) -> None:
        body = cast(object, self.body)
        if body is not None and not isinstance(body, JsonBody | RawBody):
            raise ValueError("HttpRequest body must be JsonBody, RawBody, or None")

    @property
    def url(self) -> str:
        query = self.query.render()
        url = f"{self.base_url.value}{self.endpoint_path.value}"
        return f"{url}?{query}" if query else url

    @property
    def json_body(self) -> JSONValue | None:
        return self.body.value if isinstance(self.body, JsonBody) else None

    @property
    def content(self) -> bytes | None:
        return self.body.content if isinstance(self.body, RawBody) else None
