from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from mlops_async.clients.models.value_objects import ModelDetail, ModelSummary, ModelsPage


def test_model_response_value_objects_are_frozen_slotted_semantic_types() -> None:
    summary = ModelSummary(
        id="model-1",
        name="Credit risk",
        project_id="project-1",
        model_type="analytic",
        score_code_type="python",
        role="champion",
        version=2,
    )
    page = ModelsPage(count=3, start=0, limit=20, items=(summary,))
    detail = ModelDetail(
        id="model-1",
        name="Credit risk",
        project_id="project-1",
        model_type="analytic",
        score_code_type="python",
        role="champion",
        version=2,
    )

    assert is_dataclass(summary)
    assert is_dataclass(page)
    assert is_dataclass(detail)
    assert summary == ModelSummary(
        id="model-1",
        name="Credit risk",
        project_id="project-1",
        model_type="analytic",
        score_code_type="python",
        role="champion",
        version=2,
    )
    assert page.items == (summary,)
    assert detail.name == "Credit risk"
    assert not hasattr(summary, "__dict__")
    assert not hasattr(page, "__dict__")
    assert not hasattr(detail, "__dict__")
    assert {field.name for field in fields(summary)} == {
        "id",
        "name",
        "project_id",
        "model_type",
        "score_code_type",
        "role",
        "version",
    }
    assert {field.name for field in fields(page)} == {"count", "start", "limit", "items"}
    assert {field.name for field in fields(detail)} == {
        "id",
        "name",
        "model_type",
        "score_code_type",
        "project_id",
        "role",
        "version",
    }
    for value in (summary, page, detail):
        assert not hasattr(value, "data_uris")
        assert not hasattr(value, "dataUris")
        assert not hasattr(value, "files")
        assert not hasattr(value, "variables")
        assert not hasattr(value, "links")

    with pytest.raises(FrozenInstanceError):
        summary.name = "changed"  # type: ignore[misc]


def test_models_page_items_are_already_an_immutable_tuple() -> None:
    summary = ModelSummary(
        id="model-1",
        name="Credit risk",
        project_id=None,
        model_type=None,
        score_code_type=None,
        role=None,
        version=None,
    )
    page = ModelsPage(count=1, start=0, limit=20, items=(summary,))

    assert type(page.items) is tuple
    with pytest.raises(AttributeError):
        page.items.append(summary)  # type: ignore[attr-defined]
