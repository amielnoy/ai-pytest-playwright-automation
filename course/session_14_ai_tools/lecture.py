"""
Session 14 — Building AI Tools for QA
Key concepts: test generation CLI, self-healing selectors, review automation.
"""

# ── Three AI QA tools in this session ─────────────────────────────────────────
TOOLS = {
    "cli.py test":    "Generate a pytest + Playwright file from a feature description.",
    "cli.py review":  "Audit an existing test file for anti-patterns and report findings.",
    "cli.py batch":   "Generate test files for every feature line in a text file.",
    "self_healing.py":"Try a locator; if it times out, ask Claude for a replacement.",
    "heal_report.py": "Run pytest, collect [self-heal] log lines, write a Markdown table.",
}

# ── Self-healing: how it works ─────────────────────────────────────────────────
# 1. Try page.locator(selector).wait_for(state="visible", timeout=2000)
# 2. On PlaywrightTimeout → send page HTML + selector description to Claude
# 3. Claude returns a new selector string → use it for this run
# 4. Log every heal: [self-heal] .old-class → [data-test="new-id"]
# Rule: heals are LOGGED, never silent — engineers must update Page Objects.

# ── Anti-patterns caught by cli.py review ─────────────────────────────────────
ANTI_PATTERNS = [
    "Inline selectors in test functions (violates POM)",
    "time.sleep() calls instead of expect() auto-wait",
    "Bare assert on DOM values instead of expect(locator).to_have_text()",
    "Hardcoded credentials or BASE_URL strings",
    "Shared mutable state across test functions",
    "Missing teardown for API sessions or browser contexts",
]

# ── Prompt design for test generation ─────────────────────────────────────────
# Must include:
#   • Role: "senior test automation engineer"
#   • Format: "Output ONLY Python code, no markdown fences"
#   • Locator rule: "use get_by_role, get_by_label, get_by_text"
#   • Assertion rule: "use expect(), never bare assert on DOM"
#   • Coverage minimum: "1 positive, 1 negative, 1 edge case"

if __name__ == "__main__":
    print("AI QA tools:")
    for name, desc in TOOLS.items():
        print(f"  {name:<22} {desc}")
    print("\nAnti-patterns the review tool catches:")
    for ap in ANTI_PATTERNS:
        print(f"  • {ap}")
