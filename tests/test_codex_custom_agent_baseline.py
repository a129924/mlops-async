from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_text(relative_path: str) -> str:
    return (_repo_root() / relative_path).read_text(encoding="utf-8")


def _parse_simple_toml(relative_path: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in _read_text(relative_path).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key, value = line.split(" = ", 1)
        data[key] = value.strip('"')
    return data


def test_custom_agent_tomls_use_minimal_schema_and_match_filenames() -> None:
    agent_dir = _repo_root() / ".codex" / "agents"
    expected_files = {
        "planner.toml": "planner",
        "implementer.toml": "implementer",
        "reviewer.toml": "reviewer",
    }

    assert {path.name for path in agent_dir.glob("*.toml")} == set(expected_files)

    for filename, expected_name in expected_files.items():
        data = _parse_simple_toml(f".codex/agents/{filename}")
        assert list(data) == ["name", "description", "developer_instructions"]
        assert data["name"] == expected_name
        assert filename == f"{expected_name}.toml"
        assert data["description"].strip()
        assert data["developer_instructions"].strip()


def test_workflow_skill_metadata_is_explicit_only() -> None:
    expected = "policy:\n  allow_implicit_invocation: false\n"
    metadata_paths = [
        ".agents/skills/workflow-artifact-contract/agents/openai.yaml",
        ".agents/skills/python-implementation-workflow/agents/openai.yaml",
    ]

    for relative_path in metadata_paths:
        assert _read_text(relative_path) == expected


def test_workflow_skills_live_on_official_paths_and_keep_boundaries_clear() -> None:
    workflow_skill = _read_text(".agents/skills/python-implementation-workflow/SKILL.md")
    workflow_reference = _read_text(".agents/skills/python-implementation-workflow/reference.md")
    shared_contract = _read_text(".agents/skills/workflow-artifact-contract/SKILL.md")
    disallowed_paths_warning = (
        "Do not create workflow artifacts under `./codex/**`, `./agents/**`, "
        "`./.agents/openai.yaml`, or `./.codex/openai.yaml`."
    )

    assert "wrapper recipe" in workflow_skill
    assert "not a standalone orchestrator" in workflow_skill
    assert "frozen provenance only" in workflow_reference
    assert disallowed_paths_warning in shared_contract


def test_preflight_probe_artifacts_are_removed() -> None:
    assert not (_repo_root() / ".codex" / "agents" / "preflight-probe.toml").exists()
    assert not (_repo_root() / ".agents" / "skills" / "preflight-probe").exists()
