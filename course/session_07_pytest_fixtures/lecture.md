# Session 7 - pytest Fixtures: Reliable Setup, Teardown, and Dependency Injection

## Learning Objectives

By the end of this session you will be able to:

- Explain fixtures as dependency injection for tests.
- Choose the right fixture scope: `function`, `class`, `module`, or `session`.
- Use `yield` fixtures for teardown.
- Compose fixtures without hiding important test setup.
- Use parametrized fixtures for browser, data, and role variations.
- Avoid autouse and shared-state mistakes that create flaky tests.

---

## Fixture Basics

A fixture prepares something a test needs:

```python
@pytest.fixture
def logged_in_page(page):
    login_page = LoginPage(page).open()
    login_page.login("standard_user", "secret_sauce")
    return page
```

Test:

```python
def test_cart_badge(logged_in_page):
    logged_in_page.get_by_role("button", name="Add to cart").click()
```

The test requests the dependency by name. pytest builds it before the test runs.

---

## Fixture Scopes

| Scope | Lifetime | Use for |
|---|---|---|
| `function` | One test | Browser pages, isolated data, most setup. |
| `class` | One test class | Shared expensive setup for related tests. |
| `module` | One file | Read-only data or expensive immutable objects. |
| `session` | Full run | Browser instance, config, static metadata. |

Default to `function`. Increase scope only when the object is immutable or safely isolated.

---

## Teardown With `yield`

Use `yield` when setup must be cleaned:

```python
@pytest.fixture
def temporary_cart(api_cart):
    cart_id = api_cart.create()
    yield cart_id
    api_cart.delete(cart_id)
```

Everything before `yield` is setup. Everything after `yield` is teardown.

---

## Parametrized Fixtures

Fixtures can run the same test with multiple values:

```python
@pytest.fixture(params=["chromium", "firefox"])
def browser_name(request):
    return request.param
```

Use parametrized fixtures for infrastructure variation. Use `@pytest.mark.parametrize` for business-data variation.

---

## Autouse Fixtures

`autouse=True` runs a fixture without being named in the test.

Good use:

```python
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path="failure.png")
```

Bad use: hidden login, hidden cart setup, hidden data mutation. If setup changes test meaning, make it explicit.

---

## Fixture Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| Session-scoped mutable cart | Function-scoped cart or cleanup after each test. |
| Autouse login for every test | Explicit `logged_in_page` fixture. |
| Fixture does assertions | Move assertions to tests or page methods named `expect_*`. |
| Fixture hides five workflows | Split into smaller named fixtures. |
| Fixture reads private files directly | Use data loader helpers and clear missing-secret behavior. |

---

## Before / After

Weak:

```python
def test_checkout(page):
    page.goto("/login")
    page.fill("#user", "standard_user")
    page.fill("#pass", "secret_sauce")
    page.click("#login")
```

Better:

```python
def test_checkout(logged_in_page, cart_with_item):
    checkout_page = cart_with_item.proceed_to_checkout()
    checkout_page.expect_ready()
```

The setup is named, reusable, and visible.

---

## Session Completion Checklist

- [ ] I wrote one function-scoped fixture.
- [ ] I wrote one `yield` fixture with cleanup.
- [ ] I explained why browser pages should not be session-scoped.
- [ ] I replaced hidden setup with explicit fixture names.
- [ ] I completed the exercises in `EXERCISES.md`.
