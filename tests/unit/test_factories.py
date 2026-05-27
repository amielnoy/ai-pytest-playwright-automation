"""Unit tests for utils/factories.py — correctness, uniqueness, and SOLID compliance."""
import re
from dataclasses import asdict

import allure
import pytest
from faker import Faker

from utils.factories import (
    FakerLike,
    _KNOWN_PRODUCTS,
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


@allure.feature("Factories")
@allure.story("RegistrationData factory")
class TestRegistrationPasswordComplexity:

    @allure.title("generated password is at least 12 characters long")
    def test_password_min_length(self):
        for _ in range(10):
            assert len(make_registration().password) >= 12

    @allure.title("generated password contains at least one uppercase letter")
    def test_password_has_uppercase(self):
        for _ in range(10):
            assert any(c.isupper() for c in make_registration().password)

    @allure.title("generated password contains at least one digit")
    def test_password_has_digit(self):
        for _ in range(10):
            assert any(c.isdigit() for c in make_registration().password)

    @allure.title("generated password contains at least one special character")
    def test_password_has_special_char(self):
        specials = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
        for _ in range(10):
            assert any(c in specials for c in make_registration().password)


@allure.feature("Factories")
@allure.story("RegistrationData factory")
class TestRegistrationFieldLimits:

    @allure.title("first_name is within OpenCart's 32-character limit")
    def test_first_name_max_length(self):
        for _ in range(20):
            assert len(make_registration().first_name) <= 32

    @allure.title("last_name is within OpenCart's 32-character limit")
    def test_last_name_max_length(self):
        for _ in range(20):
            assert len(make_registration().last_name) <= 32

    @allure.title("email is within a reasonable length (≤ 96 chars)")
    def test_email_max_length(self):
        for _ in range(20):
            assert len(make_registration().email) <= 96


@allure.feature("Factories")
@allure.story("RegistrationData factory")
class TestTelephoneFormat:

    @allure.title("telephone starts with '05' (Israeli mobile format)")
    def test_starts_with_05(self):
        for _ in range(20):
            assert make_registration().telephone.startswith("05")

    @allure.title("telephone is exactly 10 digits")
    def test_exactly_ten_digits(self):
        for _ in range(20):
            t = make_registration().telephone
            assert t.isdigit() and len(t) == 10


@allure.feature("Factories")
@allure.story("RegistrationData factory")
class TestParametrizedMissingFields:

    @allure.title("blanking '{field}' yields empty string for that field only")
    @pytest.mark.parametrize("field", ["first_name", "last_name", "email", "password", "telephone"])
    def test_blank_field_is_isolated(self, field: str):
        data = make_registration(**{field: ""})
        assert getattr(data, field) == ""
        other_fields = {"first_name", "last_name", "email", "telephone"} - {field}
        for other in other_fields:
            assert getattr(data, other), f"field '{other}' should not be blank"


@allure.feature("Factories")
@allure.story("Factory isolation")
class TestFactoryIsolation:

    @allure.title("two consecutive calls never share the same email")
    def test_no_shared_state_registration(self):
        emails = [make_registration().email for _ in range(50)]
        assert len(set(emails)) == 50

    @allure.title("two consecutive calls never share the same invalid-credentials email")
    def test_no_shared_state_credentials(self):
        emails = [make_invalid_credentials().email for _ in range(50)]
        assert len(set(emails)) == 50

    @allure.title("make_registration and make_invalid_credentials never collide on email")
    def test_cross_factory_no_email_collision(self):
        reg_emails = {make_registration().email for _ in range(20)}
        cred_emails = {make_invalid_credentials().email for _ in range(20)}
        assert reg_emails.isdisjoint(cred_emails)


@allure.feature("Factories")
@allure.story("SearchData factory")
class TestSearchProductCoverage:

    @allure.title("all known products appear at least once in 200 samples")
    def test_all_known_products_reachable(self):
        seen = {make_search().query for _ in range(200)}
        assert set(_KNOWN_PRODUCTS).issubset(seen), f"missing: {set(_KNOWN_PRODUCTS) - seen}"

    @allure.title("custom pool of one product always returns that product")
    def test_single_product_pool(self):
        for _ in range(10):
            assert make_search(products=("OnlyThis",)).query == "OnlyThis"


@allure.feature("Factories")
@allure.story("CartScenario factory")
class TestCartScenarioMath:

    @allure.title("max_total is exactly 5× max_price")
    def test_max_total_is_5x_max_price(self):
        for _ in range(20):
            sc = make_cart_scenario()
            assert sc.max_total == round(sc.max_price * 5, 2)

    @allure.title("overriding max_price recalculates max_total accordingly")
    def test_override_max_price_recalculates_max_total(self):
        sc = make_cart_scenario(max_price=100.0)
        assert sc.max_total == 500.0

    @allure.title("max_total is always greater than max_price")
    def test_max_total_always_exceeds_item_price(self):
        for _ in range(20):
            sc = make_cart_scenario()
            assert sc.max_total > sc.max_price


@allure.feature("Factories")
@allure.story("Seeded reproducibility")
class TestCrossFactorySeeding:

    @allure.title("same Faker seed produces identical RegistrationData email")
    def test_seeded_registration_is_reproducible(self):
        fake = Faker()
        fake.seed_instance(99)
        email_a = make_registration(fake=fake).email
        fake.seed_instance(99)
        email_b = make_registration(fake=fake).email
        assert email_a == email_b

    @allure.title("same Faker seed produces identical SearchData query")
    def test_seeded_search_is_reproducible(self):
        fake = Faker()
        fake.seed_instance(77)
        query_a = make_search(fake=fake).query
        fake.seed_instance(77)
        query_b = make_search(fake=fake).query
        assert query_a == query_b

    @allure.title("same Faker seed produces identical LoginCredentials email")
    def test_seeded_credentials_are_reproducible(self):
        fake = Faker()
        fake.seed_instance(55)
        email_a = make_invalid_credentials(fake=fake).email
        fake.seed_instance(55)
        email_b = make_invalid_credentials(fake=fake).email
        assert email_a == email_b
