"""
Session 27 - Claude Connectors

Runnable examples for using Claude connectors in QA workflows while keeping
permissions, evidence, and write actions explicit.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.claude import (  # noqa: E402
    ConnectorCategory,
    list_connectors,
    permission_summary,
    qa_connector_checklist,
    recommend_connector,
)


def demo() -> None:
    print("Source-control connectors:")
    for connector in list_connectors(ConnectorCategory.SOURCE_CONTROL):
        print(f"  - {connector.name}: {', '.join(connector.qa_uses)}")

    selected = recommend_connector("pull request review and ci triage")
    print("\nRecommended:", selected.name)
    print("Permissions:", permission_summary(selected))
    print("Checklist:")
    for item in qa_connector_checklist(selected):
        print(f"  - {item}")


if __name__ == "__main__":
    demo()


__all__ = [
    "ConnectorCategory",
    "list_connectors",
    "permission_summary",
    "qa_connector_checklist",
    "recommend_connector",
]
