"""Unit tests for utils/factories.py — correctness, uniqueness, and SOLID compliance."""
import re
from dataclasses import asdict

import allure
from faker import Faker

from utils.factories import (
    FakerLike,
    make_cart_scenario,
    make_invalid_credentials,
    make_registration,
    make_search,
)


@allure.feature("Factories")
@allure.story("RegistrationData factory")
class TestMakeRegistration:

    @allure.title("make_registration returns a fully populated RegistrationData")
    def test_all_fields_present(self):
        data = make_registration()
        assert data.first_name
        assert data.last_name
        assert data.email
        assert data.password
        assert data.confirm_password
        assert data.telephone

    @allure.title("password and confirm_password are equal on a standard build")
    def test_password_matches_confirm(self):
        data = make_registration()
        assert data.password == data.confirm_password

    @allure.title("email matches the auto+<hex8>@example.com pattern")
    def test_email_format(self):
        assert re.match(r"auto\+[0-9a-f]{8}@example\.com", make_registration().email)

    @allure.title("telephone is 10 digits")
    def test_telephone_numeric(self):
        t = make_registration().telephone
        assert t.isdigit() and len(t) == 10

    @allure.title("20 consecutive calls produce 20 distinct emails")
    def test_emails_are_unique(self):
        assert len({make_registration().email for _ in range(20)}) == 20

    @allure.title("newsletter defaults to False")
    def test_newsletter_defaults_false(self):
        assert make_registration().newsletter is False

    @allure.title("override first_name='' blanks only first_name")
    def test_override_first_name_blank(self):
        data = make_registration(first_name="")
        assert data.first_name == ""
        assert data.last_name and data.email

    @allure.title("override last_name='' blanks only last_name")
    def test_override_last_name_blank(self):
        data = make_registration(last_name="")
        assert data.last_name == ""
        assert data.first_name

    @allure.title("override email='' blanks only email")
    def test_override_email_blank(self):
        data = make_registration(email="")
        assert data.email == ""
        assert data.first_name

    @allure.title("override password='' blanks password field")
    def test_override_password_blank(self):
        assert make_registration(password="").password == ""

    @allure.title("override telephone='' blanks only telephone")
    def test_override_telephone_blank(self):
        data = make_registration(telephone="")
        assert data.telephone == ""
        assert data.first_name

    @allure.title("asdict serialises all expected keys with correct values")
    def test_asdict_has_all_keys(self):
        data = make_registration()
        d = asdict(data)
        for key in ("first_name", "last_name", "email", "password", "confirm_password", "telephone", "newsletter"):
            assert key in d
        assert d["first_name"] == data.first_name
        assert d["email"] == data.email

    @allure.title("injected FakerLike is used instead of the default generator (DIP)")
    def test_accepts_faker_like_injection(self):
        fake = Faker()
        fake.seed_instance(42)
        result1 = make_registration(fake=fake)
        fake.seed_instance(42)
        result2 = make_registration(fake=fake)
        assert result1.email == result2.email


@allure.feature("Factories")
@allure.story("SearchData factory")
class TestMakeSearch:

    @allure.title("make_search returns a SearchData with all fields populated")
    def test_fields_present(self):
        data = make_search()
        assert data.query
        assert data.max_price > 0
        assert data.limit >= 1

    @allure.title("override query is forwarded unchanged")
    def test_override_query(self):
        assert make_search(query="iPhone").query == "iPhone"

    @allure.title("override max_price is forwarded unchanged")
    def test_override_max_price(self):
        assert make_search(max_price=499.99).max_price == 499.99

    @allure.title("override limit is forwarded unchanged")
    def test_override_limit(self):
        assert make_search(limit=3).limit == 3

    @allure.title("default max_price is within 200–2000")
    def test_max_price_in_range(self):
        for _ in range(20):
            assert 200 <= make_search().max_price <= 2000

    @allure.title("default limit is between 1 and 10")
    def test_limit_in_range(self):
        for _ in range(20):
            assert 1 <= make_search().limit <= 10

    @allure.title("custom products pool is used when supplied (OCP)")
    def test_custom_products_pool(self):
        pool = ("ZPhone", "ZBook")
        for _ in range(20):
            assert make_search(products=pool).query in pool


@allure.feature("Factories")
@allure.story("CartScenario factory")
class TestMakeCartScenario:

    @allure.title("make_cart_scenario returns a CartScenario with all fields populated")
    def test_fields_present(self):
        sc = make_cart_scenario()
        assert sc.query and sc.max_price > 0 and sc.limit >= 1 and sc.max_total > 0

    @allure.title("max_total is greater than max_price")
    def test_max_total_exceeds_item_price(self):
        sc = make_cart_scenario()
        assert sc.max_total > sc.max_price

    @allure.title("override query and max_price are forwarded")
    def test_overrides_forwarded(self):
        sc = make_cart_scenario(query="iPhone", max_price=300.0)
        assert sc.query == "iPhone" and sc.max_price == 300.0


@allure.feature("Factories")
@allure.story("LoginCredentials factory")
class TestMakeInvalidCredentials:

    @allure.title("make_invalid_credentials returns non-empty email and password")
    def test_fields_present(self):
        c = make_invalid_credentials()
        assert c.email and c.password

    @allure.title("email uses @nowhere.example to avoid accidental matches")
    def test_email_domain(self):
        assert "@nowhere.example" in make_invalid_credentials().email

    @allure.title("20 consecutive calls produce 20 distinct emails")
    def test_emails_are_unique(self):
        assert len({make_invalid_credentials().email for _ in range(20)}) == 20

    @allure.title("password is at least 8 characters")
    def test_password_length(self):
        for _ in range(10):
            assert len(make_invalid_credentials().password) >= 8


@allure.feature("Factories")
@allure.story("FakerLike protocol")
class TestFakerLikeProtocol:

    @allure.title("Faker satisfies FakerLike at runtime (isinstance check)")
    def test_faker_satisfies_protocol(self):
        assert isinstance(Faker(), FakerLike)
