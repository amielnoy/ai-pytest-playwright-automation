"""
Session 15 — MCP + AI Agents
Key concepts: tool-use loop, agent vs script, goal-driven testing.
"""

# ── What is an agent? ─────────────────────────────────────────────────────────
# A script knows every step in advance.
# An agent knows the GOAL — Claude decides the steps at runtime.
#
# agent loop:
#   while not done:
#       resp = claude(history + tools)
#       for tool_use in resp:
#           result = execute(tool_use)
#           history.append(result)

AGENT_VS_SCRIPT = {
    "Script": "Fixed sequence: goto → fill → click → assert. Breaks on DOM change.",
    "Agent":  "Goal: 'log in and add cheapest item to cart.' Claude adapts to DOM.",
}

# ── Tools the agent has ────────────────────────────────────────────────────────
TOOLS = {
    "navigate":      "Go to a URL.",
    "click":         "Click by CSS selector or accessible name.",
    "fill":          "Fill a form field.",
    "snapshot":      "Read the accessibility tree (Claude's 'eyes').",
    "screenshot":    "Capture a PNG — useful for visual verification steps.",
    "wait_for_text": "Wait up to 5 s for text to appear.",
    "done":          "Signal task completion + summary string.",
}

# ── When to use agents in a test suite ────────────────────────────────────────
AGENT_USE_CASES = [
    "Exploratory testing: discover flows you haven't scripted yet.",
    "Regression diffing: replay a recorded flow on a new build and compare snapshots.",
    "Smoke tests on unknown pages: 'Is there a login form? Can I submit it?'",
    "Test generation: agent explores → produces a session transcript → CLI writes tests.",
]

# ── Agent pitfalls ─────────────────────────────────────────────────────────────
PITFALLS = [
    "Non-determinism: same goal → different steps each run → flaky 'tests'.",
    "Token cost: each step adds to history; long runs are expensive.",
    "Trust boundary: agent can click anything — including destructive buttons.",
    "No assertion: agent 'done' ≠ correct outcome. Assert the DOM yourself.",
]

# ── Rule: agent drives; test asserts ──────────────────────────────────────────
# WRONG:  assert "Thank you" in agent_log[-1]["final"]
# RIGHT:  agent(goal="complete the checkout")
#         expect(page.get_by_text("Thank you for your order!")).to_be_visible()

if __name__ == "__main__":
    print("Agent vs Script:")
    for k, v in AGENT_VS_SCRIPT.items():
        print(f"  {k}: {v}")
    print("\nWhen to use agents:")
    for uc in AGENT_USE_CASES:
        print(f"  • {uc}")
    print("\nPitfalls:")
    for p in PITFALLS:
        print(f"  ⚠  {p}")
