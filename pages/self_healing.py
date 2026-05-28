from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import Locator


@dataclass(frozen=True)
class SelfHealEvent:
    name: str
    primary: str
    healed: str


class SelfHealingLocator:
    """Lazy locator wrapper that falls back to explicit alternatives.

    This is deterministic self-healing: it does not call an AI service and it does
    not invent selectors. The page object owns the allowed fallback list, and every
    fallback use is recorded for later selector cleanup.
    """

    def __init__(
        self,
        primary: Locator,
        fallback_locators: list[Locator],
        *,
        name: str,
        primary_label: str,
        fallback_labels: list[str],
        events: list[SelfHealEvent] | None = None,
    ) -> None:
        self._primary = primary
        self._fallback_locators = fallback_locators
        self._name = name
        self._primary_label = primary_label
        self._fallback_labels = fallback_labels
        self._events = events
        self._reported: set[str] = set()

    def _resolve(self) -> Locator:
        candidates = [self._primary, *self._fallback_locators]
        labels = [self._primary_label, *self._fallback_labels]

        # First, check if the primary is immediately available
        try:
            if self._primary.count() > 0:
                return self._primary
        except Exception:
            pass

        # If primary isn't immediately present, wait for a short duration
        # to allow dynamic elements to render before falling back
        try:
            # Wait up to 1000ms for primary to attach
            self._primary.wait_for(state="attached", timeout=1000)
            if self._primary.count() > 0:
                return self._primary
        except Exception:
            # Primary failed to attach within the grace period; proceed with fallbacks
            pass

        # Iterate through fallbacks and return the first one that is attached
        for index in range(1, len(candidates)):
            locator = candidates[index]
            try:
                # Wait up to 500ms per fallback candidate
                locator.wait_for(state="attached", timeout=500)
                if locator.count() > 0:
                    self._record_heal(labels[index])
                    return locator
            except Exception:
                continue

        # If everything fails, return primary to let the actual interaction
        # trigger standard Playwright timeout exceptions for debugging
        return self._primary

    def _record_heal(self, healed_label: str) -> None:
        if healed_label in self._reported:
            return
        self._reported.add(healed_label)
        if self._events is not None:
            self._events.append(
                SelfHealEvent(
                    name=self._name,
                    primary=self._primary_label,
                    healed=healed_label,
                )
            )

    @property
    def resolved(self) -> Locator:
        """Underlying Playwright locator for expect() and multi-match assertions."""
        return self._resolve()

    @property
    def first(self) -> Locator:
        return self._resolve().first

    @property
    def last(self) -> Locator:
        return self._resolve().last

    def __getattr__(self, name: str) -> Any:
        return getattr(self._resolve(), name)


def healing_locator(
    primary: Locator,
    *,
    name: str,
    primary_label: str,
    fallbacks: list[tuple[str, Locator]] | None = None,
    events: list[SelfHealEvent] | None = None,
) -> SelfHealingLocator:
    fallback_items = fallbacks or []
    return SelfHealingLocator(
        primary,
        [locator for _, locator in fallback_items],
        name=name,
        primary_label=primary_label,
        fallback_labels=[label for label, _ in fallback_items],
        events=events,
    )
