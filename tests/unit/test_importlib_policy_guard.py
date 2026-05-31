from __future__ import annotations

import ast
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tests_root() -> Path:
    return _repo_root() / "tests"


def _is_contracts_dir(path: Path) -> bool:
    return path.parts[:2] == ("tests", "contracts")


def _is_contract_import_test(path: Path) -> bool:
    return _is_contracts_dir(path) and path.name.startswith("test_import_contract_")


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
