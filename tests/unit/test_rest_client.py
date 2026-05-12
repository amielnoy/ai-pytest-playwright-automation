from services.rest_client import RestClient


class FakeSession:
    def __init__(self):
        self.calls = []
        self.headers = {}
        self.cookies = {}

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return {"method": method, "url": url, "kwargs": kwargs}

    def close(self):
        self.closed = True


def test_rest_client_methods_delegate_to_request_with_default_timeout():
    client = RestClient(timeout=7)
    fake_session = FakeSession()
    client.session = fake_session

    client.get("https://example.test/get")
    client.post("https://example.test/post", json={"name": "item"})
    client.put("https://example.test/put", json={"name": "updated"})
    client.delete("https://example.test/delete")

    assert fake_session.calls == [
        ("GET", "https://example.test/get", {"timeout": 7}),
        (
            "POST",
            "https://example.test/post",
            {"json": {"name": "item"}, "timeout": 7},
        ),
        (
            "PUT",
            "https://example.test/put",
            {"json": {"name": "updated"}, "timeout": 7},
        ),
        ("DELETE", "https://example.test/delete", {"timeout": 7}),
    ]


def test_rest_client_allows_per_request_timeout_override():
    client = RestClient(timeout=7)
    fake_session = FakeSession()
    client.session = fake_session

    client.get("https://example.test/slow", timeout=30)

    assert fake_session.calls == [
        ("GET", "https://example.test/slow", {"timeout": 30}),
    ]


def test_rest_client_retries_only_idempotent_methods_by_default():
    client = RestClient()
    retry_config = client.session.adapters["https://"].max_retries

    assert retry_config.allowed_methods == frozenset({"GET", "HEAD", "OPTIONS"})
