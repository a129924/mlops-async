"""Readable request-contract tests for fixed-path MVP list_tables."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit.request_contract.contract_case import (
    EndpointContractCase,
    FakeResponse,
    RequestShape,
    SourceObservedFixture,
)
from tests.unit.request_contract.projects_tables_link_request_gate.conftest import (
    TOPIC_PACKAGE_DIR,
    ProjectsTablesLinkContractHarness,
    _is_topic_scoped_pytest_run,
)

FIXTURE_ROOT = "tests/unit/request_contract/projects_tables_link_request_gate/fixtures"
PROJECT_ID = "project-id-abc-123"


def test_list_tables_direct_project_identifier_request_shape(
    projects_tables_link_contract: ProjectsTablesLinkContractHarness,
) -> None:
    case_list_tables_direct_project_identifier = EndpointContractCase(
        name="model_repository_projects_tables_link.list_tables.direct_project_identifier",
        invoke=lambda: projects_tables_link_contract.client.list_tables(PROJECT_ID),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{PROJECT_ID}/tables",
            query={},
            body=None,
            required_headers={},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=SourceObservedFixture(
            request_path=f"{FIXTURE_ROOT}/list_tables.request-flow.json#direct_project_identifier",
            response_path=f"{FIXTURE_ROOT}/list_tables.mock-responses.json#direct_project_identifier",
        ),
    )

    result = projects_tables_link_contract.run(case_list_tables_direct_project_identifier)

    assert getattr(result, "items", None) == []
    assert projects_tables_link_contract.last_request is not None
    assert (
        projects_tables_link_contract.last_request["path"]
        == f"/modelRepository/projects/{PROJECT_ID}/tables"
    )
    assert projects_tables_link_contract.last_request["query"] == {}
    assert projects_tables_link_contract.last_request["body"] is None


@pytest.mark.parametrize(
    "project_id",
    [
        123,
        {"id": PROJECT_ID},
    ],
)
def test_list_tables_blocks_non_string_project_id_variants(
    blocked_topic_scope_error: type[RuntimeError],
    projects_tables_link_contract: ProjectsTablesLinkContractHarness,
    project_id: object,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty project_id string is allowed",
    ):
        projects_tables_link_contract.client.list_tables(project_id)


@pytest.mark.parametrize("project_id", ["", "   "])
def test_list_tables_blocks_blank_project_id_variants(
    blocked_topic_scope_error: type[RuntimeError],
    projects_tables_link_contract: ProjectsTablesLinkContractHarness,
    project_id: str,
) -> None:
    with pytest.raises(
        blocked_topic_scope_error,
        match="Only a non-empty project_id string is allowed",
    ):
        projects_tables_link_contract.client.list_tables(project_id)


def test_list_tables_percent_encodes_reserved_project_id_characters(
    projects_tables_link_contract: ProjectsTablesLinkContractHarness,
) -> None:
    reserved_project_id = "project/id?draft=yes"
    encoded_project_id = "project%2Fid%3Fdraft%3Dyes"

    case_list_tables_reserved_project_identifier = EndpointContractCase(
        name="model_repository_projects_tables_link.list_tables.percent_encoded_project_identifier",
        invoke=lambda: projects_tables_link_contract.client.list_tables(reserved_project_id),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{encoded_project_id}/tables",
            query={},
            body=None,
            required_headers={},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    result = projects_tables_link_contract.run(case_list_tables_reserved_project_identifier)

    assert getattr(result, "items", None) == []
    assert projects_tables_link_contract.last_request is not None
    assert (
        projects_tables_link_contract.last_request["path"]
        == f"/modelRepository/projects/{encoded_project_id}/tables"
    )
    assert projects_tables_link_contract.last_request["query"] == {}


def test_list_tables_interceptor_fails_fast_on_unregistered_request(
    projects_tables_link_contract: ProjectsTablesLinkContractHarness,
) -> None:
    mismatched_case = EndpointContractCase(
        name="model_repository_projects_tables_link.list_tables.unregistered_request",
        invoke=lambda: projects_tables_link_contract.client.list_tables(PROJECT_ID),
        expected=RequestShape(
            method="GET",
            path=f"/modelRepository/projects/{PROJECT_ID}",
            query={},
            body=None,
            required_headers={},
        ),
        response=FakeResponse(
            status_code=200,
            json_body={"items": []},
            headers={"Content-Type": "application/json"},
        ),
        source_observed=None,
    )

    with pytest.raises(AssertionError, match="Unexpected outbound request"):
        projects_tables_link_contract.run(mismatched_case)


def test_topic_scoped_pytest_run_detects_topic_target_after_option_parsing() -> None:
    config = SimpleNamespace(
        args=["tests/unit/request_contract/projects_tables_link_request_gate"],
        rootpath=TOPIC_PACKAGE_DIR.parents[3],
    )

    assert _is_topic_scoped_pytest_run(config) is True


def test_topic_scoped_pytest_run_rejects_full_suite_collection_target() -> None:
    config = SimpleNamespace(args=["tests"], rootpath=TOPIC_PACKAGE_DIR.parents[3])

    assert _is_topic_scoped_pytest_run(config) is False
