"""
Session 2 — QA in the AI Era (Claude / Codex / Gemini)
Prompt templates for generating test cases from user stories using LLMs.
"""

import json

PROMPT_TEMPLATE = """You are a senior QA engineer. Generate test cases for the user story below.

OUTPUT FORMAT (strict):
Return a JSON array. Each item: {{id, title, type, priority, preconditions, steps, expected}}.
type in {{positive, negative, edge_case, security}}.
priority in {{high, medium, low}}.

CONSTRAINTS:
- 5 test cases minimum
- At least 1 positive, 1 negative, 1 edge_case
- Steps must be atomic (one action per step)
- No assumptions outside the user story

USER STORY:
{user_story}
"""

SAMPLE_USER_STORY = (
    "As a customer, I want to apply a discount coupon at checkout so I can save money. "
    "Acceptance: a coupon code field appears at checkout. Valid codes apply a discount. "
    "Invalid codes show an error. One coupon per order."
)

SAMPLE_OUTPUT = [
    {
        "id": "TC-COUPON-001",
        "title": "Valid coupon applies correct discount",
        "type": "positive",
        "priority": "high",
        "preconditions": ["Cart contains items totaling $100", "Coupon SAVE10 is valid for 10% off"],
        "steps": ["Navigate to checkout", "Enter SAVE10 in coupon field", "Click Apply"],
        "expected": "Total drops from $100 to $90, success message shown",
    },
    {
        "id": "TC-COUPON-002",
        "title": "Invalid coupon shows error",
        "type": "negative",
        "priority": "high",
        "preconditions": ["Cart contains any item"],
        "steps": ["Navigate to checkout", "Enter INVALID123 in coupon field", "Click Apply"],
        "expected": "Error 'Invalid coupon code' appears, total unchanged",
    },
    {
        "id": "TC-COUPON-003",
        "title": "Cannot apply two coupons in same order",
        "type": "edge_case",
        "priority": "medium",
        "preconditions": ["Cart contains item", "Coupon SAVE10 already applied"],
        "steps": ["Enter SAVE20 in coupon field", "Click Apply"],
        "expected": "Error 'Only one coupon per order' appears, SAVE10 still active",
    },
    {
        "id": "TC-COUPON-004",
        "title": "Expired coupon rejected",
        "type": "negative",
        "priority": "medium",
        "preconditions": ["Coupon EXPIRED2023 exists with past expiry"],
        "steps": ["Enter EXPIRED2023 in coupon field", "Click Apply"],
        "expected": "Error 'Coupon expired' shown, total unchanged",
    },
    {
        "id": "TC-COUPON-005",
        "title": "SQL injection in coupon field handled safely",
        "type": "security",
        "priority": "high",
        "preconditions": ["Cart contains item"],
        "steps": ["Enter \"' OR 1=1 --\" in coupon field", "Click Apply"],
        "expected": "Standard 'invalid coupon' error, no DB error exposed, no abnormal discount",
    },
]


API_PROMPT_TEMPLATE = """You are a senior QA engineer specializing in API testing.
Generate API test cases for the endpoint specification below.

OUTPUT FORMAT (strict):
Return a JSON array. Each item: {{id, title, method, endpoint, request_body, expected_status, expected_response_fields, type}}.
type in {{happy_path, validation, auth, rate_limit, idempotency}}.

CONSTRAINTS:
- At least 1 happy path, 1 auth failure, 1 validation error, 1 edge case
- request_body must be a JSON object (or null for GET)
- Include boundary values for numeric fields

ENDPOINT SPEC:
{spec}
"""

CHAIN_OF_THOUGHT_TEMPLATE = """You are a senior QA engineer. Think step by step before writing test cases.

STEP 1 — Identify actors (who uses this feature?)
STEP 2 — List happy paths (what should always work?)
STEP 3 — List failure modes (what can go wrong?)
STEP 4 — List edge cases (empty, max, boundary, concurrent)
STEP 5 — List security concerns (injection, auth bypass, data leakage)

Write your reasoning for each step, then output the final JSON array.

USER STORY:
{user_story}
"""

