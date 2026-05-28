"""Unit tests for pages/self_healing.py.

Covers SelfHealingLocator resolution logic, fallback recording, property proxies,
__getattr__ delegation, and the healing_locator() factory — all without a real browser.
"""
from unittest.mock import MagicMock, call

import allure
import pytest

from pages.self_healing import SelfHealEvent, SelfHealingLocator, healing_locator


def _locator(count: int = 0, wait_raises: bool = False) -> MagicMock:
    """Build a mock Locator with configurable count() and wait_for() behaviour."""
    loc = MagicMock()
    loc.count.return_value = count
    if wait_raises:
        loc.wait_for.side_effect = Exception("timeout")
    return loc


# ---------------------------------------------------------------------------
# Resolution strategy
# ---------------------------------------------------------------------------

@allure.feature("Self-Healing Locator")
@allure.story("Resolution")
class TestSelfHealingResolution:

    @allure.title("Primary immediately visible → primary is returned, no heal event")
    def test_primary_returned_when_count_positive(self):
        primary = _locator(count=1)
        fallback = _locator(count=1)
        events: list[SelfHealEvent] = []
        shl = SelfHealingLocator(
            primary, [fallback],
            name="btn", primary_label="css:primary", fallback_labels=["css:fallback"],
            events=events,
        )
        result = shl._resolve()
        assert result is primary
        assert events == []

    @allure.title("Primary count=0, wait_for succeeds and count becomes positive → primary returned")
    def test_primary_returned_after_wait_succeeds(self):
        primary = _locator(count=0)
        # After wait_for, count becomes 1
        primary.count.side_effect = [0, 1]
        fallback = _locator(count=1)
        events: list[SelfHealEvent] = []
        shl = SelfHealingLocator(
            primary, [fallback],
            name="btn", primary_label="css:primary", fallback_labels=["css:fallback"],
            events=events,
        )
        result = shl._resolve()
        assert result is primary
        assert events == []

    @allure.title("Primary unavailable, first fallback visible → fallback returned, event recorded")
    def test_fallback_used_when_primary_fails(self):
        primary = _locator(count=0, wait_raises=True)
        fallback = _locator(count=1)
        events: list[SelfHealEvent] = []
        shl = SelfHealingLocator(
            primary, [fallback],
            name="search-box", primary_label="id:search", fallback_labels=["name:q"],
            events=events,
        )
        result = shl._resolve()
        assert result is fallback
        assert len(events) == 1
        assert events[0] == SelfHealEvent(name="search-box", primary="id:search", healed="name:q")

    @allure.title("All candidates unavailable → primary returned as last resort without raising")
    def test_primary_returned_as_last_resort_when_all_fail(self):
        primary = _locator(count=0, wait_raises=True)
        fallback = _locator(count=0, wait_raises=True)
        shl = SelfHealingLocator(
            primary, [fallback],
            name="btn", primary_label="p", fallback_labels=["f"],
            events=[],
        )
        result = shl._resolve()
        assert result is primary

    @allure.title("First fallback fails, second fallback succeeds → second fallback returned")
    def test_second_fallback_used_when_first_fails(self):
        primary = _locator(count=0, wait_raises=True)
        fb1 = _locator(count=0, wait_raises=True)
        fb2 = _locator(count=1)
        events: list[SelfHealEvent] = []
        shl = SelfHealingLocator(
            primary, [fb1, fb2],
            name="btn", primary_label="p", fallback_labels=["f1", "f2"],
            events=events,
        )
        result = shl._resolve()
        assert result is fb2
        assert events[0].healed == "f2"


# ---------------------------------------------------------------------------
# Heal-event deduplication
# ---------------------------------------------------------------------------

