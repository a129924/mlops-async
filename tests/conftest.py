from __future__ import annotations

import os

import pytest


def _is_opted_in() -> bool:
    return os.environ.get("RUN_VIYA_E2E") == "1"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "viya_e2e: opt-in test that calls a real SAS Viya environment",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    del items
    if config.option.markexpr.strip() == "viya_e2e" and not _is_opted_in():
        raise pytest.UsageError("RUN_VIYA_E2E=1 is required for pytest -m viya_e2e")


def pytest_runtest_setup(item: pytest.Item) -> None:
    if item.get_closest_marker("viya_e2e") is not None and not _is_opted_in():
        pytest.skip("Viya E2E disabled; set RUN_VIYA_E2E=1 to opt in")
