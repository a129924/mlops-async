from __future__ import annotations

import importlib.util
from pathlib import Path

IMPORT_CONTRACT_BLOCKED_CASES: tuple[str, ...] = ()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_import_contract_supported_http_client_module_path_is_importable() -> None:
    assert importlib.util.find_spec("mlops_async.transport.http_client") is not None


def test_import_contract_legacy_core_http_client_module_path_is_not_importable() -> None:
    assert importlib.util.find_spec("mlops_async.core.http_client") is None
    assert not (_repo_root() / "src/mlops_async/core/http_client.py").exists()


def test_import_contract_blocked_cases_require_manual_recheck_before_classification() -> None:
    # Ambiguous cases must be parked here for manual recheck; do not auto-classify.
    assert IMPORT_CONTRACT_BLOCKED_CASES == ()
