import pytest

from course.framework.api import (
    assert_product_contract,
    assert_required_fields,
    assert_status,
    build_search_path,
    normalize_query,
)


def test_assert_status_accepts_expected_status():
    assert_status(actual_status=200, expected_status=200)


def test_assert_status_fails_on_unexpected_status():
    with pytest.raises(AssertionError, match="Expected HTTP 200"):
        assert_status(actual_status=500, expected_status=200)


def test_required_fields_validate_presence_and_type():
    payload = {"product_id": 43, "name": "MacBook", "price": 602.0}

    assert_required_fields(
        payload,
        {"product_id": int, "name": str, "price": float},
    )


def test_required_fields_report_missing_fields():
    with pytest.raises(AssertionError, match="Missing required fields"):
        assert_required_fields({"name": "MacBook"}, {"product_id": int})


def test_product_contract_checks_business_meaning():
    product = {"product_id": 43, "name": "MacBook", "price": 602.0}

    assert_product_contract(product)


def test_product_contract_rejects_empty_name():
    product = {"product_id": 43, "name": "  ", "price": 602.0}

    with pytest.raises(AssertionError):
        assert_product_contract(product)


def test_search_path_normalizes_spaces_for_request_url():
    assert normalize_query(" Apple Cinema ") == "Apple+Cinema"
    assert build_search_path("Apple Cinema") == (
        "/index.php?route=product/search&search=Apple+Cinema"
    )
