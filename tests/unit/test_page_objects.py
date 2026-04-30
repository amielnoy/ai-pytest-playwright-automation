from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest

from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.components.alert import AlertComponent
from pages.components.base_component import BaseComponent
from pages.components.cart_summary import CartSummaryComponent
from pages.components.nav_bar import NavBarComponent
from pages.components.product_card import ProductCardComponent
from pages.components.registration_form import RegistrationFormComponent
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.models import ProductInfo, StoredProductInfo
from pages.product_detail_page import ProductDetailPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage


def test_base_component_stores_page():
    page = MagicMock()

    component = BaseComponent(page)

    assert component.page is page


def test_base_page_navigate_builds_base_and_relative_urls():
    page = MagicMock()
    base_page = BasePage(page, "https://example.test/store/")

    base_page.navigate()
    base_page.navigate("/index.php?route=account/login", wait_until="networkidle")

    assert page.goto.call_args_list == [
        call("https://example.test/store", wait_until="domcontentloaded"),
        call(
            "https://example.test/store/index.php?route=account/login",
            wait_until="networkidle",
        ),
    ]


def test_base_page_exposes_title_url_screenshot_and_alert_error():
    page = MagicMock()
    page.title.return_value = "Your Store"
    page.url = "https://example.test/current"
    page.screenshot.return_value = b"png"
    base_page = BasePage(page, "https://example.test")
    base_page.alert = MagicMock()
    base_page.alert.get_error.return_value = "Required field"

    assert base_page.title == "Your Store"
    assert base_page.url == "https://example.test/current"
    assert base_page.take_screenshot() == b"png"
    assert base_page.get_error_message() == "Required field"


def test_base_page_wait_for_visible_uses_first_matching_locator():
    page = MagicMock()
    locator = MagicMock()
    page.locator.return_value = locator
    base_page = BasePage(page, "https://example.test")

    with patch("pages.base_page.expect") as expect_mock:
        base_page.wait_for_visible(".product-thumb", timeout=3000)

    page.locator.assert_called_once_with(".product-thumb")
    expect_mock.assert_called_once_with(locator.first)
    expect_mock.return_value.to_be_visible.assert_called_once_with(timeout=3000)


def test_base_page_accessibility_helpers_use_class_locators():
    page = MagicMock()
    html = MagicMock()
    ids = MagicMock()
    html.get_attribute.return_value = "en"
    ids.evaluate_all.return_value = ["duplicate-id"]
    page.locator.side_effect = [html, ids]
    base_page = BasePage(page, "https://example.test")

    assert base_page.document_language() == "en"
    assert base_page.duplicate_ids() == ["duplicate-id"]
    assert page.locator.call_args_list == [
        call(BasePage._HTML_SELECTOR),
        call(BasePage._ANY_ID_SELECTOR),
    ]
    ids.evaluate_all.assert_called_once_with(BasePage._DUPLICATE_IDS_SCRIPT)


def test_home_page_delegates_navigation_and_nav_actions():
    page = MagicMock()
    home_page = HomePage(page, "https://example.test")
    home_page.nav = MagicMock()

    assert home_page.open() is home_page
    home_page.search("MacBook")
    home_page.go_to_login()
    home_page.go_to_register()
    home_page.logout()
    home_page.nav.has_currency_dropdown.return_value = True
    home_page.nav.is_logged_in.return_value = False

    page.goto.assert_called_once_with("https://example.test", wait_until="domcontentloaded")
    home_page.nav.search.assert_called_once_with("MacBook")
    home_page.nav.go_to_login.assert_called_once()
    home_page.nav.go_to_register.assert_called_once()
    home_page.nav.logout.assert_called_once()
    assert home_page.has_currency_dropdown() is True
    assert home_page.is_logged_in() is False


