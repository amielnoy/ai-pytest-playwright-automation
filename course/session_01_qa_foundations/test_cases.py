"""
Session 1 — Manual Test Cases for saucedemo.com
Organised by feature. Every case follows the same anatomy:
  id | title | priority | type | precondition | steps | expected
"""

BASE_URL = "https://www.saucedemo.com"

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 1 — Authentication
# ─────────────────────────────────────────────────────────────────────────────

AUTH_CASES = [
    {
        "id": "TC-AUTH-001",
        "title": "Standard user logs in successfully",
        "priority": "High",
        "type": "Smoke",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "standard_user" in the Username field',
            'Enter "secret_sauce" in the Password field',
            "Click the Login button",
        ],
        "expected": "Redirected to /inventory.html; product list is visible",
    },
    {
        "id": "TC-AUTH-002",
        "title": "Locked-out user sees a specific error",
        "priority": "High",
        "type": "Negative",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "locked_out_user" in the Username field',
            'Enter "secret_sauce" in the Password field',
            "Click the Login button",
        ],
        "expected": 'Error banner "Sorry, this user has been locked out" is shown; URL stays on login',
    },
    {
        "id": "TC-AUTH-003",
        "title": "Wrong password shows credential mismatch error",
        "priority": "High",
        "type": "Negative",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "standard_user" in the Username field',
            'Enter "wrong_password" in the Password field',
            "Click the Login button",
        ],
        "expected": 'Error "Username and password do not match" appears; no navigation',
    },
    {
        "id": "TC-AUTH-004",
        "title": "Empty password shows validation error",
        "priority": "Medium",
        "type": "Negative",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "standard_user" in the Username field',
            "Leave the Password field empty",
            "Click the Login button",
        ],
        "expected": '"Password is required" error appears; no navigation',
    },
    {
        "id": "TC-AUTH-005",
        "title": "Empty username shows validation error",
        "priority": "Medium",
        "type": "Negative",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            "Leave the Username field empty",
            'Enter "secret_sauce" in the Password field',
            "Click the Login button",
        ],
        "expected": '"Username is required" error appears; no navigation',
    },
    {
        "id": "TC-AUTH-006",
        "title": "Both fields empty — username validation fires first",
        "priority": "Low",
        "type": "Edge Case",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            "Leave both Username and Password empty",
            "Click the Login button",
        ],
        "expected": '"Username is required" error appears (username checked before password)',
    },
    {
        "id": "TC-AUTH-007",
        "title": "Session cookie persists after page reload",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "User is logged in as standard_user at /inventory.html",
        "steps": [
            "Press F5 (or Ctrl+R) to reload the page",
        ],
        "expected": "User remains on /inventory.html; session is still active",
    },
    {
        "id": "TC-AUTH-008",
        "title": "Logged-out user cannot access /inventory.html directly",
        "priority": "High",
        "type": "Security",
        "precondition": f"Browser is on {BASE_URL} (not logged in)",
        "steps": [
            "Navigate directly to https://www.saucedemo.com/inventory.html",
        ],
        "expected": "Redirected back to the login page; inventory not visible",
    },
    {
        "id": "TC-AUTH-009",
        "title": "Logout returns user to login page and invalidates session",
        "priority": "High",
        "type": "Functional",
        "precondition": "User is logged in at /inventory.html",
        "steps": [
            "Click the hamburger menu (☰) in the top-left corner",
            'Click "Logout"',
            "Navigate directly to https://www.saucedemo.com/inventory.html",
        ],
        "expected": "After logout user is on login page; direct navigation to /inventory.html redirects back to login",
    },
    {
        "id": "TC-AUTH-010",
        "title": "XSS payload in Username is rendered as plain text",
        "priority": "High",
        "type": "Security",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "<script>alert(1)</script>" in the Username field',
            'Enter "any" in the Password field',
            "Click the Login button",
        ],
        "expected": "Error message shows the literal string; no alert dialog fires",
    },
    {
        "id": "TC-AUTH-011",
        "title": "Performance-glitch user completes login within 5 seconds",
        "priority": "Medium",
        "type": "Performance",
        "precondition": f"Browser is on {BASE_URL}",
        "steps": [
            'Enter "performance_glitch_user" and "secret_sauce"',
            "Click Login and start a stopwatch",
            "Stop the stopwatch when /inventory.html is fully loaded",
        ],
        "expected": "Login completes; page fully loaded in under 5 000 ms",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 2 — Product Inventory
# ─────────────────────────────────────────────────────────────────────────────

INVENTORY_CASES = [
    {
        "id": "TC-INV-001",
        "title": "Inventory page shows exactly 6 products",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            "Count the product cards visible on the page",
        ],
        "expected": "Exactly 6 product cards are displayed",
    },
    {
        "id": "TC-INV-002",
        "title": "Each product card shows name, description, price, and Add-to-cart button",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            "Inspect one product card",
            "Verify it contains: product image, name, description, price ($X.XX format), Add to cart button",
        ],
        "expected": "All four elements are present on every card; price matches $X.XX format",
    },
    {
        "id": "TC-INV-003",
        "title": "Sort by Name (A to Z) orders products alphabetically",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            'Select "Name (A to Z)" from the Sort dropdown',
            "Read the product names top to bottom",
        ],
        "expected": "Names are in ascending alphabetical order (A before Z)",
    },
    {
        "id": "TC-INV-004",
        "title": "Sort by Name (Z to A) reverses alphabetical order",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            'Select "Name (Z to A)" from the Sort dropdown',
            "Read the product names top to bottom",
        ],
        "expected": "Names are in descending alphabetical order (Z before A)",
    },
    {
        "id": "TC-INV-005",
        "title": "Sort by Price (low to high) orders products cheapest first",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            'Select "Price (low to high)" from the Sort dropdown',
            "Read the prices top to bottom",
        ],
        "expected": "Each price is ≤ the price below it; cheapest product is first",
    },
    {
        "id": "TC-INV-006",
        "title": "Sort by Price (high to low) orders products most expensive first",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            'Select "Price (high to low)" from the Sort dropdown',
            "Read the prices top to bottom",
        ],
        "expected": "Each price is ≥ the price below it; most expensive product is first",
    },
    {
        "id": "TC-INV-007",
        "title": "Clicking a product name opens the product detail page",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in as standard_user at /inventory.html",
        "steps": [
            "Click on the name of the first product",
        ],
        "expected": "Browser navigates to /inventory-item.html?id=X; product name is shown as a heading",
    },
    {
        "id": "TC-INV-008",
        "title": "Back button on product detail returns to inventory with sort preserved",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Sorted by Price (low to high); clicked into first product",
        "steps": [
            'Click "Back to products" button',
        ],
        "expected": "Returns to /inventory.html; sort selection is still Price (low to high)",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 3 — Shopping Cart
# ─────────────────────────────────────────────────────────────────────────────

CART_CASES = [
    {
        "id": "TC-CART-001",
        "title": "Adding one product shows badge '1' on the cart icon",
        "priority": "High",
        "type": "Smoke",
        "precondition": "Logged in; cart is empty",
        "steps": [
            'Click "Add to cart" on any product',
        ],
        "expected": "Cart icon badge updates to '1'",
    },
    {
        "id": "TC-CART-002",
        "title": "Adding three products shows badge '3'",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in; cart is empty",
        "steps": [
            'Click "Add to cart" on three different products',
        ],
        "expected": "Cart icon badge shows '3'",
    },
    {
        "id": "TC-CART-003",
        "title": "After adding a product, its button changes to 'Remove'",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Logged in; cart is empty",
        "steps": [
            'Click "Add to cart" on a product',
        ],
        "expected": 'The button on that product card changes label to "Remove"',
    },
    {
        "id": "TC-CART-004",
        "title": "Removing a product via 'Remove' button decrements the badge",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in; one product in cart (badge shows '1')",
        "steps": [
            'Click the "Remove" button on the product that was added',
        ],
        "expected": "Cart badge disappears (or shows '0'); button reverts to 'Add to cart'",
    },
    {
        "id": "TC-CART-005",
        "title": "Cart page lists the correct product names and prices",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in; added 'Sauce Labs Backpack' ($29.99) to cart",
        "steps": [
            "Click the cart icon",
            "Read the item name and price",
        ],
        "expected": "Cart shows 'Sauce Labs Backpack' at $29.99; quantity shows 1",
    },
    {
        "id": "TC-CART-006",
        "title": "Cart contents persist across navigation",
        "priority": "High",
        "type": "Functional",
        "precondition": "Logged in; one product in cart",
        "steps": [
            "Navigate to the About page via the hamburger menu",
            "Press the browser Back button to return to /inventory.html",
        ],
        "expected": "Cart badge still shows '1'; the same product is still in the cart",
    },
    {
        "id": "TC-CART-007",
        "title": "Continue Shopping from cart returns to inventory",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Logged in; on /cart.html with one item",
        "steps": [
            'Click "Continue Shopping"',
        ],
        "expected": "Navigated back to /inventory.html; cart badge count unchanged",
    },
    {
        "id": "TC-CART-008",
        "title": "Empty cart shows no items and no badge",
        "priority": "Low",
        "type": "Edge Case",
        "precondition": "Logged in; cart is empty",
        "steps": [
            "Click the cart icon",
        ],
        "expected": "Cart page shows no item rows; badge is absent or shows '0'",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 4 — Checkout
# ─────────────────────────────────────────────────────────────────────────────

CHECKOUT_CASES = [
    {
        "id": "TC-CHK-001",
        "title": "Completing checkout with valid info shows order confirmation",
        "priority": "High",
        "type": "Smoke",
        "precondition": "Logged in; one product in cart; on /cart.html",
        "steps": [
            'Click "Checkout"',
            'Enter "John" in First Name, "Doe" in Last Name, "12345" in Postal Code',
            'Click "Continue"',
            'Click "Finish"',
        ],
        "expected": '"Thank you for your order!" confirmation page is shown',
    },
    {
        "id": "TC-CHK-002",
        "title": "Checkout step 1 requires First Name",
        "priority": "High",
        "type": "Negative",
        "precondition": "Logged in; one item in cart; on checkout step 1",
        "steps": [
            "Leave First Name empty",
            'Enter "Doe" in Last Name and "12345" in Postal Code',
            'Click "Continue"',
        ],
        "expected": '"First Name is required" error appears; does not advance to step 2',
    },
    {
        "id": "TC-CHK-003",
        "title": "Checkout step 1 requires Last Name",
        "priority": "High",
        "type": "Negative",
        "precondition": "Logged in; one item in cart; on checkout step 1",
        "steps": [
            'Enter "John" in First Name',
            "Leave Last Name empty",
            'Enter "12345" in Postal Code',
            'Click "Continue"',
        ],
        "expected": '"Last Name is required" error appears; does not advance to step 2',
    },
    {
        "id": "TC-CHK-004",
        "title": "Checkout step 1 requires Postal Code",
        "priority": "High",
        "type": "Negative",
        "precondition": "Logged in; one item in cart; on checkout step 1",
        "steps": [
            'Enter "John" in First Name and "Doe" in Last Name',
            "Leave Postal Code empty",
            'Click "Continue"',
        ],
        "expected": '"Postal Code is required" error appears; does not advance to step 2',
    },
    {
        "id": "TC-CHK-005",
        "title": "Checkout overview shows correct item total",
        "priority": "High",
        "type": "Functional",
        "precondition": "Added Sauce Labs Backpack ($29.99); on checkout step 2 (overview)",
        "steps": [
            "Read the Item total line",
            "Read the Tax line",
            "Read the Total line",
        ],
        "expected": "Item total = $29.99; Tax = $2.40; Total = $32.39",
    },
    {
        "id": "TC-CHK-006",
        "title": "Cancel on checkout step 1 returns to cart with items intact",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "Logged in; one item in cart; on checkout step 1",
        "steps": [
            'Click "Cancel"',
        ],
        "expected": "Returns to /cart.html; item is still in the cart",
    },
    {
        "id": "TC-CHK-007",
        "title": "Cancel on overview returns to inventory page",
        "priority": "Medium",
        "type": "Functional",
        "precondition": "On checkout overview (step 2)",
        "steps": [
            'Click "Cancel"',
        ],
        "expected": "Returns to /inventory.html",
    },
    {
        "id": "TC-CHK-008",
        "title": "Cart is empty after a completed order",
        "priority": "High",
        "type": "Functional",
        "precondition": "Just completed checkout — on the confirmation page",
        "steps": [
            'Click "Back Home"',
            "Check the cart badge",
        ],
        "expected": "Cart badge is absent; /inventory.html shows no items in cart",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# All cases combined for reporting
# ─────────────────────────────────────────────────────────────────────────────

ALL_CASES = AUTH_CASES + INVENTORY_CASES + CART_CASES + CHECKOUT_CASES

FEATURE_SUMMARY = {
    "Authentication":    len(AUTH_CASES),
    "Product Inventory": len(INVENTORY_CASES),
    "Shopping Cart":     len(CART_CASES),
    "Checkout":          len(CHECKOUT_CASES),
}


def print_test_cases(cases: list | None = None) -> None:
    for tc in (cases or ALL_CASES):
        print(f"\n{'─' * 60}")
        print(f"{tc['id']}  {tc['title']}")
        print(f"Priority: {tc['priority']}  |  Type: {tc['type']}")
        print(f"Precondition: {tc['precondition']}")
        print("Steps:")
        for i, step in enumerate(tc["steps"], 1):
            print(f"  {i}. {step}")
        print(f"Expected: {tc['expected']}")


def print_coverage_summary() -> None:
    total = sum(FEATURE_SUMMARY.values())
    print(f"\n{'Feature':<22} {'Cases':>6}")
    print("─" * 30)
    for feature, count in FEATURE_SUMMARY.items():
        bar = "█" * count
        print(f"{feature:<22} {count:>6}  {bar}")
    print("─" * 30)
    print(f"{'TOTAL':<22} {total:>6}")


if __name__ == "__main__":
    print_coverage_summary()
    choice = input("\nPrint cases for feature (auth/inv/cart/chk/all)? ").strip().lower()
    mapping = {
        "auth": AUTH_CASES,
        "inv":  INVENTORY_CASES,
        "cart": CART_CASES,
        "chk":  CHECKOUT_CASES,
        "all":  ALL_CASES,
    }
    print_test_cases(mapping.get(choice, ALL_CASES))
