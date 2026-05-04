from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .contract import (
    RawAssertion,
    extract_assertions_block,
    parse_assertions,
    resolve_contract_path,
)
from .models import (
    AssertionKind,
    AssertionRecord,
    AssertionState,
    ContractGapKind,
    ExitCode,
    Facts,
    Fingerprint,
    GapKind,
    GapRecord,
    GapState,
    JsonObject,
    JsonValue,
    Manifest,
    Meta,
    RemediationType,
    RunMode,
    SCHEMA_VERSION,
    SCRIPT_VERSION,
)

KEY_PATHS = (
    "README.md",
    ".github/",
    "pyproject.toml",
    "tests/",
    "scripts/",
    ".github/copilot-instructions.md",
)

SECRET_PATTERNS = re.compile(
    r"(token|secret|password|api_key|apikey|credential|auth)",
    re.IGNORECASE,
)


class UnsupportedAssertionKindError(ValueError):
    """Raised when an assertion kind is outside the v1 supported subset."""


def find_repo_root(start: Path) -> Path:
    """Search upward from start for a .git directory or file."""
    current = start.resolve()
    while True:
        candidate = current / ".git"
        if candidate.exists():
            return current
        parent = current.parent
        if parent == current:
            return start.resolve()
        current = parent


def resolve_output_path(output: str | None, repo_root: Path) -> Path:
    if output is None:
        return repo_root / ".github" / "env-manifest.json"

    output_path = Path(output)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    return output_path


def _snapshot_output_path(repo_root: Path) -> Path:
    return repo_root / ".github" / "env-manifest.snapshot.json"


def make_meta(mode: RunMode) -> Meta:
    return Meta(
        schema_version=SCHEMA_VERSION,
        run_mode=mode,
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        script_version=SCRIPT_VERSION,
    )


def make_fingerprint(repo_root: Path) -> Fingerprint:
    marker = ".git" if (repo_root / ".git").exists() else None
    version_info = sys.version_info
    return Fingerprint(
        repo_root_marker=marker,
        python_version=f"{version_info.major}.{version_info.minor}.{version_info.micro}",
        platform=sys.platform,
    )


