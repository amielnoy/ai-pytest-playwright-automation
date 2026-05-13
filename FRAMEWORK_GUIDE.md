# Framework Guide — course/framework vs the Production Directories

## The Short Answer

| Directory | Purpose | Use it when… |
|---|---|---|
| `course/framework/` | Teaching scaffold, session-by-session reference | Reading / studying patterns per session |
| `pages/` | Production page objects | Writing or extending real tests |
| `services/` | Production API service layer | Calling backend endpoints in tests |
| `flows/` | Multi-step reusable UI flows | Composing longer user journeys |
| `tests/` | Production test suite | Writing, running, and debugging real tests |

## Why Two Implementations Exist

Each course session builds on the one before it. `course/framework/` grows incrementally session by session — Session 3 adds Python foundations, Session 4 adds basic browser tests, Session 5 strengthens locator strategy, Session 6 adds exception handling, Session 7 teaches fixtures, Session 8 adds database helpers, Session 9 adds API contract helpers, Session 10 adds a fluent POM, Session 14 adds AI utilities, Session 25 adds Claude extension guidance, Session 26 adds Codex CLI workflows, Session 27 adds Claude connector workflows, Session 28 adds Ollama local-AI workflows, and so on. This lets you read each session's framework code in isolation and understand exactly what was introduced.

The `pages/` / `services/` / `tests/` directories contain the final, fully integrated version — the state the framework reaches after all sessions are applied. This is the codebase you run in CI, extend for new features, and submit for the capstone.

## What Goes Where

```
course/
  session_03_python_foundations/  ← illustrates Python helpers for automation
  session_04_playwright_basics/   ← illustrates basic fixtures and locators
  session_05_playwright_locators/ ← illustrates locator best practices
  session_06_exception_handling/  ← illustrates clear framework exceptions
  session_07_pytest_fixtures/     ← illustrates fixture design
  session_08_database_testing/    ← illustrates database testing helpers
  session_09_api_testing/         ← illustrates API contracts and helpers
  session_10_pom_ui_api/          ← illustrates POM + fluent API
  session_14_ai_tools/            ← illustrates self-healing and CLI tools
  session_15_mcp_agents/          ← illustrates the agent loop
  session_25_claude_skills_plugins/ ← illustrates skills, plugins, MCP, and commands
  session_26_codex_cli/           ← illustrates Codex CLI codebase workflows
  session_27_claude_connectors/   ← illustrates connector permissions and QA use cases
  session_28_ollama_local_ai/     ← illustrates local model workflows with Ollama
  ...
  framework/                     ← aggregated teaching scaffold (read-only reference)

pages/                           ← PRODUCTION: extend these for new page coverage
services/                        ← PRODUCTION: extend these for new API coverage
flows/                           ← PRODUCTION: compose new user flows here
tests/                           ← PRODUCTION: write and run real tests here
```

## Evolving Framework Rule

When a session introduces reusable Python behavior, put that behavior in `course/framework/` first and let the session file import it. Session directories should demonstrate and exercise the framework, not become parallel mini-frameworks. Pure lecture-only constants or one-off demos can stay in the session folder.

## Common Confusion Points

**"Should I import from `course/framework/` in my test?"**
No. The production tests import from `pages/`, `services/`, and `flows/`. `course/framework/` is a read-only reference.

**"The session code has a `LoginPage` and `pages/login_page.py` also has a `LoginPage`. Which one do I use?"**
Use `pages/login_page.py`. The session version demonstrates the pattern; the production version is the one wired into fixtures and kept up to date.

**"I want to add a new page object. Where do I put it?"**
`pages/your_new_page.py`. Extend `BasePage` from `pages/base_page.py`.

**"I want to add a new API service. Where does it go?"**
`services/api/your_new_service.py`. Use `services/rest_client.py` for all HTTP calls.

## Capstone Rule

For the capstone project, all deliverables must live in the production directories (`pages/`, `services/`, `flows/`, `tests/`). Work in `course/framework/` does not count toward the capstone checklist.
