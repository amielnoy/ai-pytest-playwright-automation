import re

from playwright.sync_api import Page, Response as PlaywrightResponse

from utils.price_parser import parse_price


EBAY_BASE_URL = "https://www.ebay.com"


class _EbayResponse:
    """Wraps a Playwright navigation response + rendered page content."""

    def __init__(self, page: Page, nav_response: PlaywrightResponse | None) -> None:
        self._page = page
        self._nav = nav_response
        self._text: str | None = None

    @property
    def status_code(self) -> int:
        return self._nav.status if self._nav else 200

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = self._page.content()
        return self._text


class EbaySearchService:
    def __init__(self, page: Page) -> None:
        self._page = page

    def get(self, url: str) -> _EbayResponse:
        nav = self._page.goto(url, wait_until="domcontentloaded")
        return _EbayResponse(self._page, nav)

    def search(self, query: str) -> _EbayResponse:
        nav = self._page.goto(
            f"{EBAY_BASE_URL}/sch/i.html?_nkw={query}",
            wait_until="domcontentloaded",
        )
        return _EbayResponse(self._page, nav)

    def item_cards(self, html: str) -> list[str]:
        return re.findall(r'class="s-item__title"', html)

    def item_titles(self, html: str) -> list[str]:
        # Real listing titles are wrapped in <span role="heading">; the ghost
        # "Shop on eBay" item sits directly in the div without that span.
        raw = re.findall(r'<span role="heading">([^<]+)</span>', html)
        return [t.strip() for t in raw if t.strip()]

    def item_ids(self, html: str) -> list[str]:
        return list(dict.fromkeys(re.findall(r"/itm/(\d+)", html)))

    def item_prices(self, html: str) -> list[float]:
        raw = re.findall(r'class="s-item__price">\s*([^<]+?)\s*</span>', html)
        parsed = [parse_price(r) for r in raw]
        return [p for p in parsed if p is not None]

    def first_item_id(self, query: str) -> str:
        resp = self.search(query)
        ids = self.item_ids(resp.text)
        assert ids, f"No items found for query '{query}'"
        return ids[0]
