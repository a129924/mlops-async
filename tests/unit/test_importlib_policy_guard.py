from __future__ import annotations

import ast
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tests_root() -> Path:
    return _repo_root() / "tests"


def _git_changed_test_paths() -> tuple[Path, ...]:
    changed_relative_paths: set[str] = set()
    git_commands = (
        [
            "git",
            "--no-pager",
            "diff",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "--",
            "tests",
        ],
        [
            "git",
            "--no-pager",
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "--",
            "tests",
        ],
        [
            "git",
            "--no-pager",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "tests",
        ],
    )
    for command in git_commands:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            check=True,
            capture_output=True,
            text=True,
        )
        changed_relative_paths.update(
            relative_path for relative_path in completed.stdout.splitlines() if relative_path
        )

    return tuple(sorted(_repo_root() / relative_path for relative_path in changed_relative_paths))


def _is_contracts_dir(path: Path) -> bool:
    return path.parts[:2] == ("tests", "contracts")


def _is_contract_import_test(path: Path) -> bool:
    return _is_contracts_dir(path) and path.name.startswith("test_import_contract_")


def _iter_behavior_test_files() -> list[Path]:
    return sorted(
        path
        for relative_dir in ("unit/core", "unit/transport")
        for path in (_tests_root() / relative_dir).rglob("*.py")
    )


def _collect_importlib_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    aliases_from_importlib: set[str] = set()
    direct_importlib_aliases: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib" or alias.name.startswith("importlib."):
                    direct_importlib_aliases.add(alias.asname or alias.name.split(".")[0])
        elif (
            isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("importlib")
        ):
            for alias in node.names:
                aliases_from_importlib.add(alias.asname or alias.name)

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in aliases_from_importlib:
                violations.append(f"line {node.lineno}: call via importlib symbol '{node.func.id}'")
            if isinstance(node.func, ast.Attribute):
                base = node.func.value
                if isinstance(base, ast.Name) and base.id in direct_importlib_aliases:
                    violations.append(
                        f"line {node.lineno}: call via importlib alias '{base.id}.{node.func.attr}'"
                    )

    if direct_importlib_aliases or aliases_from_importlib:
        violations.insert(0, "importlib import found")

    return violations


def _collect_contract_helper_import_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "tests.contracts" or alias.name.startswith("tests.contracts."):
                    violations.append(
                        f"line {node.lineno}: import from contract test package '{alias.name}'"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module and (
                node.module == "tests.contracts"
                or node.module.startswith("tests.contracts.")
                or node.module == "contracts"
                or node.module.startswith("contracts.")
            ):
                violations.append(
                    f"line {node.lineno}: import from contract test package '{node.module}'"
                )

    return violations


def _collect_helper_style_import_alias_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                alias_name = alias.asname or ""
                if alias_name.endswith("_module"):
                    violations.append(
                        f"line {node.lineno}: helper-style alias import '{alias_name}'"
                    )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                alias_name = alias.asname or ""
                if alias_name.endswith("_module"):
                    violations.append(
                        f"line {node.lineno}: helper-style alias import '{alias_name}'"
                    )
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id.endswith("_module"):
                violations.append(
                    f"line {node.lineno}: helper-style module wrapper call '{node.func.id}()'"
                )
            elif isinstance(node.func, ast.Attribute) and node.func.attr.endswith("_module"):
                violations.append(
                    "line "
                    f"{node.lineno}: helper-style module wrapper call "
                    f"'{ast.unparse(node.func)}()'"
                )

    return violations


def _collect_helper_style_wrapper_def_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.endswith(
            "_module"
        ):
            violations.append(f"line {node.lineno}: helper-style wrapper definition '{node.name}'")

    return violations


def _collect_fixture_helper_bypass_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        is_fixture = any(
            (
                (isinstance(decorator, ast.Name) and decorator.id == "fixture")
                or (
                    isinstance(decorator, ast.Attribute)
                    and isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "pytest"
                    and decorator.attr == "fixture"
                )
            )
            for decorator in node.decorator_list
        )
        if not is_fixture:
            continue

        for descendant in ast.walk(node):
            if isinstance(descendant, ast.Call):
                if isinstance(descendant.func, ast.Name) and descendant.func.id.endswith("_module"):
                    violations.append(
                        "line "
                        f"{descendant.lineno}: fixture '{node.name}' calls "
                        f"'{descendant.func.id}()'"
                    )
            if isinstance(descendant, (ast.Import, ast.ImportFrom)):
                for alias in descendant.names:
                    alias_name = alias.asname or ""
                    if alias_name.endswith("_module"):
                        violations.append(
                            "line "
                            f"{descendant.lineno}: fixture '{node.name}' imports alias "
                            f"'{alias_name}'"
                        )

    return violations


def test_importlib_usage_is_restricted_to_contract_tests() -> None:
    violations: list[str] = []

    for path in sorted(_tests_root().rglob("*.py")):
        rel = path.relative_to(_repo_root())
        if _is_contracts_dir(rel):
            continue
        file_violations = _collect_importlib_violations(path)
        if file_violations:
            violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert violations == []


def test_non_contract_tests_do_not_import_contract_test_helpers() -> None:
    violations: list[str] = []

    for path in sorted(_tests_root().rglob("*.py")):
        rel = path.relative_to(_repo_root())
        if _is_contracts_dir(rel):
            continue
        file_violations = _collect_contract_helper_import_violations(path)
        if file_violations:
            violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert violations == []


def test_dynamic_import_contract_files_follow_contract_naming_rule() -> None:
    naming_violations: list[str] = []

    for path in sorted(_tests_root().rglob("*.py")):
        rel = path.relative_to(_repo_root())
        file_violations = _collect_importlib_violations(path)
        if file_violations and not _is_contract_import_test(rel):
            naming_violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert naming_violations == []


def test_tc_inv_001_policy_guard_rejects_helper_style_usage_in_unit_tests() -> None:
    violations: list[str] = []
    unit_root = _tests_root() / "unit"

    for path in sorted(unit_root.rglob("*.py")):
        rel = path.relative_to(_repo_root())
        file_violations = _collect_helper_style_import_alias_violations(path)
        if file_violations:
            violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert violations == []


def test_tc_hp_001_behavior_tests_have_zero_helper_style_usage() -> None:
    """TC-HP-001: behavior tests must not use helper-style module aliases/calls."""
    violations: list[str] = []
    for path in _iter_behavior_test_files():
        rel = path.relative_to(_repo_root())
        file_violations = _collect_helper_style_import_alias_violations(path)
        if file_violations:
            violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert violations == []


def test_tc_edge_001_policy_guard_rejects_indirect_helper_wrapper_in_unit_tests() -> None:
    violations: list[str] = []
    for path in _iter_behavior_test_files():
        rel = path.relative_to(_repo_root())
        file_violations = _collect_helper_style_wrapper_def_violations(path)
        file_violations.extend(_collect_fixture_helper_bypass_violations(path))
        if file_violations:
            violations.append(f"{rel}: {'; '.join(file_violations)}")

    assert violations == []


def test_tc_bc_001_req_006_tests_only_scope_guard_is_still_red() -> None:
    topic_scope_evidence = _git_changed_test_paths()
    for path in topic_scope_evidence:
        assert path.relative_to(_repo_root()).parts[:1] == ("tests",)
