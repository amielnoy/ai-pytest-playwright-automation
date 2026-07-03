# AI Testing Learning Series

Three 90-minute hands-on sessions for QA engineers new to automation, built entirely on this repository.

| Session | Title | Focus |
|---|---|---|
| [1](session-1-foundations.md) | Foundations: Playwright, POM & Fixtures | Run and understand real UI tests |
| [2](session-2-beyond-the-ui.md) | Beyond the UI: API, Contract & Resilient Tests | Test layers, service classes, self-healing |
| [3](session-3-ai-powered-testing.md) | AI-Powered Testing | Testing AI, AI agents that test, Claude tooling |

## Prerequisites (send to attendees before Session 1)

```bash
git clone <repo> && cd AI_AUTOMATION_TESTING
pip install -r requirements.txt
playwright install chromium
pytest tests/unit -q        # should pass with no browser or network
```

- Python 3.11+, Node.js (for Allure), Docker Desktop (Session 3 only).
- No prior automation experience assumed.

## Format

Each session: ~20 min instructor walkthrough, ~50 min guided hands-on, ~15 min exercise, ~5 min wrap-up. Every code reference points at a real file in this repo — open the files live rather than using slides.

## Related material

- **AI Testing Academy** landing pages with live in-browser AI agents (a QA-Automation resume evaluator and an interview-prep helper): [`../../ai-testing-academy/ai-testing-academy.html?lang=he`](../../ai-testing-academy/ai-testing-academy.html?lang=he) (Hebrew) and [`../../ai-testing-academy/ai-testing-academy.html`](../../ai-testing-academy/ai-testing-academy.html) (English). Short explainer clips live in [`../../ai-testing-academy/videos/`](../../ai-testing-academy/videos/README.md).
- **Log analysis notebook** — [`../../notebooks/load_logs_with_pandas.ipynb`](../../notebooks/load_logs_with_pandas.ipynb) loads `logs/automation.log` into pandas for quick summaries (pairs well with Session 1's first test run).
