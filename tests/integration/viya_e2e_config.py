from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
import ssl
from urllib.parse import urlsplit
from warnings import warn

__all__ = ["ViyaE2EConfig", "ViyaE2EConfigError", "load_viya_e2e_config"]

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / ".env.test"
_IGNORED_KEYS = frozenset({"RUN_VIYA_E2E"})
_TLS_MODE_KEY = "VIYA_E2E_TLS_MODE"
_CA_BUNDLE_KEY = "VIYA_E2E_CA_BUNDLE"
_REQUIRED_KEYS = frozenset(
    {
        "VIYA_E2E_BASE_URL",
        "VIYA_E2E_USERNAME",
        "VIYA_E2E_PASSWORD",
        "VIYA_E2E_CLIENT_ID",
        "VIYA_E2E_CLIENT_SECRET",
    }
)
_SUPPORTED_KEYS = _REQUIRED_KEYS | frozenset({_TLS_MODE_KEY, _CA_BUNDLE_KEY})


class ViyaE2EConfigError(ValueError):
    """Raised when the test-only Viya E2E configuration is unsafe or incomplete."""


@dataclass(frozen=True, slots=True)
class ViyaE2EConfig:
    """Validated password-grant inputs kept out of test output."""

    base_url: str
    username: str
    password: str
    client_id: str
    client_secret: str
    verify: bool | ssl.SSLContext


def load_viya_e2e_config(path: Path = _CONFIG_PATH) -> ViyaE2EConfig:
    """Load required password-grant inputs without exporting config values."""
    values = _parse_config(path)
    _validate_required_keys(values)

    base_url = values["VIYA_E2E_BASE_URL"]
    _validate_base_url(base_url)
    username = _require_non_blank(values["VIYA_E2E_USERNAME"], "username")
    password = _require_non_blank(values["VIYA_E2E_PASSWORD"], "password")
    client_id = _require_non_blank(values["VIYA_E2E_CLIENT_ID"], "client_id")
    client_secret = values["VIYA_E2E_CLIENT_SECRET"]
    _validate_client_secret(client_id, client_secret)
    verify = _resolve_verify(values)

    return ViyaE2EConfig(
        base_url=base_url,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )


def _parse_config(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ViyaE2EConfigError("config/.env.test is required") from exc

    values: dict[str, str] = {}
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ViyaE2EConfigError("config contains an invalid line")
        normalized_key = key.strip()
        if normalized_key in _IGNORED_KEYS:
            continue
        if normalized_key not in _SUPPORTED_KEYS:
            raise ViyaE2EConfigError("config contains an unsupported key")
        if normalized_key in values:
            raise ViyaE2EConfigError("config contains a duplicate key")
        values[normalized_key] = (
            _parse_tls_mode(value) if normalized_key == _TLS_MODE_KEY else _parse_value(value)
        )
    return values


def _validate_required_keys(values: dict[str, str]) -> None:
    missing = _REQUIRED_KEYS.difference(values)
    if missing:
        raise ViyaE2EConfigError("config is missing required keys")


def _parse_value(value: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        return ""

    if normalized_value[0] in "\"'":
        if len(normalized_value) < 2 or normalized_value[-1] != normalized_value[0]:
            raise ViyaE2EConfigError("config contains an invalid quoted value")
        return normalized_value[1:-1]

    if normalized_value[-1] in "\"'":
        raise ViyaE2EConfigError("config contains an invalid quoted value")
    return normalized_value


def _parse_tls_mode(value: str) -> str:
    if not value:
        return ""

    if value[0] in "\"'":
        if len(value) < 2 or value[-1] != value[0]:
            raise ViyaE2EConfigError("config contains an invalid quoted value")
        return value[1:-1]

    if value[-1] in "\"'":
        raise ViyaE2EConfigError("config contains an invalid quoted value")
    return value


def _resolve_verify(values: dict[str, str]) -> bool | ssl.SSLContext:
    tls_mode = values.get(_TLS_MODE_KEY)
    if tls_mode is None or tls_mode == "":
        raise ViyaE2EConfigError("Viya E2E TLS mode is required")
    if tls_mode not in {"system", "insecure", "ca_bundle"}:
        raise ViyaE2EConfigError("Viya E2E TLS mode is invalid")

    ca_bundle = values.get(_CA_BUNDLE_KEY, "")
    if tls_mode != "ca_bundle" and ca_bundle.strip():
        raise ViyaE2EConfigError("Viya E2E CA bundle is only valid in ca_bundle mode")
    if tls_mode == "system":
        return True
    if tls_mode == "insecure":
        warn(
            "Viya E2E is running with TLS verification explicitly disabled",
            RuntimeWarning,
            stacklevel=2,
        )
        return False
    if not ca_bundle.strip():
        raise ViyaE2EConfigError("Viya E2E CA bundle is required")

    try:
        return ssl.create_default_context(cafile=ca_bundle)
    except OSError as exc:
        raise ViyaE2EConfigError("Viya E2E CA bundle could not be loaded") from exc


def _require_non_blank(value: str, field_name: str) -> str:
    if not value.strip():
        raise ViyaE2EConfigError(f"{field_name} must be non-blank")
    return value


def _validate_client_secret(client_id: str, client_secret: str) -> None:
    if client_id == "sas.ec" and client_secret == "":
        return
    if not client_secret.strip():
        raise ViyaE2EConfigError("client_secret must be non-blank")


def _validate_base_url(value: str) -> None:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ViyaE2EConfigError("base_url must be a HTTPS origin")

    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ViyaE2EConfigError("base_url must not target loopback")
    try:
        address = ip_address(hostname)
    except ValueError:
        return
    if address.is_loopback:
        raise ViyaE2EConfigError("base_url must not target loopback")
