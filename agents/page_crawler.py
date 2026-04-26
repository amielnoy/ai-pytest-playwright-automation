"""
Playwright-based page crawler that extracts structured page data for STD generation.
Runs headless so it doesn't interfere with existing test sessions.
"""
import json
from playwright.sync_api import sync_playwright, Page


def _extract_forms(page: Page) -> list[dict]:
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('form')).map(form => {
            const fields = Array.from(form.querySelectorAll('input, select, textarea')).map(el => {
                // Try label[for=id] first, then nearest label inside the same .form-group / tr
                let labelEl = el.id ? document.querySelector(`label[for='${el.id}']`) : null;
                if (!labelEl) {
                    const row = el.closest('.form-group') || el.closest('tr');
                    labelEl = row ? row.querySelector('label') : null;
                }
                return {
                    tag: el.tagName.toLowerCase(),
                    type: el.type || null,
                    name: el.name || null,
                    id: el.id || null,
                    placeholder: el.placeholder || null,
                    required: el.required,
                    label: labelEl ? labelEl.innerText.trim() : null,
                };
            });
            const submit = form.querySelector('[type=submit], button[type=submit], button:not([type])');
            return {
                action: form.action || null,
                method: form.method || 'get',
                fields: fields.filter(f => f.type !== 'hidden'),
                submit_text: submit ? submit.innerText.trim() : null,
            };
        });
    }""")


def _extract_buttons(page: Page) -> list[str]:
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button, a.btn, input[type=button], input[type=submit]'))
            .map(el => el.innerText.trim() || el.value || el.title)
            .filter(t => t.length > 0)
            .filter((v, i, a) => a.indexOf(v) === i)
            .slice(0, 30);
    }""")


def _extract_nav_links(page: Page) -> list[dict]:
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('nav a, #menu a, .nav a, header a'))
            .map(a => ({ text: a.innerText.trim(), href: a.href }))
            .filter(l => l.text.length > 0)
            .filter((v, i, a) => a.findIndex(x => x.text === v.text) === i)
            .slice(0, 20);
    }""")


def _extract_headings(page: Page) -> list[str]:
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('h1, h2, h3'))
            .map(h => h.innerText.trim())
            .filter(t => t.length > 0)
            .slice(0, 15);
    }""")


def _extract_alerts(page: Page) -> list[str]:
    return page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.alert, .text-danger, .has-error'))
            .map(el => el.innerText.trim())
            .filter(t => t.length > 0);
    }""")


def crawl_page(url: str) -> dict:
    """Navigate to url, extract structured page data, return as dict."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(20000)

        try:
            page.goto(url, wait_until="networkidle")
            title = page.title()
            current_url = page.url

            data = {
                "url": current_url,
                "title": title,
                "headings": _extract_headings(page),
                "forms": _extract_forms(page),
                "buttons": _extract_buttons(page),
                "nav_links": _extract_nav_links(page),
                "alerts": _extract_alerts(page),
            }
        finally:
            browser.close()

    return data


def crawl_page_as_json(url: str) -> str:
    return json.dumps(crawl_page(url), indent=2, ensure_ascii=False)
