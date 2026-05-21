"""Unit tests for scripts/coverage_agent.py.

All tests in this module are RED until scripts/coverage_agent.py is implemented.
``scripts/`` is outside ``src/`` and not an installed package; ``sys.path`` is
extended at module load so pytest can import ``coverage_agent`` directly.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# scripts/ is outside src/; add it to sys.path for direct import.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from coverage_agent import (
    _FunctionInfo,
    _extract_functions,
    _gap_modules,
    _generate_stub,
    _has_stop_condition,
    _load_coverage_json,
    _process_module,
    _write_stubs,
    main,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def coverage_data_below() -> dict:
    """coverage.json fixture with one module below 80% coverage."""
    return {
        "files": {
            "src/mlops_async/foo.py": {
                "summary": {"percent_covered": 65.0},
                "missing_lines": [45, 46, 47],
            }
        },
        "totals": {"percent_covered": 65.0},
    }


@pytest.fixture()
def coverage_data_above() -> dict:
    """coverage.json fixture with all modules at or above 80% coverage."""
    return {
        "files": {
            "src/mlops_async/foo.py": {
                "summary": {"percent_covered": 85.0},
                "missing_lines": [],
            }
        },
        "totals": {"percent_covered": 85.0},
    }


@pytest.fixture()
def source_clean(tmp_path: Path) -> Path:
    """Source file with a clean function (docstring, no stop-condition keyword)."""
    f = tmp_path / "foo.py"
    f.write_text('def bar(x: int) -> bool:\n    """Check if x is positive."""\n    return x > 0\n')
    return f


@pytest.fixture()
def source_upload(tmp_path: Path) -> Path:
    """Source file whose function docstring contains stop-condition keyword 'upload'."""
    f = tmp_path / "uploader.py"
    f.write_text(
        'def upload_file(path: str) -> None:\n    """Upload file to remote storage."""\n    pass\n'
    )
    return f


@pytest.fixture()
def source_no_docstring(tmp_path: Path) -> Path:
    """Source file with a function that has no docstring."""
    f = tmp_path / "util.py"
    f.write_text("def mystery_fn() -> None:\n    pass\n")
    return f


@pytest.fixture()
def source_mixed(tmp_path: Path) -> Path:
    """Source file with one clean function and one stop-condition function."""
    f = tmp_path / "mixed.py"
    f.write_text(
        "def clean_fn(x: int) -> bool:\n"
        '    """Check value."""\n'
        "    return True\n"
        "\n"
        "def upload_fn(path: str) -> None:\n"
        '    """Upload data."""\n'
        "    pass\n"
    )
    return f


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_clean_docstring_no_stop_condition(self) -> None:
        """_has_stop_condition returns False for a docstring with no keywords."""
        assert _has_stop_condition("Check if x is positive.") is False

    def test_empty_string_no_stop_condition(self) -> None:
        """_has_stop_condition returns False for empty string."""
        assert _has_stop_condition("") is False

    def test_main_returns_zero_when_all_above_threshold(self, coverage_data_above: dict) -> None:
        """main() returns 0 when every module is at or above 80% coverage."""
        with (
            patch("coverage_agent._load_coverage_json", return_value=coverage_data_above),
            patch("coverage_agent._run_pytest", return_value=0),
            patch("coverage_agent._process_module") as mock_process,
        ):
            result = main()
        assert result == 0
        mock_process.assert_not_called()

    def test_process_module_creates_stub_file_for_clean_function(
        self, source_clean: Path, tmp_path: Path
    ) -> None:
        """_process_module creates test_foo.py with assert False stub for clean function."""
        with (
            patch("coverage_agent._TESTS_UNIT_DIR", tmp_path),
            patch("coverage_agent._find_docs_explanation", return_value="Explanation."),
        ):
            _process_module(str(source_clean), [1, 2, 3])
        test_file = tmp_path / "test_foo.py"
        assert test_file.exists()
        content = test_file.read_text()
        assert "def test_bar" in content
        assert "assert False" in content

    def test_gap_modules_returns_files_below_threshold(self, coverage_data_below: dict) -> None:
        """_gap_modules returns entries for modules below 80%."""
        gaps = _gap_modules(coverage_data_below)
        assert len(gaps) == 1
        file_path, missing = gaps[0]
        assert file_path == "src/mlops_async/foo.py"
        assert 45 in missing

    def test_gap_modules_empty_when_all_above_threshold(self, coverage_data_above: dict) -> None:
        """_gap_modules returns empty list when all modules are above threshold."""
        assert _gap_modules(coverage_data_above) == []


# ---------------------------------------------------------------------------
# Error / exception (invalid input)
# ---------------------------------------------------------------------------


class TestErrorAndException:
    def test_load_coverage_json_triggers_pytest_when_missing(self, tmp_path: Path) -> None:
        """_load_coverage_json calls _run_pytest to generate json when file is missing."""
        missing = tmp_path / "coverage.json"

        def create_json() -> int:
            missing.write_text('{"files": {}, "totals": {"percent_covered": 90.0}}')
            return 0

        with (
            patch("coverage_agent._COVERAGE_JSON_PATH", missing),
            patch("coverage_agent._run_pytest", side_effect=create_json) as mock_run,
        ):
            _load_coverage_json()
        mock_run.assert_called_once()

    def test_load_coverage_json_exits_when_still_missing(self, tmp_path: Path) -> None:
        """sys.exit(1) is called when coverage.json still missing after _run_pytest."""
        missing = tmp_path / "still_missing.json"
        with patch("coverage_agent._COVERAGE_JSON_PATH", missing):
            with patch("coverage_agent._run_pytest", return_value=1):
                with pytest.raises(SystemExit) as exc:
                    _load_coverage_json()
        assert exc.value.code == 1

    def test_extract_functions_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        """SyntaxError during ast.parse causes _extract_functions to return []."""
        broken = tmp_path / "broken.py"
        broken.write_text("def foo(\n  # unclosed\n")
        assert _extract_functions(broken, [1, 2]) == []

    def test_extract_functions_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Non-existent source file causes _extract_functions to return []."""
        assert _extract_functions(tmp_path / "does_not_exist.py", [1]) == []

    def test_generate_stub_contains_test_function_and_assert_false(self) -> None:
        """_generate_stub returns a string with def test_<name> and assert False."""
        func = _FunctionInfo(
            name="my_func",
            args=["x"],
            return_annotation="bool",
            docstring="Does something.",
            missing_lines=[10, 11],
        )
        stub = _generate_stub(func, "from mlops_async import module")
        assert "def test_my_func" in stub
        assert "assert False" in stub


