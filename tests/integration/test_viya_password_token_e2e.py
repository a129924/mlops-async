from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx
import pytest

from mlops_async.core.request_options import RequestTimeouts
from mlops_async.core.token_endpoint.password import PasswordTokenEndpointClient
from mlops_async.transport.http_client import HttpClient

from tests.integration.viya_e2e_config import load_viya_e2e_config
from tests.integration.viya_e2e_vpn import _require_viya_e2e_vpn_preflight


def _raise_redacted_failure(error_type: str) -> None:
    raise AssertionError(f"Viya password token E2E failed: {error_type}") from None


@pytest.mark.asyncio
@pytest.mark.viya_e2e
async def test_password_token_e2e_validates_exact_success_contract() -> None:
    status_codes: list[int] = []

    async def record_status(response: httpx.Response) -> None:
        status_codes.append(response.status_code)

    try:
        config = load_viya_e2e_config()
        await _require_viya_e2e_vpn_preflight(config.base_url)
        async with HttpClient(
            config.base_url,
            timeout=RequestTimeouts(total=30),
            verify=config.verify,
        ) as http_client:
            http_client._client.event_hooks["response"].append(record_status)
            client = PasswordTokenEndpointClient(
                http_client,
                username=config.username,
                password=config.password,
                client_id=config.client_id,
                client_secret=config.client_secret,
            )
            initial_access_token = await client.fetch_access_token()
            refreshed_access_token = await client.refresh_access_token(initial_access_token)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        _raise_redacted_failure(type(exc).__name__)

    assert status_codes == [200, 200]
    assert initial_access_token.value
    assert initial_access_token.expires_at > datetime.now(timezone.utc)
    assert refreshed_access_token.value
    assert refreshed_access_token.expires_at > datetime.now(timezone.utc)
