"""
Session 4 - Playwright Locators
Key concepts: user-facing locators, test ids, chaining, filtering, strictness.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LocatorRule:
    priority: int
    locator: str
    use_when: str
    example: str


LOCATOR_PRIORITY = [
    LocatorRule(
        priority=1,
        locator="get_by_role",
        use_when="The element has a semantic role and accessible name.",
        example='page.get_by_role("button", name="Search").click()',
    ),
    LocatorRule(
        priority=2,
        locator="get_by_label",
        use_when="A form field has a visible associated label.",
        example='page.get_by_label("Password").fill("secret")',
    ),
    LocatorRule(
        priority=3,
        locator="get_by_text",
        use_when="Visible text is the behavior you want to verify.",
        example='expect(page.get_by_text("Your cart is empty")).to_be_visible()',
    ),
    LocatorRule(
        priority=4,
        locator="get_by_placeholder",
        use_when="An input is best identified by placeholder text.",
        example='page.get_by_placeholder("Search").fill("iPod")',
    ),
    LocatorRule(
        priority=5,
        locator="get_by_alt_text",
        use_when="An image or media element has meaningful alternative text.",
        example='page.get_by_alt_text("iPod Classic").click()',
    ),
    LocatorRule(
        priority=6,
        locator="get_by_title",
        use_when="The title attribute is the stable user-facing identifier.",
        example='page.get_by_title("Shopping Cart").click()',
    ),
    LocatorRule(
        priority=7,
        locator="get_by_test_id",
        use_when="The UI needs an explicit stable testing contract.",
        example='page.get_by_test_id("cart-total").click()',
    ),
    LocatorRule(
        priority=8,
        locator="locator(css_or_xpath)",
        use_when="Legacy markup has no reliable user-facing or test id locator.",
        example='page.locator(".legacy-widget button").click()',
    ),
]


ANTI_PATTERNS = {
    "raw selector in test": "Move it into a page object method.",
    "generated CSS class": "Use role, label, text, or test id.",
    "XPath by position": "Use chaining and filter(has_text=...).",
    "nth() on dynamic list": "Filter by product name, row text, or test id.",
    "sleep before click": "Rely on locator auto-waiting or assert target state.",
}


def print_locator_priority() -> None:
    print("Locator priority:")
    for rule in LOCATOR_PRIORITY:
        print(f"  {rule.priority}. {rule.locator}")
        print(f"     Use when: {rule.use_when}")
        print(f"     Example: {rule.example}")


def print_anti_patterns() -> None:
    print("\nLocator anti-patterns:")
    for problem, fix in ANTI_PATTERNS.items():
        print(f"  - {problem}: {fix}")


if __name__ == "__main__":
    print_locator_priority()
    print_anti_patterns()
