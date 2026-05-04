from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, IntEnum

SCRIPT_VERSION = "1.0.0"
SCHEMA_VERSION = "1"

JsonScalar = str | int | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]

AssertionExpected = bool | str
AssertionObserved = bool | str | None


class RunMode(str, Enum):
    DISCOVERY = "discovery"
    ACCEPTANCE = "acceptance"


class ExitCode(IntEnum):
    OK = 0
    IO_ERROR = 10
    ACCEPTANCE_FAIL = 20
    CONTRACT_ERROR = 30


class AssertionKind(str, Enum):
    PATH_EXISTS = "path_exists"
    PATH_TYPE = "path_type"
    COMMAND_AVAILABLE = "command_available"


class AssertionState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class GapState(str, Enum):
    UNRESOLVED = "UNRESOLVED"


class RemediationType(str, Enum):
    MISSING = "MISSING"
    DEPRECATED = "DEPRECATED"
    MISMATCH = "MISMATCH"
    MALFORMED = "MALFORMED"


class ContractGapKind(str, Enum):
    CONTRACT_MISSING = "CONTRACT_MISSING"
    CONTRACT_MALFORMED = "CONTRACT_MALFORMED"
    CONTRACT_ERROR = "CONTRACT_ERROR"


GapKind = AssertionKind | ContractGapKind


@dataclass(frozen=True)
class Meta:
    schema_version: str
    run_mode: RunMode
    timestamp_utc: str
    script_version: str
    error: str | None = None

    def with_error(self, error: str) -> Meta:
        return replace(self, error=error)

    def to_dict(self) -> JsonObject:
        payload: JsonObject = {
            "schema_version": self.schema_version,
            "run_mode": self.run_mode.value,
            "timestamp_utc": self.timestamp_utc,
            "script_version": self.script_version,
        }
        if self.error is not None:
            payload["error"] = self.error
        return payload


@dataclass(frozen=True)
class Fingerprint:
    repo_root_marker: str | None
    python_version: str
    platform: str

    def to_dict(self) -> JsonObject:
        return {
            "repo_root_marker": self.repo_root_marker,
            "python_version": self.python_version,
            "platform": self.platform,
        }


@dataclass(frozen=True)
class Facts:
    repo_present: bool
    git_available: bool
    current_branch: str | None
    workspace_clean: bool | None
    key_paths: dict[str, bool]

    def to_dict(self) -> JsonObject:
        return {
            "repo_present": self.repo_present,
            "git_available": self.git_available,
            "current_branch": self.current_branch,
            "workspace_clean": self.workspace_clean,
            "key_paths": dict(self.key_paths),
        }


@dataclass(frozen=True)
class AssertionRecord:
    id: str
    kind: AssertionKind
    target: str
    state: AssertionState
    expected: AssertionExpected
    observed: AssertionObserved
    remediation_type: RemediationType | None

    def with_id(self, record_id: str) -> AssertionRecord:
        return replace(self, id=record_id)

    def to_dict(self) -> JsonObject:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "target": self.target,
            "state": self.state.value,
            "expected": self.expected,
            "observed": self.observed,
            "remediation_type": None
            if self.remediation_type is None
            else self.remediation_type.value,
        }


@dataclass(frozen=True)
class GapRecord:
    id: str
    kind: GapKind
    target: str
    state: GapState
    detail: str
    remediation_type: RemediationType | None

    def with_id(self, record_id: str) -> GapRecord:
        return replace(self, id=record_id)

    def to_dict(self) -> JsonObject:
        kind_value = self.kind.value
        return {
            "id": self.id,
            "kind": kind_value,
            "target": self.target,
            "state": self.state.value,
            "detail": self.detail,
            "remediation_type": None
            if self.remediation_type is None
            else self.remediation_type.value,
        }


@dataclass(frozen=True)
class Manifest:
    meta: Meta
    fingerprint: Fingerprint
    facts: Facts
    assertions: list[AssertionRecord]
    gaps: list[GapRecord]

    def with_meta_error(self, error: str) -> Manifest:
        return replace(self, meta=self.meta.with_error(error))

    def to_dict(self) -> JsonObject:
        return {
            "meta": self.meta.to_dict(),
            "fingerprint": self.fingerprint.to_dict(),
            "facts": self.facts.to_dict(),
            "assertions": [record.to_dict() for record in self.assertions],
            "gaps": [record.to_dict() for record in self.gaps],
        }


__all__ = [
    "AssertionExpected",
    "AssertionKind",
    "AssertionObserved",
    "AssertionRecord",
    "AssertionState",
    "ContractGapKind",
    "ExitCode",
    "Facts",
    "Fingerprint",
    "GapKind",
    "GapRecord",
    "GapState",
    "JsonObject",
    "JsonScalar",
    "JsonValue",
    "Manifest",
    "Meta",
    "RemediationType",
    "RunMode",
    "SCHEMA_VERSION",
    "SCRIPT_VERSION",
]
