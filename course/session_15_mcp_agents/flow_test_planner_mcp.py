"""
Session 15 - MCP + AI Agents
Flow test planner MCP server.

The MCP tool receives a sequence of screenshots or wireframes that describe a
product flow. With ANTHROPIC_API_KEY it asks a vision model to inspect the
images and produce a detailed step-level test plan. Without an API key it
returns a deterministic planning template, which keeps the lesson runnable in
class and easy to unit test.

Run as an MCP server:
    python course/session_15_mcp_agents/flow_test_planner_mcp.py
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - dependency is installed in the course env
    Anthropic = None  # type: ignore[assignment]

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("flow-test-planner")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


def _resolve_image_path(path: str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = _PROJECT_ROOT / candidate
    return candidate.resolve()


def _image_media_type(path: Path) -> str:
    guessed, _encoding = mimetypes.guess_type(path.name)
    if guessed in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        return guessed
    return "image/png"


def _load_image_block(path: Path) -> dict[str, Any]:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": _image_media_type(path),
            "data": data,
        },
    }


def _normalise_images(images: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalised: list[dict[str, Any]] = []
    for index, image in enumerate(images, start=1):
        path_value = str(image.get("path", "")).strip()
        if not path_value:
            raise ValueError(f"Image {index} is missing a 'path' value.")

        path = _resolve_image_path(path_value)
        if not path.exists():
            raise FileNotFoundError(f"Image {index} does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Image {index} is not a file: {path}")

        normalised.append(
            {
                "index": index,
                "path": path,
                "title": str(image.get("title") or f"Screen {index}"),
                "note": str(image.get("note") or "").strip(),
            }
        )
    return normalised


def _fallback_test_plan(
    *,
    feature: str,
    flow_goal: str,
    images: list[dict[str, Any]],
    assumptions: list[str],
) -> str:
    image_lines = []
    for image in images:
        note = f" - {image['note']}" if image["note"] else ""
        image_lines.append(f"{image['index']}. {image['title']} ({image['path'].name}){note}")

    assumption_lines = assumptions or [
        "Screens are ordered from the first user action to the expected final state.",
        "Any visual element that is not readable from the image must be verified with the product owner.",
    ]

    step_lines = []
    for image in images:
        step_lines.extend(
            [
                f"{image['index']}. Observe screen: {image['title']}",
                f"   - Action: Identify the primary user action that moves this flow forward.",
                f"   - Expected result: The UI matches the intended state for {image['title']}.",
                "   - Assertions: Verify visible copy, enabled/disabled controls, navigation target, and error state.",
                "   - Data checks: Record any required input values, validation rules, and persisted state.",
            ]
        )

    return "\n".join(
        [
            f"# Test Plan: {feature}",
            "",
            f"## Flow Goal",
            flow_goal,
            "",
            "## Input Screens",
            *image_lines,
            "",
            "## Assumptions",
            *[f"- {assumption}" for assumption in assumption_lines],
            "",
            "## Detailed Test Steps",
            *step_lines,
            "",
            "## Coverage Checklist",
            "- Happy path from first screen to final screen.",
            "- Required field validation.",
            "- Navigation and back/refresh behaviour.",
            "- Error handling for failed network or invalid server response.",
            "- Accessibility checks for labels, focus order, keyboard navigation, and screen reader names.",
            "- Analytics or audit event checks, if the product requires them.",
            "",
            "## Open Questions",
            "- Which exact selectors, test data, and backend contracts should be used?",
            "- Are there role, locale, viewport, or device-specific variants of this flow?",
            "- Which failures should block release and which should be logged as follow-up risk?",
        ]
    )


def _vision_test_plan(
    *,
    feature: str,
    flow_goal: str,
    images: list[dict[str, Any]],
    assumptions: list[str],
    model: str,
) -> str:
    if Anthropic is None:
        raise RuntimeError("anthropic package is not installed.")

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "You are a senior QA test architect. Inspect the ordered images as a single user flow. "
                "Create a detailed manual test plan at step level. Do not invent hidden product behaviour; "
                "mark uncertainty as an open question.\n\n"
                f"Feature: {feature}\n"
                f"Flow goal: {flow_goal}\n"
                f"Assumptions: {json.dumps(assumptions, ensure_ascii=False)}\n\n"
                "For each screen include: step number, user action, expected result, assertions, "
                "test data, edge cases, accessibility checks, and automation notes."
            ),
        }
    ]

    for image in images:
        content.append(
            {
                "type": "text",
                "text": f"Screen {image['index']}: {image['title']}. Note: {image['note'] or 'none'}",
            }
        )
        content.append(_load_image_block(image["path"]))

    response = client.messages.create(
        model=model,
        max_tokens=3000,
        temperature=0,
        messages=[{"role": "user", "content": content}],
    )

    return "\n".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    ).strip()


def generate_test_plan_from_images(
    *,
    feature: str,
    flow_goal: str,
    images: list[dict[str, Any]],
    assumptions: list[str] | None = None,
    use_vision: bool | None = None,
    model: str = _DEFAULT_MODEL,
) -> str:
    """
    Generate a detailed test plan from ordered flow images.

    Set use_vision=False in tests or classroom dry-runs. Leave it as None to
    use the vision model only when ANTHROPIC_API_KEY is available.
    """
    if not images:
        raise ValueError("At least one image is required.")

    normalised_images = _normalise_images(images)
    safe_assumptions = assumptions or []
    should_use_vision = bool(os.environ.get("ANTHROPIC_API_KEY")) if use_vision is None else use_vision

    if should_use_vision:
        return _vision_test_plan(
            feature=feature,
            flow_goal=flow_goal,
            images=normalised_images,
            assumptions=safe_assumptions,
            model=model,
        )

    return _fallback_test_plan(
        feature=feature,
        flow_goal=flow_goal,
        images=normalised_images,
        assumptions=safe_assumptions,
    )


@mcp.tool()
def plan_flow_from_images(
    feature: str,
    flow_goal: str,
    images: list[dict[str, Any]],
    assumptions: list[str] | None = None,
    use_vision: bool | None = None,
) -> str:
    """
    Create a detailed step-level QA test plan from ordered flow images.

    images example:
    [
      {"path": "artifacts/login_01.png", "title": "Login form", "note": "empty state"},
      {"path": "artifacts/login_02.png", "title": "Inventory", "note": "after valid login"}
    ]
    """
    return generate_test_plan_from_images(
        feature=feature,
        flow_goal=flow_goal,
        images=images,
        assumptions=assumptions,
        use_vision=use_vision,
    )


if __name__ == "__main__":
    mcp.run()
