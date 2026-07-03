"""HTTP client abstraction used by the API service layer.

Service classes depend on this structural `Protocol` rather than the concrete
`RestClient`, so they can be exercised with any object exposing the same small
surface (e.g. a fake/mock in unit tests). `RestClient` satisfies it by shape —
no explicit subclassing required.
"""
from typing import Any, Protocol, runtime_checkable

from requests import Response
from requests.cookies import RequestsCookieJar


@runtime_checkable
class HttpClient(Protocol):
    @property
    def cookies(self) -> RequestsCookieJar: ...

    def get(self, url: str, **kwargs: Any) -> Response: ...

    def post(self, url: str, **kwargs: Any) -> Response: ...

    def put(self, url: str, **kwargs: Any) -> Response: ...

    def delete(self, url: str, **kwargs: Any) -> Response: ...