def test_home_page_accessibility_helpers_delegate_to_nav_and_image_locator():
    page = MagicMock()
    image_locator = MagicMock()
    image_locator.evaluate_all.return_value = []
    page.locator.return_value = image_locator
    home_page = HomePage(page, "https://example.test")
    home_page.nav = MagicMock()
    home_page.nav.has_account_menu.return_value = True
    home_page.nav.has_currency_dropdown.return_value = True
    home_page.nav.has_search_input.return_value = True
    home_page.nav.has_empty_cart_summary.return_value = True

    assert home_page.has_header_accessible_controls() is True
    assert home_page.has_search_input() is True
    assert home_page.has_empty_cart_summary() is True
    assert home_page.visible_featured_images_missing_alt() == []
    page.locator.assert_called_once_with(HomePage._FEATURED_PRODUCT_IMAGES)
    image_locator.evaluate_all.assert_called_once_with(
        HomePage._VISIBLE_IMAGES_MISSING_ALT_SCRIPT
    )


def test_cart_page_delegates_to_summary_component():
    page = MagicMock()
    cart_page = CartPage(page, "https://example.test")
    cart_page.summary = MagicMock()
    cart_page.summary.get_total.return_value = 42.5
    cart_page.summary.is_empty.return_value = False
    cart_page.summary.get_item_count.return_value = 3

    cart_page.open()

    page.goto.assert_called_once_with(
        "https://example.test/index.php?route=checkout/cart",
        wait_until="domcontentloaded",
    )
    assert cart_page.get_cart_total() == 42.5
    assert cart_page.is_empty() is False
    assert cart_page.get_item_count() == 3


def test_register_page_delegates_full_registration_flow_to_form():
    page = MagicMock()
    register_page = RegisterPage(page, "https://example.test")
    register_page.form = MagicMock()
    register_page.form.is_submitted_successfully.return_value = True
    register_page.form.has_required_field_labels.return_value = True
    register_page.form.has_newsletter_options.return_value = True

    register_page.register(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
        telephone="123456789",
        password="secret",
        confirm_password="secret",
        newsletter=True,
    )

    register_page.form.fill.assert_called_once_with(
        "Ada",
        "Lovelace",
        "ada@example.test",
        "123456789",
        "secret",
        "secret",
        True,
    )
    register_page.form.accept_privacy_policy.assert_called_once()
    register_page.form.submit.assert_called_once()
    assert register_page.is_registration_successful() is True
    assert register_page.has_required_field_labels() is True
    assert register_page.has_newsletter_options() is True


def test_login_page_open_login_and_status_checks_use_class_locators():
    page = MagicMock()
    email = MagicMock()
    password = MagicMock()
    login_button = MagicMock()
    success_heading = MagicMock()
    warning = MagicMock()
    success_heading.is_visible.return_value = True
    warning.is_visible.return_value = True
    page.get_by_role.side_effect = [email, login_button, success_heading]
    page.get_by_label.return_value = password
    page.locator.return_value = warning
    login_page = LoginPage(page, "https://example.test")

    login_page.open()
    login_page.login("user@example.test", "bad-password")

    page.goto.assert_called_once_with(
        "https://example.test/index.php?route=account/login",
        wait_until="domcontentloaded",
    )
    email.fill.assert_called_once_with("user@example.test")
    password.fill.assert_called_once_with("bad-password")
    login_button.click.assert_called_once()
    assert login_page.is_login_successful() is True
    assert login_page.has_invalid_credentials_warning() is True
    assert page.get_by_role.call_args_list == [
        call(LoginPage._EMAIL_ROLE, name=LoginPage._EMAIL_NAME),
        call(LoginPage._LOGIN_BUTTON_ROLE, name=LoginPage._LOGIN_BUTTON_NAME),
        call(
            LoginPage._MY_ACCOUNT_HEADING_ROLE,
            name=LoginPage._MY_ACCOUNT_HEADING_NAME,
            level=LoginPage._MY_ACCOUNT_HEADING_LEVEL,
        ),
    ]
    page.locator.assert_called_once_with(LoginPage._INVALID_CREDENTIALS_WARNING)


