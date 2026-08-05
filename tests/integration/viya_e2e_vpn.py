"""Private VPN reachability guard for opt-in Viya E2E tests."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from typing import Protocol, TypeAlias
from urllib.parse import SplitResult, urlsplit

_VPN_CONFIRMATION_ENV = "VIYA_E2E_VPN_CONFIRMED"
_VPN_PREFLIGHT_ERROR_MESSAGE = "Viya E2E VPN preflight failed"
_VPN_TCP_CONNECT_TIMEOUT_SECONDS = 5.0


class _ClosableStreamWriter(Protocol):
    """Minimal writer lifecycle required by the test-only preflight."""

    def close(self) -> None:
        """Begin closing the connection."""

    async def wait_closed(self) -> None:
        """Wait until the connection has closed."""


_TcpConnector: TypeAlias = Callable[
    [str, int],
    Awaitable[tuple[asyncio.StreamReader, _ClosableStreamWriter]],
]


class _ViyaE2EVpnPreflightError(Exception):
    """Raised when the private VPN preflight cannot complete safely."""


async def _require_viya_e2e_vpn_preflight(
    base_url: str,
    *,
    connector: _TcpConnector = asyncio.open_connection,
) -> None:
    """Require explicit VPN confirmation and prove TCP reachability once."""
    if os.environ.get(_VPN_CONFIRMATION_ENV) != "1":
        raise _ViyaE2EVpnPreflightError(_VPN_PREFLIGHT_ERROR_MESSAGE) from None

    connector_cancellation: asyncio.CancelledError | None = None

    async def connect(host: str, port: int) -> tuple[asyncio.StreamReader, _ClosableStreamWriter]:
        nonlocal connector_cancellation
        try:
            return await connector(host, port)
        except asyncio.CancelledError as error:
            connector_cancellation = error
            raise

    try:
        parsed = _parse_https_origin(base_url)
        host = parsed.hostname
        if host is None:
            raise ValueError("base URL host is required")
        port = 443 if parsed.port is None else parsed.port
        _reader, writer = await asyncio.wait_for(
            connect(host, port),
            timeout=_VPN_TCP_CONNECT_TIMEOUT_SECONDS,
        )
        writer.close()
        await writer.wait_closed()
    except asyncio.CancelledError:
        if connector_cancellation is not None:
            raise connector_cancellation from None
        raise
    except Exception:
        raise _ViyaE2EVpnPreflightError(_VPN_PREFLIGHT_ERROR_MESSAGE) from None


def _parse_https_origin(base_url: str) -> SplitResult:
    """Return a validated HTTPS origin without exposing its value on failure."""
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base URL is not a HTTPS origin")
    return parsed
