from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.integration.viya_e2e_config import ViyaE2EConfigError, load_viya_e2e_config


def _write_config(tmp_path: Path, lines: list[str]) -> Path:
    path = tmp_path / ".env.test"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def test_load_config_ignores_run_opt_in_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _write_config(
        tmp_path,
        [
            "RUN_VIYA_E2E=1",
            "VIYA_E2E_BASE_URL=https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=test-client",
            "VIYA_E2E_CLIENT_SECRET=test-secret",
        ],
    )
    monkeypatch.delenv("RUN_VIYA_E2E", raising=False)

    config = load_viya_e2e_config(path)

    assert config.base_url == "https://viya.example.test"
    assert os.environ.get("RUN_VIYA_E2E") is None


def test_load_config_accepts_sas_ec_empty_secret_only(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL=https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=sas.ec",
            "VIYA_E2E_CLIENT_SECRET=",
        ],
    )

    config = load_viya_e2e_config(path)

    assert config.client_id == "sas.ec"
    assert config.client_secret == ""


def test_load_config_accepts_quoted_dotenv_values(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL = 'https://viya.example.test/'",
            'VIYA_E2E_USERNAME = "test-user"',
            "VIYA_E2E_PASSWORD = 'test-password'",
            "VIYA_E2E_CLIENT_ID = test-client",
            "VIYA_E2E_CLIENT_SECRET = test-secret",
        ],
    )

    config = load_viya_e2e_config(path)

    assert config.base_url == "https://viya.example.test/"
    assert config.username == "test-user"


@pytest.mark.parametrize(
    "client_id,client_secret",
    [("other-client", ""), ("sas.ec", "' '"), ("other-client", "  ")],
)
def test_load_config_rejects_invalid_secret_without_echoing_value(
    tmp_path: Path,
    client_id: str,
    client_secret: str,
) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL=https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            f"VIYA_E2E_CLIENT_ID={client_id}",
            f"VIYA_E2E_CLIENT_SECRET={client_secret}",
        ],
    )

    with pytest.raises(ViyaE2EConfigError) as exc_info:
        load_viya_e2e_config(path)

    assert "client_secret" in str(exc_info.value)
    assert "other-client" not in str(exc_info.value)


def test_load_config_rejects_missing_required_key(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL=https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=test-client",
        ],
    )

    with pytest.raises(ViyaE2EConfigError, match="required"):
        load_viya_e2e_config(path)


def test_load_config_rejects_invalid_syntax_without_echoing_line(tmp_path: Path) -> None:
    path = _write_config(tmp_path, ["secret-value-without-an-equals-sign"])

    with pytest.raises(ViyaE2EConfigError) as exc_info:
        load_viya_e2e_config(path)

    assert "secret-value" not in str(exc_info.value)


def test_load_config_rejects_unmatched_quote_without_echoing_value(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL='https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=test-client",
            "VIYA_E2E_CLIENT_SECRET=test-secret",
        ],
    )

    with pytest.raises(ViyaE2EConfigError) as exc_info:
        load_viya_e2e_config(path)

    assert "viya.example.test" not in str(exc_info.value)


@pytest.mark.parametrize(
    "base_url",
    ["http://viya.example.test", "https://localhost", "https://127.0.0.1"],
)
def test_load_config_rejects_unsafe_base_url(tmp_path: Path, base_url: str) -> None:
    path = _write_config(
        tmp_path,
        [
            f"VIYA_E2E_BASE_URL={base_url}",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=test-client",
            "VIYA_E2E_CLIENT_SECRET=test-secret",
        ],
    )

    with pytest.raises(ViyaE2EConfigError, match="base_url"):
        load_viya_e2e_config(path)