def test_login_page_accessibility_helpers_use_class_locators():
    page = MagicMock()
    email = MagicMock()
    password = MagicMock()
    login_button = MagicMock()
    warning_text = MagicMock()
    email.is_visible.return_value = True
    password.is_visible.return_value = True
    login_button.is_visible.return_value = True
    warning_text.inner_text.return_value = LoginPage._INVALID_LOGIN_WARNING_PREFIX
    page.get_by_role.side_effect = [email, login_button]
    page.get_by_label.return_value = password
    page.locator.return_value = warning_text
    login_page = LoginPage(page, "https://example.test")

    assert login_page.has_accessible_login_controls() is True
    assert login_page.has_invalid_credentials_warning_text() is True
    assert page.get_by_role.call_args_list == [
        call(LoginPage._EMAIL_ROLE, name=LoginPage._EMAIL_NAME),
        call(LoginPage._LOGIN_BUTTON_ROLE, name=LoginPage._LOGIN_BUTTON_NAME),
    ]
    page.get_by_label.assert_called_once_with(LoginPage._PASSWORD_LABEL)
    page.locator.assert_called_once_with(LoginPage._INVALID_CREDENTIALS_WARNING)
    warning_text.wait_for.assert_called_once_with(state="visible", timeout=5000)


def test_search_results_returns_empty_when_no_results_message_is_visible():
    page = MagicMock()
    page.get_by_text.return_value.is_visible.return_value = True
    search_page = SearchResultsPage(page, "https://example.test")

    assert search_page.get_products_under_price("missing", 10.0) == []

    page.goto.assert_called_once_with(
        "https://example.test/index.php?route=product%2Fsearch&search=missing",
        wait_until="domcontentloaded",
    )


def test_search_results_filters_products_under_price_and_limit():
    page = MagicMock()
    page.get_by_text.return_value.is_visible.return_value = False
    search_page = SearchResultsPage(page, "https://example.test")
    search_page._load_search = MagicMock()
    search_page._cards = MagicMock(
        return_value=[
            SimpleNamespace(name="Cheap", price=10.0, index=0),
            SimpleNamespace(name="No price", price=None, index=1),
            SimpleNamespace(name="Expensive", price=100.0, index=2),
            SimpleNamespace(name="Also cheap", price=12.0, index=3),
        ]
    )

    products = search_page.get_products_under_price("query", max_price=50.0, limit=1)

    assert products == [ProductInfo(name="Cheap", price=10.0, index=0)]
    search_page._load_search.assert_called_once_with("query")


def test_search_results_adds_items_to_cart_and_waits_for_success():
    page = MagicMock()
    thumbs = MagicMock()
    page.locator.return_value = thumbs
    search_page = SearchResultsPage(page, "https://example.test")
    search_page.alert = MagicMock()
    products = [
        ProductInfo(name="MacBook", price=602.0, index=0),
        ProductInfo(name="iPhone", price=123.2, index=2),
    ]

    with patch("pages.search_results_page.ProductCardComponent") as card_class:
        cards = [MagicMock(), MagicMock()]
        card_class.side_effect = cards
        added = search_page.add_items_to_cart(products)

    assert added == ["MacBook", "iPhone"]
    assert thumbs.nth.call_args_list == [call(0), call(2)]
    assert card_class.call_args_list == [
        call(thumbs.nth.return_value, 0),
        call(thumbs.nth.return_value, 2),
    ]
    cards[0].add_to_cart.assert_called_once()
    cards[1].add_to_cart.assert_called_once()
    assert search_page.alert.wait_for_success.call_count == 2


