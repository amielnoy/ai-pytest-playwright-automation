"""API service fixtures — HTTP session, REST service objects."""
import pytest

from services.api.account_service import AccountService
from services.api.cart_service import CartService
from services.api.public_service import PublicService
from services.api.search_service import SearchService
from services.rest_client import RestClient
from utils.api_client import build_session
from utils.data_loader import get_config


@pytest.fixture
def api_base_url() -> str:
    return get_config()["base_url"]


@pytest.fixture
def session(api_base_url: str) -> RestClient:
    """Fresh HTTP session per test: own OCSESSID, no shared cart state."""
    client = build_session()
    client.get(api_base_url)
    yield client
    client.close()


@pytest.fixture
def public_service(session: RestClient, api_base_url: str) -> PublicService:
    return PublicService(session, api_base_url)


@pytest.fixture
def search_service(session: RestClient, api_base_url: str) -> SearchService:
    return SearchService(session, api_base_url)


@pytest.fixture
def cart_service(session: RestClient, api_base_url: str) -> CartService:
    return CartService(session, api_base_url)


@pytest.fixture
def account_service(session: RestClient, api_base_url: str) -> AccountService:
    return AccountService(session, api_base_url)
