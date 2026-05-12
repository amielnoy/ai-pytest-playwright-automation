"""
Playwright CLI STD Agent
------------------------
Creates a detailed Software Test Document (STD) for a web page URL.

The agent uses the Playwright CLI to capture visual evidence for the URL, then
uses the existing Playwright crawler to inspect page structure and generate
step-by-step test cases.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from agents.page_crawler import crawl_page

_ROOT = Path(__file__).parent.parent
_STDS_DIR = _ROOT / "stds"
_ARTIFACTS_DIR = _ROOT / "artifacts" / "std_page_snapshots"


@dataclass(frozen=True)
class StdAgentResult:
    url: str
    std_path: Path
    screenshot_path: Path
    title: str
    test_case_count: int


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "web-page"


def _feature_from_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    route = query.get("route", [""])[0]
    search = query.get("search", [""])[0]

    if route:
        return route.replace("/", " ").replace("_", " ").title()
    if search:
        return f"Search Results For {search}".title()
    host = parsed.netloc or "Web Page"
    return host.replace(".", " ").title()


def _run_playwright_screenshot(url: str, screenshot_path: Path) -> None:
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "playwright",
        "screenshot",
        "--wait-for-timeout",
        "1000",
        url,
        str(screenshot_path),
    ]
    subprocess.run(command, check=True, cwd=_ROOT)


def _table_row(step: int, action: str, test_data: str, expected: str) -> str:
    return f"| {step} | {action} | {test_data} | {expected} |"


def _page_load_case(case_id: str, page_data: dict) -> str:
    title = page_data.get("title") or "page title"
    headings = page_data.get("headings") or []
    primary_heading = headings[0] if headings else "primary page content"
    rows = [
        _table_row(1, "Open the target URL in Chromium", page_data["url"], "Page loads without browser or HTTP error."),
        _table_row(2, "Read the browser page title", "N/A", f"Title is `{title}`."),
        _table_row(3, "Verify the primary page content is visible", "N/A", f"`{primary_heading}` is visible."),
        _table_row(4, "Check that the page remains on the expected URL", "N/A", "Current URL matches the loaded route or expected redirect."),
    ]
    return _format_case(
        case_id=case_id,
        name="Page loads with expected title and primary content",
        objective="Validate that the target URL is reachable and renders the expected page shell.",
        severity="Critical",
        rows=rows,
        post_conditions="Browser remains on the loaded page.",
    )


def _navigation_case(case_id: str, nav_links: list[dict]) -> str:
    rows = [
        _table_row(1, "Open the target URL", "N/A", "Page loads successfully."),
        _table_row(2, "Inspect the header or navigation area", "N/A", "Navigation links are visible and have readable names."),
    ]
    for index, link in enumerate(nav_links[:8], start=3):
        rows.append(
            _table_row(
                index,
                f"Verify navigation link `{link['text']}`",
                link.get("href") or "N/A",
                "Link has a non-empty href and can be used as a navigation target.",
            )
        )
    return _format_case(
        case_id=case_id,
        name="Primary navigation links are visible and usable",
        objective="Validate that the page exposes stable navigation anchors for users and tests.",
        severity="High",
        rows=rows,
        post_conditions="No navigation click is required; page state is unchanged.",
    )


def _form_required_case(case_id: str, form: dict, form_index: int) -> str:
    fields = form.get("fields", [])
    required_fields = [f for f in fields if f.get("required") or f.get("label")]
    submit_text = form.get("submit_text") or "submit"
    rows = [
        _table_row(1, "Open the target URL", "N/A", "Page loads successfully."),
        _table_row(2, f"Locate form #{form_index}", form.get("action") or "N/A", "Form is visible and ready for input."),
        _table_row(3, f"Click `{submit_text}` without filling required fields", "Empty form", "Validation prevents incomplete submission."),
    ]
    for index, field in enumerate(required_fields[:10], start=4):
        label = field.get("label") or field.get("name") or field.get("id") or field.get("tag")
        rows.append(
            _table_row(
                index,
                f"Verify validation feedback for `{label}`",
                "Empty value",
                "A visible validation message or browser required-field state is shown.",
            )
        )
    return _format_case(
        case_id=case_id,
        name=f"Form #{form_index} validates missing required input",
        objective="Confirm that incomplete form submission is blocked and visible feedback is provided.",
        severity="High",
        rows=rows,
        post_conditions="No valid data is submitted.",
    )


def _form_happy_path_case(case_id: str, form: dict, form_index: int) -> str:
    rows = [
        _table_row(1, "Open the target URL", "N/A", "Page loads successfully."),
        _table_row(2, f"Locate form #{form_index}", form.get("action") or "N/A", "Form fields are visible."),
    ]
    for index, field in enumerate(form.get("fields", [])[:12], start=3):
        label = field.get("label") or field.get("name") or field.get("id") or field.get("tag")
        value = _sample_value_for_field(field)
        rows.append(
            _table_row(
                index,
                f"Fill `{label}`",
                value,
                "Field accepts the value and keeps it visible.",
            )
        )
    rows.append(
        _table_row(
            len(rows) + 1,
            f"Click `{form.get('submit_text') or 'submit'}`",
            "N/A",
            "Submission completes or shows expected server-side feedback.",
        )
    )
    return _format_case(
        case_id=case_id,
        name=f"Form #{form_index} accepts valid user input",
        objective="Validate the expected happy-path behavior for the form.",
        severity="Normal",
        rows=rows,
        post_conditions="Application reaches the expected post-submit state or displays server feedback.",
    )


def _button_case(case_id: str, buttons: list[str]) -> str:
    rows = [
        _table_row(1, "Open the target URL", "N/A", "Page loads successfully."),
        _table_row(2, "Inspect visible command controls", "N/A", "Buttons and command links are visible with readable labels."),
    ]
    for index, text in enumerate(buttons[:10], start=3):
        rows.append(
            _table_row(
                index,
                f"Verify command `{text}` is discoverable",
                "N/A",
                "Control is visible, enabled, and has a clear accessible name.",
            )
        )
    return _format_case(
        case_id=case_id,
        name="Visible page commands are available",
        objective="Validate that important command controls can be discovered before deeper flow testing.",
        severity="Normal",
        rows=rows,
        post_conditions="Page state is unchanged.",
    )


def _format_case(
    case_id: str,
    name: str,
    objective: str,
    severity: str,
    rows: list[str],
    post_conditions: str,
) -> str:
    table = "\n".join(rows)
    return f"""### {case_id}: {name}
