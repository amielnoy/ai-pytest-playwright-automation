from dataclasses import dataclass

from requests import Response

from services.http_client import HttpClient


@dataclass(frozen=True)
class EndpointCase:
    path: str
    required_text: str


class PublicService:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def get_path(self, path: str) -> Response:
        return self.client.get(f"{self.base_url}{path}")
