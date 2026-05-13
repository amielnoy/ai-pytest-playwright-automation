from __future__ import annotations

from course.framework.claude import (
    ConnectorCategory,
    list_connectors,
    permission_summary,
    qa_connector_checklist,
    recommend_connector,
)


def test_list_connectors_filters_by_category() -> None:
    source_control = list_connectors(ConnectorCategory.SOURCE_CONTROL)

    assert [connector.name for connector in source_control] == ["GitHub"]


def test_recommend_connector_for_pr_and_ci_work() -> None:
    connector = recommend_connector("Need pull request review and ci triage")

    assert connector.name == "GitHub"


def test_recommend_connector_for_requirement_documents() -> None:
    connector = recommend_connector("read test plans and summarize requirements")

    assert connector.name == "Google Drive"


def test_permission_summary_marks_write_actions_as_confirmed() -> None:
    connector = recommend_connector("share test status")

    assert connector.name == "Slack"
    assert "writes require confirmation" in permission_summary(connector)


def test_connector_checklist_requires_confirmation_before_write() -> None:
    connector = recommend_connector("draft QA status")
    checklist = qa_connector_checklist(connector)

    assert any("Ask for confirmation" in item for item in checklist)
    assert any("evidence" in item for item in checklist)