def _run_git_command(repo_root: Path, arguments: list[str]) -> str | None:
    try:
        result = subprocess.run(
            arguments,
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def make_facts(repo_root: Path) -> Facts:
    repo_present = (repo_root / ".git").exists()

    git_available = False
    current_branch: str | None = None
    workspace_clean: bool | None = None

    if shutil.which("git") is not None:
        current_branch = _run_git_command(
            repo_root, ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        )
        if current_branch is not None:
            git_available = True
            branch_status = _run_git_command(
                repo_root, ["git", "status", "--porcelain"]
            )
            if branch_status is not None:
                workspace_clean = branch_status == ""

    key_paths = {
        relative_path: (repo_root / relative_path).exists()
        for relative_path in KEY_PATHS
    }

    return Facts(
        repo_present=repo_present,
        git_available=git_available,
        current_branch=current_branch or None,
        workspace_clean=workspace_clean,
        key_paths=key_paths,
    )


def build_manifest(
    *,
    mode: RunMode,
    repo_root: Path,
    assertions: list[AssertionRecord],
    gaps: list[GapRecord],
) -> Manifest:
    return Manifest(
        meta=make_meta(mode),
        fingerprint=make_fingerprint(repo_root),
        facts=make_facts(repo_root),
        assertions=assertions,
        gaps=gaps,
    )


def make_gap(
    *,
    kind: GapKind,
    target: str,
    detail: str,
    remediation_type: RemediationType | None,
) -> GapRecord:
    return GapRecord(
        id="",
        kind=kind,
        target=target,
        state=GapState.UNRESOLVED,
        detail=detail,
        remediation_type=remediation_type,
    )


def make_assertion_record(
    *,
    kind: AssertionKind,
    target: str,
    state: AssertionState,
    expected: bool | str,
    observed: bool | str | None,
    remediation_type: RemediationType | None,
) -> AssertionRecord:
    return AssertionRecord(
        id="",
        kind=kind,
        target=target,
        state=state,
        expected=expected,
        observed=observed,
        remediation_type=remediation_type,
    )


def _parse_assertion_kind(raw_kind: str) -> AssertionKind:
    try:
        return AssertionKind(raw_kind)
    except ValueError as exc:
        raise UnsupportedAssertionKindError(
            f"assertion kind {raw_kind!r} is not in the v1 supported subset "
            f"(path_exists, path_type, command_available)"
        ) from exc


def evaluate_assertion(
    record: RawAssertion, repo_root: Path
) -> tuple[AssertionRecord, GapRecord | None]:
    """
    Evaluate one assertion record.

    Returns (assertion_record_without_id, gap_without_id | None).
    Raises UnsupportedAssertionKindError for any kind outside the v1 subset.
    """
    kind = _parse_assertion_kind(record.get("kind", ""))
    target = record.get("target", "")
    expected_raw = record.get("expected", "")

    match kind:
        case AssertionKind.PATH_EXISTS:
            expected = expected_raw.lower() in ("true", "yes", "1")
            is_observed = (repo_root / target).exists()
            state = (
                AssertionState.PASS if is_observed == expected else AssertionState.FAIL
            )
            if state is AssertionState.PASS:
                return (
                    make_assertion_record(
                        kind=kind,
                        target=target,
                        state=state,
                        expected=expected,
                        observed=is_observed,
                        remediation_type=None,
                    ),
                    None,
                )

            remediation = (
                RemediationType.MISSING if expected else RemediationType.DEPRECATED
            )
            gap = make_gap(
                kind=kind,
                target=target,
                detail=f"path_exists: expected {expected}, got {is_observed}",
                remediation_type=remediation,
            )
            return (
                make_assertion_record(
                    kind=kind,
                    target=target,
                    state=state,
                    expected=expected,
                    observed=is_observed,
                    remediation_type=remediation,
                ),
                gap,
            )

        case AssertionKind.PATH_TYPE:
            path = repo_root / target
            if path.is_dir():
                observed: str | None = "directory"
            elif path.is_file():
                observed = "file"
            else:
                observed = None

            expected = expected_raw.strip()
            state = AssertionState.PASS if observed == expected else AssertionState.FAIL
            if state is AssertionState.PASS:
                return (
                    make_assertion_record(
                        kind=kind,
                        target=target,
                        state=state,
                        expected=expected,
                        observed=observed,
                        remediation_type=None,
                    ),
                    None,
                )

            remediation = (
                RemediationType.MISSING
                if observed is None
                else RemediationType.MISMATCH
            )
            gap = make_gap(
                kind=kind,
                target=target,
                detail=f"path_type: expected {expected!r}, got {observed!r}",
                remediation_type=remediation,
            )
            return (
                make_assertion_record(
                    kind=kind,
                    target=target,
                    state=state,
                    expected=expected,
                    observed=observed,
                    remediation_type=remediation,
                ),
                gap,
            )

        case AssertionKind.COMMAND_AVAILABLE:
            expected = expected_raw.lower() in ("true", "yes", "1")
            is_observed = shutil.which(target) is not None
            state = (
                AssertionState.PASS if is_observed == expected else AssertionState.FAIL
            )
            if state is AssertionState.PASS:
                return (
                    make_assertion_record(
                        kind=kind,
                        target=target,
                        state=state,
                        expected=expected,
                        observed=is_observed,
                        remediation_type=None,
                    ),
                    None,
                )

            remediation = (
                RemediationType.MISSING if expected else RemediationType.DEPRECATED
            )
            gap = make_gap(
                kind=kind,
                target=target,
                detail=f"command_available: expected {expected}, got {is_observed}",
                remediation_type=remediation,
            )
            return (
                make_assertion_record(
                    kind=kind,
                    target=target,
                    state=state,
                    expected=expected,
                    observed=is_observed,
                    remediation_type=remediation,
                ),
                gap,
            )


def _require_object(value: JsonValue, field_name: str) -> JsonObject:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be a JSON object")
    return value


def _is_secret_shaped(key: str, value: JsonValue) -> bool:
    return isinstance(value, str) and SECRET_PATTERNS.search(key) is not None


def shape_snapshot(manifest: Manifest) -> JsonObject:
    payload = manifest.to_dict()

    fingerprint = _require_object(payload["fingerprint"], "fingerprint")
    for key in list(fingerprint.keys()):
        if key not in {"repo_root_marker", "python_version", "platform"}:
            del fingerprint[key]

    facts = _require_object(payload["facts"], "facts")
    key_paths = _require_object(facts["key_paths"], "facts.key_paths")
    for key, value in list(key_paths.items()):
        if isinstance(value, str) and os.path.isabs(value):
            key_paths[key] = None

    for key, value in list(facts.items()):
        if _is_secret_shaped(key, value):
            del facts[key]

    return payload


def write_manifest(payload: JsonObject, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    output_path.write_text(f"{rendered}\n", encoding="utf-8")


def _emit_to_stderr(payload: JsonObject) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)


def _try_emit(manifest: Manifest, output_path: Path) -> bool:
    """
    Try to write manifest to output_path.
    On failure, annotates manifest with the error and emits to stderr.
    Returns True if written to disk, False if fell back to stderr.
    """
    try:
        write_manifest(manifest.to_dict(), output_path)
        return True
    except OSError as exc:
        _emit_to_stderr(manifest.with_meta_error(str(exc)).to_dict())
        return False


def _try_emit_payload(
    payload: JsonObject, output_path: Path, fallback_manifest: Manifest
) -> bool:
    try:
        write_manifest(payload, output_path)
        return True
    except OSError as exc:
        _emit_to_stderr(fallback_manifest.with_meta_error(str(exc)).to_dict())
        return False


def _next_record_id(kind: GapKind | AssertionKind, counts: dict[str, int]) -> str:
    kind_value = kind.value
    current_index = counts.get(kind_value, 0)
    counts[kind_value] = current_index + 1
    return f"{kind_value}/{current_index}"


def _contract_gap_remediation(kind: ContractGapKind) -> RemediationType:
    if kind is ContractGapKind.CONTRACT_MISSING:
        return RemediationType.MISSING
    return RemediationType.MALFORMED


def _contract_failure_manifest(
    *,
    repo_root: Path,
    kind: ContractGapKind,
    target: str,
    detail: str,
    assertions: list[AssertionRecord] | None = None,
) -> Manifest:
    gap = make_gap(
        kind=kind,
        target=target,
        detail=detail,
        remediation_type=_contract_gap_remediation(kind),
    ).with_id(f"{kind.value}/0")
    return build_manifest(
        mode=RunMode.ACCEPTANCE,
        repo_root=repo_root,
        assertions=[] if assertions is None else assertions,
        gaps=[gap],
    )


def run_discovery(repo_root: Path, output_path: Path, snapshot: bool) -> ExitCode:
    manifest = build_manifest(
        mode=RunMode.DISCOVERY,
        repo_root=repo_root,
        assertions=[],
        gaps=[],
    )

    if not _try_emit(manifest, output_path):
        return ExitCode.IO_ERROR

    if snapshot:
        if not _try_emit_payload(
            shape_snapshot(manifest), _snapshot_output_path(repo_root), manifest
        ):
            return ExitCode.IO_ERROR

    return ExitCode.OK


def run_acceptance(
    repo_root: Path,
    output_path: Path,
    contract_file: str | None,
    snapshot: bool,
) -> ExitCode:
    contract_path = resolve_contract_path(contract_file, repo_root)
    if contract_path is None or not contract_path.is_file():
        manifest = _contract_failure_manifest(
            repo_root=repo_root,
            kind=ContractGapKind.CONTRACT_MISSING,
            target=str(contract_path) if contract_path is not None else "<none>",
            detail="no readable contract file found",
        )
        _try_emit(manifest, output_path)
        return ExitCode.CONTRACT_ERROR

    try:
        contract_text = contract_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        manifest = _contract_failure_manifest(
            repo_root=repo_root,
            kind=ContractGapKind.CONTRACT_MISSING,
            target=str(contract_path),
            detail="contract file not readable",
        )
        _try_emit(manifest, output_path)
        return ExitCode.CONTRACT_ERROR

    block = extract_assertions_block(contract_text)
    if block is None:
        manifest = _contract_failure_manifest(
            repo_root=repo_root,
            kind=ContractGapKind.CONTRACT_MALFORMED,
            target=str(contract_path),
            detail="no ```yaml [sensing-assertions] block found in contract",
        )
        _try_emit(manifest, output_path)
        return ExitCode.CONTRACT_ERROR

    try:
        raw_records = parse_assertions(block)
    except ValueError as exc:
        manifest = _contract_failure_manifest(
            repo_root=repo_root,
            kind=ContractGapKind.CONTRACT_MALFORMED,
            target=str(contract_path),
            detail=f"malformed assertion block: {exc}",
        )
        _try_emit(manifest, output_path)
        return ExitCode.CONTRACT_ERROR

    assertion_results: list[AssertionRecord] = []
    gaps: list[GapRecord] = []
    any_fail = False
    assertion_counts: dict[str, int] = {}
    gap_counts: dict[str, int] = {}

    try:
        for raw_record in raw_records:
            assertion_record, gap_record = evaluate_assertion(raw_record, repo_root)
            assertion_record = assertion_record.with_id(
                _next_record_id(assertion_record.kind, assertion_counts)
            )
            assertion_results.append(assertion_record)

            if gap_record is not None:
                gap_record = gap_record.with_id(
                    _next_record_id(gap_record.kind, gap_counts)
                )
                gaps.append(gap_record)

            if assertion_record.state is AssertionState.FAIL:
                any_fail = True
    except UnsupportedAssertionKindError as exc:
        manifest = _contract_failure_manifest(
            repo_root=repo_root,
            kind=ContractGapKind.CONTRACT_ERROR,
            target="<assertion>",
            detail=str(exc),
            assertions=assertion_results,
        )
        _try_emit(manifest, output_path)
        return ExitCode.CONTRACT_ERROR

    manifest = build_manifest(
        mode=RunMode.ACCEPTANCE,
        repo_root=repo_root,
        assertions=assertion_results,
        gaps=gaps,
    )

    if not _try_emit(manifest, output_path):
        return ExitCode.IO_ERROR

    if any_fail:
        return ExitCode.ACCEPTANCE_FAIL

    if snapshot:
        if not _try_emit_payload(
            shape_snapshot(manifest), _snapshot_output_path(repo_root), manifest
        ):
            return ExitCode.IO_ERROR

    return ExitCode.OK


__all__ = [
    "UnsupportedAssertionKindError",
    "evaluate_assertion",
    "find_repo_root",
    "resolve_output_path",
    "run_acceptance",
    "run_discovery",
    "shape_snapshot",
]
