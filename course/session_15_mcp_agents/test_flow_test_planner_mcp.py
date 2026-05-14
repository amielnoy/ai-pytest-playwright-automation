"""
Tests for the Session 15 flow test planner MCP helper.

These tests force dry-run mode so they do not require ANTHROPIC_API_KEY or a
network call to a vision model.
"""

from __future__ import annotations

import pytest

from course.session_15_mcp_agents.flow_test_planner_mcp import (
    generate_test_plan_from_images,
)


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01"
    b"\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_generate_test_plan_from_images_returns_step_level_plan(tmp_path):
    first = tmp_path / "registration_01.png"
    second = tmp_path / "registration_02.png"
    first.write_bytes(PNG_1X1)
    second.write_bytes(PNG_1X1)

    plan = generate_test_plan_from_images(
        feature="Registration",
        flow_goal="A new user creates an account.",
        images=[
            {
                "path": str(first),
                "title": "Empty registration form",
                "note": "No validation errors yet",
            },
            {
                "path": str(second),
                "title": "Successful registration",
                "note": "Welcome state is visible",
            },
        ],
        assumptions=["Email verification is out of scope."],
        use_vision=False,
    )

    assert "# Test Plan: Registration" in plan
    assert "A new user creates an account." in plan
    assert "Empty registration form" in plan
    assert "Successful registration" in plan
    assert "## Detailed Test Steps" in plan
    assert "- Assertions:" in plan
    assert "Email verification is out of scope." in plan


def test_generate_test_plan_from_images_requires_images():
    with pytest.raises(ValueError, match="At least one image is required"):
        generate_test_plan_from_images(
            feature="Checkout",
            flow_goal="Buy one item.",
            images=[],
            use_vision=False,
        )


def test_generate_test_plan_from_images_rejects_missing_file(tmp_path):
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        generate_test_plan_from_images(
            feature="Checkout",
            flow_goal="Buy one item.",
            images=[{"path": str(missing), "title": "Cart"}],
            use_vision=False,
        )
