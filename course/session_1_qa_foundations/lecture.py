"""
Session 1 — QA Foundations & Environment Setup
Key concepts: test case anatomy, defect lifecycle, priority, and test pyramid.
"""

# ── Test case anatomy ──────────────────────────────────────────────────────────
# Every test case has: ID | Title | Priority | Type | Precondition | Steps | Expected

PRIORITIES   = ["High", "Medium", "Low"]           # impact × likelihood
TEST_TYPES   = ["Smoke", "Functional", "Negative",
                "Edge Case", "Security", "Performance"]
DEFECT_LIFECYCLE = ["New", "Assigned", "In Progress", "Fixed", "Verified", "Closed"]

# ── Test pyramid ───────────────────────────────────────────────────────────────
# Unit (fast, many) → Integration (medium) → E2E / UI (slow, few)
TEST_PYRAMID = {
    "unit":        {"speed": "fast",   "cost": "low",    "count": "many"},
    "integration": {"speed": "medium", "cost": "medium", "count": "moderate"},
    "e2e":         {"speed": "slow",   "cost": "high",   "count": "few"},
}

# ── Equivalence partitioning example (login password field) ───────────────────
VALID_PARTITIONS   = ["correct_password"]
INVALID_PARTITIONS = ["empty", "wrong_password", "sql_injection", "xss_payload"]
BOUNDARY_VALUES    = ["", "a" * 8, "a" * 72, "a" * 73]  # min, common, max, over

# ── Quick-reference: when to write which test type ────────────────────────────
WHEN_TO_WRITE = {
    "Smoke":       "After every deploy — does the app start and the happy path work?",
    "Functional":  "For each acceptance criterion in the user story.",
    "Negative":    "For every input that should be rejected (empty, invalid, locked).",
    "Edge Case":   "Boundaries: min/max values, empty collections, concurrent actions.",
    "Security":    "Injection (SQLi, XSS), auth bypass, sensitive data in responses.",
    "Performance": "SLA breakers: page load > N ms, DB query > N ms under load.",
}

if __name__ == "__main__":
    for kind, rule in WHEN_TO_WRITE.items():
        print(f"{kind:<14} → {rule}")
