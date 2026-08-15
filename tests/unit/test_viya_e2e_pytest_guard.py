from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import pytest

import tests.conftest as viya_e2e_guard


_OPT_IN_REQUIRED_MESSAGE = (
    "RUN_VIYA_E2E=1 and VIYA_E2E_VPN_CONFIRMED=1 are required for pytest -m viya_e2e"
)


@dataclass(frozen=True)
class _FakeOption:
    markexpr: str


@dataclass(frozen=True)
class _FakeConfig:
    option: _FakeOption


class _FakeItem:
    def __init__(self, *, is_viya_e2e: bool) -> None:
        self._is_viya_e2e = is_viya_e2e

    def get_closest_marker(self, name: str) -> object | None:
        if name == "viya_e2e" and self._is_viya_e2e:
            return object()
        return None


def _config(markexpr: str) -> pytest.Config:
    return cast(pytest.Config, _FakeConfig(option=_FakeOption(markexpr=markexpr)))


def _items(*item_markers: bool) -> list[pytest.Item]:
    return cast(
        list[pytest.Item],
        [_FakeItem(is_viya_e2e=is_viya_e2e) for is_viya_e2e in item_markers],
    )


@pytest.mark.parametrize(
    ("run_viya_e2e", "vpn_confirmed", "expected"),
    (
        (None, None, False),
        ("1", None, False),
        (None, "1", False),
        ("true", "1", False),
        ("1", "true", False),
        ("1", "1", True),
    ),
)
def test_opt_in_requires_both_environment_variables_to_be_exactly_one(
    monkeypatch: pytest.MonkeyPatch,
    run_viya_e2e: str | None,
    vpn_confirmed: str | None,
    expected: bool,
) -> None:
    if run_viya_e2e is None:
        monkeypatch.delenv("RUN_VIYA_E2E", raising=False)
    else:
        monkeypatch.setenv("RUN_VIYA_E2E", run_viya_e2e)

    if vpn_confirmed is None:
        monkeypatch.delenv("VIYA_E2E_VPN_CONFIRMED", raising=False)
    else:
        monkeypatch.setenv("VIYA_E2E_VPN_CONFIRMED", vpn_confirmed)

    assert viya_e2e_guard._is_opted_in() is expected


@pytest.mark.parametrize(
    "markexpr",
    [
        "viya_e2e",
        "viya_e2e or unrelated_marker",
        "viya_e2e and not slow",
    ],
)
def test_collection_guard_rejects_selected_viya_e2e_without_opt_in(
    monkeypatch: pytest.MonkeyPatch,
    markexpr: str,
) -> None:
    monkeypatch.setattr(viya_e2e_guard, "_is_opted_in", lambda: False)
    items = _items(False, True)

    with pytest.raises(pytest.UsageError) as exc_info:
        viya_e2e_guard.pytest_collection_modifyitems(_config(markexpr), items)

    assert str(exc_info.value) == _OPT_IN_REQUIRED_MESSAGE


@pytest.mark.parametrize(
    "markexpr",
    [
        "unrelated_marker and viya_e2e",
        "not viya_e2e",
    ],
)
def test_collection_guard_allows_expression_when_no_viya_e2e_item_remains(
    monkeypatch: pytest.MonkeyPatch,
    markexpr: str,
) -> None:
    monkeypatch.setattr(viya_e2e_guard, "_is_opted_in", lambda: False)
    items = _items(False)
    original_items = list(items)

    viya_e2e_guard.pytest_collection_modifyitems(_config(markexpr), items)

    assert items == original_items


def test_collection_guard_allows_ordinary_run_for_later_skip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(viya_e2e_guard, "_is_opted_in", lambda: False)
    items = _items(True)
    original_items = list(items)

    viya_e2e_guard.pytest_collection_modifyitems(_config(""), items)

    assert items == original_items


@pytest.mark.parametrize(
    "markexpr",
    [
        "viya_e2e",
        "viya_e2e or unrelated_marker",
        "viya_e2e and not slow",
    ],
)
def test_collection_guard_allows_selected_viya_e2e_with_opt_in(
    monkeypatch: pytest.MonkeyPatch,
    markexpr: str,
) -> None:
    monkeypatch.setattr(viya_e2e_guard, "_is_opted_in", lambda: True)
    items = _items(False, True)
    original_items = list(items)

    viya_e2e_guard.pytest_collection_modifyitems(_config(markexpr), items)

    assert items == original_items


def test_collection_guard_runs_after_native_marker_deselection() -> None:
    hook_options = cast(
        dict[str, object],
        getattr(viya_e2e_guard.pytest_collection_modifyitems, "pytest_impl", {}),
    )

    assert hook_options.get("trylast") is True
