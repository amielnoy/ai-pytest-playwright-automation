from requests import Response

from services.http_client import HttpClient


class AccountService:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def get_register_page(self) -> Response:
        return self.client.get(
            f"{self.base_url}/index.php?route=account/register",
        )
