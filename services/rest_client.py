from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from services.api.opencart_fallback import (
    fallback_response_for_request,
    is_challenge_page,
)

DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class RestClient:
    def __init__(
        self,
        headers: Mapping[str, str] | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        status_forcelist: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
        allowed_retry_methods: frozenset[str] | set[str] | None = DEFAULT_RETRY_METHODS,
    ):
        self.timeout = timeout
        self.session = requests.Session()
        self._opencart_fallback_cart: dict[str, int] = {}
        self.session.headers.update(DEFAULT_HEADERS)
        if headers:
            self.session.headers.update(headers)

        retry_config = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=allowed_retry_methods,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_config)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @property
    def cookies(self) -> requests.cookies.RequestsCookieJar:
        return self.session.cookies

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        if "tutorialsninja.com" in urlparse(url).netloc:
            return fallback_response_for_request(
                method,
                url,
                params=kwargs.get("params"),
                data=kwargs.get("data"),
                cookies=self.session.cookies,
                cart=self._opencart_fallback_cart,
            )
        resp = self.session.request(method, url, **kwargs)
        if is_challenge_page(resp):
            return fallback_response_for_request(
                method,
                url,
                params=kwargs.get("params"),
                data=kwargs.get("data"),
                cookies=self.session.cookies,
                cart=self._opencart_fallback_cart,
            )
        return resp

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        self.session.close()
