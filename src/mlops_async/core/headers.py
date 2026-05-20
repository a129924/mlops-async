from __future__ import annotations

from collections.abc import Mapping


def merge_headers(*mappings: Mapping[str, str] | None) -> dict[str, str]:
    """Merge headers case-insensitively while preserving the last original casing."""
    merged: dict[str, tuple[str, str]] = {}
    for mapping in mappings:
        if mapping is None:
            continue

        for name, value in mapping.items():
            merged[name.lower()] = (name, value)

    return dict(merged.values())
