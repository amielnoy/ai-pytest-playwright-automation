"""
Session 2 — QA in the AI Era (Claude / Codex / Gemini)
Key concepts: prompt engineering patterns, AI output validation, and prompt roles.
"""

# ── Four prompting patterns for test generation ────────────────────────────────
PATTERNS = {
    "zero-shot":       "Give the task with no examples — fastest, least structured output.",
    "few-shot":        "Provide 1-2 example inputs+outputs — guides format and depth.",
    "chain-of-thought":"Ask the model to reason step by step before writing cases.",
    "role+constraint": "Assign a role (senior QA) + hard constraints (5 cases, 1 negative).",
}

# ── Prompt anatomy: the six components ────────────────────────────────────────
PROMPT_COMPONENTS = [
    "Role      — who the model is ('You are a senior SDET')",
    "Task      — what to do ('Generate test cases for…')",
    "Context   — the user story / spec / code to analyse",
    "Format    — output schema (JSON array, Markdown table, pytest file…)",
    "Constraints — minimum counts, required types, no hallucinations",
    "Examples  — (few-shot only) one or two reference input/output pairs",
]

# ── AI output quality checklist ────────────────────────────────────────────────
OUTPUT_CHECKS = {
    "Coverage":    "At least one positive, negative, and edge-case test present?",
    "Atomicity":   "Each step is a single action — no compound steps?",
    "Specificity": "Expected result is concrete and verifiable — not 'it works'?",
    "Duplicates":  "No two test cases have identical expected results?",
    "Scope":       "No assumptions outside the story (no invented endpoints)?",
}

# ── When NOT to trust AI output as-is ─────────────────────────────────────────
HALLUCINATION_RISKS = [
    "Endpoint paths that do not exist in the spec",
    "Field names invented from similar-sounding APIs",
    "Business rules contradicted by acceptance criteria",
    "Security tests that only test the obvious (SQLi but not IDOR)",
]

if __name__ == "__main__":
    print("Prompt patterns:")
    for name, desc in PATTERNS.items():
        print(f"  {name:<20} {desc}")
    print("\nOutput quality checks:")
    for name, check in OUTPUT_CHECKS.items():
        print(f"  {name:<14} {check}")
