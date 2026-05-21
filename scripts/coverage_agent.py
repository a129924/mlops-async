"""Coverage Agent: 讀取 coverage.json, 生成 test stub 或輸出 human-review feedback."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

_STOP_KEYWORDS: tuple[str, ...] = (
    "upload",
    "download",
    "streaming",
    "polling",
    "retry",
    "pagination",
    "session",
    "live api",
    "external io",
)
_COVERAGE_JSON_PATH: Path = Path(".coverage-reports/coverage.json")
_COVERAGE_THRESHOLD: int = 80
_TESTS_UNIT_DIR: Path = Path("tests/unit")
_DOCS_DIRS: tuple[str, ...] = ("docs", "analysis")


class _FunctionInfo(NamedTuple):
    name: str
    args: list[str]
    return_annotation: str
    docstring: str
    missing_lines: list[int]


def _run_pytest() -> int:
    """Run pytest with coverage; return exit code."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "pytest",
            "tests/unit/",
            "--cov=src/mlops_async",
            f"--cov-report=json:{_COVERAGE_JSON_PATH}",
            "--cov-report=term-missing",
            "-q",
            "--no-header",
        ],
        check=False,
    )
    return result.returncode


def _load_coverage_json() -> dict:  # type: ignore[type-arg]
    """Load coverage.json; run pytest first if missing. sys.exit(1) if still absent."""
    if not _COVERAGE_JSON_PATH.exists():
        _run_pytest()
    if not _COVERAGE_JSON_PATH.exists():
        print(f"ERROR: {_COVERAGE_JSON_PATH} not found after pytest run.", file=sys.stderr)
        sys.exit(1)
    return json.loads(_COVERAGE_JSON_PATH.read_text())


def _gap_modules(coverage_data: dict) -> list[tuple[str, list[int]]]:  # type: ignore[type-arg]
    """Return (file_path, missing_lines) for files below coverage threshold."""
    gaps: list[tuple[str, list[int]]] = []
    for file_path, file_data in coverage_data.get("files", {}).items():
        percent = file_data.get("summary", {}).get("percent_covered", 100.0)
        if percent < _COVERAGE_THRESHOLD:
            missing: list[int] = file_data.get("missing_lines", [])
            gaps.append((file_path, missing))
    return gaps


def _has_stop_condition(text: str) -> bool:
    """Return True if text contains any stop-condition keyword (case-insensitive)."""
    lower = text.lower()
    return any(kw in lower for kw in _STOP_KEYWORDS)


def _find_docs_explanation(module_stem: str) -> str:
    """Search docs/ and analysis/ for markdown containing module_stem; return first 500 chars."""
    for docs_dir in _DOCS_DIRS:
        for md_file in Path(docs_dir).rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if module_stem in content:
                    return content[:500]
            except OSError:
                continue
    return ""


def _extract_functions(source_path: Path, missing_lines: list[int]) -> list[_FunctionInfo]:
    """Parse source_path with ast; return _FunctionInfo for functions overlapping missing_lines."""
    try:
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return []

    missing_set = set(missing_lines)
    results: list[_FunctionInfo] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        func_lines = set(range(node.lineno, node.end_lineno + 1))
        if not func_lines.intersection(missing_set):
            continue
        args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
        return_ann = ""
        if node.returns is not None:
            return_ann = ast.unparse(node.returns)
        docstring = ast.get_docstring(node) or ""
        overlap = sorted(func_lines.intersection(missing_set))
        results.append(
            _FunctionInfo(
                name=node.name,
                args=args,
                return_annotation=return_ann,
                docstring=docstring,
                missing_lines=overlap,
            )
        )
    return results


def _module_stem(file_path: str) -> str:
    """Return the stem (filename without extension) of a file path."""
    return Path(file_path).stem


def _test_file_path(file_path: str) -> Path:
    """Return the target test file path for a given source file."""
    stem = _module_stem(file_path)
    return _TESTS_UNIT_DIR / f"test_{stem}.py"


def _generate_stub(func: _FunctionInfo, _module_import: str) -> str:
    """Generate a pytest stub function string for a given _FunctionInfo."""
    args_str = ", ".join(func.args)
    return (
        f"\ndef test_{func.name}() -> None:\n"
        f"    # TODO: implement test for {func.name}({args_str}) -> {func.return_annotation}\n"
        f'    assert False, "stub — implement this test"\n'
    )


def _write_stubs(test_file: Path, stubs: list[str], module_import: str) -> None:
    """Append stubs to test_file, skipping any whose function name already exists."""
    existing = test_file.read_text(encoding="utf-8") if test_file.exists() else ""
    new_stubs: list[str] = []
    for stub in stubs:
        match = re.search(r"def (test_\w+)", stub)
        if match and re.search(rf"def {re.escape(match.group(1))}\b", existing):
            continue
        new_stubs.append(stub)
    if not new_stubs:
        return
    if not existing:
        header = f"{module_import}\n" if module_import else ""
        test_file.write_text(header + "".join(new_stubs), encoding="utf-8")
    else:
        with test_file.open("a", encoding="utf-8") as f:
            f.write("\n" + "".join(new_stubs))


def _human_review_feedback(
    file_path: str,
    reason: str,
    missing_lines: list[int],
) -> None:
    """Print a [COVERAGE GAP - HUMAN REVIEW REQUIRED] block to stdout."""
    print(
        f"\n[COVERAGE GAP - HUMAN REVIEW REQUIRED]\n"
        f"  file: {file_path}\n"
        f"  reason: {reason}\n"
        f"  missing_lines: {missing_lines}\n"
    )


def _process_module(file_path: str, missing_lines: list[int]) -> None:
    """Process one gap module: extract functions, generate stubs or emit feedback."""
    source_path = Path(file_path)
    stem = _module_stem(file_path)
    functions = _extract_functions(source_path, missing_lines)
    if not functions:
        _human_review_feedback(
            file_path, "無法解析 source (SyntaxError 或檔案不存在)", missing_lines
        )
        return

    test_file = _test_file_path(file_path)
    module_import = f"# Source: {file_path}"
    stubs: list[str] = []

    for func in functions:
        docs_explanation = _find_docs_explanation(stem)
        combined_text = f"{func.docstring} {docs_explanation}"
        if _has_stop_condition(combined_text):
            _human_review_feedback(
                file_path,
                f"stop condition detected in {func.name!r}: {func.docstring!r}",
                func.missing_lines,
            )
        elif not func.docstring and not docs_explanation:
            _human_review_feedback(
                file_path,
                f"no docstring and no docs explanation for {func.name!r}",
                func.missing_lines,
            )
        else:
            stubs.append(_generate_stub(func, module_import))

    if stubs:
        _write_stubs(test_file, stubs, module_import)


def main() -> int:
    """Coverage Agent entry point.

    Returns:
        0 if coverage threshold is met after processing.
        1 if coverage threshold is not met after stub generation.
    """
    coverage_data = _load_coverage_json()
    gaps = _gap_modules(coverage_data)
    for file_path, missing_lines in gaps:
        _process_module(file_path, missing_lines)
    return _run_pytest()


if __name__ == "__main__":
    sys.exit(main())
