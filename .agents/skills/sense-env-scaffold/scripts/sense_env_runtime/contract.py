from __future__ import annotations

import re
from pathlib import Path

FENCED_BLOCK_RE = re.compile(
    r"^\s*```yaml\s+\[sensing-assertions\]\s*\r?\n(.*?)```",
    re.MULTILINE | re.DOTALL,
)

DEFAULT_CONTRACT_CANDIDATES = ("retrofit-plan.md", "blueprint.md")

RawAssertion = dict[str, str]


def resolve_contract_path(contract_file: str | None, repo_root: Path) -> Path | None:
    if contract_file:
        path = Path(contract_file)
        if not path.is_absolute():
            path = repo_root / path
        return path

    for candidate in DEFAULT_CONTRACT_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path

    return None


def extract_assertions_block(text: str) -> str | None:
    match = FENCED_BLOCK_RE.search(text)
    if match is None:
        return None
    return match.group(1)


def parse_assertions(block: str) -> list[RawAssertion]:
    records: list[RawAssertion] = []
    current: RawAssertion | None = None

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("- "):
            if current is not None:
                records.append(current)
            current = {}
            rest = line[2:].strip()
            if rest:
                key, _, value = rest.partition(":")
                current[key.strip()] = value.strip().strip('"').strip("'")
            continue

        if current is not None and ":" in line:
            key, _, value = line.partition(":")
            current[key.strip()] = value.strip().strip('"').strip("'")
            continue

        raise ValueError(f"Unsupported assertion syntax: {raw_line!r}")

    if current is not None:
        records.append(current)

    return records


__all__ = [
    "RawAssertion",
    "extract_assertions_block",
    "parse_assertions",
    "resolve_contract_path",
]
