"""Pre-commit 防護: 阻擋提交機器本機的絕對路徑."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Final

_ALLOWED_PLACEHOLDERS: Final[frozenset[str]] = frozenset({"<LOCAL_LEGACY_SERVICE_CODE_PATH>"})
_TRAILING_PUNCTUATION: Final[str] = ".,:;)]}`\"'"
_PATH_BODY_PATTERN: Final[str] = r"[^\s`\"'<>]+"


@dataclass(frozen=True)
class _Rule:
    name: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Finding:
    file_path: str
    line_number: int
    rule_name: str
    matched_text: str


_RULES: Final[tuple[_Rule, ...]] = (
    _Rule(
        name="macos_home_path",
        pattern=re.compile(r"(?<![A-Za-z0-9.])/" + "Users/" + _PATH_BODY_PATTERN),
    ),
    _Rule(
        name="linux_home_path",
        pattern=re.compile(r"(?<![A-Za-z0-9.])/" + "home/" + _PATH_BODY_PATTERN),
    ),
    _Rule(
        name="windows_home_path",
        pattern=re.compile(r"[A-Za-z]:(?:\\){1,2}Users(?:\\){1,2}" + _PATH_BODY_PATTERN),
    ),
)


def _normalize_match(raw_match: str) -> str:
    return raw_match.rstrip(_TRAILING_PUNCTUATION)


def _read_text_lines(path: Path) -> list[str] | None:
    try:
        raw_content = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw_content:
        return None

    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return raw_content.decode(encoding).splitlines()
        except UnicodeDecodeError:
            continue

    return None


def scan_paths(paths: list[str]) -> list[Finding]:
    """回傳提供檔案中所有被阻擋的本機絕對路徑命中結果."""
    findings: list[Finding] = []

    for raw_path in paths:
        candidate_path = Path(raw_path)
        lines = _read_text_lines(candidate_path)
        if lines is None:
            continue

        for line_number, line in enumerate(lines, start=1):
            for rule in _RULES:
                for match in rule.pattern.finditer(line):
                    matched_text = _normalize_match(match.group(0))
                    if not matched_text or matched_text in _ALLOWED_PLACEHOLDERS:
                        continue

                    findings.append(
                        Finding(
                            file_path=str(candidate_path),
                            line_number=line_number,
                            rule_name=rule.name,
                            matched_text=matched_text,
                        )
                    )

    return findings


def build_failure_message(findings: list[Finding]) -> str:
    """建立同時適合人類與代理閱讀的阻擋訊息."""
    header = [
        "偵測到禁止提交的本機絕對路徑 (local absolute paths).",
        "請改用 <LOCAL_LEGACY_SERVICE_CODE_PATH> 或移除個人機器路徑後再 commit.",
        "",
        f"共找到 {len(findings)} 個命中項目:",
    ]

    details: list[str] = []
    for finding in findings:
        details.extend(
            [
                "",
                f"- file: {finding.file_path}",
                f"  line: {finding.line_number}",
                f"  rule: {finding.rule_name}",
                f"  matched: {finding.matched_text}",
                (
                    "  remediation: 若這是文件中的本機參考路徑, 請改成 "
                    "<LOCAL_LEGACY_SERVICE_CODE_PATH>; 若不是必要資訊, 請移除後再 commit."
                ),
            ]
        )

    return "\n".join(header + details)


def main(argv: list[str] | None = None) -> int:
    """以 pre-commit entry point 方式執行本機路徑防護."""
    candidate_paths = list(sys.argv[1:] if argv is None else argv)
    findings = scan_paths(candidate_paths)

    if not findings:
        return 0

    print(build_failure_message(findings), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
