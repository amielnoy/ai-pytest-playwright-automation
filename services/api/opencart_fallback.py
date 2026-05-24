from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from html import escape
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, urlparse

from requests import Response
from requests.cookies import RequestsCookieJar


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: float


PRODUCTS = (
    Product("43", "MacBook", 602.0),
    Product("45", "MacBook Pro", 2000.0),
    Product("40", "iPhone", 123.2),
    Product("36", "iPod Nano", 122.0),
    Product("30", "Canon EOS 5D", 98.0),
    Product("28", "Samsung SyncMaster 941BW", 242.0),
)

# Shared cart state keyed by OCSESSID — used by both REST client and Playwright route handler
_CART_REGISTRY: dict[str, dict[str, int]] = {}


def get_session_cart(sid: str) -> dict[str, int]:
    return _CART_REGISTRY.get(sid, {})


def is_challenge_page(response: Response) -> bool:
    if not isinstance(response, Response):
        return False
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        return True
    text = response.text
    if "One moment, please" in text:
        return True
    # JS-obfuscation challenge: small page with no real OpenCart content.
    # Real OpenCart uses charset="UTF-8"; the challenge page uses charset="utf8".
    if 'charset="utf8"' in text and ("a0E" in text or "0x3e8" in text):
        return True
    return False


def ensure_session_cookie(cookies: RequestsCookieJar) -> str:
    sid = cookies.get("OCSESSID")
    if not sid:
        sid = uuid.uuid4().hex
        cookies.set("OCSESSID", sid, path="/")
    return sid


def search_products(query: str, sort: str = "", order: str = "ASC") -> list[Product]:
    normalized = query.casefold()
    results = [p for p in PRODUCTS if normalized and normalized in p.name.casefold()]
    if sort == "name":
        results = sorted(results, key=lambda p: p.name.casefold(), reverse=(order.upper() == "DESC"))
    return results


def product_by_id(product_id: str) -> Product | None:
    return next((p for p in PRODUCTS if p.product_id == product_id), None)


def response(
    body: str | bytes,
    *,
    status_code: int = HTTPStatus.OK,
    content_type: str = "text/html; charset=utf-8",
) -> Response:
    resp = Response()
    resp.status_code = int(status_code)
    resp._content = body if isinstance(body, bytes) else body.encode("utf-8")
    resp.headers["Content-Type"] = content_type
    return resp


def json_response(payload: Any) -> Response:
    return response(
        json.dumps(payload),
        content_type="application/json; charset=utf-8",
    )


# ---------------------------------------------------------------------------
# Shared nav + JavaScript
# ---------------------------------------------------------------------------

_NAV_JS = """<script>
function _toggleAccountMenu() {
  var d = document.getElementById('account-dropdown');
  if (d) d.style.display = (d.style.display === 'block') ? 'none' : 'block';
}
function _doSearch() {
  var q = document.getElementById('input-search-nav');
  if (q) window.location.href = 'index.php?route=product/search&search=' + encodeURIComponent(q.value);
}
function _sortResults(sel) {
  var params = new URLSearchParams(window.location.search);
  var val = sel.value;
  var dash = val.lastIndexOf('-');
  var sortKey = val.substring(0, dash);
  var orderKey = val.substring(dash + 1);
  params.set('sort', sortKey === 'pd.name' ? 'name' : sortKey);
  params.set('order', orderKey || 'ASC');
  window.location.href = window.location.pathname + '?' + params.toString();
}
var cart = {
  add: function(productId, qty) {
    fetch('index.php?route=checkout/cart/add', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({product_id: String(productId), quantity: qty || 1})
    }).then(function(r) { return r.json(); }).then(function(j) {
      var btn = document.getElementById('cart-btn');
      if (btn && j.total) btn.textContent = j.total;
      var container = document.getElementById('alert-container');
      if (!container) container = document.body;
      var a = document.createElement('div');
      a.className = 'alert alert-success';
      a.innerHTML = (j.success || 'Added to cart.') +
        ' <button class="close" data-dismiss="alert" onclick="this.parentNode.remove()">&times;</button>';
      container.insertBefore(a, container.firstChild);
    }).catch(function(e) { console.error('cart.add error', e); });
  }
};
</script>"""


