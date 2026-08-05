from __future__ import annotations

import asyncio
from typing import cast

import pytest

from tests.integration.viya_e2e_vpn import (
    _ViyaE2EVpnPreflightError,
    _require_viya_e2e_vpn_preflight,
)


class _FakeWriter:
    def __init__(
        self,
        *,
        close_error: Exception | None = None,
        wait_closed_error: BaseException | None = None,
    ) -> None:
        self.close_calls = 0
        self.wait_closed_calls = 0
        self._close_error = close_error
        self._wait_closed_error = wait_closed_error

    def close(self) -> None:
        self.close_calls += 1
        if self._close_error is not None:
            raise self._close_error

    async def wait_closed(self) -> None:
        self.wait_closed_calls += 1
        if self._wait_closed_error is not None:
            raise self._wait_closed_error


@pytest.mark.asyncio
@pytest.mark.parametrize("confirmation", [None, "0", "true", " 1"])
async def test_preflight_rejects_non_exact_confirmation_without_connecting(
    monkeypatch: pytest.MonkeyPatch,
    confirmation: str | None,
) -> None:
    if confirmation is None:
        monkeypatch.delenv("VIYA_E2E_VPN_CONFIRMED", raising=False)
    else:
        monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", confirmation)

    calls: list[tuple[str, int]] = []

    async def connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        calls.append((host, port))
        return cast(asyncio.StreamReader, object()), _FakeWriter()

    with pytest.raises(_ViyaE2EVpnPreflightError):
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=connector,
        )

    assert calls == []


@pytest.mark.asyncio
async def test_preflight_uses_default_https_port_and_closes_writer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    writer = _FakeWriter()
    calls: list[tuple[str, int]] = []

    async def connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        calls.append((host, port))
        return cast(asyncio.StreamReader, object()), writer

    await _require_viya_e2e_vpn_preflight("https://viya.example.test", connector=connector)

    assert calls == [("viya.example.test", 443)]
    assert writer.close_calls == 1
    assert writer.wait_closed_calls == 1


@pytest.mark.asyncio
async def test_preflight_uses_explicit_port_with_injected_connector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    calls: list[tuple[str, int]] = []

    async def connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        calls.append((host, port))
        return cast(asyncio.StreamReader, object()), _FakeWriter()

    await _require_viya_e2e_vpn_preflight(
        "https://vpn.example.test:8443",
        connector=connector,
    )

    assert calls == [("vpn.example.test", 8443)]


@pytest.mark.asyncio
async def test_preflight_rejects_invalid_url_without_connecting_or_leaking_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    invalid_url = "https://user:credential-value@viya.example.test:not-a-port"
    calls: list[tuple[str, int]] = []

    async def connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        calls.append((host, port))
        return cast(asyncio.StreamReader, object()), _FakeWriter()

    with pytest.raises(_ViyaE2EVpnPreflightError) as exc_info:
        await _require_viya_e2e_vpn_preflight(invalid_url, connector=connector)

    assert calls == []
    assert str(exc_info.value) != ""
    assert invalid_url not in str(exc_info.value)
    assert "credential-value" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None
    assert exc_info.value.__suppress_context__ is True


@pytest.mark.asyncio
async def test_preflight_redacts_connection_and_cleanup_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    sensitive_text = "access-token-value-must-not-appear"

    async def failing_connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        del host, port
        raise RuntimeError(sensitive_text)

    with pytest.raises(_ViyaE2EVpnPreflightError) as connector_error:
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=failing_connector,
        )

    writer = _FakeWriter(close_error=RuntimeError(sensitive_text))

    async def connector_with_close_failure(
        host: str,
        port: int,
    ) -> tuple[asyncio.StreamReader, _FakeWriter]:
        del host, port
        return cast(asyncio.StreamReader, object()), writer

    with pytest.raises(_ViyaE2EVpnPreflightError) as close_error:
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=connector_with_close_failure,
        )

    writer_wait_failure = _FakeWriter(wait_closed_error=RuntimeError(sensitive_text))

    async def connector_with_wait_failure(
        host: str,
        port: int,
    ) -> tuple[asyncio.StreamReader, _FakeWriter]:
        del host, port
        return cast(asyncio.StreamReader, object()), writer_wait_failure

    with pytest.raises(_ViyaE2EVpnPreflightError) as wait_closed_error:
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=connector_with_wait_failure,
        )

    errors = [connector_error.value, close_error.value, wait_closed_error.value]
    assert len({str(error) for error in errors}) == 1
    for error in errors:
        assert sensitive_text not in str(error)
        assert error.__cause__ is None
        assert error.__suppress_context__ is True


@pytest.mark.asyncio
async def test_preflight_propagates_connection_cancellation_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    cancelled = asyncio.CancelledError()

    async def cancelled_connector(
        host: str,
        port: int,
    ) -> tuple[asyncio.StreamReader, _FakeWriter]:
        del host, port
        raise cancelled

    with pytest.raises(asyncio.CancelledError) as exc_info:
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=cancelled_connector,
        )

    assert exc_info.value is cancelled


@pytest.mark.asyncio
async def test_preflight_propagates_cleanup_cancellation_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", "1")
    cancelled = asyncio.CancelledError()
    writer = _FakeWriter(wait_closed_error=cancelled)

    async def connector(host: str, port: int) -> tuple[asyncio.StreamReader, _FakeWriter]:
        del host, port
        return cast(asyncio.StreamReader, object()), writer

    with pytest.raises(asyncio.CancelledError) as exc_info:
        await _require_viya_e2e_vpn_preflight(
            "https://viya.example.test",
            connector=connector,
        )

    assert exc_info.value is cancelled
    assert writer.close_calls == 1
    assert writer.wait_closed_calls == 1
