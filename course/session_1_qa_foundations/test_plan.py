"""
Session 1 — Test Plan for saucedemo.com v1.0
A test plan answers: WHAT will be tested, HOW, by WHOM, and by WHEN.
It is written before testing begins and reviewed with the whole team.

Sections:
  1. Scope          — what is in and out of scope
  2. Approach       — types of testing, tools, environments
  3. Resources      — who does what
  4. Schedule       — timeline and milestones
  5. Risk register  — what can go wrong and how to handle it
  6. Entry criteria — when testing may begin
  7. Exit criteria  — when testing is complete
  8. Coverage matrix— which features map to which test cases
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. SCOPE
# ─────────────────────────────────────────────────────────────────────────────

IN_SCOPE = [
    "Authentication (login / logout / session handling)",
    "Product inventory page (display, sorting)",
    "Product detail page (navigation, content)",
    "Shopping cart (add, remove, persist)",
    "Checkout flow (form validation, overview, confirmation)",
    "Cross-browser: Chrome, Firefox, Safari",
]

OUT_OF_SCOPE = [
    "Payment processing (no real payment gateway on the demo)",
    "Admin / back-office functionality",
    "Mobile native app (web only in this test cycle)",
    "Load / stress testing beyond basic performance checks",
    "Internationalisation (English only for this sprint)",
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. APPROACH
# ─────────────────────────────────────────────────────────────────────────────

APPROACH = {
    "Manual exploratory": (
        "Session 1 — testers follow charters (see exploratory.py) "
        "to discover unscripted defects. Time-boxed to 45 minutes per charter."
    ),
    "Scripted manual": (
        "Session 1 — execute the structured test cases in test_cases.py "
        "in order of priority (High → Medium → Low)."
    ),
    "Automated regression": (
        "Sessions 3–9 — Playwright + pytest suite runs on every PR via GitHub Actions. "
        "Blocks merge on any failure."
    ),
    "AI-assisted generation": (
        "Session 2 — use prompt templates to generate additional test cases "
        "from acceptance criteria. Review output with classify_ai_output()."
    ),
}

ENVIRONMENTS = {
    "dev":     "http://localhost:3000 — developer testing before PR",
    "staging": "https://staging.saucedemo.com — pre-release validation",
    "prod":    "https://www.saucedemo.com — smoke only after release",
}

BROWSERS = ["Chrome (latest)", "Firefox (latest)", "Safari (latest)"]

TEST_ACCOUNTS = {
    "standard_user":         "Happy-path testing — full access",
    "locked_out_user":       "Negative testing — login blocked",
    "performance_glitch_user": "Performance testing — intentionally slow login",
    "error_user":            "Error-path testing — random errors injected",
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. RESOURCES
# ─────────────────────────────────────────────────────────────────────────────

TEAM = {
    "QA Lead":      "Owns the test plan, reviews coverage, signs off on exit criteria",
    "QA Engineer":  "Executes manual test cases, logs defects, runs automation",
    "Developer":    "Fixes defects, answers questions about implementation",
    "Product Owner":"Clarifies acceptance criteria, prioritises defects",
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. SCHEDULE
# ─────────────────────────────────────────────────────────────────────────────

SCHEDULE = [
    {"milestone": "Test plan review",          "owner": "QA Lead",     "day": 1},
    {"milestone": "Exploratory session — auth","owner": "QA Engineer", "day": 2},
    {"milestone": "Exploratory session — cart","owner": "QA Engineer", "day": 2},
    {"milestone": "Scripted execution — High", "owner": "QA Engineer", "day": 3},
    {"milestone": "Scripted execution — Med",  "owner": "QA Engineer", "day": 4},
    {"milestone": "Defect review meeting",     "owner": "Whole team",  "day": 4},
    {"milestone": "Regression automation run", "owner": "QA Engineer", "day": 5},
    {"milestone": "Exit criteria check",       "owner": "QA Lead",     "day": 5},
    {"milestone": "Sign-off",                  "owner": "QA Lead + PO","day": 5},
]

# ─────────────────────────────────────────────────────────────────────────────
# 5. RISK REGISTER
# ─────────────────────────────────────────────────────────────────────────────

RISKS = [
    {
        "risk":        "Test environment is down",
        "likelihood":  "Medium",
        "impact":      "High",
        "mitigation":  "Set up a local Docker instance as fallback; notify DevOps 24 h before",
    },
    {
        "risk":        "Checkout payment flow is incomplete",
        "likelihood":  "Low",
        "impact":      "Critical",
        "mitigation":  "Escalate immediately to PO; consider delaying release",
    },
    {
        "risk":        "Flaky automation causes false failures in CI",
        "likelihood":  "Medium",
        "impact":      "Medium",
        "mitigation":  "Tag flaky tests with @pytest.mark.flaky_prone; monitor with flaky_detector.py",
    },
    {
        "risk":        "Not enough time to execute all test cases",
        "likelihood":  "High",
        "impact":      "Medium",
        "mitigation":  "Execute High-priority cases first; skip Low-priority if time runs out",
    },
    {
        "risk":        "Defect count exceeds capacity to fix before release",
        "likelihood":  "Medium",
        "impact":      "High",
        "mitigation":  "Daily defect triage; defer Minor/Trivial; escalate Critical immediately",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 6 & 7. ENTRY AND EXIT CRITERIA
# ─────────────────────────────────────────────────────────────────────────────

ENTRY_CRITERIA = [
    "Build v1.0 is deployed to the staging environment",
    "All Critical defects from the previous sprint are fixed and verified",
    "Test data seeded: accounts, 6 products, a completed historical order",
    "All High-priority test cases reviewed and approved by PO",
]

EXIT_CRITERIA = [
    "100% of High-priority test cases executed",
    "80%+ of Medium-priority test cases executed",
    "Zero open Critical or High defects",
    "Defect density < 2 new bugs per feature",
    "Automated regression suite passing on Chrome + Firefox",
    "Test summary report accepted by QA Lead and PO",
]

# ─────────────────────────────────────────────────────────────────────────────
# 8. COVERAGE MATRIX
# ─────────────────────────────────────────────────────────────────────────────
# Maps each feature to its test case IDs so you can quickly see gaps.

COVERAGE_MATRIX = {
    "Authentication": {
        "test_cases": ["TC-AUTH-001", "TC-AUTH-002", "TC-AUTH-003", "TC-AUTH-004",
                       "TC-AUTH-005", "TC-AUTH-006", "TC-AUTH-007", "TC-AUTH-008",
                       "TC-AUTH-009", "TC-AUTH-010", "TC-AUTH-011"],
        "automation":  ["test_login_negative", "test_successful_login_redirects_to_inventory",
                        "test_logout_clears_session", "test_failed_login_does_not_set_session_cookie"],
        "coverage":    "High — all user types and error paths covered",
    },
    "Product Inventory": {
        "test_cases": ["TC-INV-001", "TC-INV-002", "TC-INV-003", "TC-INV-004",
                       "TC-INV-005", "TC-INV-006", "TC-INV-007", "TC-INV-008"],
        "automation":  ["test_sort_price_low_to_high", "test_sort_name_a_to_z",
                        "test_sort_dropdown_shows_correct_selected_label"],
        "coverage":    "Medium — display and sort covered; product search not tested (out of scope)",
    },
    "Shopping Cart": {
        "test_cases": ["TC-CART-001", "TC-CART-002", "TC-CART-003", "TC-CART-004",
                       "TC-CART-005", "TC-CART-006", "TC-CART-007", "TC-CART-008"],
        "automation":  ["test_add_single_item_to_cart", "test_add_multiple_items_updates_badge",
                        "test_remove_item_from_cart_updates_badge", "test_cart_contents_survive_navigation"],
        "coverage":    "High — add, remove, persist, and navigation covered",
    },
    "Checkout": {
        "test_cases": ["TC-CHK-001", "TC-CHK-002", "TC-CHK-003", "TC-CHK-004",
                       "TC-CHK-005", "TC-CHK-006", "TC-CHK-007", "TC-CHK-008"],
        "automation":  ["test_full_checkout_flow", "test_checkout_missing_first_name_shows_error"],
        "coverage":    "Medium — happy path and field validation covered; tax edge cases manual only",
    },
}


def print_coverage_gaps() -> None:
    print("\n=== Coverage Matrix ===\n")
    for feature, data in COVERAGE_MATRIX.items():
        tc_count  = len(data["test_cases"])
        aut_count = len(data["automation"])
        ratio     = aut_count / tc_count * 100
        print(f"  {feature:<22} {tc_count:>3} manual cases  "
              f"{aut_count:>3} automated  ({ratio:.0f}% automated)")
        print(f"  {'':>22} {data['coverage']}")
        print()


def print_schedule() -> None:
    print("=== Schedule ===\n")
    for item in SCHEDULE:
        print(f"  Day {item['day']}  {item['owner']:<20} {item['milestone']}")


if __name__ == "__main__":
    print(f"In scope  ({len(IN_SCOPE)} areas):")
    for s in IN_SCOPE:
        print(f"  ✓ {s}")
    print(f"\nOut of scope ({len(OUT_OF_SCOPE)} areas):")
    for s in OUT_OF_SCOPE:
        print(f"  ✗ {s}")
    print_schedule()
    print_coverage_gaps()
    print("Entry criteria:")
    for c in ENTRY_CRITERIA:
        print(f"  [ ] {c}")
    print("\nExit criteria:")
    for c in EXIT_CRITERIA:
        print(f"  [ ] {c}")
