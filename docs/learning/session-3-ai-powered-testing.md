# Session 3 — AI-Powered Testing (90 min)

**Audience:** Attendees of Sessions 1–2.
**Goal:** Cover both directions of "AI testing": testing AI systems (chat endpoint, prompt injection, DLP) and using AI to test (failure-analysis agent, test planner agent, Claude slash commands + Playwright MCP).

## Agenda

### 1. Two meanings of "AI testing" (5 min)

- Direction A: your product contains an LLM — how do you test it deterministically?
- Direction B: AI as a force multiplier for the tester — generating, reviewing, and triaging tests.

### 2. Testing an AI endpoint (25 min)

- `server/app.py` — local FastAPI wrapper around the Anthropic API; with no `ANTHROPIC_API_KEY` it returns deterministic mock responses, so tests run anywhere. Metrics auto-collected via `prometheus-fastapi-instrumentator`.
- `tests/api/test_chat_ai.py` — functional behavior of `/chat` through `services/api/chat_service.py`. Run: `pytest -m ai tests/api/test_chat_ai.py`.
- **Prompt injection:** `tests/api/test_prompt_injection.py` — the SENTINEL technique: assert a string that would appear *only if* the attack succeeded. Covers direct override, role replacement, and system-prompt leak. Key lesson: deterministic assertions about non-deterministic systems.
- **DLP:** `tests/api/test_chat_dlp.py` — asserting secrets/PII don't leak into responses.
- **Security suites:** `tests/api/test_pentest.py`, `test_pentest_data_driven.py` driven by `data/pentest_cases.json`.

### 3. AI agents that analyze failures (20 min)

- `agents/allure_failure_agent.py` — reads `allure-results/`, classifies each failure into categories (`product_bug`, `dom_change`, `automation_bug`, `environment_issue`, `flaky`) using a RAG-augmented LLM prompt (Groq).
- Live demo on the failing results saved in Session 2: `./scripts/run_allure_failure_agent.sh` (requires `GROQ_API_KEY` in `.env`; use `--no-ai` for heuristic-only mode if no key).
- Unit-tested like any other code: `tests/unit/test_allure_failure_agent.py` — agents are software; test them.

### 4. AI agents that plan and write tests (15 min)

- `agents/test_planner_agent.py` + `agents/page_crawler.py` — Playwright crawls a live page into structured JSON, Claude produces an STD (Software Test Document) into `stds/`, with `read_existing_tests()` as context so it doesn't duplicate coverage.
- Discussion: the human stays in the loop — the agent proposes, the engineer reviews.

### 5. Claude Code tooling on this repo (15 min)

- Slash commands in `.claude/commands/`: demo `/generate-test user can add to cart` and `/review-tests tests/web-ui/` live. Also cover `/create-page-object`, `/fix-selectors`, `/analyze-failures`, `/add-allure`.
- Playwright MCP server (`.claude/settings.json`) — lets Claude drive a real browser to inspect elements when creating page objects.
- `CLAUDE.md` as the contract that keeps AI-generated code following project conventions (skills for UI/API/contract/unit/DevOps/review).

### 6. Monitoring the whole thing (5 min)

- `npm run test:compose:report` — tests + Grafana (http://localhost:3000) + Prometheus (http://localhost:9090) + Swagger UI (http://localhost:8090). Show the Automation Runs dashboard.

### 7. Hands-on exercise & wrap-up (5 min)

1. Add one new injection payload with a fresh SENTINEL to `tests/api/test_prompt_injection.py` and run it.
2. Stretch: run the failure agent with `--no-ai` and compare its heuristic bucket to the AI classification.
3. Closing discussion: which of these patterns applies to your product first?

## Instructor checklist

- [ ] `GROQ_API_KEY` in `.env` for the live agent demo (fallback: `--no-ai`).
- [ ] Docker Desktop running for the Compose/monitoring demo.
- [ ] A failing `allure-results/` set available (from Session 2 homework or run `pytest tests/web-ui/test_intentional_failure.py --alluredir=allure-results`).
