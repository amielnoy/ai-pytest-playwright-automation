---
name: plan-tests
description: Produce Software Test Documents (STDs) for a feature by crawling live pages with Playwright, then writing one STD per feature to stds/. Use when the user wants a test plan / STDs before any tests are written.
---

# Plan tests (STDs)

Turn live pages into detailed **Software Test Documents** under `stds/`.

**Input:** the demo-store pages to cover (or "all major features").
**Output:** `stds/STD_<Feature>.md`, matching the format of the existing files in `stds/`.

## Preferred: run the planner agent
Needs `ANTHROPIC_API_KEY` in `.env`. From the repo root:

```bash
python -m agents.test_planner_agent
# or specific URLs are configured inside the agent
```

## Or do it directly
1. Crawl each relevant page's structure (forms, fields, buttons, nav, alerts) — use the Playwright MCP or `agents/page_crawler.py`.
2. Read existing tests in `tests/` to avoid planning duplicate coverage.
3. Write one STD per feature to `stds/STD_<Feature>.md` following the exact structure of the existing STDs (Overview table, Objective, Preconditions, numbered Test Cases with Step/Action/Test Data/Expected Result, Post-conditions). Steps must be concrete; reference only elements that actually exist on the page.

Next stage: **write-tests** turns these STDs into runnable tests.
