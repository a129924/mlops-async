from __future__ import annotations

import os
import ssl
from pathlib import Path

import pytest

import tests.integration.viya_e2e_config as viya_e2e_config
from tests.integration.viya_e2e_config import ViyaE2EConfigError, load_viya_e2e_config


def _write_config(tmp_path: Path, lines: list[str]) -> Path:
    path = tmp_path / ".env.test"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _valid_config_lines(
    *,
    tls_mode: str | None = "system",
    ca_bundle: str | None = None,
) -> list[str]:
    lines = [
        "VIYA_E2E_BASE_URL=https://viya.example.test",
        "VIYA_E2E_USERNAME=test-user",
        "VIYA_E2E_PASSWORD=test-password",
        "VIYA_E2E_CLIENT_ID=test-client",
        "VIYA_E2E_CLIENT_SECRET=test-secret",
    ]
    if tls_mode is not None:
        lines.append(f"VIYA_E2E_TLS_MODE={tls_mode}")
    if ca_bundle is not None:
        lines.append(f"VIYA_E2E_CA_BUNDLE={ca_bundle}")
    return lines


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
            "VIYA_E2E_TLS_MODE=system",
        ],
    )
    monkeypatch.setenv("RUN_VIYA_E2E", "unexpected-process-value")

    config = load_viya_e2e_config(path)

    assert config.base_url == "https://viya.example.test"
    assert config.verify is True
    assert os.environ["RUN_VIYA_E2E"] == "unexpected-process-value"


def test_load_config_accepts_sas_ec_empty_secret_only(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        [
            "VIYA_E2E_BASE_URL=https://viya.example.test",
            "VIYA_E2E_USERNAME=test-user",
            "VIYA_E2E_PASSWORD=test-password",
            "VIYA_E2E_CLIENT_ID=sas.ec",
            "VIYA_E2E_CLIENT_SECRET=",
            "VIYA_E2E_TLS_MODE=system",
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
            "VIYA_E2E_TLS_MODE=system",
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
            "VIYA_E2E_TLS_MODE=system",
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
            "VIYA_E2E_TLS_MODE=system",
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
            "VIYA_E2E_TLS_MODE=system",
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
            "VIYA_E2E_TLS_MODE=system",
        ],
    )

    with pytest.raises(ViyaE2EConfigError, match="base_url"):
        load_viya_e2e_config(path)


def test_load_config_system_mode_uses_tls_verification(tmp_path: Path) -> None:
    path = _write_config(tmp_path, _valid_config_lines(tls_mode="system"))

    config = load_viya_e2e_config(path)

    assert config.verify is True


def test_load_config_insecure_mode_warns_once_and_disables_tls_verification(
    tmp_path: Path,
) -> None:
    path = _write_config(tmp_path, _valid_config_lines(tls_mode="insecure"))

    with pytest.warns(
        RuntimeWarning,
        match=r"^Viya E2E is running with TLS verification explicitly disabled$",
    ) as warning_records:
        config = load_viya_e2e_config(path)

    assert len(warning_records) == 1
    assert config.verify is False


def test_load_config_ca_bundle_mode_builds_ssl_context_from_exact_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ca_bundle = tmp_path / "company-ca.pem"
    expected_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    captured_cafile: list[str | None] = []

    def create_default_context(*, cafile: str | None = None) -> ssl.SSLContext:
        captured_cafile.append(cafile)
        return expected_context

    monkeypatch.setattr(ssl, "create_default_context", create_default_context)
    path = _write_config(
        tmp_path,
        _valid_config_lines(tls_mode="ca_bundle", ca_bundle=str(ca_bundle)),
    )

    config = load_viya_e2e_config(path)

    assert captured_cafile == [str(ca_bundle)]
    assert config.verify is expected_context


