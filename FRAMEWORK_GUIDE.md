# Framework Guide — course/framework vs the Production Directories

## The Short Answer

| Directory | Purpose | Use it when… |
| --------- | ------- | ------------ |
| `course/framework/` | Teaching scaffold, session-by-session reference | Reading / studying patterns per session |
| `pages/` | Production page objects | Writing or extending real tests |
| `services/` | Production API service layer | Calling backend endpoints in tests |
| `flows/` | Multi-step reusable UI flows | Composing longer user journeys |
| `tests/` | Production test suite | Writing, running, and debugging real tests |

## Why Two Implementations Exist

Each course session builds on the one before it. `course/framework/` grows incrementally session by session — Session 3 adds Python foundations, Session 4 adds basic browser tests, Session 5 strengthens locator strategy, Session 6 adds exception handling, Session 7 teaches fixtures, Session 8 adds database helpers, Session 9 adds API contract helpers, Session 10 adds a fluent POM, Session 14 adds AI utilities, Session 25 adds Claude extension guidance, Session 26 adds Codex CLI workflows, Session 27 adds Claude connector workflows, Session 28 adds Ollama local-AI workflows, Session 29 adds Docker Compose monitoring, Session 30 adds AWS EC2/S3 deployment testing for Allure TestOps, and so on. This lets you read each session's framework code in isolation and understand exactly what was introduced.

The `pages/` / `services/` / `tests/` directories contain the final, fully integrated version — the state the framework reaches after all sessions are applied. This is the codebase you run in CI, extend for new features, and submit for the capstone.

## Production Page Object Conventions

The production page layer follows these rules:

- Stable locators are initialized as instance data members in each page object or component constructor.
- Methods should call those initialized members instead of reconstructing the same locator.
- Locators that require runtime data stay close to the method input. Example: opening a product by `product_name`.
- CSS-only locators should use deterministic self-healing fallbacks from `pages/self_healing.py` when there is a reasonable backup selector.
- Self-healing is reviewable, not silent: fallback usage is recorded as `SelfHealEvent` and exposed through `self_heal_events()`.

This keeps tests readable, makes locator ownership explicit, and gives reviewers a concrete signal when a primary selector has drifted.

## What Goes Where

```text
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
  session_29_docker_compose_grafana/ ← illustrates Compose, Prometheus, and Grafana
  session_30_aws_allure_testops/  ← illustrates AWS EC2, S3, TestOps, and Allure 3 checks
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
`pages/your_new_page.py`. Extend `BasePage` from `pages/base_page.py`, initialize stable locators in `__init__`, and expose business-level actions from methods.

**"When should I add self-healing?"**
Use deterministic self-healing only for CSS-heavy selectors that have a clear, explicit fallback. Do not use it to hide a weak locator strategy. Prefer semantic Playwright locators first.

**"I want to add a new API service. Where does it go?"**
`services/api/your_new_service.py`. Use `services/rest_client.py` for all HTTP calls.

**"I want to add more search queries or security payloads without editing Python."**
Add cases to the relevant `data/*.json` file. `get_data_file("filename.json")` in `utils/data_loader.py` loads it at import time into a `@pytest.mark.parametrize` list. The shipped corpora are `data/api_test_cases.json` (search, price, cart cases) and `data/pentest_cases.json` (injection, auth, ACL, file-exposure vectors).

## Capstone Rule

For the capstone project, all deliverables must live in the production directories (`pages/`, `services/`, `flows/`, `tests/`). Work in `course/framework/` does not count toward the capstone checklist.

## Secrets

- `data/secrets.json` is gitignored and created only at runtime (local copy or CI from `TEST_SECRETS_JSON`).
- Commit `data/secrets.json.example` for structure, not real credentials.
- Do not log passwords in Allure step names; the production registration test only names the email in steps.
