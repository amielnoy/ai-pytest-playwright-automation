"""
Session 10 — Self-healing selector wrapper.
Try the primary selector; if it times out, ask Claude for a replacement.
Every heal is logged so engineers can update stale Page Object selectors later.
"""
import os
import anthropic
from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeout

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

_HEAL_PROMPT = (
    "This Playwright selector no longer matches: `{selector}`.\n"
    "Element description: {description}\n"
    "HTML snippet (first 8 000 chars):\n{html}\n\n"
    "Reply with ONLY a new Playwright selector string, nothing else."
)


def find_or_heal(page: Page, selector: str, description: str) -> Locator:
    """Return a locator for *selector*; if invisible within 2 s, ask Claude for a fix."""
    locator = page.locator(selector)
    try:
        locator.wait_for(state="visible", timeout=2_000)
        return locator
    except PlaywrightTimeout:
        msg = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": _HEAL_PROMPT.format(
                    selector=selector,
                    description=description,
                    html=page.content()[:8_000],
                ),
            }],
        )
        new_selector = next(
            (b.text for b in msg.content if hasattr(b, "text")), selector
        ).strip().strip("`")
        print(f"[self-heal] {selector} → {new_selector}")
        return page.locator(new_selector)


def explain_heal(original: str, healed: str, page_title: str) -> str:
    """Ask Claude why a selector needed healing — for root-cause reports."""
    msg = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"A Playwright selector broke on page '{page_title}'.\n"
                f"  Original: `{original}`\n"
                f"  Healed:   `{healed}`\n\n"
                "In 2-3 sentences explain the likely cause and suggest a permanent fix."
            ),
        }],
    )
    return next((b.text for b in msg.content if hasattr(b, "text")), "").strip()


class HealTracker:
    """Accumulates heal events during a test run so they can be reviewed in bulk."""

    def __init__(self) -> None:
        self._heals: list[dict] = []

    def find_or_heal(self, page: Page, selector: str, description: str) -> Locator:
        locator = page.locator(selector)
        try:
            locator.wait_for(state="visible", timeout=2_000)
            return locator
        except PlaywrightTimeout:
            healed = find_or_heal(page, selector, description)
            self._heals.append({
                "original": selector,
                "description": description,
                "healed": str(healed),
            })
            return healed

    def summary(self) -> list[dict]:
        return list(self._heals)

    def print_summary(self) -> None:
        if not self._heals:
            print("[self-heal] no heals this run ✓")
            return
        print(f"[self-heal] {len(self._heals)} heal(s) this run:")
        for h in self._heals:
            print(f"  {h['original']} → {h['healed']}  ({h['description']})")
