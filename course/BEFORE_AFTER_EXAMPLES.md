# Before / After Examples

## Locator

Weak:

```python
page.locator("#content .btn-primary").click()
```

Strong:

```python
page.get_by_role("button", name="Add to Cart").click()
```

## Page Object

Weak:

```python
def test_add_to_cart(page):
    page.get_by_placeholder("Search").fill("iPod")
    page.get_by_role("button", name="Search").click()
```

Strong:

```python
def test_add_to_cart(home_page, search_results_page):
    home_page.search("iPod")
    search_results_page.add_product_to_cart("iPod Classic")
```

## Fixture

Weak:

```python
def test_checkout(page):
    login(page)
    add_item(page)
```

Strong:

```python
def test_checkout(logged_in_page, cart_with_item):
    cart_with_item.proceed_to_checkout()
```

## Review Comment

Weak:

```text
Fix this flaky test.
```

Strong:

```text
The test uses `nth(1)` to choose a product, so it can add the wrong item when sorting changes. Filter the product card by product name inside the page object.
```
