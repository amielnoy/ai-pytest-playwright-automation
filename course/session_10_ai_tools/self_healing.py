"""
Session 10 — Building AI Tools for QA
Self-healing selector wrapper: tries the original locator; if it fails, asks AI for a replacement.
Every heal is logged so engineers can update the stale selector later.
"""

import os
import anthropic
from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeout

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def find_or_heal(page: Page, primary_selector: str, description: str) -> Locator:
    locator = page.locator(primary_selector)
    try:
        locator.wait_for(state="visible", timeout=2000)
        return locator
    except PlaywrightTimeout:
        html = page.content()[:8000]
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"This Playwright selector no longer matches: `{primary_selector}`.\n"
                        f"Element description: {description}\n"
                        f"HTML snippet:\n{html}\n\n"
                        "Reply with ONLY a new Playwright selector string, nothing else."
                    ),
                }
            ],
        )
        new_selector = msg.content[0].text.strip().strip("`")
        print(f"[self-heal] {primary_selector} → {new_selector}")
        return page.locator(new_selector)


class HealTracker:
    """Accumulates heal events during a test run so they can be reviewed in bulk."""

    def __init__(self) -> None:
        self._heals: list[dict] = []

    def find_or_heal(self, page: Page, primary_selector: str, description: str) -> Locator:
        locator = page.locator(primary_selector)
        try:
            locator.wait_for(state="visible", timeout=2000)
            return locator
        except PlaywrightTimeout:
            healed = find_or_heal(page, primary_selector, description)
            new_selector = healed._selector  # type: ignore[attr-defined]
            self._heals.append({"original": primary_selector, "healed": new_selector, "description": description})
            return healed

    def summary(self) -> list[dict]:
        return list(self._heals)

    def print_summary(self) -> None:
        if not self._heals:
            print("[self-heal] No heals this run.")
            return
        print(f"[self-heal] {len(self._heals)} heal(s) this run:")
        for h in self._heals:
            print(f"  {h['original']} → {h['healed']}  ({h['description']})")


def explain_heal(original_selector: str, healed_selector: str, page_title: str) -> str:
    """Ask Claude to explain why a selector needed healing — useful for root-cause reports."""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    f"A Playwright selector stopped working on page '{page_title}'.\n"
                    f"  Original: `{original_selector}`\n"
                    f"  Healed:   `{healed_selector}`\n\n"
                    "In 2-3 sentences explain the likely cause (e.g. class rename, "
                    "DOM restructure, id change) and suggest a permanent fix."
                ),
            }
        ],
    )
    return msg.content[0].text.strip()
