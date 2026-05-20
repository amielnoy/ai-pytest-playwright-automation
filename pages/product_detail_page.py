import re
from typing import Pattern

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.self_healing import healing_locator


class ProductDetailPage(BasePage):
    _HEADING_ROLE = "heading"
    _QUANTITY_LABEL = "Qty"
    _DEFAULT_QUANTITY = "1"
    _ADD_TO_CART_BUTTON_SELECTOR = "#button-cart"
    _REVIEWS_LINK_ROLE = "link"
    _REVIEWS_LINK_NAME: Pattern[str] = re.compile("Reviews")
    _REVIEW_FIELD_LABELS = ("Qty", "Your Name", "Your Review")

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.quantity_input = page.get_by_label(self._QUANTITY_LABEL)
        self.add_to_cart_button = healing_locator(
            page.locator(self._ADD_TO_CART_BUTTON_SELECTOR),
            name="product detail add-to-cart button",
            primary_label=self._ADD_TO_CART_BUTTON_SELECTOR,
            fallbacks=[
                ("button[name='button-cart']", page.locator("button[name='button-cart']")),
                ("button:has-text('Add to Cart')", page.locator("button:has-text('Add to Cart')")),
            ],
            events=self._self_heal_events,
        )
        self.reviews_tab = page.get_by_role(
            self._REVIEWS_LINK_ROLE, name=self._REVIEWS_LINK_NAME
        )
        self.review_form_fields = tuple(
            page.get_by_label(label) for label in self._REVIEW_FIELD_LABELS
        )

    def has_product_heading(self, product_name: str) -> bool:
        return self.page.get_by_role(
            self._HEADING_ROLE, name=product_name
        ).is_visible()

    def has_default_quantity(self) -> bool:
        return self.quantity_input.input_value() == self._DEFAULT_QUANTITY

    def has_add_to_cart_button(self) -> bool:
        return self.add_to_cart_button.is_visible()

    def open_reviews_tab(self) -> None:
        self.reviews_tab.click()

    def has_review_form_fields(self) -> bool:
        return all(field.is_visible() for field in self.review_form_fields)
