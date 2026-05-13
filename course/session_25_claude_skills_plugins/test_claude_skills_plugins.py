from __future__ import annotations

from course.framework.claude import (
    ExtensionType,
    implementation_checklist,
    list_extensions,
    recommend_extension,
    risk_note,
)


def test_list_extensions_can_filter_by_type() -> None:
    skills = list_extensions(ExtensionType.SKILL)

    assert len(skills) == 1
    assert skills[0].extension_type == ExtensionType.SKILL


def test_recommend_extension_matches_browser_inspection() -> None:
    extension = recommend_extension("Need browser inspection for a broken selector")

    assert extension.name == "Playwright MCP"
    assert extension.extension_type == ExtensionType.MCP


def test_recommend_extension_matches_pull_request_workflow() -> None:
    extension = recommend_extension("Review a pull request and check CI")

    assert extension.name == "GitHub Plugin"
    assert extension.extension_type == ExtensionType.PLUGIN


def test_recommend_extension_has_safe_default() -> None:
    extension = recommend_extension("Improve our testing process")

    assert extension.name == "QA Review Skill"


def test_risk_note_mentions_external_access_when_needed() -> None:
    extension = recommend_extension("browser inspection")

    assert "access" in risk_note(extension)


def test_implementation_checklist_adds_permission_item_for_external_extension() -> None:
    extension = recommend_extension("ci triage")

    assert implementation_checklist(extension)[-1].startswith("Document permissions")
