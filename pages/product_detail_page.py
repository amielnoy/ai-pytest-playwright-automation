import re
from typing import Pattern

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    _HEADING_ROLE = "heading"
    _QUANTITY_LABEL = "Qty"
    _DEFAULT_QUANTITY = "1"
    _ADD_TO_CART_BUTTON_ROLE = "button"
    _ADD_TO_CART_BUTTON_NAME = "Add to Cart"
    _REVIEWS_LINK_ROLE = "link"
    _REVIEWS_LINK_NAME: Pattern[str] = re.compile("Reviews")
    _REVIEW_FIELD_LABELS = ("Qty", "Your Name", "Your Review")

    def has_product_heading(self, product_name: str) -> bool:
        return self.page.get_by_role(
            self._HEADING_ROLE, name=product_name
        ).is_visible()

    def has_default_quantity(self) -> bool:
        return (
            self.page.get_by_label(self._QUANTITY_LABEL).input_value()
            == self._DEFAULT_QUANTITY
        )

    def has_add_to_cart_button(self) -> bool:
        return self.page.get_by_role(
            self._ADD_TO_CART_BUTTON_ROLE, name=self._ADD_TO_CART_BUTTON_NAME
        ).is_visible()

    def open_reviews_tab(self) -> None:
        self.page.get_by_role(
            self._REVIEWS_LINK_ROLE, name=self._REVIEWS_LINK_NAME
        ).click()

    def has_review_form_fields(self) -> bool:
        return all(
            self.page.get_by_label(label).is_visible()
            for label in self._REVIEW_FIELD_LABELS
        )
