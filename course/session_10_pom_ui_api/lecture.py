"""
Session 10 — Advanced Playwright: POM + UI + API
Key concepts: Page Object Model, Fluent API, UI/API hybrid testing.
"""

# ── POM structure ──────────────────────────────────────────────────────────────
# BasePage          — navigate(), page, base_url
# LoginPage(Base)   — open(), login() → InventoryPage, expect_error()
# InventoryPage     — add_first_item(), add_item_by_name(), sort_by(), go_to_cart()
# CartPage          — item_count(), remove_item_by_name(), proceed_to_checkout()
# CheckoutPage      — fill_info(), continue_to_overview(), finish(), expect_order_complete()

# ── Fluent API: every method returns self (or the next page) ──────────────────
# LoginPage(page, BASE_URL).open().login("user", "pass")   → InventoryPage
# inventory.add_first_item().expect_cart_count(1)           → InventoryPage
# cart.proceed_to_checkout().fill_info(info).finish()       → CheckoutPage

# ── POM rules ─────────────────────────────────────────────────────────────────
POM_RULES = [
    "Tests describe WHAT; page objects describe HOW.",
    "No raw selectors in test functions — always delegate to a page class.",
    "One class per page or major component; split when >200 lines.",
    "Locators are lazily evaluated — define in __init__, call in methods.",
    "Return the next page object on navigation; return self on same-page actions.",
]

# ── UI vs API setup: when to use each ─────────────────────────────────────────
SETUP_STRATEGY = {
    "UI setup": "Only for tests validating the UI setup flow itself (e.g. registration).",
    "API setup": "Prefer for pre-conditions: add items to cart, create accounts, seed data.",
}

# ── Playwright APIRequestContext for API calls inside tests ────────────────────
# api = playwright.request.new_context(base_url="https://api.example.com")
# resp = api.post("/users", data={"name": "Amiel"})
# assert resp.status == 201
# api.dispose()

# ── Data factory pattern ───────────────────────────────────────────────────────
# Use faker + dataclasses for typed, realistic test data.
# make_checkout_info()            → CheckoutInfo(first, last, postal)
# make_incomplete_checkout_info() → missing one field (tests validation errors)

if __name__ == "__main__":
    print("POM rules:")
    for rule in POM_RULES:
        print(f"  • {rule}")
    print("\nSetup strategy:")
    for kind, rule in SETUP_STRATEGY.items():
        print(f"  {kind}: {rule}")