**Objective:** {objective}
**Severity:** {severity}

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
{table}

**Post-conditions:** {post_conditions}
"""


def _sample_value_for_field(field: dict) -> str:
    field_type = (field.get("type") or "").lower()
    name = (field.get("name") or field.get("id") or "").lower()

    if field_type == "email" or "email" in name:
        return "test_{timestamp}@example.com"
    if field_type == "password" or "password" in name:
        return "Password123!"
    if field_type in {"tel", "number"} or "phone" in name or "telephone" in name:
        return "123456789"
    if field_type == "checkbox":
        return "checked"
    if field_type == "radio":
        return "first available option"
    if field.get("tag") == "select":
        return "first non-empty option"
    if "search" in name:
        return "MacBook"
    return f"sample {field.get('label') or field.get('name') or 'value'}"


def _build_std(url: str, feature: str, page_data: dict, screenshot_path: Path) -> tuple[str, int]:
    headings = page_data.get("headings") or []
    forms = page_data.get("forms") or []
    buttons = page_data.get("buttons") or []
    nav_links = page_data.get("nav_links") or []
    alerts = page_data.get("alerts") or []

    feature_id = _slugify(feature).upper().replace("-", "_")
    cases: list[str] = [_page_load_case(f"TC-{feature_id}-01", page_data)]

    next_case = 2
    if nav_links:
        cases.append(_navigation_case(f"TC-{feature_id}-{next_case:02d}", nav_links))
        next_case += 1

    for form_index, form in enumerate(forms, start=1):
        cases.append(_form_required_case(f"TC-{feature_id}-{next_case:02d}", form, form_index))
        next_case += 1
        cases.append(_form_happy_path_case(f"TC-{feature_id}-{next_case:02d}", form, form_index))
        next_case += 1

    if buttons:
        cases.append(_button_case(f"TC-{feature_id}-{next_case:02d}", buttons))

    page_inventory = [
        f"- Title: `{page_data.get('title') or 'N/A'}`",
        f"- URL after load: `{page_data.get('url') or url}`",
        f"- Screenshot: `{screenshot_path.relative_to(_ROOT)}`",
        f"- Headings: {', '.join(headings) if headings else 'None found'}",
        f"- Forms found: {len(forms)}",
        f"- Buttons/commands found: {len(buttons)}",
        f"- Navigation links found: {len(nav_links)}",
        f"- Alerts visible on load: {', '.join(alerts) if alerts else 'None'}",
    ]

    content = f"""# STD-{feature_id}: {feature}