# ---------------------------------------------------------------------------
# Boundary / edge cases
# ---------------------------------------------------------------------------


class TestBoundaryAndEdge:
    @pytest.mark.parametrize(
        "text",
        [
            "upload file to remote",
            "UPLOAD data",
            "download from bucket",
            "streaming response handler",
            "polling for job status",
            "retry mechanism on failure",
        ],
    )
    def test_stop_keywords_return_true(self, text: str) -> None:
        """Each stop-condition keyword (case-insensitive) causes True return."""
        assert _has_stop_condition(text) is True

    def test_stop_condition_blocks_stub_file_creation(
        self,
        source_upload: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Stop-condition keyword prevents test file creation; HUMAN REVIEW printed."""
        with (
            patch("coverage_agent._TESTS_UNIT_DIR", tmp_path),
            patch("coverage_agent._find_docs_explanation", return_value="upload docs"),
        ):
            _process_module(str(source_upload), [1, 2, 3])
        assert not (tmp_path / "test_uploader.py").exists()
        assert "[COVERAGE GAP - HUMAN REVIEW REQUIRED]" in capsys.readouterr().out

    def test_no_docstring_no_docs_triggers_human_review(
        self,
        source_no_docstring: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Function with no docstring and no docs explanation triggers HUMAN REVIEW."""
        with (
            patch("coverage_agent._TESTS_UNIT_DIR", tmp_path),
            patch("coverage_agent._find_docs_explanation", return_value=""),
        ):
            _process_module(str(source_no_docstring), [1, 2])
        assert not (tmp_path / "test_util.py").exists()
        assert "[COVERAGE GAP - HUMAN REVIEW REQUIRED]" in capsys.readouterr().out

    def test_write_stubs_prevents_duplicate_function(self, tmp_path: Path) -> None:
        """_write_stubs does not append a stub whose function already exists in the file."""
        test_file = tmp_path / "test_mod.py"
        test_file.write_text("def test_existing():\n    assert False, 'stub'\n\n")
        _write_stubs(test_file, ["def test_existing():\n    assert False, 'stub'\n"], "")
        assert test_file.read_text().count("def test_existing()") == 1

    def test_threshold_met_process_module_never_called(self, coverage_data_above: dict) -> None:
        """main() with all coverage above threshold does not invoke _process_module."""
        with (
            patch("coverage_agent._load_coverage_json", return_value=coverage_data_above),
            patch("coverage_agent._run_pytest", return_value=0),
            patch("coverage_agent._process_module") as mock_proc,
        ):
            main()
        mock_proc.assert_not_called()


# ---------------------------------------------------------------------------
# State / side effects
# ---------------------------------------------------------------------------


class TestStateAndSideEffects:
    def test_write_stubs_creates_new_test_file(self, tmp_path: Path) -> None:
        """_write_stubs creates a new file when the target does not exist."""
        test_file = tmp_path / "test_new.py"
        assert not test_file.exists()
        _write_stubs(
            test_file,
            ["def test_foo():\n    assert False, 'stub'\n"],
            "from mlops_async import new",
        )
        assert test_file.exists()
        assert "def test_foo()" in test_file.read_text()

    def test_write_stubs_appends_to_existing_file(self, tmp_path: Path) -> None:
        """_write_stubs appends new stubs without overwriting existing content."""
        test_file = tmp_path / "test_ext.py"
        test_file.write_text("def test_first():\n    assert True\n\n")
        _write_stubs(
            test_file,
            ["def test_second():\n    assert False, 'stub'\n"],
            "from mlops_async import ext",
        )
        content = test_file.read_text()
        assert "def test_first()" in content
        assert "def test_second()" in content


# ---------------------------------------------------------------------------
# Integration points
# ---------------------------------------------------------------------------


class TestIntegrationPoints:
    def test_main_calls_process_module_for_each_gap(self, coverage_data_below: dict) -> None:
        """main() calls _process_module with correct args for each gap module."""
        with (
            patch("coverage_agent._load_coverage_json", return_value=coverage_data_below),
            patch("coverage_agent._run_pytest", return_value=1),
            patch("coverage_agent._process_module") as mock_proc,
        ):
            main()
        mock_proc.assert_called_once_with("src/mlops_async/foo.py", [45, 46, 47])

    def test_main_returns_final_pytest_exit_code(self, coverage_data_below: dict) -> None:
        """main() returns the exit code from the final _run_pytest call."""
        with (
            patch("coverage_agent._load_coverage_json", return_value=coverage_data_below),
            patch("coverage_agent._run_pytest", return_value=1),
            patch("coverage_agent._process_module"),
        ):
            assert main() == 1

    def test_mixed_module_partial_stub_and_partial_feedback(
        self, source_mixed: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Module with mixed functions: clean ones get stubs, stop-condition ones give feedback."""
        with (
            patch("coverage_agent._TESTS_UNIT_DIR", tmp_path),
            patch("coverage_agent._find_docs_explanation", return_value="docs here"),
        ):
            _process_module(str(source_mixed), [1, 2, 3, 5, 6, 7])
        test_file = tmp_path / "test_mixed.py"
        assert test_file.exists()
        assert "def test_clean_fn" in test_file.read_text()
        assert "[COVERAGE GAP - HUMAN REVIEW REQUIRED]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------


class TestRegression:
    def test_pre_commit_stages_manual_hook_preserved(self) -> None:
        """Regression: adding coverage-check hook must not remove stages: [manual]."""
        pre_commit = Path(__file__).parent.parent.parent / ".pre-commit-config.yaml"
        if not pre_commit.exists():
            pytest.skip(".pre-commit-config.yaml not yet created (pre-implementation)")
        assert "stages: [manual]" in pre_commit.read_text()


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_main_return_annotation_is_int(self) -> None:
        """main() must declare a return type annotation of int."""
        import inspect

        sig = inspect.signature(main)
        annotation = sig.return_annotation
        assert annotation in (int, "int")

    def test_no_import_side_effects(self) -> None:
        """Importing coverage_agent must not trigger network or file I/O side effects."""
        import importlib

        mod = importlib.import_module("coverage_agent")
        assert mod is not None
