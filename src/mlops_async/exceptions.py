from __future__ import annotations

__all__ = ["MlopsAsyncBaseException"]


class MlopsAsyncBaseException(Exception):  # noqa: N818 - name locked by topic contract
    """Base exception for internal mlops-async failures."""
