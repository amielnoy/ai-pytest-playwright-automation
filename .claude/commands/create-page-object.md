Create a new page object for: $ARGUMENTS

The argument should be a page name or URL path (e.g. "product detail page" or "/product/123").

## Steps to follow

1. **Inspect the page** — use the Playwright MCP browser tools to navigate to the page and take a snapshot of the accessibility tree. Identify all interactive elements: buttons, inputs, links, headings.

2. **Choose locators** — for each element, choose the most stable locator using this priority:
   - `get_by_role(...)` with `name=`
   - `get_by_label(...)`
   - `get_by_placeholder(...)`
   - `get_by_text(...)`
   - `locator('[data-test="..."]')`
   - `locator('.css-class')` only as last resort

3. **Create the file** — write `pages/<page_name>_page.py` following this structure:
   ```python
   from playwright.sync_api import Page, expect
   from pages.base_page import BasePage

   class <PageName>Page(BasePage):
       def __init__(self, page: Page, base_url: str) -> None:
           super().__init__(page, base_url)
           # Define all locators here (lazy — evaluated at call time)
           self.<element> = page.get_by_role(...)

       def <action>(self) -> "Self | OtherPage":
           with allure.step("..."):
               self.<element>.click()
           return self  # or return NextPage(self._page, self._base_url)
   ```

4. **Add type hints** — all methods must have return type annotations. Methods that stay on the same page return `Self`. Methods that navigate return the next page object type.

5. **Update `pages/__init__.py`** — add the import so the new class is accessible from the package.

6. **Write a smoke test** — create or suggest a minimal test in `tests/web-ui/` that imports the new page object and asserts it can be instantiated and navigated to.

7. **Run collection** — run `pytest --collect-only -q` to confirm nothing is broken.

Output each file separately, clearly labelled with its path.
