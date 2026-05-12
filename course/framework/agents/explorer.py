"""
Session 11 — Browser exploration agent.
Claude drives Playwright via tool calls to accomplish a natural-language goal.
"""
import os
import anthropic

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element by accessible name or CSS selector.",
        "input_schema": {
            "type": "object",
            "properties": {"selector": {"type": "string"}},
            "required": ["selector"],
        },
    },
    {
        "name": "fill",
        "description": "Fill a form field.",
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
        "description": "Return the accessibility tree of the current page.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "screenshot",
        "description": "Save a PNG screenshot to a file path.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "wait_for_text",
        "description": "Wait up to 5 s for a text string to appear on the page.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "done",
        "description": "Signal task completion with a summary.",
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
        },
    },
]


def run_agent(page, goal: str, max_steps: int = 15) -> list[dict]:
    """Run the browser agent until it calls 'done' or exhausts max_steps.

    Returns a step log: [{"step": n, "tool": name, "input": …}, …, {"final": summary}]
    """
    history = [{
        "role": "user",
        "content": f"Goal: {goal}\nUse the tools to accomplish it. Call 'done' when finished.",
    }]
    log: list[dict] = []

    for step in range(max_steps):
        resp = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1_024,
            tools=TOOLS,
            messages=history,
        )

        tool_called = False
        for block in resp.content:
            if block.type != "tool_use":
                continue
            tool_called = True
            name, inp = block.name, block.input
            log.append({"step": step, "tool": name, "input": inp})

            if name == "navigate":
                page.goto(inp["url"])
                result = f"Navigated to {inp['url']}"
            elif name == "click":
                page.locator(inp["selector"]).click()
                result = f"Clicked {inp['selector']}"
            elif name == "fill":
                page.locator(inp["selector"]).fill(inp["value"])
                result = f"Filled {inp['selector']} with '{inp['value']}'"
            elif name == "snapshot":
                result = page.accessibility.snapshot()
            elif name == "screenshot":
                page.screenshot(path=inp["path"])
                result = f"Screenshot → {inp['path']}"
            elif name == "wait_for_text":
                page.get_by_text(inp["text"]).first.wait_for(state="visible", timeout=5_000)
                result = f"Text visible: {inp['text']}"
            elif name == "done":
                log.append({"final": inp["summary"]})
                return log
            else:
                result = f"Unknown tool: {name}"

            history.append({"role": "assistant", "content": resp.content})
            history.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": block.id, "content": str(result)}],
            })

        if not tool_called:
            break

    return log
