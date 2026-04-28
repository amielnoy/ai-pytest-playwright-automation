from dataclasses import dataclass

from services.rest_client import RestClient


@dataclass(frozen=True)
class EndpointCase:
    path: str
    required_text: str


class PublicService:
    def __init__(self, client: RestClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def get_path(self, path: str):
        return self.client.get(f"{self.base_url}{path}")
