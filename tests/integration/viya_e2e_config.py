from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit

__all__ = ["ViyaE2EConfig", "ViyaE2EConfigError", "load_viya_e2e_config"]

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / ".env.test"
_IGNORED_KEYS = frozenset({"RUN_VIYA_E2E"})
_REQUIRED_KEYS = frozenset(
    {
        "VIYA_E2E_BASE_URL",
        "VIYA_E2E_USERNAME",
        "VIYA_E2E_PASSWORD",
        "VIYA_E2E_CLIENT_ID",
        "VIYA_E2E_CLIENT_SECRET",
    }
)


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

    return ViyaE2EConfig(
        base_url=base_url,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
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
        if normalized_key not in _REQUIRED_KEYS:
            raise ViyaE2EConfigError("config contains an unsupported key")
        if normalized_key in values:
            raise ViyaE2EConfigError("config contains a duplicate key")
        values[normalized_key] = _parse_value(value)
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
