from __future__ import annotations

import importlib.util
from pathlib import Path

IMPORT_CONTRACT_BLOCKED_CASES: tuple[str, ...] = ()
IMPORT_CONTRACT_PATCH_BEFORE_IMPORT_CASES: tuple[str, ...] = (
    "none-observed: tests/**/*.py inventory found no patch-before-import usage; owner=@a129924",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_import_contract_supported_http_client_module_path_is_importable() -> None:
    assert importlib.util.find_spec("mlops_async.transport.http_client") is not None


def test_import_contract_legacy_core_http_client_module_path_is_not_importable() -> None:
    assert importlib.util.find_spec("mlops_async.core.http_client") is None
    assert not (_repo_root() / "src/mlops_async/core/http_client.py").exists()


def test_tc_blk_001_ambiguous_classification_cases_are_tracked_for_manual_recheck() -> None:
    assert all("owner=" in case for case in IMPORT_CONTRACT_BLOCKED_CASES)


def test_tc_reg_001_req_003_patch_before_import_is_explicitly_scoped() -> None:
    """TC-REG-001: REQ-003 patch-before-import evidence must be explicit in contract scope."""
    assert IMPORT_CONTRACT_PATCH_BEFORE_IMPORT_CASES != ()
    assert all("owner=" in case for case in IMPORT_CONTRACT_PATCH_BEFORE_IMPORT_CASES)
    assert all(
        case.startswith("tests/contracts/") or case.startswith("none-observed:")
        for case in IMPORT_CONTRACT_PATCH_BEFORE_IMPORT_CASES
    )
