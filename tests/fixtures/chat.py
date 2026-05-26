"""AI chat fixtures — local FastAPI server lifecycle and chat service client."""
import pytest

from services.api.chat_service import ChatService
from services.rest_client import RestClient
from tests.conftest_server import ensure_server_running, shutdown_server
from utils.data_loader import get_config

_SERVER_URL = get_config().get("server_url", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def _local_api_server() -> str:
    """Ensure FastAPI is up; uses mock /chat when no API key is set."""
    base_url = ensure_server_running(_SERVER_URL)
    yield base_url
    shutdown_server()


@pytest.fixture
def server_url(_local_api_server: str) -> str:
    return _local_api_server


@pytest.fixture
def chat_service(server_url: str) -> ChatService:
    """Client for the local FastAPI /chat endpoint."""
    client = RestClient(timeout=60)
    yield ChatService(client, server_url)
    client.close()