## Overview
| Field | Value |
|---|---|
| Test Suite | Web UI |
| Feature | {feature} |
| Priority | High |
| Author | Playwright CLI STD Agent |
| Date | {date.today().isoformat()} |
| Source URL | {url} |

## Objective
Validate the visible behavior, navigation anchors, forms, and command controls discovered on the target page.

## Playwright CLI Evidence
The agent captured the page with:

```bash
python -m playwright screenshot --wait-for-timeout 1000 "{url}" "{screenshot_path.relative_to(_ROOT)}"
```

## Page Inventory
{chr(10).join(page_inventory)}

## Preconditions
- Chromium browser binaries are installed for Playwright.
- The target URL is reachable from the test environment.
- Test data that mutates server state must use unique values or disposable accounts.
- Tests should start from a clean browser context.

## Test Cases

{chr(10).join(cases)}
## Notes
- Generated from live page structure; review expected results against product requirements before implementation.
- Refactor generated actions into page objects and flows before adding automation tests.
- Prefer accessible locators and user-visible labels when implementing these cases in Playwright.
"""
    return content, len(cases)


def run(url: str, feature: str | None = None, output: str | None = None) -> StdAgentResult:
    resolved_feature = feature or _feature_from_url(url)
    slug = _slugify(resolved_feature)
    screenshot_path = _ARTIFACTS_DIR / f"{slug}.png"

    print(f"Capturing page with Playwright CLI: {url}", flush=True)
    _run_playwright_screenshot(url, screenshot_path)

    print("Crawling page structure...", flush=True)
    page_data = crawl_page(url)

    content, case_count = _build_std(url, resolved_feature, page_data, screenshot_path)

    _STDS_DIR.mkdir(exist_ok=True)
    output_name = output or f"STD_{slug.replace('-', '_').title().replace('_', '')}.md"
    if not output_name.endswith(".md"):
        output_name += ".md"
    std_path = _STDS_DIR / output_name
    std_path.write_text(content, encoding="utf-8")

    print(f"Saved STD: {std_path}", flush=True)
    return StdAgentResult(
        url=url,
        std_path=std_path,
        screenshot_path=screenshot_path,
        title=page_data.get("title") or "",
        test_case_count=case_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a detailed STD for a webpage using Playwright CLI evidence."
    )
    parser.add_argument("url", help="Full URL of the webpage to analyze.")
    parser.add_argument("--feature", help="Feature name to use in the STD.")
    parser.add_argument("--output", help="Output Markdown filename under stds/.")
    args = parser.parse_args()

    result = run(args.url, feature=args.feature, output=args.output)
    print(f"Title: {result.title}")
    print(f"Test cases: {result.test_case_count}")
    print(f"Screenshot: {result.screenshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
