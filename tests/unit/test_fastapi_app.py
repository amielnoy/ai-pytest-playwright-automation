from fastapi.testclient import TestClient

import server.app as app_module
from server.app import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_test_data_endpoint_returns_search_data():
    response = client.get("/automation/test-data/search")

    assert response.status_code == 200
    assert response.json()["query"] == "MacBook"


def test_test_data_endpoint_returns_404_for_unknown_key():
    response = client.get("/automation/test-data/does-not-exist")

    assert response.status_code == 404
    assert "Unknown test data key" in response.json()["detail"]


def test_allure_status_exposes_report_url():
    response = client.get("/reports/allure/status")

    assert response.status_code == 200
    assert response.json()["report_url"] == "/reports/allure/view/index.html"


def test_allure_summary_returns_404_when_summary_missing(tmp_path, monkeypatch):
    missing_summary = tmp_path / "summary.json"
    monkeypatch.setattr(app_module, "ALLURE_SUMMARY_PATH", missing_summary)

    response = client.get("/reports/allure/summary")

    assert response.status_code == 404
    assert "Allure summary not found" in response.json()["detail"]


def test_mock_cart_flow():
    client.delete("/mock/cart")

    search_response = client.get("/mock/products/search", params={"query": "MacBook"})
    assert search_response.status_code == 200
    assert search_response.json()[0]["product_id"] == "43"

    add_response = client.post(
        "/mock/cart/add",
        json={"product_id": "43", "quantity": 2},
    )
    assert add_response.status_code == 200
    assert add_response.json()["cart"]["total"] == 1204.0

    cart_response = client.get("/mock/cart")
    assert cart_response.status_code == 200
    assert cart_response.json()["items"][0]["quantity"] == 2


def test_mock_cart_add_returns_404_for_unknown_product():
    response = client.post(
        "/mock/cart/add",
        json={"product_id": "unknown", "quantity": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_run_pytest_rejects_unsafe_arguments():
    response = client.post("/runs/pytest", json={"args": ["-k", "smoke && rm -rf /"]})

    assert response.status_code == 400
    assert "Unsafe pytest arg" in response.json()["detail"]
