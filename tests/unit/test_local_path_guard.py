from __future__ import annotations

from pathlib import Path

import pytest

from mlops_async._repo_hooks.local_path_guard import Finding, build_failure_message, scan_paths


def _macos_path() -> str:
    return "/" + "Users/example-user/work/sample-project"


def _linux_path() -> str:
    return "/" + "home/example-user/work/sample-project"


def _windows_path() -> str:
    return "C:" + "\\Users\\example-user\\work\\sample-project"


def _escaped_windows_path() -> str:
    return "C:" + "\\\\Users\\\\example-user\\\\work\\\\sample-project"


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("single-backslash", _windows_path()),
        ("escaped-double-backslash", _escaped_windows_path()),
    ],
)
def test_scan_paths_detects_windows_home_path_variants(
    tmp_path: Path, label: str, value: str
) -> None:
    # Regression for reviewer comment r3231281356: escaped Windows paths must also be blocked.
    sample_file = tmp_path / f"{label}.md"
    sample_file.write_text(f"windows path: `{value}`\n", encoding="utf-8")

    findings = scan_paths([str(sample_file)])

    assert [
        (finding.rule_name, finding.line_number, finding.matched_text) for finding in findings
    ] == [
        ("windows_home_path", 1, value),
    ]


def test_scan_paths_detects_supported_unix_home_directory_patterns(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.md"
    sample_file.write_text(
        "\n".join(
            [
                f"mac path: `{_macos_path()}`",
                f"linux path: `{_linux_path()}`",
            ]
        ),
        encoding="utf-8",
    )

    findings = scan_paths([str(sample_file)])

    assert [(finding.rule_name, finding.line_number) for finding in findings] == [
        ("macos_home_path", 1),
        ("linux_home_path", 2),
    ]


def test_scan_paths_allows_document_placeholder(tmp_path: Path) -> None:
    sample_file = tmp_path / "placeholder.md"
    sample_file.write_text(
        "Legacy service path: <LOCAL_LEGACY_SERVICE_CODE_PATH>\n",
        encoding="utf-8",
    )

    assert scan_paths([str(sample_file)]) == []


def test_scan_paths_skips_binary_files(tmp_path: Path) -> None:
    binary_file = tmp_path / "sample.bin"
    binary_file.write_bytes(b"\x00\x01\x02")

    assert scan_paths([str(binary_file)]) == []


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/home/docs",
        "https://example.com/Users/docs",
    ],
)
def test_scan_paths_does_not_flag_url_path_segments(tmp_path: Path, url: str) -> None:
    sample_file = tmp_path / "urls.md"
    sample_file.write_text(f"reference: {url}\n", encoding="utf-8")

    assert scan_paths([str(sample_file)]) == []


def test_build_failure_message_is_human_and_agent_friendly() -> None:
    finding = Finding(
        file_path="docs/reference.md",
        line_number=12,
        rule_name="macos_home_path",
        matched_text=_macos_path(),
    )

    message = build_failure_message([finding])

    assert "偵測到禁止提交的本機絕對路徑" in message
    assert "file: docs/reference.md" in message
    assert "line: 12" in message
    assert "rule: macos_home_path" in message
    assert f"matched: {_macos_path()}" in message
    assert "<LOCAL_LEGACY_SERVICE_CODE_PATH>" in message