def test_search_results_open_product_clicks_title_link_in_matching_card():
    page = MagicMock()
    product_link = MagicMock()
    thumbs = MagicMock()
    filtered = MagicMock()
    title = MagicMock()
    title_link = MagicMock()
    page.get_by_role.return_value = product_link
    page.locator.return_value = thumbs
    thumbs.filter.return_value = filtered
    filtered.first.locator.return_value = title
    title.get_by_role.return_value = title_link
    search_page = SearchResultsPage(page, "https://example.test")

    search_page.open_product("MacBook")

    page.get_by_role.assert_called_once_with("link", name="MacBook", exact=True)
    thumbs.filter.assert_called_once_with(has=product_link)
    filtered.first.locator.assert_called_once_with(SearchResultsPage._PRODUCT_TITLE_SELECTOR)
    title.get_by_role.assert_called_once_with("link", name="MacBook", exact=True)
    title_link.click.assert_called_once()
    page.wait_for_load_state.assert_called_once_with("domcontentloaded")


def test_search_results_view_sort_and_cards_helpers():
    page = MagicMock()
    list_view = MagicMock()
    sort_select = MagicMock()
    thumbs = MagicMock()
    thumbs.count.return_value = 2
    thumbs.nth.side_effect = ["thumb-0", "thumb-1"]
    page.locator.side_effect = [list_view, thumbs]
    page.get_by_role.return_value = sort_select
    search_page = SearchResultsPage(page, "https://example.test")
    search_page.wait_for_product_results = MagicMock()

    with patch("pages.search_results_page.expect") as expect_mock:
        search_page.choose_list_view()
        search_page.sort_by_name_ascending()

    list_view.click.assert_called_once()
    sort_select.select_option.assert_called_once_with(
        label=SearchResultsPage._SORT_NAME_ASCENDING_LABEL
    )
    page.wait_for_load_state.assert_called_once_with("domcontentloaded")
    assert expect_mock.call_count == 2

    with patch("pages.search_results_page.ProductCardComponent") as card_class:
        cards = search_page._cards()

    assert cards == [card_class.return_value, card_class.return_value]
    assert card_class.call_args_list == [call("thumb-0", 0), call("thumb-1", 1)]


def test_search_results_product_names_sort_and_stored_information():
    search_page = SearchResultsPage(MagicMock(), "https://example.test")
    search_page.wait_for_product_results = MagicMock()
    search_page._cards = MagicMock(
        return_value=[
            SimpleNamespace(name="b", stored_info=lambda: "stored-b"),
            SimpleNamespace(name="A", stored_info=lambda: "stored-a"),
        ]
    )

    assert search_page.product_names() == ["b", "A"]
    assert search_page.are_product_names_sorted_ascending() is False
    assert search_page.stored_product_information() == ["stored-b", "stored-a"]


def test_search_results_accessibility_helpers_use_class_locators():
    page = MagicMock()
    label_locators = [MagicMock(), MagicMock(), MagicMock()]
    product_links = MagicMock()
    for label in label_locators:
        label.is_visible.return_value = True
    product_links.all_inner_texts.return_value = ["MacBook", "MacBook Pro"]
    page.get_by_label.side_effect = label_locators
    page.locator.return_value = product_links
    search_page = SearchResultsPage(page, "https://example.test")
    search_page.wait_for_product_results = MagicMock()

    assert search_page.has_filter_controls() is True
    assert search_page.product_title_link_names() == ["MacBook", "MacBook Pro"]
    assert page.get_by_label.call_args_list == [
        call(SearchResultsPage._SEARCH_CRITERIA_LABEL),
        call(SearchResultsPage._SORT_BY_LABEL),
        call(SearchResultsPage._SHOW_LABEL),
    ]
    page.locator.assert_called_once_with(
        f"{SearchResultsPage._PRODUCT_THUMBS} "
        f"{SearchResultsPage._PRODUCT_TITLE_SELECTOR} a"
    )


