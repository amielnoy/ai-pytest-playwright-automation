"""
Session 27 - Claude connectors reference layer.

Connectors are permissioned integrations to real work systems. In QA
automation, they are useful for reading project context, preparing test work,
and reporting outcomes, but they need explicit boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ConnectorCategory(StrEnum):
    SOURCE_CONTROL = "source_control"
    COMMUNICATION = "communication"
    KNOWLEDGE_BASE = "knowledge_base"
    CALENDAR = "calendar"
    EMAIL = "email"


@dataclass(frozen=True)
class ClaudeConnector:
    name: str
    category: ConnectorCategory
    qa_uses: tuple[str, ...]
    read_actions: tuple[str, ...]
    write_actions: tuple[str, ...] = ()


CONNECTORS: tuple[ClaudeConnector, ...] = (
    ClaudeConnector(
        name="GitHub",
        category=ConnectorCategory.SOURCE_CONTROL,
        qa_uses=("pull request review", "ci triage", "issue analysis"),
        read_actions=("read pull requests", "read issues", "read workflow logs"),
        write_actions=("comment on pull requests", "open issues", "create branches"),
    ),
    ClaudeConnector(
        name="Google Drive",
        category=ConnectorCategory.KNOWLEDGE_BASE,
        qa_uses=("read test plans", "summarize requirements", "prepare QA notes"),
        read_actions=("read docs", "read sheets", "read slides"),
        write_actions=("create docs", "update sheets"),
    ),
    ClaudeConnector(
        name="Slack",
        category=ConnectorCategory.COMMUNICATION,
        qa_uses=("summarize bug threads", "prepare release notes", "share test status"),
        read_actions=("read channels", "read threads"),
        write_actions=("send messages",),
    ),
    ClaudeConnector(
        name="Google Calendar",
        category=ConnectorCategory.CALENDAR,
        qa_uses=("plan test windows", "prepare meeting briefs", "check availability"),
        read_actions=("read events", "read availability"),
        write_actions=("create events", "update events"),
    ),
    ClaudeConnector(
        name="Gmail",
        category=ConnectorCategory.EMAIL,
        qa_uses=("summarize stakeholder requests", "draft QA status", "find approvals"),
        read_actions=("read email", "search email"),
        write_actions=("draft email", "send email"),
    ),
)


def list_connectors(category: ConnectorCategory | None = None) -> list[ClaudeConnector]:
    if category is None:
        return list(CONNECTORS)
    return [connector for connector in CONNECTORS if connector.category == category]


def recommend_connector(task: str) -> ClaudeConnector:
    normalized = task.lower()
    scored_matches = [
        (
            sum(1 for use in connector.qa_uses if use in normalized)
            + sum(1 for action in connector.read_actions if action in normalized),
            connector,
        )
        for connector in CONNECTORS
    ]
    score, connector = max(scored_matches, key=lambda item: item[0])
    if score > 0:
        return connector
    return CONNECTORS[0]


def permission_summary(connector: ClaudeConnector) -> str:
    read_part = ", ".join(connector.read_actions)
    if not connector.write_actions:
        return f"{connector.name}: read actions only ({read_part})."
    write_part = ", ".join(connector.write_actions)
    return f"{connector.name}: reads {read_part}; writes require confirmation ({write_part})."


def qa_connector_checklist(connector: ClaudeConnector) -> list[str]:
    return [
        f"Confirm {connector.name} is the right connector for the QA task.",
        "Use the narrowest source or thread that contains the needed context.",
        "Summarize findings before making any write action.",
        "Ask for confirmation before sending, commenting, creating, or updating.",
        "Record links or IDs used as evidence in the final QA note.",
    ]
