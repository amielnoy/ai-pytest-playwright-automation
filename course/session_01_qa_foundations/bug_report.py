"""
Session 1 — Bug Reports
How to write a bug report that a developer can reproduce, understand, and fix
without asking follow-up questions.

A good bug report has eight fields:
  ID           — unique identifier (BUG-NNN)
  Title        — one sentence: <component> + <observed behaviour> + <expected behaviour>
  Severity     — Critical / Major / Minor / Trivial
  Priority     — High / Medium / Low
  Environment  — OS, browser, version, user account used
  Steps        — numbered, atomic, reproducible every time
  Actual       — exactly what happened (screenshot / log / error text)
  Expected     — what should have happened per spec or common sense
  Attachments  — screenshots, console errors, video, network logs
"""

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

BUG_TEMPLATE = {
    "id":          "BUG-NNN",
    "title":       "<Component>: <observed> instead of <expected>",
    "severity":    "Critical | Major | Minor | Trivial",
    "priority":    "High | Medium | Low",
    "environment": {
        "os":      "macOS 15.4 / Windows 11 / Ubuntu 24.04",
        "browser": "Chrome 124 / Firefox 125 / Safari 17",
        "url":     "https://www.saucedemo.com",
        "user":    "standard_user / locked_out_user / …",
    },
    "steps": [
        "1. <first action>",
        "2. <second action>",
        "3. <etc.>",
    ],
    "actual":    "Describe exactly what happened — paste error text verbatim.",
    "expected":  "Describe what should have happened per spec or common sense.",
    "attachments": ["screenshot.png", "console-errors.txt"],
}

SEVERITY_GUIDE = {
    "Critical": "System unusable; data loss or security breach; no workaround",
    "Major":    "Core feature broken; workaround exists but is painful",
    "Minor":    "Feature works but behaves unexpectedly in edge cases",
    "Trivial":  "Cosmetic issue (typo, alignment, wrong colour)",
}

# ─────────────────────────────────────────────────────────────────────────────
# REAL EXAMPLES — bugs found while manually testing saucedemo.com
# ─────────────────────────────────────────────────────────────────────────────

