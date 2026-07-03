import re
from typing import Pattern

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    _HEADING_ROLE = "heading"
    _QUANTITY_INPUT_SELECTOR = "#input-quantity"
    _DEFAULT_QUANTITY = "1"
    _ADD_TO_CART_BUTTON_SELECTOR = "#button-cart"
    _REVIEWS_LINK_ROLE = "link"
    _REVIEWS_LINK_NAME: Pattern[str] = re.compile("Reviews")
    _REVIEW_FIELD_LABELS = ("Your Name", "Your Review")
    _PRICE_SELECTOR = ".price-new, #product-price .price, h2.price"
    _PRODUCT_IMAGE_SELECTOR = "#product img.img-thumbnail"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.quantity_input = page.locator(self._QUANTITY_INPUT_SELECTOR)
        self.price = page.locator(self._PRICE_SELECTOR).first
        self.product_image = page.locator(self._PRODUCT_IMAGE_SELECTOR).first
        self.add_to_cart_button = self._healed(
            self._ADD_TO_CART_BUTTON_SELECTOR, "product detail add-to-cart button",
            ["button[name='button-cart']", "button:has-text('Add to Cart')"],
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