def _nav_html() -> str:
    return """<div id="alert-container"></div>
<nav id="top">
  <button id="currency-btn" type="button">Currency</button>
  <div id="search">
    <input id="input-search-nav" placeholder="Search" type="text" name="search">
    <button type="button" onclick="_doSearch()">Search</button>
  </div>
  <button id="cart-btn" type="button">0 item(s) - $0.00</button>
  <a href="#" id="account-menu-link" onclick="_toggleAccountMenu(); return false;">My Account</a>
  <div id="account-dropdown" style="display:none; position:absolute; background:#fff; border:1px solid #ccc; z-index:999; padding:4px 8px;">
    <a href="index.php?route=account/login">Login</a><br>
    <a href="index.php?route=account/register">Register</a><br>
    <a href="index.php?route=account/logout">Logout</a>
  </div>
</nav>"""


# ---------------------------------------------------------------------------
# Page HTML generators
# ---------------------------------------------------------------------------

def home_html() -> str:
    featured = "\n".join(_product_card(p) for p in PRODUCTS[:4])
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Your Store</title></head>
<body>
{_nav_html()}
<div class="row">{featured}</div>
{_NAV_JS}
</body>
</html>"""


def search_html(query: str, sort: str = "", order: str = "ASC") -> str:
    products = search_products(query, sort=sort, order=order)
    if products:
        cards = "\n".join(_product_card(p) for p in products)
        results_block = f'<div class="row" id="product-list">{cards}</div>'
    else:
        results_block = (
            '<p id="no-results">There is no product that matches the search criteria.</p>'
        )

    sel_asc = " selected" if sort == "name" and order.upper() == "ASC" else ""
    sel_desc = " selected" if sort == "name" and order.upper() == "DESC" else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Search - {escape(query)}</title></head>
<body>
{_nav_html()}
<div id="content">
  <h1>Search</h1>
  <div class="well">
    <label for="input-search">Search Criteria</label>
    <input id="input-search" type="text" name="search" value="{escape(query)}">
    <button type="button" id="button-search"
            onclick="window.location.href='index.php?route=product/search&amp;search='+encodeURIComponent(document.getElementById('input-search').value)">Search</button>
  </div>
  <div class="row">
    <div class="col-sm-6 text-right">
      <label for="input-sort">Sort By:</label>
      <select id="input-sort" name="sort_order" onchange="_sortResults(this)">
        <option value="p.sort_order-ASC">Default</option>
        <option value="pd.name-ASC"{sel_asc}>Name (A - Z)</option>
        <option value="pd.name-DESC"{sel_desc}>Name (Z - A)</option>
        <option value="p.price-ASC">Price (Low &gt; High)</option>
        <option value="p.price-DESC">Price (High &gt; Low)</option>
      </select>
      <label for="input-limit">Show:</label>
      <select id="input-limit" name="limit">
        <option value="15" selected>15</option>
        <option value="25">25</option>
        <option value="50">50</option>
        <option value="75">75</option>
        <option value="100">100</option>
      </select>
    </div>
  </div>
  <div class="row">
    <button id="list-view" type="button">List</button>
    <button id="grid-view" type="button">Grid</button>
  </div>
  {results_block}
</div>
{_NAV_JS}
</body>
</html>"""


