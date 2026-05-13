# Session 21 - Exercises

## Exercise 1: Verify CLI Availability

Run:

```bash
python3 -m playwright --help
```

If that works, run:

```bash
python3 -m playwright install chromium
```

Record:

- Command used.
- Whether it succeeded.
- Any setup issue you had to fix.

---

## Exercise 2: Use Codegen for Locator Discovery

Run:

```bash
python3 -m playwright codegen https://tutorialsninja.com/demo
```

Perform this flow:

1. Search for `iPod`.
2. Open one product.
3. Add it to the cart.
4. Open the cart.

Copy three generated locators into your notes and classify each as:

- Good locator.
- Acceptable but could be improved.
- Fragile locator.

Explain why.

---

## Exercise 3: Refactor Codegen Into the Framework

Take one generated interaction from Exercise 2.

Refactor it into the correct production layer:

- Page behavior goes in `pages/`.
- Reusable flow behavior goes in `flows/`.
- Assertion stays in `tests/`.

Run the narrowest relevant test after the change.

---

## Exercise 4: Capture Visual Evidence

Create an `artifacts/` directory if needed, then run:

```bash
python3 -m playwright screenshot https://tutorialsninja.com/demo artifacts/tutorialsninja-home.png
```

Use the screenshot to write a short observation:

- Page loaded: yes or no.
- Visible page title or header.
- One element you would use as a stable test anchor.

---

## Exercise 5: Trace Debugging Plan

Find or create a Playwright trace from a failing test run.

Open it with:

```bash
python3 -m playwright show-trace path/to/trace.zip
```

Write a debugging note with:

- Failing action.
- Locator used.
- Page state at failure.
- Likely root cause.
- Fix or next experiment.
