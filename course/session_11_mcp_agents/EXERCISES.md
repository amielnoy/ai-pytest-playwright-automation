# Session 11 — Exercises

## Exercise 1: Add a New Tool

The explorer agent in `explorer.py` does not have a `scroll` tool.

1. Add a `scroll` tool with `direction` ("up" | "down") and `amount` (pixels) as inputs.
2. Write a clear `description` so the model knows when to use it vs `click`.
3. Implement the `execute()` dispatch for `scroll` using `page.evaluate("window.scrollBy(...)")`.
4. Test the agent on a goal that requires scrolling (e.g. "Find and click the last product on the inventory page").

---

## Exercise 2: Improve Tool Descriptions

The `snapshot` tool currently has the description "Return the accessibility tree of the current page."

1. Run the explorer on a goal that requires multiple interactions and count how often it calls `snapshot` unnecessarily.
2. Rewrite the description to guide the model to call `snapshot` only when it needs to re-orient (e.g. after a navigation or a failed click).
3. Re-run the same goal and compare the number of `snapshot` calls.

---

## Exercise 3: Step Limit Experiment

Set `max_steps=3` in the explorer agent and run it on a goal that requires at least 5 steps.

1. What happens when the agent hits the step limit?
2. Add a `"step_limit_reached"` early exit that returns a partial log instead of silently truncating.
3. What is a sensible default `max_steps` for a full checkout flow? Justify your answer.

---

## Exercise 4: Regression Snapshot Diffing

1. Run the regression agent on the inventory page and save the "before" snapshot.
2. Manually add a hidden element to the page DOM using browser dev tools (or intercept the response in a fixture and inject HTML).
3. Run the regression agent again and confirm `diff_snapshots()` detects the change.
4. What kinds of DOM changes would NOT be detected by the current diff logic? Name two.

---

## Exercise 5: MCP Server Connection

1. Install `@playwright/mcp` and start the MCP server.
2. Update `test_agent.py` to use the MCP server instead of the custom `execute()` function.
3. Confirm the agent completes the same goals as before.
4. Explain in two sentences what you removed from the codebase by switching to MCP.
