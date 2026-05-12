"""
Session 1 — Exploratory Testing
Session-Based Test Management (SBTM): structured, time-boxed exploration
with a charter that states WHAT to explore and WHY.

An exploratory session has three parts:
  Charter   — the mission: area + goal + time limit
  Session   — the actual exploration (notes taken in real time)
  Debrief   — results: bugs found, areas covered, questions raised

Rules:
  • Time-box every session (45–90 min). Stop when the timer ends.
  • One charter per session. Broad charters produce shallow coverage.
  • Take notes AS you explore — what you did, what you saw, what surprised you.
  • Separate discovering bugs from investigating them. Log a ticket, move on.
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHARTERS — saucedemo.com
# Each charter is a focused mission for one exploratory session.
# ─────────────────────────────────────────────────────────────────────────────

CHARTERS = [
    {
        "id": "EX-001",
        "area": "Authentication",
        "mission": (
            "Explore the login form with unusual inputs and user accounts "
            "to discover gaps in input validation and error handling."
        ),
        "time_box": "45 min",
        "focus_questions": [
            "What happens with very long usernames (> 500 chars)?",
            "What happens when you paste HTML or script tags into the fields?",
            "Does pressing Enter submit the form?",
            "Can you log in with correct credentials immediately after a failed attempt?",
            "What does the error banner look like on a narrow mobile viewport?",
            "Does the browser auto-fill work, and does the form accept it?",
        ],
        "oracles": [
            "Error messages must be specific enough to guide the user",
            "Successful login always redirects to /inventory.html",
            "No session data is set after a failed login",
            "Input is sanitised — no script executes in the error message",
        ],
    },
    {
        "id": "EX-002",
        "area": "Shopping Cart",
        "mission": (
            "Explore the cart's state management: adding, removing, and "
            "navigating to verify the cart is consistent across page changes."
        ),
        "time_box": "45 min",
        "focus_questions": [
            "What is the maximum number of items you can add?",
            "Does the badge update immediately or after a delay?",
            "What happens if you open the cart in a second browser tab?",
            "Does reloading /inventory.html reset the cart?",
            "Can you add the same product twice? Does quantity increment?",
            "What happens if you navigate directly to /cart.html without adding anything?",
            "Does the cart persist across logout and re-login?",
        ],
        "oracles": [
            "Badge count always equals the number of distinct items added",
            "Cart state is server-side: refreshing should not clear it",
            "Removing an item updates the badge immediately",
            "Empty cart shows a helpful message, not a blank page",
        ],
    },
    {
        "id": "EX-003",
        "area": "Checkout Flow",
        "mission": (
            "Explore checkout step 1 (info) and step 2 (overview) "
            "to find validation gaps and calculation errors."
        ),
        "time_box": "60 min",
        "focus_questions": [
            "What characters are accepted in the First Name field?",
            "What happens with a postal code of '00000' or 'ABCDE'?",
            "Does pressing Back from step 2 preserve the info entered in step 1?",
            "Is the item total correct for multiple items of different prices?",
            "Does tax round correctly for totals that produce fractional cents?",
            "What happens if you refresh the page mid-checkout?",
            "Can you reach the confirmation page by navigating directly to /checkout-complete.html?",
        ],
        "oracles": [
            "Item total = sum of all item prices",
            "Tax = 8% of item total, rounded to 2 decimal places",
            "Grand total = item total + tax",
            "Completing checkout empties the cart",
            "Direct URL access to checkout steps without a session redirects to login",
        ],
    },
    {
        "id": "EX-004",
        "area": "Product Inventory — Sorting and Navigation",
        "mission": (
            "Explore how the sort dropdown and product navigation interact "
            "to find state-management issues across page transitions."
        ),
        "time_box": "30 min",
        "focus_questions": [
            "Does the sort option persist after clicking a product and coming back?",
            "Are prices always numeric and formatted as $X.XX?",
            "What happens if you rapidly switch sort options multiple times?",
            "Is the product order stable (same results each time) for the same sort key?",
            "Does the product image link and the name link both go to the same page?",
        ],
        "oracles": [
            "Sort order matches the selected option on every render",
            "All prices parse to a valid float greater than zero",
            "Back navigation returns to the same scroll position and sort state",
        ],
    },
    {
        "id": "EX-005",
        "area": "Security — Auth and Session",
        "mission": (
            "Probe the authentication and session model for common "
            "web security weaknesses."
        ),
        "time_box": "45 min",
        "focus_questions": [
            "Is the session cookie marked HttpOnly and Secure?",
            "Is the session invalidated server-side on logout?",
            "Can you replay a captured session cookie after logout?",
            "Does the browser Back button after logout show the inventory page?",
            "Is there a CSRF token on the login form?",
            "Are credentials transmitted over HTTPS?",
            "Can you access /inventory.html without a valid session?",
        ],
        "oracles": [
            "Session cookie: HttpOnly=true, Secure=true, SameSite=Strict or Lax",
            "After logout, GET /inventory.html returns 302 → /",
            "Credentials sent only over HTTPS (no HTTP fallback)",
            "No sensitive data (passwords, tokens) in URL parameters",
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# SESSION NOTE TEMPLATE — filled in during and after the session
# ─────────────────────────────────────────────────────────────────────────────

SESSION_NOTE_TEMPLATE = {
    "charter_id":    "EX-NNN",
    "tester":        "Your name",
    "date":          "YYYY-MM-DD",
    "duration_min":  45,
    "environment":   "Chrome 124 / macOS 15.4 / saucedemo.com",
    "notes": [
        "HH:MM — action taken, observation made",
        "HH:MM — found something unexpected (log as bug if confirmed)",
    ],
    "bugs_found":    ["BUG-NNN — one-line title"],
    "questions":     ["Question to ask the developer or PO"],
    "areas_covered": ["login form inputs", "error messages", "session cookies"],
    "areas_missed":  ["password reset flow — out of scope for this session"],
    "coverage_pct":  75,
}

# ─────────────────────────────────────────────────────────────────────────────
# COMPLETED SESSION EXAMPLE — EX-001 (Authentication)
# ─────────────────────────────────────────────────────────────────────────────

COMPLETED_SESSION_EX001 = {
    "charter_id":   "EX-001",
    "tester":       "Amiel",
    "date":         "2026-05-09",
    "duration_min": 43,
    "environment":  "Chrome 124 / macOS 15.4 / https://www.saucedemo.com",
    "notes": [
        "10:02 — Opened login page. Auto-fill offered saved credentials. Accepted — login succeeded normally.",
        "10:05 — Entered 500-char username. Form accepted it; submitted. Standard 'do not match' error shown. No crash.",
        "10:09 — Entered '<script>alert(1)</script>' as username. Login failed. Error message showed literal string — no XSS.",
        "10:13 — Pressed Enter in the Password field without clicking the button. Form submitted correctly.",
        "10:17 — Failed login with wrong password, then immediately retried with correct credentials. Login succeeded.",
        "10:22 — Tested locked_out_user. Error message: 'Epic sadface: Sorry, this user has been locked out.'",
        "10:25 — Noticed error message prefix 'Epic sadface:' is informal. Logging as BUG-001 (Minor).",
        "10:30 — Opened DevTools → Application → Cookies. After failed login: no session cookie set. Correct.",
        "10:35 — After successful login: cookie 'session-username' present. NOT marked HttpOnly. Logging as BUG-006.",
        "10:40 — Checked cookie is absent after logout. Correct.",
        "10:43 — Session ended.",
    ],
    "bugs_found": [
        "BUG-001 — Auth: locked_out_user error message prefix is informal ('Epic sadface:')",
        "BUG-006 — Auth: session cookie is not marked HttpOnly — accessible via document.cookie",
    ],
    "questions": [
        "Is the 'Epic sadface:' prefix intentional copy or a developer joke left in production?",
        "Is setting HttpOnly on the session cookie in scope for this sprint?",
    ],
    "areas_covered": [
        "Auto-fill interaction",
        "Very long username input",
        "XSS payload in username",
        "Enter key submission",
        "Retry after failed login",
        "Locked-out user error message",
        "Cookie state after failed login",
        "Cookie state after successful login",
        "Cookie state after logout",
    ],
    "areas_missed": [
        "Mobile viewport error message layout",
        "password_glitch_user login speed",
    ],
    "coverage_pct": 80,
}

# ─────────────────────────────────────────────────────────────────────────────
# HEURISTICS REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

GOLDILOCKS_HEURISTIC = {
    "Too small":  "Empty string, zero, null, single character",
    "Just right": "Typical valid value",
    "Too big":    "Max length + 1, integer overflow, huge file",
}

CRUD_HEURISTIC = {
    "Create": "Can you create a resource? Does it appear correctly?",
    "Read":   "Can you read it back? Is the data accurate?",
    "Update": "Can you change it? Are changes persisted correctly?",
    "Delete": "Can you remove it? Is it truly gone? Can you undo?",
}

CONSISTENCY_ORACLE = [
    "Does the UI match the API response?",
    "Does the confirmation page match what was in the cart?",
    "Does the cart badge count match the number of items on the cart page?",
    "Does the error message match the actual validation rule?",
]


def print_charter(charter: dict) -> None:
    print(f"\n{'─' * 60}")
    print(f"[{charter['id']}] {charter['area']}")
    print(f"Mission:  {charter['mission']}")
    print(f"Time box: {charter['time_box']}")
    print("Focus questions:")
    for q in charter["focus_questions"]:
        print(f"  ? {q}")
    print("Oracles:")
    for o in charter["oracles"]:
        print(f"  ✓ {o}")


if __name__ == "__main__":
    print(f"=== {len(CHARTERS)} Exploratory Charters for saucedemo.com ===")
    for charter in CHARTERS:
        print_charter(charter)

    print(f"\n=== Completed Session: {COMPLETED_SESSION_EX001['charter_id']} ===")
    print(f"Tester: {COMPLETED_SESSION_EX001['tester']}  "
          f"Date: {COMPLETED_SESSION_EX001['date']}  "
          f"Duration: {COMPLETED_SESSION_EX001['duration_min']} min")
    print(f"Coverage: {COMPLETED_SESSION_EX001['coverage_pct']}%")
    print("Bugs found:")
    for bug in COMPLETED_SESSION_EX001["bugs_found"]:
        print(f"  [{bug}]")
    print("Open questions:")
    for q in COMPLETED_SESSION_EX001["questions"]:
        print(f"  ? {q}")