@pytest.mark.parametrize("tls_mode", [None, ""], ids=["missing", "blank"])
def test_load_config_requires_non_blank_tls_mode(
    tmp_path: Path,
    tls_mode: str | None,
) -> None:
    path = _write_config(tmp_path, _valid_config_lines(tls_mode=tls_mode))

    with pytest.raises(
        ViyaE2EConfigError,
        match=r"^Viya E2E TLS mode is required$",
    ):
        load_viya_e2e_config(path)


@pytest.mark.parametrize(
    "tls_mode",
    ["SYSTEM", " system", "system ", "internal-secret-mode"],
)
def test_load_config_rejects_non_exact_tls_mode_without_echoing_value(
    tmp_path: Path,
    tls_mode: str,
) -> None:
    path = _write_config(tmp_path, _valid_config_lines(tls_mode=tls_mode))

    with pytest.raises(ViyaE2EConfigError) as exc_info:
        load_viya_e2e_config(path)

    assert str(exc_info.value) == "Viya E2E TLS mode is invalid"
    assert tls_mode.strip() not in str(exc_info.value)


@pytest.mark.parametrize("tls_mode", ["system", "insecure"])
def test_load_config_rejects_non_blank_ca_bundle_outside_ca_bundle_mode(
    tmp_path: Path,
    tls_mode: str,
) -> None:
    path = _write_config(
        tmp_path,
        _valid_config_lines(tls_mode=tls_mode, ca_bundle="internal-company-ca.pem"),
    )

    with pytest.raises(
        ViyaE2EConfigError,
        match=r"^Viya E2E CA bundle is only valid in ca_bundle mode$",
    ):
        load_viya_e2e_config(path)


@pytest.mark.parametrize(
    ("tls_mode", "expected_verify", "warning_expected"),
    [("system", True, False), ("insecure", False, True)],
)
def test_load_config_treats_blank_ca_bundle_as_not_provided(
    tmp_path: Path,
    tls_mode: str,
    expected_verify: bool,
    warning_expected: bool,
) -> None:
    path = _write_config(
        tmp_path,
        _valid_config_lines(tls_mode=tls_mode, ca_bundle=""),
    )

    if warning_expected:
        with pytest.warns(RuntimeWarning):
            config = load_viya_e2e_config(path)
    else:
        config = load_viya_e2e_config(path)

    assert config.verify is expected_verify


@pytest.mark.parametrize("ca_bundle", [None, ""], ids=["missing", "blank"])
def test_load_config_ca_bundle_mode_requires_non_blank_ca_bundle(
    tmp_path: Path,
    ca_bundle: str | None,
) -> None:
    path = _write_config(
        tmp_path,
        _valid_config_lines(tls_mode="ca_bundle", ca_bundle=ca_bundle),
    )

    with pytest.raises(
        ViyaE2EConfigError,
        match=r"^Viya E2E CA bundle is required$",
    ):
        load_viya_e2e_config(path)


def test_load_config_translates_ca_load_error_without_exposing_path_or_cause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ca_bundle = tmp_path / "internal-company-ca.pem"
    load_error = ssl.SSLError(f"could not load secret CA at {ca_bundle}")

    def fail_to_create_default_context(*, cafile: str | None = None) -> ssl.SSLContext:
        del cafile
        raise load_error

    monkeypatch.setattr(ssl, "create_default_context", fail_to_create_default_context)
    path = _write_config(
        tmp_path,
        _valid_config_lines(tls_mode="ca_bundle", ca_bundle=str(ca_bundle)),
    )

    with pytest.raises(ViyaE2EConfigError) as exc_info:
        load_viya_e2e_config(path)

    assert str(exc_info.value) == "Viya E2E CA bundle could not be loaded"
    assert exc_info.value.__cause__ is load_error
    assert str(ca_bundle) not in str(exc_info.value)
    assert "could not load secret CA" not in str(exc_info.value)


def test_viya_e2e_config_verify_annotation_accepts_bool_or_ssl_context() -> None:
    assert viya_e2e_config.ViyaE2EConfig.__annotations__["verify"] == ("bool | ssl.SSLContext")
