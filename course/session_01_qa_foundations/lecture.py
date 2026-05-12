"""
Session 1 — QA Foundations & Manual Testing Techniques
Key concepts: test case design, defect lifecycle, test pyramid,
              decision tables, state transitions, risk-based testing,
              exploratory heuristics, coverage analysis.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. TEST CASE ANATOMY
# ─────────────────────────────────────────────────────────────────────────────
# Every test case has exactly these fields:
#   ID          — unique, traceable (TC-FEAT-NNN)
#   Title       — what behaviour is verified, not how
#   Priority    — High / Medium / Low (impact × likelihood of finding a defect)
#   Type        — see TEST_TYPES below
#   Precondition— state the system must be in BEFORE step 1
#   Steps       — atomic: ONE action per step, no assumptions
#   Expected    — concrete and measurable, never "it works"

PRIORITIES = ["High", "Medium", "Low"]

TEST_TYPES = {
    "Smoke":       "Does the happy path work after this deploy?",
    "Functional":  "Does each acceptance criterion behave correctly?",
    "Negative":    "Is every invalid input rejected with the right error?",
    "Edge Case":   "What happens at boundaries (min, max, empty, overflow)?",
    "Security":    "Is user data and auth protected (XSS, SQLi, auth bypass)?",
    "Performance": "Does the page/API respond within the SLA?",
    "Usability":   "Can a real user complete the task without guidance?",
    "Regression":  "Did this change break something that worked before?",
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. TEST PYRAMID
# ─────────────────────────────────────────────────────────────────────────────
TEST_PYRAMID = {
    "unit":        {"speed": "< 1 ms",  "cost": "low",    "count": "many (70%)"},
    "integration": {"speed": "< 1 s",   "cost": "medium", "count": "moderate (20%)"},
    "e2e":         {"speed": "seconds", "cost": "high",   "count": "few (10%)"},
}
# Rule: if you find yourself writing the same E2E test that a unit test
# could cover, you have an inverted pyramid. Inverted pyramids are slow,
# flaky, and expensive to maintain.

# ─────────────────────────────────────────────────────────────────────────────
# 3. TEST DESIGN TECHNIQUES
# ─────────────────────────────────────────────────────────────────────────────

# — Equivalence Partitioning (EP) —
# Divide inputs into groups that should behave identically.
# Test ONE value per group. If one fails, all in that group likely fail.
EP_LOGIN_PASSWORD = {
    "valid":     "correct_password              → login succeeds",
    "wrong":     "any_wrong_string              → credential error",
    "empty":     "'' (empty string)             → validation error",
    "too_long":  "'a' * 200                     → validation error or truncation",
    "injection": "' OR 1=1 --                   → standard error (not auth bypass)",
}

# — Boundary Value Analysis (BVA) —
# Test at the exact edge of each equivalence class: min, min+1, max-1, max.
# Most bugs hide at boundaries because developers write > instead of >=.
BOUNDARY_EXAMPLES = {
    "Password length (8–72 chars)": {
        "min-1 (7)":  "Rejected — too short",
        "min   (8)":  "Accepted",
        "max   (72)": "Accepted",
        "max+1 (73)": "Rejected — too long",
    },
    "Cart quantity": {
        "0":   "Rejected (cannot add zero items)",
        "1":   "Accepted (lower boundary)",
        "99":  "Accepted (plausible upper boundary)",
        "100": "Behaviour depends on business rule — test it",
    },
}

# — Decision Table —
# Use when behaviour depends on a COMBINATION of conditions.
# Each column = one test case. Covers all condition combinations.
#
# Login decision table (Username valid × Password valid):
#
#  Condition                  | C1  | C2  | C3  | C4
#  ─────────────────────────── ──── ──── ──── ────
#  Username is valid          |  Y  |  Y  |  N  |  N
#  Password is valid          |  Y  |  N  |  Y  |  N
#  ─────────────────────────── ──── ──── ──── ────
#  Action: login succeeds     |  ✓  |     |     |
#  Action: credential error   |     |  ✓  |  ✓  |  ✓
#
DECISION_TABLE_LOGIN = {
    "C1": {"username_valid": True,  "password_valid": True,  "outcome": "login succeeds"},
    "C2": {"username_valid": True,  "password_valid": False, "outcome": "credential error"},
    "C3": {"username_valid": False, "password_valid": True,  "outcome": "credential error"},
    "C4": {"username_valid": False, "password_valid": False, "outcome": "credential error"},
}

# — State Transition Testing —
# Model the system as states + transitions triggered by events.
# Cover: every valid transition AND every invalid transition from each state.
#
#  LOGGED_OUT ──login──► LOGGED_IN ──checkout──► STEP1 ──continue──► STEP2 ──finish──► CONFIRMED
#
CART_STATE_TRANSITIONS = {
    "EMPTY":     {"add_item": "HAS_ITEMS"},
    "HAS_ITEMS": {"add_item": "HAS_ITEMS", "remove_all": "EMPTY", "checkout": "CHECKOUT_STEP1"},
    "CHECKOUT_STEP1": {"continue": "CHECKOUT_STEP2", "cancel": "HAS_ITEMS"},
    "CHECKOUT_STEP2": {"finish": "ORDER_PLACED",     "cancel": "EMPTY"},
    "ORDER_PLACED":   {"back_home": "EMPTY"},
}
# Invalid transitions to test: skip STEP1, submit empty cart, double-submit finish.

# — Pairwise (All-Pairs) Testing —
# When N factors each have M values, full combinatorial = M^N tests.
# Pairwise reduces this: cover every PAIR of values at least once.
# For 4 browsers × 3 OS × 2 screen sizes = 24 full; pairwise ≈ 9.
PAIRWISE_NOTE = (
    "Use when 3+ independent variables and full combinatorial is too expensive. "
    "Tools: pairwisepy, allpairs."
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. DEFECT LIFECYCLE & SEVERITY vs PRIORITY
# ─────────────────────────────────────────────────────────────────────────────
DEFECT_LIFECYCLE = [
    "New       — tester opens the bug report",
    "Assigned  — PM/lead assigns it to a developer",
    "In Progress — developer investigates and fixes",
    "Fixed     — developer marks done, ready for re-test",
    "Verified  — tester confirms fix on target environment",
    "Closed    — bug confirmed resolved",
    "Reopened  — fix was incomplete; back to Assigned",
]

SEVERITY_VS_PRIORITY = {
    "Severity": "How much does this break the system? (Critical / Major / Minor / Trivial)",
    "Priority": "How urgently must it be fixed? (High / Medium / Low)",
    "Examples": [
        "Cosmetic typo on the CEO dashboard — Severity: Trivial, Priority: High",
        "Data corruption on a rarely-used admin screen — Severity: Critical, Priority: Medium",
        "Checkout crashes for all users — Severity: Critical, Priority: High (block release)",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. RISK-BASED TESTING
# ─────────────────────────────────────────────────────────────────────────────
# When time is limited, test where risk = likelihood × impact is highest.
# Score (1–9): likelihood (1–3) × impact (1–3).

RISK_REGISTER = [
    {"area": "Checkout / payment",      "likelihood": 2, "impact": 3, "score": 6, "mitigation": "Prioritise TC-CHK-* every sprint"},
    {"area": "Login / auth",            "likelihood": 2, "impact": 3, "score": 6, "mitigation": "Smoke gate on every deploy"},
    {"area": "Cart total calculation",  "likelihood": 1, "impact": 3, "score": 3, "mitigation": "Automated price assertion"},
    {"area": "Sort dropdown",           "likelihood": 2, "impact": 1, "score": 2, "mitigation": "Regression suite only"},
    {"area": "UI cosmetics",            "likelihood": 3, "impact": 1, "score": 3, "mitigation": "Visual diff tool in CI"},
]


def risk_priority(register: list) -> list:
    return sorted(register, key=lambda r: r["score"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# 6. EXPLORATORY TESTING HEURISTICS
# ─────────────────────────────────────────────────────────────────────────────

# SFDIPOT — a structured checklist for what to explore without a script
SFDIPOT = {
    "Structure":  "What is the product made of? (pages, forms, APIs, DB)",
    "Function":   "What does it do? (features, workflows, business rules)",
    "Data":       "What data flows through? (inputs, outputs, storage, formats)",
    "Interfaces": "How does it connect? (APIs, third-party, OS, browser)",
    "Platform":   "Where does it run? (browsers, OS, mobile, screen sizes)",
    "Operations": "How is it used in production? (load, error recovery, monitoring)",
    "Time":       "How does time affect it? (session expiry, race conditions, timezones)",
}

# FEW HICCUPS — rapid edge-case discovery heuristic
FEW_HICCUPS = {
    "Funny characters":   "Unicode, emoji, RTL text, null bytes, very long strings",
    "Empty / null":       "Empty fields, empty collections, missing JSON keys",
    "Wrong type":         "String where number expected, negative IDs, floats as quantities",
    "Huge values":        "Max int, 10 000-char strings, enormous file uploads",
    "Invalid boundaries": "One below min, one above max",
    "Combinations":       "Two valid inputs that conflict (e.g. two coupons)",
    "Concurrency":        "Two users doing the same action simultaneously",
    "Cancellation":       "Close tab mid-flow, click Cancel during payment",
    "Undo / back button": "Browser Back at unexpected points in a multi-step flow",
    "Permissions":        "Access a resource owned by a different user",
    "States":             "Double-submit, reload during submit, expired session",
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. ENTRY AND EXIT CRITERIA
# ─────────────────────────────────────────────────────────────────────────────
ENTRY_CRITERIA = [
    "Test environment is stable and matches production spec",
    "Build is deployed to the test environment",
    "All blocking defects from the previous cycle are fixed",
    "Test data is seeded (accounts, products, orders)",
    "Test cases have been reviewed and signed off",
]

EXIT_CRITERIA = [
    "All High-priority test cases executed",
    "Zero open Critical or High defects",
    "Defect density below agreed threshold",
    "Test coverage report reviewed by the team",
    "Regression suite passes with 0 failures on the release candidate",
]

# ─────────────────────────────────────────────────────────────────────────────
# 8. WRITING GOOD STEPS: COMMON MISTAKES
# ─────────────────────────────────────────────────────────────────────────────
STEP_MISTAKES = {
    "Compound step":   "Click Login and verify redirect  →  split into TWO steps",
    "Vague action":    "Fill in the form                 →  'Enter X in the Y field'",
    "Missing precond": "Steps assume a logged-in user    →  state it in Precondition",
    "Vague expected":  "'The page works correctly'       →  'URL is /inventory.html and 6 products are visible'",
    "Testing two things": "One case verifies login AND cart  →  split into two cases",
}


if __name__ == "__main__":
    print("=== Test types ===")
    for t, desc in TEST_TYPES.items():
        print(f"  {t:<14} {desc}")

    print("\n=== Decision table: login ===")
    for col, case in DECISION_TABLE_LOGIN.items():
        u = "valid  " if case["username_valid"] else "invalid"
        p = "valid  " if case["password_valid"] else "invalid"
        print(f"  {col}: username={u} password={p} → {case['outcome']}")

    print("\n=== Risk register (highest risk first) ===")
    for r in risk_priority(RISK_REGISTER):
        print(f"  [{r['score']}/9] {r['area']:<30} {r['mitigation']}")

    print("\n=== SFDIPOT heuristic ===")
    for letter, desc in SFDIPOT.items():
        print(f"  {letter:<14} {desc}")

    print("\n=== FEW HICCUPS ===")
    for h, desc in FEW_HICCUPS.items():
        print(f"  {h:<22} {desc}")
