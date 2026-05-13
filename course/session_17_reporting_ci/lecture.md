# Session 17 — Reporting & CI: Allure 3 + GitHub Pages

## Learning Objectives

By the end of this session you will be able to:

- Decorate every test with `@allure.feature`, `@allure.story`, `@allure.title`, and `@allure.severity`.
- Wrap test steps with `with allure.step(...)` so the report shows a readable step trace.
- Configure `categories.json` and `environment.properties` to enrich the Allure overview tab.
- Run the two-job GitHub Actions pipeline: test job uploads results, report job publishes to GitHub Pages.
- Preserve trend history across runs by copying `allure-history/` before generating the report.
- Distinguish Allure 3 from Allure 2 and use the correct `npm`-based install and generate command.

---

## Why Allure?

pytest's built-in terminal output is unreadable for non-engineers and disappears when the terminal closes.
Allure generates a persistent HTML report with pass/fail trends, step-level detail, and screenshots attached on failure.
Stakeholders can open a URL and see exactly what broke, with a screenshot and the full step trace.

---

## Allure Decorator Pattern

Every test class and function must be decorated:

```python
@allure.feature("Cart")
@allure.story("Add to cart")
class TestCart:
    @allure.title("Add one item — badge shows 1")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_single_item(self, page):
        with allure.step("Click Add to cart"):
            …
        with allure.step("Verify badge"):
            …
```

`allure.feature` groups tests in the Features tab. `allure.title` replaces the function name in the UI. `allure.step` makes each logical action visible in the step trace.

---

## allure-results Directory

After a pytest run, `allure-results/` contains:

- `*-result.json` — one file per test: status, steps, attachments, labels.
- `*-container.json` — fixture setup/teardown for a group of tests.
- `categories.json` — (optional) maps failure patterns to human-readable category names.
- `environment.properties` — key-value pairs shown on the Overview tab (browser, URL, CI run number).

Place `categories.json` and `environment.properties` in `allure-results/` **before** running `npx allure generate`.

---

## Two-Job GitHub Actions Pipeline

**Job 1 — test**: runs pytest, uploads `allure-results/` as an artifact (retained 7 days).

**Job 2 — report** (`needs: test`, `if: always()`):
1. Downloads `allure-results/` artifact.
2. Checks out the `gh-pages` branch to restore `allure-history/` for trend charts.
3. Runs `npx allure generate allure-results` → `allure-report/`.
4. Copies `allure-history/` into the new report for the next run.
5. Publishes `allure-report/` to the `gh-pages` branch.

The `if: always()` condition ensures the report is published even when tests fail.

---

## Allure 3 vs Allure 2 Key Differences

- Install via **npm** (`allure-commandline`), not `apt` or `brew` — consistent on all CI runners.
- Command: `npx allure generate allure-results` (no `--clean` flag; output dir is `allure-report/`).
- Trend charts require copying `allure-history/` from the **previous** report into the results dir **before** running generate.
- Configure the results directory in `pytest.ini`: `addopts = --alluredir=allure-results`.

---

## Session Completion Checklist

You have finished the course. Before calling the project done, verify:

- [ ] Every test class has `@allure.feature` and `@allure.story`; every test method has `@allure.title` and `@allure.severity`.
- [ ] At least one test has `with allure.step(...)` blocks and the report shows them.
- [ ] `categories.json` and `environment.properties` are present in `allure-results/` and appear in the report.
- [ ] The two-job pipeline runs end-to-end: tests pass, `allure-results` artifact is uploaded, report is published to GitHub Pages.
- [ ] Trend charts show at least two runs (i.e. `allure-history/` was copied correctly on the second run).
- [ ] Running `npm run allure:version` prints `3.x`.
- [ ] I completed the exercises in `EXERCISES.md`.
- [ ] The full Capstone Checklist in Session 23 is satisfied.
