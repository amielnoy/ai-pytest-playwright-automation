# Session 6 — MCP & AI Agents

## What Is an AI Agent?

An agent is a loop: the model receives a goal, decides which tool to call, receives the result, and decides the next action — until it calls a "done" tool or hits a step limit.

Unlike a single prompt, the agent can recover from mistakes: if a click fails, it can take a snapshot, re-read the page, and try a different selector.

This session builds two agents: an **explorer** (accomplish any goal on a live page) and a **regression agent** (replay a known flow and compare accessibility snapshots).

---

## Tool Definitions

Each tool is a JSON object with `name`, `description`, and `input_schema`.
The model reads these descriptions and decides which tool to call next.
Good descriptions are the most important part — vague descriptions lead to wrong tool choices.

Tools in the explorer agent:
- `navigate` — go to a URL
- `click` — click by accessible name or CSS selector
- `fill` — fill a form field
- `snapshot` — return the accessibility tree of the current page
- `screenshot` — save a PNG (visual verification)
- `wait_for_text` — wait until a string appears (up to 5 s)
- `done` — signal completion with a summary

---

## The Agent Loop

```
history = [{"role": "user", "content": f"Goal: {goal}"}]

for step in range(max_steps):
    resp = client.messages.create(model=…, tools=TOOLS, messages=history)
    for block in resp.content:
        if block.type != "tool_use": continue
        result = execute(block.name, block.input)   # call Playwright
        history.append({"role": "assistant", "content": resp.content})
        history.append({"role": "user", "content": [tool_result(block.id, result)]})
        if block.name == "done": return log
```

The full `resp.content` (not just the tool block) is appended to history so the model retains its prior reasoning.

---

## Regression Agent & Snapshot Diffing

The regression agent replays a recorded flow (e.g. "login → view inventory") and compares the accessibility tree before and after.

`diff_snapshots(before, after)` returns whether the tree changed and how many top-level children moved.
A changed snapshot signals a UI regression — new element, removed element, or text change — without any explicit assertion.

This is useful for catching unintentional DOM changes after a deploy.

---

## MCP (Model Context Protocol)

MCP is a standard for exposing tools to AI models over a protocol rather than hardcoded JSON blobs.
An MCP server exposes tool schemas; the model client fetches them at runtime.

The Playwright MCP server (`@playwright/mcp`) exposes browser tools (navigate, click, snapshot, etc.) over MCP so Claude can control a browser without any custom tool-dispatch code.

Using MCP means: no `execute()` function to maintain — the server handles it.
