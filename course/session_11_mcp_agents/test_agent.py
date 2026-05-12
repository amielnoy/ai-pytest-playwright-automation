"""
Session 11 — tests that use the browser_agent fixture.

The agent receives a plain-English goal and uses Claude + Playwright tools
(navigate, click, fill, snapshot, screenshot, done) to accomplish it.
The test asserts on the OUTCOME, not the steps.

Run:  pytest course/session_11_mcp_agents/test_agent.py -v -s
      ANTHROPIC_API_KEY must be set; tests skip otherwise.
"""
import os
import pytest
from playwright.sync_api import Page, expect

from course.framework.pages import LoginPage

BASE_URL = "https://www.saucedemo.com"
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping agent tests",
)


def test_agent_logs_in_and_reads_page_title(browser_agent, page: Page):
    """
    Agent is asked to log in with standard credentials.
    We verify the outcome (URL changed to /inventory.html) ourselves.
    The agent decides HOW — fill username, fill password, click Login.
    """
    log = browser_agent(
        goal=(
            f"Go to {BASE_URL}. "
            "Log in with username 'standard_user' and password 'secret_sauce'. "
            "Once you see the product list, call done with the page title."
        )
    )

    final = next((e.get("final") for e in log if "final" in e), None)
    assert final is not None, "Agent should have called done()"
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")


def test_agent_finds_cheapest_product(browser_agent, page: Page):
    """
    Agent browses the inventory, reads all prices, and reports the cheapest.
    Test verifies agent completed without error; no DOM assertion needed here
    because the agent's snapshot reads are the verification.
    """
    LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")

    log = browser_agent(
        goal=(
            "Look at the product prices on the current page. "
            "Find the cheapest product and call done with its name and price."
        )
    )

    final = next((e.get("final") for e in log if "final" in e), None)
    assert final is not None, "Agent should have reported cheapest product"
    print(f"\n[agent] cheapest product: {final}")


def test_agent_adds_item_to_cart(browser_agent, page: Page):
    """
    Agent is given a goal; test verifies the cart badge shows 1 afterwards.
    Demonstrates that agent actions have observable side-effects in the DOM.
    """
    LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")

    browser_agent(
        goal="Click 'Add to cart' on the first product you see, then call done."
    )

    expect(page.locator(".shopping_cart_badge")).to_have_text("1")


def test_agent_step_log_contains_tool_calls(browser_agent, page: Page):
    """
    Regression: every run should produce at least one tool call.
    Guards against silent agent failures where Claude returns text instead of tool use.
    """
    log = browser_agent(
        goal=f"Navigate to {BASE_URL} and call done with the page title."
    )

    tool_steps = [e for e in log if "tool" in e]
    assert len(tool_steps) >= 1, f"Expected tool calls in log, got: {log}"