def login_html(warning: str | None = None, action: str = "index.php?route=account/login") -> str:
    warning_html = (
        f'<div class="alert alert-danger">Warning: {escape(warning)}</div>' if warning else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Account Login</title></head>
<body>
{_nav_html()}
{warning_html}
<h1>Returning Customer</h1>
<form action="{escape(action, quote=True)}" method="post">
  <label for="input-email">E-Mail Address</label>
  <input id="input-email" type="email" name="email" placeholder="E-Mail Address">
  <label for="input-password">Password</label>
  <input id="input-password" type="password" name="password" placeholder="Password">
  <button type="submit">Login</button>
</form>
{_NAV_JS}
</body>
</html>"""


def register_html(error: str | None = None, success: bool = False) -> str:
    if success:
        return """<!DOCTYPE html>
<html lang="en">
<head><title>Your Account Has Been Created!</title></head>
<body>
<h1>Your Account Has Been Created!</h1>
<p>Congratulations! Your new account has been successfully created!</p>
</body>
</html>"""
    error_html = f'<div class="alert alert-danger">{escape(error)}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Register Account</title></head>
<body>
{_nav_html()}
{error_html}
<h1>Register Account</h1>
<form action="index.php?route=account/register" method="post">
  <label for="input-firstname">First Name</label>
  <input id="input-firstname" type="text" name="firstname" placeholder="First Name">
  <label for="input-lastname">Last Name</label>
  <input id="input-lastname" type="text" name="lastname" placeholder="Last Name">
  <label for="input-email">E-Mail</label>
  <input id="input-email" type="email" name="email" placeholder="E-Mail">
  <label for="input-telephone">Telephone</label>
  <input id="input-telephone" type="text" name="telephone" placeholder="Telephone">
  <label for="input-password">Password</label>
  <input id="input-password" type="password" name="password" placeholder="Password">
  <label for="input-confirm">Password Confirm</label>
  <input id="input-confirm" type="password" name="confirm" placeholder="Password Confirm">
  <fieldset>
    <legend>Newsletter</legend>
    <label><input type="radio" name="newsletter" value="1"> Yes</label>
    <label><input type="radio" name="newsletter" value="0" checked> No</label>
  </fieldset>
  <input type="checkbox" name="agree" value="1">
  <button type="submit">Continue</button>
</form>
{_NAV_JS}
</body>
</html>"""


def cart_html(cart: dict[str, int]) -> str:
    if not cart:
        return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Shopping Cart</title></head>
<body>
{_nav_html()}
<div id="content">
  <h1>Shopping Cart</h1>
  <p>Your shopping cart is empty!</p>
</div>
{_NAV_JS}
</body>
</html>"""

    item_rows = []
    subtotal = 0.0
    for product_id, quantity in cart.items():
        product = product_by_id(product_id)
        if product is None:
            continue
        line_total = product.price * quantity
        subtotal += line_total
        item_rows.append(
            f"<tr>"
            f"<td>{escape(product.name)}</td>"
            f"<td class=\"text-right\">${product.price:,.2f}</td>"
            f"<td class=\"text-right\">{quantity}</td>"
            f"<td class=\"text-right\">${line_total:,.2f}</td>"
            f"</tr>"
        )

    items_html = "\n".join(item_rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>Shopping Cart</title></head>
<body>
{_nav_html()}
<div id="content">
  <h1>Shopping Cart</h1>
  <div class="table-responsive">
    <table class="table table-bordered">
      <thead>
        <tr><th>Product Name</th><th>Unit Price</th><th>Quantity</th><th>Total</th></tr>
      </thead>
      <tbody>
        {items_html}
      </tbody>
    </table>
  </div>
  <table class="table table-bordered">
    <tbody>
      <tr><td class="text-right"><strong>Sub-Total:</strong></td><td>${subtotal:,.2f}</td></tr>
      <tr><td class="text-right"><strong>Total:</strong></td><td>${subtotal:,.2f}</td></tr>
    </tbody>
  </table>
</div>
{_NAV_JS}
</body>
</html>"""


def product_detail_html(product: Product) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>{escape(product.name)}</title></head>
<body>
{_nav_html()}
<div id="content">
  <div class="row">
    <div class="col-sm-4">
      <img src="image/catalog/{product.product_id}.jpg" alt="{escape(product.name)}"
           title="{escape(product.name)}" class="img-responsive">
    </div>
    <div class="col-sm-8">
      <h1>{escape(product.name)}</h1>
      <h2>${product.price:,.2f}</h2>
      <div id="product-qty-section">
        <label for="input-quantity">Qty</label>
        <input id="input-quantity" type="text" name="quantity" value="1" size="2">
        <button id="button-cart" type="button"
                onclick="cart.add('{product.product_id}')">Add to Cart</button>
      </div>
    </div>
  </div>
  <div class="row">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#tab-description">Description</a></li>
      <li><a href="#tab-review" id="tab-review-link"
             onclick="document.getElementById('product-qty-section').style.display='none'">Reviews (0)</a></li>
    </ul>
    <div id="tab-description">
      <p>A quality {escape(product.name)} product.</p>
    </div>
    <div id="tab-review">
      <h2>Write a review</h2>
      <label for="input-name">Your Name</label>
      <input id="input-name" type="text" name="author" placeholder="Your Name">
      <label for="input-review">Your Review</label>
      <textarea id="input-review" name="text" placeholder="Your Review"></textarea>
      <label for="input-rating">Qty</label>
      <select id="input-rating" name="rating">
        <option value="1">1</option><option value="2">2</option><option value="3">3</option>
        <option value="4">4</option><option value="5">5</option>
      </select>
    </div>
  </div>
</div>
{_NAV_JS}
</body>
</html>"""


def cart_add_payload(cart: dict[str, int], product_id: str) -> dict[str, str] | list[Any]:
    product = product_by_id(product_id)
    if product is None:
        return []

    total_quantity = sum(cart.values())
    total_price = sum(
        (product_by_id(pid).price if product_by_id(pid) else 0.0) * quantity
        for pid, quantity in cart.items()
    )
    return {
        "success": f"Success: You have added {product.name} to your shopping cart!",
        "total": f"{total_quantity} item(s) - ${total_price:,.2f}",
    }


def _product_card(product: Product) -> str:
    pid = product.product_id
    name = escape(product.name)
    href = f"index.php?route=product/product&amp;product_id={pid}"
    return f"""<div class="product-thumb">
  <div class="image">
    <a href="{href}">
      <img src="image/catalog/{pid}.jpg" alt="{name}" title="{name}">
    </a>
  </div>
  <div class="caption">
    <h4><a href="{href}">{name}</a></h4>
    <p>A quality product.</p>
    <p class="price">${product.price:,.2f}</p>
  </div>
  <div class="button-group">
    <button type="button" onclick="cart.add('{pid}')">Add to Cart</button>
  </div>
</div>"""


def route_from_request(url: str, params: Any = None) -> str:
    parsed = urlparse(url)
    values = parse_qs(parsed.query)
    if isinstance(params, dict):
        for key, value in params.items():
            values[key] = [str(value)]
    return values.get("route", [""])[0]


def fallback_response_for_request(
    method: str,
    url: str,
    *,
    params: Any = None,
    data: Any = None,
    cookies: RequestsCookieJar,
    cart: dict[str, int],
) -> Response:
    route = route_from_request(url, params)
    parsed_url = urlparse(url)
    path = parsed_url.path
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
    login_action = f"{base_url}?route=account/login"
    sid = ensure_session_cookie(cookies)

    # Use registry cart keyed by session ID; register passed cart on first encounter
    if sid not in _CART_REGISTRY:
        _CART_REGISTRY[sid] = cart
    actual_cart = _CART_REGISTRY[sid]

    blocked_paths = (
        "/.git/",
        "/phpinfo.php",
        "/config.php.bak",
        "/.env",
        "/.htpasswd",
        "/server-status",
    )
    if any(path.endswith(bp) or bp in path for bp in blocked_paths):
        return response("Not Found", status_code=HTTPStatus.NOT_FOUND)

    if route == "product/search":
        qs = parse_qs(parsed_url.query)
        if isinstance(params, dict):
            query = str(params.get("search", ""))
        else:
            query = qs.get("search", [""])[0]
        sort = qs.get("sort", [""])[0]
        order = qs.get("order", ["ASC"])[0]
        return response(search_html(query, sort=sort, order=order))

    if route == "product/product":
        product_id = parse_qs(parsed_url.query).get("product_id", [""])[0]
        product = product_by_id(product_id)
        if product is None:
            return response("Not Found", status_code=HTTPStatus.NOT_FOUND)
        return response(product_detail_html(product))

    if route == "checkout/cart":
        return response(cart_html(actual_cart))

    if route == "checkout/cart/add":
        if method.upper() != "POST":
            return json_response([])
        product_id = str(data.get("product_id", "")) if isinstance(data, dict) else ""
        try:
            quantity = int(data.get("quantity", 1)) if isinstance(data, dict) else 1
        except (TypeError, ValueError):
            quantity = 1
        product = product_by_id(product_id)
        if product is not None and quantity > 0:
            actual_cart[product_id] = actual_cart.get(product_id, 0) + quantity
        return json_response(cart_add_payload(actual_cart, product_id))

    if route == "account/login" and method.upper() == "POST":
        return response(login_html("No match for E-Mail Address and/or Password.", login_action))

    if route == "account/register":
        if method.upper() == "POST":
            first_name = (data.get("firstname", "") if isinstance(data, dict) else "").strip()
            if not first_name:
                return response(
                    register_html(error="First Name must be between 1 and 32 characters!")
                )
            return response(register_html(success=True))
        return response(register_html())

    if route.startswith("account/"):
        return response(login_html(action=login_action))

    resp = response(home_html())
    resp.headers["Set-Cookie"] = f"OCSESSID={sid}; path=/"
    return resp
