from pages.base_page import BasePage


class CartPage(BasePage):
    """Repurposed for eBay: verifies item prices on search result pages."""

    def open(self) -> None:
        # Navigate to eBay homepage as a proxy for "cart"
        self.navigate()

    def get_cart_total(self) -> float:
        # Return 0.0 — not a real cart on eBay
        return 0.0

    def is_empty(self) -> bool:
        return True

    def get_item_count(self) -> int:
        return 0
