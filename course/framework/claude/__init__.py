"""Claude skills and plugins helpers added in Session 25."""

from course.framework.claude.extensions import (
    EXTENSIONS,
    ClaudeExtension,
    ExtensionType,
    implementation_checklist,
    list_extensions,
    recommend_extension,
    risk_note,
)
from course.framework.claude.connectors import (
    CONNECTORS,
    ClaudeConnector,
    ConnectorCategory,
    list_connectors,
    permission_summary,
    qa_connector_checklist,
    recommend_connector,
)

__all__ = [
    "CONNECTORS",
    "EXTENSIONS",
    "ClaudeConnector",
    "ClaudeExtension",
    "ConnectorCategory",
    "ExtensionType",
    "implementation_checklist",
    "list_connectors",
    "list_extensions",
    "permission_summary",
    "qa_connector_checklist",
    "recommend_connector",
    "recommend_extension",
    "risk_note",
]
