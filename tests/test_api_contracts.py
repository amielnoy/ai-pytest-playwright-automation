"""
API & Contract Tests
--------------------
Verify that the OpenCart HTTP endpoints the UI tests depend on behave
correctly in isolation — no browser involved.

Each test owns its own requests.Session (fresh OCSESSID) so they run
fully in parallel without any shared server-side state.
"""
import re
import uuid

import allure
import pytest
import requests

from utils.data_loader import get_config, get_test_data
from utils.price_parser import parse_price

# ---------------------------------------------------------------------------
# Shared session factory — each call returns a brand-new isolated session
# ---------------------------------------------------------------------------

@pytest.fixture
def api_base_url() -> str:
    return get_config()["base_url"]


@pytest.fixture
def session(api_base_url: str) -> requests.Session:
    """Fresh HTTP session per test — own OCSESSID, no shared cart state."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (contract-test/1.0)",
        "X-Requested-With": "XMLHttpRequest",
    })
    # Establish a session cookie by visiting the home page
    s.get(api_base_url, timeout=15)
    return s


# ---------------------------------------------------------------------------
# Contract: Search endpoint
# ---------------------------------------------------------------------------

@allure.feature("API Contracts")
@allure.story("Search endpoint")
@pytest.mark.api
class TestSearchContract:

    @allure.title("Search returns 200 and non-empty HTML for a known query")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_200(self, session: requests.Session, api_base_url: str):
        with allure.step("GET search results for 'MacBook'"):
            resp = session.get(
                f"{api_base_url}/index.php?route=product/search&search=MacBook",
                timeout=15,
            )

        with allure.step("Assert HTTP 200"):
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        with allure.step("Assert response contains product cards"):
            assert 'class="product-thumb"' in resp.text, (
                "Search response contains no product cards"
            )

    @allure.title("Search results contain product names and prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_response_has_names_and_prices(
        self, session: requests.Session, api_base_url: str
    ):
        resp = session.get(
            f"{api_base_url}/index.php?route=product/search&search=MacBook",
            timeout=15,
        )
        html = resp.text

        with allure.step("Assert at least one product name is present"):
            names = re.findall(r"<h4>\s*<a[^>]*>([^<]+)</a>", html)
            assert names, "No product names found in search response"

        with allure.step("Assert at least one parseable price is present"):
            raw_prices = re.findall(r'class="price">(.*?)</p>', html, re.DOTALL)
            prices = [parse_price(re.sub(r"<[^>]+>", "", p)) for p in raw_prices]
            valid = [p for p in prices if p is not None]
            assert valid, "No parseable prices found in search response"

    @allure.title("Search for non-existent product returns no product cards")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results_contract(self, session: requests.Session, api_base_url: str):
        resp = session.get(
            f"{api_base_url}/index.php?route=product/search&search=xyznonexistent{uuid.uuid4().hex[:6]}",
            timeout=15,
        )
        assert resp.status_code == 200
        assert 'class="product-thumb"' not in resp.text, (
            "Expected no product cards for a nonsense query"
        )

    @allure.title("Search result product IDs are parseable integers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_ids_are_integers(
        self, session: requests.Session, api_base_url: str
    ):
        resp = session.get(
            f"{api_base_url}/index.php?route=product/search&search=Apple",
            timeout=15,
        )
        pids = re.findall(r"cart\.add\('(\d+)'", resp.text)
        assert pids, "No product IDs found via cart.add() pattern"
        for pid in pids:
            assert pid.isdigit(), f"Product ID '{pid}' is not a digit string"


# ---------------------------------------------------------------------------
# Contract: Cart add endpoint
# ---------------------------------------------------------------------------

@allure.feature("API Contracts")
@allure.story("Cart add endpoint")
@pytest.mark.api
class TestCartAddContract:

    @allure.title("POST to cart/add returns 200 and issues an OCSESSID cookie")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_add_returns_200_and_sets_session(
        self, session: requests.Session, api_base_url: str
    ):
        pid = self._first_product_id(session, api_base_url, "MacBook")

        with allure.step(f"POST product_id={pid} to cart"):
            resp = session.post(
                f"{api_base_url}/index.php?route=checkout/cart/add",
                data={"product_id": pid, "quantity": "1"},
                timeout=15,
            )

        with allure.step("Assert HTTP 200"):
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        with allure.step("Assert OCSESSID cookie is present"):
            assert "OCSESSID" in session.cookies, "No OCSESSID cookie after cart add"

    @allure.title("Cart page reflects the product added via API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_page_reflects_api_add(
        self, session: requests.Session, api_base_url: str
    ):
        pid = self._first_product_id(session, api_base_url, "MacBook")

        with allure.step(f"Add product {pid} via API"):
            session.post(
                f"{api_base_url}/index.php?route=checkout/cart/add",
                data={"product_id": pid, "quantity": "1"},
                timeout=15,
            )

        with allure.step("Fetch cart page with the same session"):
            cart_resp = session.get(
                f"{api_base_url}/index.php?route=checkout/cart",
                timeout=15,
            )

        with allure.step("Assert cart is not empty"):
            assert "Your shopping cart is empty" not in cart_resp.text, (
                "Cart page shows empty after API add"
            )

        with allure.step("Assert cart page contains a parseable total"):
            total_match = re.search(
                r"Total:.*?<td[^>]*>(.*?)</td>", cart_resp.text, re.DOTALL
            )
            assert total_match, "Could not find Total row in cart page"
            total = parse_price(re.sub(r"<[^>]+>", "", total_match.group(1)))
            assert total is not None and total > 0, (
                f"Cart total could not be parsed or is zero: {total_match.group(1)!r}"
            )

    @allure.title("Two concurrent sessions have independent carts")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sessions_are_isolated(self, api_base_url: str):
        """Each session gets its own OCSESSID → no cart bleed-through."""
        headers = {
            "User-Agent": "Mozilla/5.0 (contract-test/1.0)",
            "X-Requested-With": "XMLHttpRequest",
        }

        session_a = requests.Session()
        session_b = requests.Session()
        session_a.headers.update(headers)
        session_b.headers.update(headers)

        # Discover a product ID
        resp = session_a.get(
            f"{api_base_url}/index.php?route=product/search&search=MacBook",
            timeout=15,
        )
        pids = re.findall(r"cart\.add\('(\d+)'", resp.text)
        assert pids, "No products found to test isolation"
        pid = pids[0]

        with allure.step("Add product to session A only"):
            session_a.post(
                f"{api_base_url}/index.php?route=checkout/cart/add",
                data={"product_id": pid, "quantity": "1"},
                timeout=15,
            )

        with allure.step("Check session B cart is still empty"):
            # Session B hasn't visited the site yet — force a session
            session_b.get(api_base_url, timeout=15)
            cart_b = session_b.get(
                f"{api_base_url}/index.php?route=checkout/cart",
                timeout=15,
            )
            assert "Your shopping cart is empty" in cart_b.text, (
                "Session B cart is not empty — sessions are leaking state"
            )

        with allure.step("Assert session A and B have different OCSESSID values"):
            sid_a = session_a.cookies.get("OCSESSID")
            sid_b = session_b.cookies.get("OCSESSID")
            assert sid_a and sid_b, "One or both sessions have no OCSESSID"
            assert sid_a != sid_b, (
                f"Sessions share the same OCSESSID ({sid_a}) — no isolation"
            )

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _first_product_id(session: requests.Session, base_url: str, query: str) -> str:
        resp = session.get(
            f"{base_url}/index.php?route=product/search&search={query}",
            timeout=15,
        )
        pids = re.findall(r"cart\.add\('(\d+)'", resp.text)
        assert pids, f"No products found for query '{query}'"
        return pids[0]


# ---------------------------------------------------------------------------
# Contract: Registration page structure
# ---------------------------------------------------------------------------

@allure.feature("API Contracts")
@allure.story("Registration page structure")
@pytest.mark.api
class TestRegistrationPageContract:

    @allure.title("Registration page returns 200 and contains all required fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_page_has_required_fields(
        self, session: requests.Session, api_base_url: str
    ):
        resp = session.get(
            f"{api_base_url}/index.php?route=account/register",
            timeout=15,
        )

        with allure.step("Assert HTTP 200"):
            assert resp.status_code == 200

        required_fields = [
            "input-firstname",
            "input-lastname",
            "input-email",
            "input-telephone",
            "input-password",
            "input-confirm",
        ]
        with allure.step("Assert all required input IDs are present in the HTML"):
            missing = [f for f in required_fields if f not in resp.text]
            assert not missing, f"Registration page missing fields: {missing}"

    @allure.title("Registration page contains privacy policy checkbox")
    @allure.severity(allure.severity_level.NORMAL)
    def test_registration_page_has_privacy_checkbox(
        self, session: requests.Session, api_base_url: str
    ):
        resp = session.get(
            f"{api_base_url}/index.php?route=account/register",
            timeout=15,
        )
        assert 'name="agree"' in resp.text, (
            "Privacy policy checkbox not found on registration page"
        )


# ---------------------------------------------------------------------------
# Contract: Price data integrity
# ---------------------------------------------------------------------------

@allure.feature("API Contracts")
@allure.story("Price data integrity")
@pytest.mark.api
class TestPriceContract:

    @allure.title("All prices in search results are positive numbers")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_search_prices_are_positive(
        self, session: requests.Session, api_base_url: str
    ):
        resp = session.get(
            f"{api_base_url}/index.php?route=product/search&search=MacBook",
            timeout=15,
        )
        raw_blocks = re.findall(r'class="price">(.*?)</p>', resp.text, re.DOTALL)
        prices = [
            parse_price(re.sub(r"<[^>]+>", "", block)) for block in raw_blocks
        ]
        parsed = [p for p in prices if p is not None]

        with allure.step(f"Assert all {len(parsed)} prices are > 0"):
            non_positive = [p for p in parsed if p <= 0]
            assert not non_positive, f"Non-positive prices found: {non_positive}"

    @allure.title("Cart total matches sum of individual item prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_matches_item_sum(
        self, session: requests.Session, api_base_url: str
    ):
        data = get_test_data("search")

        # Add one product via API
        resp = session.get(
            f"{api_base_url}/index.php?route=product/search&search={data['query']}",
            timeout=15,
        )
        pids = re.findall(r"cart\.add\('(\d+)'", resp.text)
        assert pids, "No products found"

        session.post(
            f"{api_base_url}/index.php?route=checkout/cart/add",
            data={"product_id": pids[0], "quantity": "1"},
            timeout=15,
        )

        with allure.step("Fetch cart page and parse individual row prices and total"):
            cart_resp = session.get(
                f"{api_base_url}/index.php?route=checkout/cart", timeout=15
            )
            html = cart_resp.text

        # Product rows appear before the first totals section — split there to
        # avoid picking up Sub-Total / Eco Tax / VAT value cells.
        product_section = html.split("<strong>Sub-Total")[0]
        row_price_strs = re.findall(
            r'<td class="text-right">\s*(\$[\d,]+\.?\d*)\s*</td>',
            product_section,
        )
        row_prices = [parse_price(s) for s in row_price_strs]
        row_sum = sum(p for p in row_prices if p is not None)

        # Grand total — match <strong>Total:</strong> exactly to skip Sub-Total
        total_match = re.search(
            r"<strong>Total:?</strong>\s*</td>\s*<td[^>]*>(.*?)</td>",
            html, re.DOTALL,
        )
        assert total_match, "Total row not found in cart HTML"
        grand_total = parse_price(re.sub(r"<[^>]+>", "", total_match.group(1)))
        assert grand_total is not None and grand_total > 0

        with allure.step(
            f"Assert row sum ${row_sum:.2f} approximately equals grand total ${grand_total:.2f}"
        ):
            assert abs(row_sum - grand_total) < 1.0, (
                f"Row sum ${row_sum:.2f} diverges from grand total ${grand_total:.2f}"
            )
