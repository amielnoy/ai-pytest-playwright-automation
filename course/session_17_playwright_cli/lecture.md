# Session 17 - Playwright CLI: Codegen, Debugging, Screenshots, and Traces

## Learning Objectives

By the end of this session you will be able to:

- Use the Playwright CLI to install browsers, inspect pages, and generate starter scripts.
- Run `codegen` as a learning and discovery tool without committing raw generated code.
- Capture screenshots and traces for debugging.
- Use CLI output to improve page objects and assertions in the production framework.
- Explain when CLI tools are useful and when pytest tests are the correct execution path.

---

## Python Playwright CLI

This project uses Playwright for Python. The most portable CLI form is:

```bash
python3 -m playwright <command>
```

Inside an activated virtual environment, this may also work:

```bash
playwright <command>
```

Use `python3 -m playwright` in course instructions because it does not depend on the shell PATH.

---

## Core Commands

| Command | Purpose |
|---|---|
| `python3 -m playwright install chromium` | Install Chromium browser binaries. |
| `python3 -m playwright codegen <url>` | Open a browser and generate actions while you interact. |
| `python3 -m playwright open <url>` | Open a page for quick manual inspection. |
| `python3 -m playwright screenshot <url> <file>` | Capture a screenshot without writing a test. |
| `python3 -m playwright show-trace <trace.zip>` | Open a saved Playwright trace. |

The CLI is for discovery, debugging, and learning. The durable test suite still runs through `pytest`.

---

## Codegen Workflow

Use codegen to discover locators and interaction order:

```bash
python3 -m playwright codegen https://tutorialsninja.com/demo
```

Recommended workflow:

1. Perform the flow manually in the codegen browser.
2. Copy only the useful locator ideas.
3. Move interactions into `pages/` or `pages/components/`.
4. Write assertions in `tests/`.
5. Delete raw generated script code unless it is being kept as a temporary learning note.

Generated code is a draft, not framework-quality automation.

---

## Turning Codegen Into Page Objects

Raw generated code often looks like this:

```python
page.get_by_placeholder("Search").fill("iPod")
page.get_by_role("button", name="Search").click()
expect(page.get_by_text("iPod")).to_be_visible()
```

Production framework shape:

```python
home_page.search("iPod")
search_results_page.expect_results_for("iPod")
```

The test should describe behavior. The page object should own locators and Playwright calls.

---

## Screenshots From the CLI

Use screenshots when you need quick visual evidence:

```bash
python3 -m playwright screenshot https://tutorialsninja.com/demo artifacts/home.png
```

Good uses:

- Confirm the application is reachable.
- Capture a page state before writing a test.
- Attach visual evidence to a bug report.
- Compare what a student sees with what the instructor expects.

Do not use CLI screenshots as a replacement for assertions.

---

## Trace Viewer

When a pytest Playwright test records a trace, inspect it with:

```bash
python3 -m playwright show-trace path/to/trace.zip
```

Trace viewer helps answer:

- What action ran before the failure?
- What locator was used?
- What did the page look like at that moment?
- Which network calls happened?
- Did the test fail because of product behavior, selector drift, or timing?

---

## CLI vs Test Runner

| Need | Use |
|---|---|
| Learn a flow manually | `codegen` |
| Inspect current page state | `open` |
| Capture visual evidence | `screenshot` |
| Debug a saved run | `show-trace` |
| Verify product behavior repeatedly | `pytest` |
| Run in CI | `pytest`, not `codegen` |
| Produce Allure reporting | `pytest --alluredir=allure-results` |

The CLI is a workshop tool. The automated suite is the product.

---

## Session Completion Checklist

- [ ] I installed Chromium with the Playwright CLI.
- [ ] I ran `codegen` against the demo store.
- [ ] I translated one generated action into a page object method.
- [ ] I captured one screenshot from the CLI.
- [ ] I can explain why raw codegen output should not be committed as a final test.
- [ ] I can explain when to use `show-trace` during debugging.