def test_alert_component_returns_banner_field_success_and_waits():
    page = MagicMock()
    danger = MagicMock()
    field = MagicMock()
    success = MagicMock()
    danger.is_visible.return_value = False
    field.first.is_visible.return_value = True
    field.first.inner_text.return_value = "First name is required"
    success.is_visible.return_value = True
    success.inner_text.return_value = "Success"
    page.locator.side_effect = [danger, field, success, success]
    alert = AlertComponent(page)

    assert alert.get_error() == "First name is required"
    assert alert.get_success() == "Success"
    with patch("pages.components.alert.expect") as expect_mock:
        alert.wait_for_success(timeout=1234)

    expect_mock.assert_called_once_with(success)
    expect_mock.return_value.to_be_visible.assert_called_once_with(timeout=1234)


def test_alert_component_prefers_visible_banner_and_returns_empty_without_errors():
    page = MagicMock()
    danger = MagicMock()
    field = MagicMock()
    danger.is_visible.return_value = True
    danger.inner_text.return_value = "Login failed"
    field.first.is_visible.return_value = False
    page.locator.side_effect = [danger, field]
    alert = AlertComponent(page)

    assert alert.get_error() == "Login failed"

    danger.is_visible.return_value = False
    page.locator.side_effect = [danger, field]
    assert alert.get_error() == ""


def test_cart_summary_reads_total_count_and_empty_state():
    page = MagicMock()
    total_cell = MagicMock()
    item_rows = MagicMock()
    empty_message = MagicMock()
    total_cell.last.is_visible.return_value = True
    total_cell.last.inner_text.return_value = "$602.00"
    item_rows.count.return_value = 2
    empty_message.is_visible.return_value = True
    page.locator.side_effect = [total_cell, item_rows]
    page.get_by_text.return_value = empty_message
    summary = CartSummaryComponent(page)

    assert summary.get_total() == 602.0
    assert summary.get_item_count() == 2
    assert summary.is_empty() is True


def test_cart_summary_returns_zero_when_total_is_hidden_or_unparseable():
    page = MagicMock()
    hidden_total = MagicMock()
    hidden_total.last.is_visible.return_value = False
    page.locator.return_value = hidden_total
    summary = CartSummaryComponent(page)

    assert summary.get_total() == 0.0

    visible_total = MagicMock()
    visible_total.last.is_visible.return_value = True
    visible_total.last.inner_text.return_value = "not a price"
    page.locator.return_value = visible_total

    assert summary.get_total() == 0.0


def test_nav_bar_search_currency_login_register_logout_and_status():
    page = MagicMock()
    search_input = MagicMock()
    search_container = MagicMock()
    search_button = MagicMock()
    currency = MagicMock()
    login_link = MagicMock()
    register_link = MagicMock()
    logout_link = MagicMock()
    account_link = MagicMock()
    currency.is_visible.return_value = True
    logout_link.count.return_value = 1
    page.get_by_placeholder.return_value = search_input
    page.locator.return_value = search_container
    search_container.get_by_role.return_value = search_button
    page.get_by_role.side_effect = [
        currency,
        login_link,
        account_link,
        register_link,
        account_link,
        logout_link,
        account_link,
        logout_link,
    ]
    nav = NavBarComponent(page)

    nav.search("iPod")
    assert nav.has_currency_dropdown() is True
    with patch("pages.components.nav_bar.expect") as expect_mock:
        nav.go_to_login()
        nav.go_to_register()
        nav.logout()
    assert nav.is_logged_in() is True

    search_input.fill.assert_called_once_with("iPod")
    search_button.click.assert_called_once()
    assert page.wait_for_load_state.call_args_list == [
        call("domcontentloaded"),
        call("domcontentloaded"),
        call("domcontentloaded"),
        call("domcontentloaded"),
    ]
    assert account_link.first.click.call_count == 3
    assert expect_mock.call_count == 3
    login_link.click.assert_called_once()
    register_link.click.assert_called_once()
    logout_link.click.assert_called_once()


