"""
Session 25 - Claude skills and plugins reference layer.

These helpers model the decision process for extending Claude/Codex workflows
without hard-coding vendor setup into tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExtensionType(StrEnum):
    SKILL = "skill"
    PLUGIN = "plugin"
    MCP = "mcp"
    SLASH_COMMAND = "slash_command"


@dataclass(frozen=True)
class ClaudeExtension:
    name: str
    extension_type: ExtensionType
    purpose: str
    best_for: tuple[str, ...]
    needs_external_access: bool = False


EXTENSIONS: tuple[ClaudeExtension, ...] = (
    ClaudeExtension(
        name="QA Review Skill",
        extension_type=ExtensionType.SKILL,
        purpose="Reusable local instructions for reviewing tests consistently.",
        best_for=("review", "standards", "repeatable prompts"),
    ),
    ClaudeExtension(
        name="Playwright MCP",
        extension_type=ExtensionType.MCP,
        purpose="Browser control through a model context protocol server.",
        best_for=("browser inspection", "debugging selectors", "interactive exploration"),
        needs_external_access=True,
    ),
    ClaudeExtension(
        name="GitHub Plugin",
        extension_type=ExtensionType.PLUGIN,
        purpose="Repository, pull request, issue, and CI workflows.",
        best_for=("pull request", "pull requests", "issues", "ci", "ci triage"),
        needs_external_access=True,
    ),
    ClaudeExtension(
        name="/generate-test",
        extension_type=ExtensionType.SLASH_COMMAND,
        purpose="Project command that turns a QA intent into a test draft.",
        best_for=("test generation", "local workflow", "team conventions"),
    ),
)


def list_extensions(extension_type: ExtensionType | None = None) -> list[ClaudeExtension]:
    if extension_type is None:
        return list(EXTENSIONS)
    return [item for item in EXTENSIONS if item.extension_type == extension_type]


def recommend_extension(task: str) -> ClaudeExtension:
    normalized = task.lower()
    scored_matches = [
        (
            sum(1 for keyword in extension.best_for if keyword in normalized),
            extension,
        )
        for extension in EXTENSIONS
    ]
    score, extension = max(scored_matches, key=lambda item: item[0])
    if score > 0:
        return extension
    return EXTENSIONS[0]


def risk_note(extension: ClaudeExtension) -> str:
    if extension.needs_external_access:
        return f"{extension.name} needs connector, browser, network, or repository access."
    return f"{extension.name} can run from local project instructions."


def implementation_checklist(extension: ClaudeExtension) -> list[str]:
    checklist = [
        f"Define the exact workflow for {extension.name}.",
        "Document expected inputs and outputs.",
        "Add a small example students can run or inspect.",
        "Describe review and approval boundaries.",
    ]
    if extension.needs_external_access:
        checklist.append("Document permissions, credentials, and fallback behavior.")
    return checklist
