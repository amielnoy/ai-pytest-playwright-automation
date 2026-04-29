from fastapi.testclient import TestClient
import pytest

import server.app as app_module
from services.api.http_response_constants import (
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
    HTTP_OK,
)
from server.app import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_test_data_endpoint_returns_search_data():
    response = client.get("/automation/test-data/search")

    assert response.status_code == HTTP_OK
    assert response.json()["query"] == "MacBook"


def test_test_data_endpoint_returns_404_for_unknown_key():
    response = client.get("/automation/test-data/does-not-exist")

    assert response.status_code == HTTP_NOT_FOUND
    assert "Unknown test data key" in response.json()["detail"]


def test_allure_status_exposes_report_url():
    response = client.get("/reports/allure/status")

    assert response.status_code == HTTP_OK
    assert response.json()["report_url"] == "/reports/allure/view/index.html"


def test_allure_summary_returns_404_when_summary_missing(tmp_path, monkeypatch):
    missing_summary = tmp_path / "summary.json"
    monkeypatch.setattr(app_module, "ALLURE_SUMMARY_PATH", missing_summary)

    response = client.get("/reports/allure/summary")

    assert response.status_code == HTTP_NOT_FOUND
    assert "Allure summary not found" in response.json()["detail"]


def test_mock_cart_flow():
    client.delete("/mock/cart")

    search_response = client.get("/mock/products/search", params={"query": "MacBook"})
    assert search_response.status_code == HTTP_OK
    assert search_response.json()[0]["product_id"] == "43"

    add_response = client.post(
        "/mock/cart/add",
        json={"product_id": "43", "quantity": 2},
    )
    assert add_response.status_code == HTTP_OK
    assert add_response.json()["cart"]["total"] == 1204.0

    cart_response = client.get("/mock/cart")
    assert cart_response.status_code == HTTP_OK
    assert cart_response.json()["items"][0]["quantity"] == 2


@pytest.mark.parametrize(
    ("query", "expected_product_id", "expected_name", "expected_price"),
    [
        ("MacBook", "43", "MacBook", 602.0),
        ("iPhone", "40", "iPhone", 123.2),
    ],
)
def test_mock_product_search_returns_matching_products(
    query, expected_product_id, expected_name, expected_price
):
    response = client.get("/mock/products/search", params={"query": query})

    assert response.status_code == HTTP_OK
    products = response.json()
    assert products == [
        {
            "product_id": expected_product_id,
            "name": expected_name,
            "price": expected_price,
        }
    ]


@pytest.mark.parametrize(
    ("product_id", "quantity", "expected_total"),
    [
        ("43", 1, 602.0),
        ("40", 3, 369.6),
    ],
)
def test_mock_cart_add_calculates_total_from_quantity(
    product_id, quantity, expected_total
):
    client.delete("/mock/cart")

    response = client.post(
        "/mock/cart/add",
        json={"product_id": product_id, "quantity": quantity},
    )

    assert response.status_code == HTTP_OK
    cart = response.json()["cart"]
    assert cart["items"][0]["quantity"] == quantity
    assert cart["total"] == expected_total


def test_mock_cart_add_returns_404_for_unknown_product():
    response = client.post(
        "/mock/cart/add",
        json={"product_id": "unknown", "quantity": 1},
    )

    assert response.status_code == HTTP_NOT_FOUND
    assert response.json()["detail"] == "Product not found"


def test_run_pytest_rejects_unsafe_arguments():
    response = client.post("/runs/pytest", json={"args": ["-k", "smoke && rm -rf /"]})

    assert response.status_code == HTTP_BAD_REQUEST
    assert "Unsafe pytest arg" in response.json()["detail"]