def test_nav_bar_accessibility_helpers_use_class_locators():
    page = MagicMock()
    search_input = MagicMock()
    currency = MagicMock()
    empty_cart = MagicMock()
    account_menu = MagicMock()
    search_input.is_visible.return_value = True
    currency.is_visible.return_value = True
    empty_cart.is_visible.return_value = True
    account_menu.first.is_visible.return_value = True
    page.get_by_placeholder.return_value = search_input
    page.get_by_role.side_effect = [currency, empty_cart, account_menu]
    nav = NavBarComponent(page)

    assert nav.has_search_input() is True
    assert nav.has_currency_dropdown() is True
    assert nav.has_empty_cart_summary() is True
    assert nav.has_account_menu() is True
    page.get_by_placeholder.assert_called_once_with(NavBarComponent._SEARCH_PLACEHOLDER)
    assert page.get_by_role.call_args_list == [
        call(
            NavBarComponent._CURRENCY_BUTTON_ROLE,
            name=NavBarComponent._CURRENCY_BUTTON_NAME,
        ),
        call(
            NavBarComponent._EMPTY_CART_BUTTON_ROLE,
            name=NavBarComponent._EMPTY_CART_BUTTON_NAME,
        ),
        call(
            NavBarComponent._ACCOUNT_LINK_ROLE,
            name=NavBarComponent._ACCOUNT_LINK_NAME,
        ),
    ]


def test_registration_form_fill_accept_submit_and_success_state():
    page = MagicMock()
    first_name = MagicMock()
    last_name = MagicMock()
    email = MagicMock()
    telephone = MagicMock()
    newsletter = MagicMock()
    password = MagicMock()
    confirm = MagicMock()
    privacy = MagicMock()
    submit = MagicMock()
    success = MagicMock()
    success.is_visible.return_value = True
    page.get_by_role.side_effect = [
        first_name,
        last_name,
        email,
        telephone,
        newsletter,
        submit,
        success,
    ]
    page.get_by_label.side_effect = [password, confirm]
    page.locator.return_value = privacy
    form = RegistrationFormComponent(page)

    form.fill(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
        telephone="123456789",
        password="secret",
        confirm_password="secret",
        newsletter=True,
    )
    form.accept_privacy_policy()
    form.submit()

    assert form.is_submitted_successfully() is True
    first_name.fill.assert_called_once_with("Ada")
    last_name.fill.assert_called_once_with("Lovelace")
    email.fill.assert_called_once_with("ada@example.test")
    telephone.fill.assert_called_once_with("123456789")
    password.fill.assert_called_once_with("secret")
    confirm.fill.assert_called_once_with("secret")
    newsletter.check.assert_called_once()
    privacy.check.assert_called_once()
    submit.click.assert_called_once()


def test_registration_form_chooses_no_newsletter_by_default():
    page = MagicMock()
    page.get_by_role.return_value = MagicMock()
    page.get_by_label.return_value = MagicMock()
    form = RegistrationFormComponent(page)

    form.fill("", "", "", "", "", "")

    assert call("radio", name="No") in page.get_by_role.call_args_list


def test_registration_form_accessibility_helpers_use_class_locators():
    page = MagicMock()
    labels = [MagicMock() for _ in RegistrationFormComponent._REQUIRED_FIELD_LABELS]
    yes = MagicMock()
    no = MagicMock()
    for label in labels:
        label.is_visible.return_value = True
    yes.is_visible.return_value = True
    no.is_visible.return_value = True
    page.get_by_label.side_effect = labels
    page.get_by_role.side_effect = [yes, no]
    form = RegistrationFormComponent(page)

    assert form.has_required_field_labels() is True
    assert form.has_newsletter_options() is True
    assert page.get_by_label.call_args_list == [
        call(label, exact=True)
        for label in RegistrationFormComponent._REQUIRED_FIELD_LABELS
    ]
    assert page.get_by_role.call_args_list == [
        call(
            RegistrationFormComponent._NEWSLETTER_RADIO_ROLE,
            name=RegistrationFormComponent._NEWSLETTER_YES_NAME,
        ),
        call(
            RegistrationFormComponent._NEWSLETTER_RADIO_ROLE,
            name=RegistrationFormComponent._NEWSLETTER_NO_NAME,
        ),
    ]


