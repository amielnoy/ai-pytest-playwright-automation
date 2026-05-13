# Session 18 - Automation Learning: From Course Work to Daily Practice

## Learning Objectives

By the end of this session you will be able to:

- Build a personal automation learning plan with clear weekly outcomes.
- Convert manual test knowledge into automation tasks without skipping test design.
- Practice automation in small loops: observe, script, refactor, verify, report.
- Use code review feedback and failed tests as learning inputs.
- Choose the right next skill to learn based on framework gaps, not hype.
- Keep a learning portfolio that proves real capability through working tests.

---

## Why Automation Learning Needs Structure

Automation is not only "learning Playwright" or "learning Python." A strong automation engineer combines:

| Skill area | What it means in practice |
|---|---|
| Test design | Knowing what should be tested and what should not. |
| Programming | Writing readable, maintainable Python. |
| Browser automation | Controlling the UI through stable locators and page objects. |
| API automation | Preparing state and verifying contracts quickly. |
| Debugging | Reading failures, traces, logs, screenshots, and reports. |
| CI discipline | Running tests repeatably on another machine. |
| Communication | Explaining risk, failure cause, and coverage clearly. |

Weak automation learning focuses on tools first. Strong automation learning starts with behavior, risk, and feedback.

---

## The Automation Learning Loop

Use this loop for every new skill:

```
1. Observe   - Understand the product behavior manually.
2. Design    - Write the test idea, risk, inputs, and expected result.
3. Script    - Automate the smallest useful path.
4. Refactor  - Move selectors, setup, and assertions into the right layer.
5. Verify    - Run locally, inspect failure output, and rerun.
6. Report    - Add readable names, Allure steps, screenshots, and notes.
7. Reflect   - Write what failed, what changed, and what to practice next.
```

Skipping design creates automated noise. Skipping refactor creates brittle scripts. Skipping reflection means the same mistakes repeat.

---

## From Manual Scenario to Automation Task

Start with a manual scenario:

> A user searches for `iPod`, sorts results alphabetically, adds the first product to the cart, and verifies the cart total.

Convert it into automation tasks:

| Step | Automation decision |
|---|---|
| Search for `iPod` | Use `HomePage.search()` or a search flow. |
| Sort alphabetically | Add behavior to `SearchResultsPage`, not directly inside the test. |
| Add first product | Use a product card or page object method. |
| Verify cart total | Parse prices through a utility, assert exact expected total. |
| Report result | Add Allure title, story, severity, and steps. |

The learning target is not only "make the test pass." The target is to place every responsibility in the right framework layer.

---

## Weekly Learning Plan

Use a four-week cycle:

| Week | Focus | Output |
|---|---|---|
| 1 | Test design and selectors | Three manual cases and one automated smoke test. |
| 2 | Page objects and fixtures | Two tests with no raw selectors in test files. |
| 3 | API setup and contracts | One UI test shortened by API setup plus two API tests. |
| 4 | CI, reports, and debugging | One failing test analyzed through trace, screenshot, and Allure report. |

At the end of each week, write a short learning note:

- What behavior did I automate?
- What failed the first time?
- What did I move into the framework?
- What test is now easier to maintain?
- What is the next bottleneck?

---

## Practice Ladder

Do not jump from simple scripts directly to "AI agents." Build in layers:

| Level | Practice task | Evidence of readiness |
|---|---|---|
| 1 | Write one isolated Playwright test. | It passes twice locally and has clear assertions. |
| 2 | Move interactions into a page object. | The test has no raw locators. |
| 3 | Add fixtures and test data. | The test can run in parallel without shared state. |
| 4 | Add API setup or contract checks. | UI setup is shorter and failures are clearer. |
| 5 | Add reporting and debug artifacts. | A failed run explains itself through Allure or screenshots. |
| 6 | Add analysis tooling. | Repeated failures can be grouped by cause. |
| 7 | Add AI assistance. | AI output is reviewed, tested, and owned by the engineer. |

---

## What To Avoid

| Anti-pattern | Better approach |
|---|---|
| Recording long tests and committing them unchanged. | Refactor into page objects and focused assertions. |
| Adding sleeps after failures. | Wait for specific UI state or network behavior. |
| Automating every manual test. | Automate high-value, repeatable checks first. |
| Keeping selectors inside tests. | Hide UI structure inside page/component classes. |
| Trusting AI-generated tests without review. | Treat AI output like junior code: inspect, run, and improve. |
| Measuring learning by hours watched. | Measure by working tests, reviewed code, and solved failures. |

---

## Personal Automation Backlog

Keep a backlog with small tasks:

| Backlog item | Example |
|---|---|
| New test | Add coverage for cart quantity update. |
| Refactor | Move duplicate login steps into `LoginFlow`. |
| Debugging drill | Break a selector and diagnose the failure from trace output. |
| API setup | Create cart state through service layer instead of UI clicks. |
| Reporting | Add Allure steps and failure screenshot to a weak test. |
| CI improvement | Add a marker-based smoke job. |

Good backlog items are small enough to complete in one focused session.

---

## Session Completion Checklist

- [ ] I created a four-week automation learning plan.
- [ ] I converted one manual scenario into automation tasks.
- [ ] I identified the correct framework layer for each task.
- [ ] I automated or improved one small test.
- [ ] I wrote a short learning note with the failure, fix, and next step.
- [ ] I can explain what I should practice next and why.
