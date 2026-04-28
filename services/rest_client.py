from collections.abc import Mapping
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)


class RestClient:
    def __init__(
        self,
        headers: Mapping[str, str] | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        status_forcelist: tuple[int, ...] = DEFAULT_RETRY_STATUSES,
    ):
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

        retry_config = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods={"GET", "POST", "PUT", "DELETE"},
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
        return self.session.request(method, url, **kwargs)

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
