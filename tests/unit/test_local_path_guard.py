from __future__ import annotations

from pathlib import Path

from mlops_async._repo_hooks.local_path_guard import Finding, build_failure_message, scan_paths


def _macos_path() -> str:
    return "/" + "Users/andrew/code/python/mlops-async"


def _linux_path() -> str:
    return "/" + "home/andrew/code/python/mlops-async"


def _windows_path() -> str:
    return "C:" + "\\Users\\andrew\\code\\python\\mlops-async"


def test_scan_paths_detects_supported_home_directory_patterns(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.md"
    sample_file.write_text(
        "\n".join(
            [
                f"mac path: `{_macos_path()}`",
                f"linux path: `{_linux_path()}`",
                f"windows path: `{_windows_path()}`",
            ]
        ),
        encoding="utf-8",
    )

    findings = scan_paths([str(sample_file)])

    assert [(finding.rule_name, finding.line_number) for finding in findings] == [
        ("macos_home_path", 1),
        ("linux_home_path", 2),
        ("windows_home_path", 3),
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
