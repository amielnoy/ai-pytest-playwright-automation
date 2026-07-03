---
name: heal-test
description: Diagnose and fix a FAILING Playwright + pytest test — prefer healing the Page Object selector over changing the test, then re-run to verify. Use when a web-ui test is failing or flaky.
---

# Heal a failing test

**Input:** a failing test — a file name or pytest node id (e.g. `test_login.py::TestLogin::test_valid`).
**Output:** a repaired Page Object / test that passes (or a clearly-reported product bug).

## Preferred: run the healer agent
Needs `ANTHROPIC_API_KEY` in `.env`. From the repo root:

```bash
python -m agents.test_healer_agent test_login.py::TestLogin::test_valid
```

## Or do it directly
1. **Reproduce:** run the failing target and read the traceback
   (`pytest tests/web-ui/<file> -p no:xdist -o addopts= -q`).
2. **Diagnose the category:**
   - **DOM / selector drift** — a locator no longer matches. Fix it in the **Page Object** (`pages/…`), not the test; prefer stable locators (role/label/id) and the existing self-healing helper.
   - **Automation bug** — wrong step order, bad wait, mis-scoped assertion. Fix the test or the page-object method.
   - **Real product bug** — the app genuinely misbehaves. Do **not** weaken the assertion to force a pass; leave it failing and report it as a product defect.
3. **Re-run after every change** until green (or the product bug is confirmed).
4. Keep raw selectors in Page Objects, preserve the test's intent, Allure decorators and marker. Only regenerate from the STD (via **write-tests**) as a last resort.