BUG_REPORTS = [
    {
        "id": "BUG-001",
        "title": "Auth: locked_out_user error message does not match the spec text",
        "severity": "Minor",
        "priority": "Medium",
        "environment": {
            "os": "macOS 15.4",
            "browser": "Chrome 124",
            "url": "https://www.saucedemo.com",
            "user": "locked_out_user",
        },
        "steps": [
            "1. Navigate to https://www.saucedemo.com",
            "2. Enter 'locked_out_user' in the Username field",
            "3. Enter 'secret_sauce' in the Password field",
            "4. Click the Login button",
        ],
        "actual": (
            "Error banner reads: "
            "'Epic sadface: Sorry, this user has been locked out.'"
        ),
        "expected": (
            "Per acceptance criteria the message should read: "
            "'Your account has been locked. Please contact support.'"
        ),
        "attachments": ["BUG-001-screenshot.png"],
        "notes": (
            "The prefix 'Epic sadface:' is informal and may be intentional for "
            "this demo site. Confirm with the PM whether the copy is final."
        ),
    },
    {
        "id": "BUG-002",
        "title": "Cart: badge count does not update when removing the last item via the cart page",
        "severity": "Major",
        "priority": "High",
        "environment": {
            "os": "Windows 11",
            "browser": "Firefox 125",
            "url": "https://www.saucedemo.com/cart.html",
            "user": "standard_user",
        },
        "steps": [
            "1. Log in as standard_user",
            "2. Click 'Add to cart' on any product — badge shows '1'",
            "3. Click the cart icon to open /cart.html",
            "4. Click 'Remove' on the item inside the cart page",
        ],
        "actual": (
            "The item row disappears but the cart badge still shows '1'. "
            "Refreshing the page clears the badge."
        ),
        "expected": (
            "Badge should update to '0' (or disappear) immediately after "
            "clicking Remove, without requiring a page refresh."
        ),
        "attachments": ["BUG-002-before.png", "BUG-002-after.png"],
        "notes": "Reproducible 100% of the time on Firefox 125. Not reproduced on Chrome 124.",
    },
    {
        "id": "BUG-003",
        "title": "Checkout: Tax amount on the overview step is incorrectly rounded",
        "severity": "Major",
        "priority": "High",
        "environment": {
            "os": "macOS 15.4",
            "browser": "Chrome 124",
            "url": "https://www.saucedemo.com/checkout-step-two.html",
            "user": "standard_user",
        },
        "steps": [
            "1. Log in as standard_user",
            "2. Add 'Sauce Labs Backpack' ($29.99) to the cart",
            "3. Click the cart icon → Click 'Checkout'",
            "4. Enter any valid name and postal code → Click 'Continue'",
            "5. Read the 'Tax' line on the overview page",
        ],
        "actual": "Tax shows $2.40 (8.0075% of $29.99 ≈ $2.401 rounded to $2.40).",
        "expected": (
            "Tax rate is documented as 8% in the product spec. "
            "8% of $29.99 = $2.3992, which should round to $2.40. "
            "The displayed value matches, but the calculation uses 8.0075% "
            "which may differ for larger carts. Confirm the intended tax rate."
        ),
        "attachments": ["BUG-003-overview.png"],
        "notes": "Low impact for single items; rounding drift accumulates with large carts.",
    },
    {
        "id": "BUG-004",
        "title": "Sort: selected sort option resets to default after navigating to a product and back",
        "severity": "Minor",
        "priority": "Medium",
        "environment": {
            "os": "macOS 15.4",
            "browser": "Safari 17",
            "url": "https://www.saucedemo.com/inventory.html",
            "user": "standard_user",
        },
        "steps": [
            "1. Log in as standard_user",
            "2. Select 'Price (low to high)' from the sort dropdown",
            "3. Verify products are sorted correctly",
            "4. Click any product name to open its detail page",
            "5. Click 'Back to products'",
        ],
        "actual": "Sort dropdown reverts to 'Name (A to Z)' (the default).",
        "expected": "The sort selection should be preserved after navigating back.",
        "attachments": ["BUG-004-before-nav.png", "BUG-004-after-back.png"],
        "notes": (
            "Not reproducible on Chrome or Firefox — Safari does not restore "
            "the select element state via the back-forward cache."
        ),
    },
    {
        "id": "BUG-005",
        "title": "Auth: browser back button after logout allows viewing the inventory page",
        "severity": "Critical",
        "priority": "High",
        "environment": {
            "os": "Windows 11",
            "browser": "Chrome 124",
            "url": "https://www.saucedemo.com",
            "user": "standard_user",
        },
        "steps": [
            "1. Log in as standard_user — land on /inventory.html",
            "2. Open the hamburger menu → click 'Logout'",
            "3. Confirm you are on the login page",
            "4. Press the browser Back button",
        ],
        "actual": "/inventory.html is visible and all products are shown — no re-authentication required.",
        "expected": (
            "Pressing Back after logout should redirect to the login page. "
            "Session cookie should be invalidated on logout."
        ),
        "attachments": ["BUG-005-inventory-after-logout.png"],
        "notes": (
            "Security issue: cached page shown without a valid session. "
            "The server should return 302 → /login on any request after logout."
        ),
    },
]


def print_bug_report(bug: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"[{bug['id']}] {bug['title']}")
    print(f"Severity: {bug['severity']}  |  Priority: {bug['priority']}")
    env = bug["environment"]
    print(f"Env: {env['os']} / {env['browser']} / user={env['user']}")
    print("Steps:")
    for step in bug["steps"]:
        print(f"  {step}")
    print(f"Actual:   {bug['actual']}")
    print(f"Expected: {bug['expected']}")
    if bug.get("notes"):
        print(f"Notes:    {bug['notes']}")


def print_all_bugs() -> None:
    for bug in BUG_REPORTS:
        print_bug_report(bug)
    print(f"\n{len(BUG_REPORTS)} bug report(s) total")


if __name__ == "__main__":
    print("Bug report template fields:")
    for field, value in BUG_TEMPLATE.items():
        if field != "environment":
            print(f"  {field:<14} {value if isinstance(value, str) else value[0]}")
    print("\nSeverity guide:")
    for sev, desc in SEVERITY_GUIDE.items():
        print(f"  {sev:<10} {desc}")
    print_all_bugs()
