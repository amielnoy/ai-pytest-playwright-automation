"""Offline OpenCart fallback: serves the demo store when the live site is blocked.

This module owns session/challenge handling, HTTP `Response` building, and
request routing/dispatch. The product catalogue lives in
``opencart_products`` and the page HTML in ``opencart_templates``; both are
re-exported here so existing ``from services.api.opencart_fallback import ...``
call sites keep working.
"""
from __future__ import annotations

import json
import uuid
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, urlparse

from requests import Response
from requests.cookies import RequestsCookieJar

from services.api.opencart_products import (  # re-exported for back-compat
    PRODUCTS,
    Product,
    product_by_id,
    search_products,
)
from services.api.opencart_templates import (  # re-exported for back-compat
    cart_html,
    home_html,
    login_html,
    product_detail_html,
    register_html,
    search_html,
)

__all__ = [
    "PRODUCTS",
    "Product",
    "product_by_id",
    "search_products",
    "cart_html",
    "home_html",
    "login_html",
    "product_detail_html",
    "register_html",
    "search_html",
    "get_session_cart",
    "is_challenge_page",
    "ensure_session_cookie",
    "response",
    "json_response",
    "cart_add_payload",
    "route_from_request",
    "fallback_response_for_request",
]

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