FEW_SHOT_TEMPLATE = """You are a senior QA engineer. Here are two example test cases in the required format:

EXAMPLE:
User story: "User can change their password from account settings"
Output:
[
  {{
    "id": "TC-EX-001",
    "title": "Change password with valid current password",
    "type": "positive",
    "priority": "high",
    "steps": ["Navigate to account settings", "Enter current password", "Enter new password", "Click Save"],
    "expected": "Success message shown, user can log in with new password"
  }},
  {{
    "id": "TC-EX-002",
    "title": "New password same as current password rejected",
    "type": "edge_case",
    "priority": "medium",
    "steps": ["Enter current password in both fields", "Click Save"],
    "expected": "Error: new password must differ from current"
  }}
]

Now generate 5 test cases in the same format for this user story:
{user_story}
"""

SAMPLE_API_SPEC = (
    "POST /api/v1/orders — Create a new order. "
    "Body: {{product_id: int, quantity: int (1-99), shipping_address: string}}. "
    "Auth: Bearer token required. "
    "Returns 201 with order_id on success, 400 on invalid input, 401 on bad token."
)

SAMPLE_API_OUTPUT = [
    {
        "id": "TC-ORDER-001",
        "title": "Create order with valid product and quantity",
        "method": "POST",
        "endpoint": "/api/v1/orders",
        "request_body": {"product_id": 42, "quantity": 3, "shipping_address": "123 Main St"},
        "expected_status": 201,
        "expected_response_fields": ["order_id"],
        "type": "happy_path",
    },
    {
        "id": "TC-ORDER-002",
        "title": "Missing Bearer token returns 401",
        "method": "POST",
        "endpoint": "/api/v1/orders",
        "request_body": {"product_id": 42, "quantity": 1, "shipping_address": "123 Main St"},
        "expected_status": 401,
        "expected_response_fields": ["error"],
        "type": "auth",
    },
    {
        "id": "TC-ORDER-003",
        "title": "Quantity 0 returns 400",
        "method": "POST",
        "endpoint": "/api/v1/orders",
        "request_body": {"product_id": 42, "quantity": 0, "shipping_address": "123 Main St"},
        "expected_status": 400,
        "expected_response_fields": ["error"],
        "type": "validation",
    },
    {
        "id": "TC-ORDER-004",
        "title": "Quantity at max boundary (99) accepted",
        "method": "POST",
        "endpoint": "/api/v1/orders",
        "request_body": {"product_id": 42, "quantity": 99, "shipping_address": "123 Main St"},
        "expected_status": 201,
        "expected_response_fields": ["order_id"],
        "type": "validation",
    },
    {
        "id": "TC-ORDER-005",
        "title": "Quantity over max (100) rejected",
        "method": "POST",
        "endpoint": "/api/v1/orders",
        "request_body": {"product_id": 42, "quantity": 100, "shipping_address": "123 Main St"},
        "expected_status": 400,
        "expected_response_fields": ["error"],
        "type": "validation",
    },
]


def build_prompt(user_story: str) -> str:
    return PROMPT_TEMPLATE.format(user_story=user_story)


def build_api_prompt(spec: str) -> str:
    return API_PROMPT_TEMPLATE.format(spec=spec)


def build_chain_of_thought_prompt(user_story: str) -> str:
    return CHAIN_OF_THOUGHT_TEMPLATE.format(user_story=user_story)


def build_few_shot_prompt(user_story: str) -> str:
    return FEW_SHOT_TEMPLATE.format(user_story=user_story)


def classify_ai_output(test_cases: list[dict]) -> dict:
    """Classify AI-generated test cases for quality metrics."""
    metrics = {
        "total": len(test_cases),
        "valid": 0,
        "duplicates": 0,
        "hallucinations": 0,
        "real_edge_cases": 0,
    }
    seen_expected = set()
    for tc in test_cases:
        expected = tc.get("expected", "")
        if expected in seen_expected:
            metrics["duplicates"] += 1
        else:
            seen_expected.add(expected)
            metrics["valid"] += 1
        if tc.get("type") == "edge_case":
            metrics["real_edge_cases"] += 1
    return metrics


if __name__ == "__main__":
    print("=== Basic prompt ===")
    print(build_prompt(SAMPLE_USER_STORY))
    print("\n=== API prompt ===")
    print(build_api_prompt(SAMPLE_API_SPEC))
    print("\n=== Chain-of-thought prompt ===")
    print(build_chain_of_thought_prompt(SAMPLE_USER_STORY))
    print("\n=== Few-shot prompt ===")
    print(build_few_shot_prompt(SAMPLE_USER_STORY))
    print("\nUI sample output (quality metrics):")
    print(classify_ai_output(SAMPLE_OUTPUT))
    print("\nAPI sample output:")
    print(json.dumps(SAMPLE_API_OUTPUT, indent=2))
