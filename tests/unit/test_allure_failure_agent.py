from agents.allure_failure_agent import (
    _classify_failure_heuristic,
    _extract_failure_context,
    _extract_json,
    _result_is_flaky,
)


def test_extract_failure_context_with_steps():
    raw = {
        "name": "Test failure",
        "fullName": "tests.example.TestSuite#test_example",
        "status": "failed",
        "statusDetails": {
            "message": "AssertionError: expected 1 but got 0",
            "trace": "Traceback (most recent call last):...",
        },
        "steps": [
            {
                "name": "Open page",
                "status": "passed",
                "statusDetails": {"message": "", "trace": ""},
            },
            {
                "name": "Check cart count",
                "status": "failed",
                "statusDetails": {
                    "message": "Locator expected to have count '1' Actual value: 0",
                    "trace": "...locator resolved to 0 elements...",
                },
            },
        ],
    }

    context = _extract_failure_context(raw)
    assert context["name"] == "Test failure"
    assert context["full_name"] == "tests.example.TestSuite#test_example"
    assert context["status"] == "failed"
    assert "locator expected to have count" in context["steps"][1]["message"]


def test_heuristic_classifies_dom_change():
    context = {
        "name": "DOM failure",
        "full_name": "tests.example#test_dom",
        "status": "failed",
        "message": "Locator expected to have count '1' Actual value: 0",
        "trace": "locator resolved to 0 elements",
        "steps": [],
        "labels": [],
        "attachments": [],
    }

    assert _classify_failure_heuristic(context) == "dom_change"


def test_heuristic_classifies_product_bug():
    context = {
        "name": "Product validation",
        "full_name": "tests.example#test_product",
        "status": "failed",
        "message": "AssertionError: expected total 100 but got 95",
        "trace": "",
        "steps": [],
        "labels": [],
        "attachments": [],
    }

    assert _classify_failure_heuristic(context) == "product_bug"


def test_heuristic_classifies_automation_bug_from_fixture():
    context = {
        "name": "Automation issue",
        "full_name": "tests.example#test_automation",
        "status": "failed",
        "message": "AttributeError: 'NoneType' object has no attribute 'click'",
        "trace": "",
        "steps": [],
        "labels": [],
        "attachments": [],
    }

    assert _classify_failure_heuristic(context) == "automation_bug"


def test_extract_json_reads_json_object():
    text = 'Here is the classification: {"category": "dom_change", "summary": "Locator issue", "confidence": "high"}'
    parsed = _extract_json(text)
    assert parsed == {
        "category": "dom_change",
        "summary": "Locator issue",
        "confidence": "high",
    }


def test_result_is_flaky_when_history_contains_pass_and_fail():
    raw_pass = {"historyId": "abc", "status": "passed", "statusDetails": {}}
    raw_fail = {"historyId": "abc", "status": "failed", "statusDetails": {}}
    history_map = {"abc": [raw_pass, raw_fail]}
    assert _result_is_flaky(raw_fail, history_map)


def test_result_is_flaky_when_status_details_marks_flaky():
    raw = {"historyId": "xyz", "status": "failed", "statusDetails": {"flaky": True}}
    history_map = {"xyz": [raw]}
    assert _result_is_flaky(raw, history_map)
