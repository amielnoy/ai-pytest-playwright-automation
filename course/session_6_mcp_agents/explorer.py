"""
Session 6 — MCP + AI Agents
Browser agent that takes a URL and a goal, then uses Playwright tools to accomplish it.
The agent loop calls Claude with tool definitions; each tool result is fed back so the
model can recover from mistakes and plan the next step.

Usage:
    from playwright.sync_api import sync_playwright
    from explorer import run_agent

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        log = run_agent(page, "Find the cheapest product and add it to the cart")
        print(log)
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a URL",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element by accessible name or CSS selector",
        "input_schema": {
            "type": "object",
            "properties": {"selector": {"type": "string"}},
            "required": ["selector"],
        },
    },
    {
        "name": "fill",
        "description": "Fill a form field",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["selector", "value"],
        },
    },
    {
        "name": "snapshot",
        "description": "Return the accessibility tree of the current page",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot and return the file path (useful for visual verification)",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "File path to save PNG"}},
            "required": ["path"],
        },
    },
    {
        "name": "wait_for_text",
        "description": "Wait until a text string appears on the page (up to 5 seconds)",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "done",
        "description": "Signal task completion with a summary of what was done",
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
        },
    },
]


def run_agent(page, goal: str, max_steps: int = 15) -> list[dict]:
    history = [
        {
            "role": "user",
            "content": f"Goal: {goal}\nUse the tools to accomplish it. Call 'done' when finished.",
        }
    ]
    log: list[dict] = []

    for step in range(max_steps):
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
            log.append({"step": step, "tool": tool_name, "input": tool_input})

            if tool_name == "navigate":
                page.goto(tool_input["url"])
                result = f"Navigated to {tool_input['url']}"
            elif tool_name == "click":
                page.locator(tool_input["selector"]).click()
                result = f"Clicked {tool_input['selector']}"
            elif tool_name == "fill":
                page.locator(tool_input["selector"]).fill(tool_input["value"])
                result = f"Filled {tool_input['selector']} with '{tool_input['value']}'"
            elif tool_name == "snapshot":
                result = page.accessibility.snapshot()
            elif tool_name == "screenshot":
                page.screenshot(path=tool_input["path"])
                result = f"Screenshot saved to {tool_input['path']}"
            elif tool_name == "wait_for_text":
                page.get_by_text(tool_input["text"]).first.wait_for(state="visible", timeout=5000)
                result = f"Text visible: {tool_input['text']}"
            elif tool_name == "done":
                log.append({"final": tool_input["summary"]})
                return log
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

    return log
