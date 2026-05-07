"""
Session 1 — Classic QA Foundations + Environment Setup
Structured test cases for the login feature of saucedemo.com.
"""

BASE_URL = "https://www.saucedemo.com"

TEST_CASES = [
    {
        "id": "TC-001",
        "title": "Successful Login with Valid Credentials",
        "priority": "High",
        "type": "Smoke",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            'Enter "standard_user" in Username field',
            'Enter "secret_sauce" in Password field',
            "Click Login button",
        ],
        "expected": "User is redirected to /inventory.html and sees the product list",
    },
    {
        "id": "TC-002",
        "title": "Login Fails with Locked-Out User",
        "priority": "High",
        "type": "Negative",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            'Enter "locked_out_user" in Username field',
            'Enter "secret_sauce" in Password field',
            "Click Login button",
        ],
        "expected": 'Error message "Sorry, this user has been locked out" appears, URL stays on login',
    },
    {
        "id": "TC-003",
        "title": "Empty Password Shows Validation Error",
        "priority": "Medium",
        "type": "Negative",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            'Enter "standard_user" in Username field',
            "Leave Password empty",
            "Click Login button",
        ],
        "expected": 'Error "Password is required" appears, no navigation occurs',
    },
    {
        "id": "TC-004",
        "title": "Empty Username Shows Validation Error",
        "priority": "Medium",
        "type": "Negative",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            "Leave Username empty",
            'Enter "secret_sauce" in Password field',
            "Click Login button",
        ],
        "expected": 'Error "Username is required" appears, no navigation occurs',
    },
    {
        "id": "TC-005",
        "title": "Login With Both Fields Empty",
        "priority": "Low",
        "type": "Edge Case",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            "Leave Username empty",
            "Leave Password empty",
            "Click Login button",
        ],
        "expected": 'Error "Username is required" appears (username validated first)',
    },
    {
        "id": "TC-006",
        "title": "Session Persists After Page Reload",
        "priority": "Medium",
        "type": "Functional",
        "precondition": f"User is logged in as standard_user at {BASE_URL}/inventory.html",
        "steps": [
            "Press F5 to reload the page",
        ],
        "expected": "User stays on /inventory.html, session cookie still valid",
    },
    {
        "id": "TC-007",
        "title": "Login Page Has No XSS Vulnerability in Error Message",
        "priority": "High",
        "type": "Security",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            'Enter "<script>alert(1)</script>" in Username field',
            'Enter "any" in Password field',
            "Click Login button",
        ],
        "expected": "Error message displays the string literally; no alert dialog fires",
    },
    {
        "id": "TC-008",
        "title": "Performance User Sees Product List Within 3 Seconds",
        "priority": "Medium",
        "type": "Performance",
        "precondition": f"User is on {BASE_URL}",
        "steps": [
            'Enter "performance_glitch_user" in Username field',
            'Enter "secret_sauce" in Password field',
            "Click Login button and start timer",
            "Stop timer when /inventory.html is fully loaded",
        ],
        "expected": "Page load time is under 3 000 ms (may be slow but must complete)",
    },
]


def print_test_cases():
    for tc in TEST_CASES:
        print(f"\n{tc['id']} | {tc['title']}")
        print(f"Priority: {tc['priority']} | Type: {tc['type']}")
        print(f"Precondition: {tc['precondition']}")
        print("Steps:")
        for i, step in enumerate(tc["steps"], 1):
            print(f"  {i}. {step}")
        print(f"Expected: {tc['expected']}")


if __name__ == "__main__":
    print_test_cases()
