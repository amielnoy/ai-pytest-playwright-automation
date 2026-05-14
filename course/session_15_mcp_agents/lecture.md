# Session 15 — MCP & AI Agents

## Learning Objectives

By the end of this session you will be able to:

- Explain the agent loop (goal → tool call → result → next decision) and implement it with the Anthropic SDK.
- Define tools with clear `name`, `description`, and `input_schema` fields and explain why descriptions drive model behaviour.
- Build an explorer agent that can accomplish open-ended goals on a live page using Playwright tools.
- Build a regression agent that detects UI changes by diffing accessibility tree snapshots.
- Explain what MCP is and how it decouples tool definitions from the agent loop.
- Connect the Playwright MCP server so Claude controls a browser without custom dispatch code.
- Build an MCP flow-planning agent that receives ordered screenshots and returns a detailed step-level test plan.

---

## What Is an AI Agent?

An agent is a loop: the model receives a goal, decides which tool to call, receives the result, and decides the next action — until it calls a "done" tool or hits a step limit.

Unlike a single prompt, the agent can recover from mistakes: if a click fails, it can take a snapshot, re-read the page, and try a different selector.

This session builds three agents:

- An **explorer** that accomplishes any goal on a live page.
- A **regression agent** that replays a known flow and compares accessibility snapshots.
- A **flow test planner** that receives ordered screenshots or wireframes and turns them into a detailed test plan.

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

---

## MCP Flow Test Planner

`flow_test_planner_mcp.py` exposes an MCP tool named `plan_flow_from_images`.
The tool receives a sequence of images that describe a user flow and returns a detailed QA test plan at the level of executable steps.

Input contract:

```json
{
  "feature": "Checkout",
  "flow_goal": "A logged-in user buys one product with a valid credit card.",
  "images": [
    {
      "path": "artifacts/checkout_01_cart.png",
      "title": "Cart",
      "note": "User has one item"
    },
    {
      "path": "artifacts/checkout_02_payment.png",
      "title": "Payment form",
      "note": "All fields are empty"
    },
    {
      "path": "artifacts/checkout_03_confirmation.png",
      "title": "Order confirmation",
      "note": "Successful purchase"
    }
  ],
  "assumptions": [
    "Images are ordered from first screen to final screen.",
    "The user is already logged in."
  ]
}
```

Expected output:

- Flow goal and assumptions.
- Screen-by-screen test steps.
- User action for each step.
- Expected result for each step.
- Assertions to automate.
- Test data and validation checks.
- Edge cases and accessibility checks.
- Open questions where the images do not provide enough evidence.

The lesson implementation has two modes:

- With `ANTHROPIC_API_KEY`: the tool sends the images to a vision model and asks it to inspect the UI.
- Without `ANTHROPIC_API_KEY`: the tool returns a deterministic planning template so the class can run it without external access.

Run the MCP server:

```bash
python course/session_15_mcp_agents/flow_test_planner_mcp.py
```

This agent is intentionally read-only. It should produce planning material, not create or change tests automatically.

---

## Session Completion Checklist

Before moving to Session 16, verify you can answer yes to each item:

- [ ] I ran the explorer agent against the demo site and it completed at least one goal autonomously.
- [ ] I added a new tool to the explorer (e.g. `scroll`) and the model used it correctly.
- [ ] I ran the regression agent on two versions of a page and it detected the difference.
- [ ] I can explain the agent loop in plain English without looking at the code.
- [ ] I can explain why tool descriptions are more important than tool implementations.
- [ ] I connected the Playwright MCP server and confirmed Claude controlled the browser without custom dispatch.
- [ ] I generated a step-level test plan from a series of flow images using `plan_flow_from_images`.
- [ ] I completed the exercises in `EXERCISES.md`.
