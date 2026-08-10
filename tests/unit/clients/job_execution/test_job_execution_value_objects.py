from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from mlops_async.clients.job_execution.value_objects import (
    Job,
    JobExecutionResponseError,
    JobState,
    parse_job,
    parse_job_state,
)


def test_job_state_has_the_six_locked_wire_values() -> None:
    assert {state.value for state in JobState} == {
        "pending",
        "running",
        "canceled",
        "completed",
        "failed",
        "timedOut",
    }


def test_parse_job_maps_the_supported_wire_fields_without_retaining_payload_containers() -> None:
    payload = {
        "id": "job-1",
        "state": "running",
        "stateDetails": "waiting for a worker",
        "results": {"outputTable": "SCORED"},
        "error": {"code": "none", "nested": {"safe": True}},
        "jobRequest": {"id": "request-1"},
        "heartbeatInterval": 30,
        "heartbeatTimeStamp": "2026-08-10T01:02:03Z",
        "creationTimeStamp": "2026-08-10T01:00:00Z",
        "modifiedTimeStamp": "2026-08-10T01:02:00Z",
        "endTimeStamp": "2026-08-10T01:03:00Z",
        "elapsedTime": 120.5,
        "logLocation": "/logs/job-1",
        "expirationTimeStamp": "2026-08-11T01:00:00Z",
        "createdBy": "creator",
        "modifiedBy": "modifier",
        "submittedByApplication": "mlops-async",
        "links": [{"rel": "self", "uri": "/jobExecution/jobs/job-1"}],
        "version": 4,
        "ignoredByTheClient": "not retained",
    }

    job = parse_job(payload)
    payload["error"]["nested"]["safe"] = False
    payload["jobRequest"]["id"] = "changed"
    payload["links"][0]["rel"] = "changed"

    assert type(job) is Job
    assert is_dataclass(job)
    assert not hasattr(job, "__dict__")
    assert {field.name for field in fields(job)} == {
        "id",
        "state",
        "state_details",
        "results",
        "error",
        "job_request",
        "heartbeat_interval",
        "heartbeat_timestamp",
        "creation_timestamp",
        "modified_timestamp",
        "end_timestamp",
        "elapsed_time",
        "log_location",
        "expiration_timestamp",
        "created_by",
        "modified_by",
        "submitted_by_application",
        "links",
        "version",
    }
    assert job.id == "job-1"
    assert job.state is JobState.RUNNING
    assert job.state_details == "waiting for a worker"
    assert job.results == {"outputTable": "SCORED"}
    assert job.error == {"code": "none", "nested": {"safe": True}}
    assert job.job_request == {"id": "request-1"}
    assert job.links == ({"rel": "self", "uri": "/jobExecution/jobs/job-1"},)
    assert job.heartbeat_interval == 30
    assert job.elapsed_time == 120.5
    assert job.version == 4
    assert not hasattr(job, "ignored_by_the_client")

    with pytest.raises(FrozenInstanceError):
        job.id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "payload",
    (
        [],
        {"state": "unknown"},
        {"state": 1},
        {"stateDetails": 1},
        {"results": {"output": 1}},
        {"error": []},
        {"jobRequest": []},
        {"heartbeatInterval": True},
        {"elapsedTime": True},
        {"links": {}},
        {"links": ["not-an-object"]},
        {"version": 1.0},
    ),
)
def test_parse_job_rejects_semantic_mismatches(payload: object) -> None:
    with pytest.raises(JobExecutionResponseError):
        parse_job(payload)  # type: ignore[arg-type]


def test_parse_job_allows_absent_optional_fields_and_preserves_null_as_none() -> None:
    job = parse_job(
        {
            "id": None,
            "state": None,
            "stateDetails": None,
            "results": None,
            "error": None,
            "jobRequest": None,
            "heartbeatInterval": None,
            "heartbeatTimeStamp": None,
            "creationTimeStamp": None,
            "modifiedTimeStamp": None,
            "endTimeStamp": None,
            "elapsedTime": None,
            "logLocation": None,
            "expirationTimeStamp": None,
            "createdBy": None,
            "modifiedBy": None,
            "submittedByApplication": None,
            "links": None,
            "version": None,
        }
    )
    assert all(getattr(job, field.name) is None for field in fields(job))


@pytest.mark.parametrize(
    "content", (b"pending", b"running", b"canceled", b"completed", b"failed", b"timedOut")
)
def test_parse_job_state_accepts_only_exact_utf8_plain_text(content: bytes) -> None:
    assert parse_job_state(content).value == content.decode("utf-8")


@pytest.mark.parametrize(
    "content",
    (b" running", b"running\n", b'"running"', b'{"state":"running"}', b"unknown", b"\xff"),
)
def test_parse_job_state_rejects_non_exact_or_non_utf8_text(content: bytes) -> None:
    with pytest.raises(JobExecutionResponseError):
        parse_job_state(content)
