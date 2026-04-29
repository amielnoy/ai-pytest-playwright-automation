from pages.components.base_component import BaseComponent


class CartSummaryComponent(BaseComponent):
    """Stub: eBay does not expose a cart without login. All methods are no-ops."""

    def get_total(self) -> float:
        return 0.0

    def get_item_count(self) -> int:
        return 0

    def is_empty(self) -> bool:
        return True
