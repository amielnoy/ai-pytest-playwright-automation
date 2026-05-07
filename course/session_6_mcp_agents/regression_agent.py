"""
Session 6 — MCP + AI Agents
Regression agent: replays discovered flows and diffs accessibility snapshots to detect
behavioral changes between deploys.

Usage:
    from playwright.sync_api import sync_playwright
    from regression_agent import replay_flow, diff_snapshots

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        result = replay_flow(page, {"name": "login → inventory", "steps": 3})
        print(result)
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate to a URL",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element",
        "input_schema": {
            "type": "object",
            "properties": {"selector": {"type": "string"}},
            "required": ["selector"],
        },
    },
    {
        "name": "snapshot",
        "description": "Return the accessibility tree",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "done",
        "description": "Signal flow completion",
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
        },
    },
]


def diff_snapshots(before: dict | None, after: dict | None) -> dict:
    """Return a simple diff summary between two accessibility snapshots."""
    return {
        "before_children": len(before.get("children", [])) if before else 0,
        "after_children": len(after.get("children", [])) if after else 0,
        "changed": before != after,
    }


def replay_flow(page, flow: dict, max_steps: int = 15) -> dict:
    history = [{"role": "user", "content": f"Replay this flow exactly: {flow}"}]
    initial_snapshot = page.accessibility.snapshot()

    for _ in range(max_steps):
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=history,
        )

        for block in resp.content:
            if block.type != "tool_use":
                continue

            tool_name, tool_input = block.name, block.input

            if tool_name == "navigate":
                page.goto(tool_input["url"])
                result = f"Navigated to {tool_input['url']}"
            elif tool_name == "click":
                page.locator(tool_input["selector"]).click()
                result = f"Clicked {tool_input['selector']}"
            elif tool_name == "snapshot":
                result = page.accessibility.snapshot()
            elif tool_name == "done":
                final_snapshot = page.accessibility.snapshot()
                return diff_snapshots(initial_snapshot, final_snapshot)
            else:
                result = f"Unknown tool: {tool_name}"

            history.append({"role": "assistant", "content": resp.content})
            history.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}
                    ],
                }
            )

    final_snapshot = page.accessibility.snapshot()
    return diff_snapshots(initial_snapshot, final_snapshot)
