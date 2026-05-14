"""
Flaky test demonstration for Allure 3 reporting.

How it works:
  pytest-rerunfailures retries a failing test once (--reruns=1 in pytest.ini).
  When a test fails on attempt 1 but passes on attempt 2, allure-pytest writes
  statusDetails.flaky=true into the result JSON. The Allure 3 awesome plugin
  surfaces these tests in the "Flaky" widget on the dashboard (summary.json
  flakyTests list).

Tests in this file:
  test_flaky_on_first_attempt  — fails once, passes on retry  → marked FLAKY
  test_always_passes           — passes immediately            → marked PASSED
"""

import allure
import pytest

# Module-level set persists across reruns in the same worker process.
# First attempt: key absent → fail and record it.
# Second attempt (rerun): key present → pass.
_seen: set[str] = set()


@allure.feature("Flaky Test Reporting")
@allure.story("Allure 3 flaky detection")
class TestFlakyDemo:

    @allure.title("Flaky test — fails once, passes on retry")
    @allure.severity(allure.severity_level.MINOR)
    def test_flaky_on_first_attempt(self) -> None:
        key = "TestFlakyDemo.test_flaky_on_first_attempt"
        if key not in _seen:
            _seen.add(key)
            pytest.fail("Simulated transient failure (will pass on retry)")

    @allure.title("Stable test — always passes")
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_always_passes(self) -> None:
        assert True