def test_product_card_reads_fields_and_adds_to_cart():
    root = MagicMock()
    heading = MagicMock()
    name_link = MagicMock()
    image = MagicMock()
    description = MagicMock()
    price = MagicMock()
    button = MagicMock()
    name_link.inner_text.return_value = "  iPod Classic  "
    image.get_attribute.return_value = "https://example.test/ipod.jpg"
    description.first.inner_text.return_value = "  Great\n music   player "
    price.inner_text.return_value = "$123.45"
    def get_by_role(role, **kwargs):
        if role == ProductCardComponent._NAME_HEADING_ROLE:
            return heading
        if role == ProductCardComponent._IMAGE_ROLE:
            return image
        if role == ProductCardComponent._ADD_TO_CART_BUTTON_ROLE:
            return button
        raise AssertionError(f"Unexpected role: {role!r}, kwargs={kwargs!r}")

    root.get_by_role.side_effect = get_by_role
    heading.get_by_role.return_value = name_link
    root.locator.side_effect = [description, price]
    card = ProductCardComponent(root, index=4)

    assert card.name == "iPod Classic"
    assert card.cleaned_name == "Classic"
    assert card.picture_url == "https://example.test/ipod.jpg"
    assert card.description == "Great music player"
    assert card.price == 123.45
    card.add_to_cart()

    button.click.assert_called_once()


def test_product_card_stored_info_and_price_parse_error():
    card = ProductCardComponent(MagicMock(), index=0)
    with patch.object(
        ProductCardComponent, "name", new_callable=PropertyMock
    ) as name_mock, patch.object(
        ProductCardComponent, "picture_url", new_callable=PropertyMock
    ) as picture_mock, patch.object(
        ProductCardComponent, "description", new_callable=PropertyMock
    ) as description_mock, patch.object(
        ProductCardComponent, "price", new_callable=PropertyMock
    ) as price_mock:
        name_mock.return_value = "iPod Nano"
        picture_mock.return_value = "https://example.test/nano.jpg"
        description_mock.return_value = "Small player"
        price_mock.return_value = 99.0

        assert card.stored_info() == StoredProductInfo(
            name="Nano",
            picture_url="https://example.test/nano.jpg",
            description="Small player",
            price=99.0,
        )

        price_mock.return_value = None
        with pytest.raises(ValueError, match="Product price could not be parsed"):
            card.stored_info()


def test_product_detail_page_uses_class_locator_members():
    page = MagicMock()
    heading = MagicMock()
    quantity = MagicMock()
    add_button = MagicMock()
    reviews = MagicMock()
    review_fields = [MagicMock(), MagicMock(), MagicMock()]
    heading.is_visible.return_value = True
    quantity.input_value.return_value = ProductDetailPage._DEFAULT_QUANTITY
    add_button.is_visible.return_value = True
    for field in review_fields:
        field.is_visible.return_value = True
    page.get_by_role.side_effect = [heading, add_button, reviews]
    page.get_by_label.side_effect = [quantity, *review_fields]
    product_page = ProductDetailPage(page, "https://example.test")

    assert product_page.has_product_heading("MacBook") is True
    assert product_page.has_default_quantity() is True
    assert product_page.has_add_to_cart_button() is True
    product_page.open_reviews_tab()
    assert product_page.has_review_form_fields() is True
    reviews.click.assert_called_once()
    assert page.get_by_role.call_args_list == [
        call(ProductDetailPage._HEADING_ROLE, name="MacBook"),
        call(
            ProductDetailPage._ADD_TO_CART_BUTTON_ROLE,
            name=ProductDetailPage._ADD_TO_CART_BUTTON_NAME,
        ),
        call(
            ProductDetailPage._REVIEWS_LINK_ROLE,
            name=ProductDetailPage._REVIEWS_LINK_NAME,
        ),
    ]
