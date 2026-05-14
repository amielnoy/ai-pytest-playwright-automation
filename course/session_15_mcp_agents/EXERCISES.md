# Session 15 — Exercises

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

---

## Exercise 6: Image Flow Test Planner MCP Agent

Use `flow_test_planner_mcp.py` to generate a detailed test plan from a series of images that describe a product flow.

1. Collect 3-5 screenshots or wireframes for one flow, such as registration, login, add-to-cart, checkout, or password reset.
2. Start the MCP server:

   ```bash
   python course/session_15_mcp_agents/flow_test_planner_mcp.py
   ```

3. Call `plan_flow_from_images` with:

   ```json
   {
     "feature": "Registration",
     "flow_goal": "A new user creates an account and reaches the logged-in home page.",
     "images": [
       {
         "path": "artifacts/registration_01_empty_form.png",
         "title": "Empty registration form",
         "note": "No validation errors yet"
       },
       {
         "path": "artifacts/registration_02_validation.png",
         "title": "Validation errors",
         "note": "Required fields missing"
       },
       {
         "path": "artifacts/registration_03_success.png",
         "title": "Successful registration",
         "note": "User sees welcome state"
       }
     ],
     "assumptions": [
       "Images are ordered by user journey.",
       "Email verification is not part of this flow."
     ]
   }
   ```

4. Review the generated plan and mark:
   - Steps that are directly supported by the images.
   - Steps that are assumptions.
   - Missing assertions that a human QA should add.
   - Which steps should become automated Playwright tests.

5. Rewrite one generated step as a framework task: target page object, test file, test data, and expected assertion.
