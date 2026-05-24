import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Pin all web-UI tests to a single xdist worker.

    Running multiple headless Chromium instances against tutorialsninja.com
    simultaneously triggers rate-limiting / bot-protection responses.
    Grouping tests here keeps them sequential within one worker while the
    rest of the suite (API, unit, contract) still runs in parallel.
    """
    for item in items:
        if "web-ui" in str(item.fspath):
            item.add_marker(pytest.mark.xdist_group("web-ui"))