@allure.feature("Self-Healing Locator")
@allure.story("Event recording")
class TestHealEventRecording:

    @allure.title("Same fallback used twice → only one event recorded")
    def test_duplicate_heal_event_not_recorded(self):
        primary = _locator(count=0, wait_raises=True)
        fallback = _locator(count=1)
        events: list[SelfHealEvent] = []
        shl = SelfHealingLocator(
            primary, [fallback],
            name="btn", primary_label="p", fallback_labels=["f"],
            events=events,
        )
        shl._resolve()
        shl._resolve()
        assert len(events) == 1

    @allure.title("events=None → no AttributeError when fallback is used")
    def test_events_none_does_not_raise(self):
        primary = _locator(count=0, wait_raises=True)
        fallback = _locator(count=1)
        shl = SelfHealingLocator(
            primary, [fallback],
            name="btn", primary_label="p", fallback_labels=["f"],
            events=None,
        )
        result = shl._resolve()   # must not raise
        assert result is fallback

    @allure.title("SelfHealEvent fields are accessible and frozen")
    def test_self_heal_event_is_frozen_dataclass(self):
        evt = SelfHealEvent(name="n", primary="p", healed="h")
        assert evt.name == "n"
        assert evt.primary == "p"
        assert evt.healed == "h"
        with pytest.raises((AttributeError, TypeError)):
            evt.name = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Property and __getattr__ proxies
# ---------------------------------------------------------------------------

@allure.feature("Self-Healing Locator")
@allure.story("Proxy interface")
class TestSelfHealingProxies:

    @allure.title(".resolved returns the underlying Playwright locator")
    def test_resolved_property(self):
        primary = _locator(count=1)
        shl = SelfHealingLocator(
            primary, [], name="x", primary_label="p", fallback_labels=[],
        )
        assert shl.resolved is primary

    @allure.title(".first returns resolved().first")
    def test_first_property(self):
        primary = _locator(count=1)
        shl = SelfHealingLocator(
            primary, [], name="x", primary_label="p", fallback_labels=[],
        )
        result = shl.first
        assert result is primary.first

    @allure.title(".last returns resolved().last")
    def test_last_property(self):
        primary = _locator(count=1)
        shl = SelfHealingLocator(
            primary, [], name="x", primary_label="p", fallback_labels=[],
        )
        result = shl.last
        assert result is primary.last

    @allure.title("__getattr__ proxies arbitrary method calls to the resolved locator")
    def test_getattr_proxies_to_resolved(self):
        primary = _locator(count=1)
        primary.inner_text.return_value = "hello"
        shl = SelfHealingLocator(
            primary, [], name="x", primary_label="p", fallback_labels=[],
        )
        assert shl.inner_text() == "hello"
        primary.inner_text.assert_called_once()


# ---------------------------------------------------------------------------
# healing_locator() factory
# ---------------------------------------------------------------------------

@allure.feature("Self-Healing Locator")
@allure.story("Factory function")
class TestHealingLocatorFactory:

    @allure.title("healing_locator() with no fallbacks builds a SelfHealingLocator with empty lists")
    def test_no_fallbacks(self):
        primary = _locator(count=1)
        shl = healing_locator(primary, name="btn", primary_label="css:btn")
        assert isinstance(shl, SelfHealingLocator)
        assert shl._primary is primary
        assert shl._fallback_locators == []
        assert shl._fallback_labels == []
        assert shl._name == "btn"

    @allure.title("healing_locator() wires fallback locators and labels in order")
    def test_fallbacks_wired_in_order(self):
        primary = _locator()
        fb1, fb2 = _locator(), _locator()
        shl = healing_locator(
            primary, name="inp",
            primary_label="css:primary",
            fallbacks=[("aria:label", fb1), ("name:q", fb2)],
        )
        assert shl._fallback_locators == [fb1, fb2]
        assert shl._fallback_labels == ["aria:label", "name:q"]

    @allure.title("healing_locator() forwards events list to the SelfHealingLocator")
    def test_events_list_forwarded(self):
        events: list[SelfHealEvent] = []
        primary = _locator()
        shl = healing_locator(primary, name="x", primary_label="p", events=events)
        assert shl._events is events
