# Automation QA Course

This course teaches practical QA automation from manual test design through a production-ready Playwright, pytest, API, AI tooling, CI, and reporting framework.

The course is designed to be followed in order. Each session contains:

- `lecture.md` — concepts, patterns, and reference notes.
- `lecture.py` — runnable examples or instructor demo code.
- `EXERCISES.md` — hands-on work for students.
- Supporting Python files — focused examples for that session.

## Prerequisites

Before starting, set up the repository from the project root:

```bash
pip install -r requirements.txt
playwright install chromium
npm install
```

Run a quick verification:

```bash
pytest --collect-only -q
```

## Learning Path

| Session | Topic | Main outcome |
|---|---|---|
| [1](session_01_qa_foundations/lecture.md) | QA Foundations & Manual Testing | Write clear test cases, bug reports, risk analysis, and exploratory charters. |
| [2](session_02_ai_qa/lecture.md) | QA in the AI Era | Use AI for QA work without losing verification discipline. |
| [3](session_03_python_foundations/lecture.md) | Python Foundations | Learn the Python syntax, data structures, and helper patterns used in automation. |
| [4](session_04_playwright_basics/lecture.md) | Playwright Basics | Write the first browser tests with fixtures, locators, and assertions. |
| [5](session_05_playwright_locators/lecture.md) | Playwright Locators | Apply Playwright locator best practices for stable, maintainable tests. |
| [6](session_06_exception_handling/lecture.md) | Exception Handling | Turn expected automation errors into clear failures without hiding bugs. |
| [7](session_07_pytest_fixtures/lecture.md) | pytest Fixtures | Build explicit, scoped, parallel-safe setup and teardown. |
| [8](session_08_database_testing/lecture.md) | Database Testing | Validate schema constraints, persistence rules, migrations, and API-to-database behavior. |
| [9](session_09_api_testing/lecture.md) | API Testing | Design API smoke, contract, negative, state, and integration coverage. |
| [10](session_10_pom_ui_api/lecture.md) | POM + UI + API | Build reusable page objects and combine UI flows with API setup. |
| [11](session_11_test_data_strategy/lecture.md) | Test Data Strategy | Manage static, generated, API-created, and secret data safely. |
| [12](session_12_mini_project/lecture.md) | Mini Project | Build one complete feature slice before advanced topics. |
| [13](session_13_debugging_playwright/lecture.md) | Debugging Playwright | Diagnose selector, timing, data, environment, and product failures. |
| [14](session_14_ai_tools/lecture.md) | AI Tools for QA | Add self-healing and command-line analysis utilities. |
| [15](session_15_mcp_agents/lecture.md) | MCP & AI Agents | Explore agent-driven regression planning and codebase inspection. |
| [16](session_16_ci_cd_ai_analysis/lecture.md) | CI/CD & Failure Analysis | Analyze flaky tests and CI failures with repeatable tooling. |
| [17](session_17_reporting_ci/lecture.md) | Allure 3 + GitHub Pages | Publish readable reports with trend history through CI. |
| [18](session_18_automation_learning/lecture.md) | Automation Learning | Turn course work into a structured learning plan and portfolio. |
| [19](session_19_ai_agents_for_testing/lecture.md) | AI Agents for Testing | Use agents for test planning, exploration, and QA review with guardrails. |
| [20](session_20_agentic_automation_testing/lecture.md) | Agentic Automation Testing | Design supervised agent workflows for failure investigation and CI analysis. |
| [21](session_21_playwright_cli/lecture.md) | Playwright CLI | Use codegen, screenshots, and trace viewer as learning and debugging tools. |
| [22](session_22_automation_code_review/lecture.md) | Automation Code Review | Review tests for reliability, layering, fixtures, data, and report quality. |
| [23](session_23_capstone/lecture.md) | Capstone Framework | Deliver production-level framework changes in the real project structure. |
| [24](session_24_claude_code/lecture.md) | Claude Code Integration | Use Claude Code slash commands and Playwright MCP for QA workflows. |
| [25](session_25_claude_skills_plugins/lecture.md) | Claude Skills & Plugins | Extend Claude workflows with skills, plugins, MCP, and slash commands safely. |
| [26](session_26_codex_cli/lecture.md) | Codex CLI | Use Codex CLI for scoped codebase edits, reviews, fixes, and verification. |
| [27](session_27_claude_connectors/lecture.md) | Claude Connectors | Use connectors for PRs, docs, chat, email, and calendar QA workflows safely. |
| [28](session_28_ollama_local_ai/lecture.md) | Ollama Local AI | Use local models for QA summaries, test ideas, failure classification, and small reviews. |
| [29](session_29_docker_compose_grafana/lecture.md) | Docker Compose + Grafana | Run automation through Docker Compose and monitor test health with Prometheus and Grafana. |

## How To Use Each Session

1. Read `lecture.md` and run the examples in `lecture.py` where present.
2. Inspect the supporting files in the same session directory and the matching `course/framework/` layer when the session adds reusable Python behavior.
3. Complete `EXERCISES.md`.
4. Run the narrowest relevant tests before moving on.
5. Update production code only when the exercise or capstone explicitly asks for it.

## Where Student Work Goes

The session directories are teaching material. For production framework work, use the main project directories:

| Work type | Directory |
|---|---|
| UI page objects | `pages/` |
| Reusable flows | `flows/` |
| API clients/services | `services/` |
| Test data | `data/` |
| Real tests | `tests/` |
| Teaching reference framework | `course/framework/` |

See [`../FRAMEWORK_GUIDE.md`](../FRAMEWORK_GUIDE.md) for the full explanation of `course/framework/` versus the production directories.

Reusable Python code introduced by a course session should evolve `course/framework/` where practical. Session files should import that framework code and demonstrate it through focused examples and tests.

## Suggested Session Workflow

Use this rhythm for every session:

```bash
# 1. Run examples or tests for the current session
pytest course/session_04_playwright_basics -q

# 2. Run the related production test slice
pytest tests/web-ui -q

# 3. Check collection before broader runs
pytest --collect-only -q
```

Adjust the paths for the current topic. For example, Session 16 maps mostly to CI and failure analysis, while Session 17 maps to Allure reporting and pipeline validation.

## Course Support Files

- [`RUBRICS.md`](RUBRICS.md) — grading criteria for exercises and project work.
- [`BEFORE_AFTER_EXAMPLES.md`](BEFORE_AFTER_EXAMPLES.md) — weak vs strong automation examples.
- [`INSTRUCTOR_NOTES.md`](INSTRUCTOR_NOTES.md) — timing, prompts, and common student mistakes.
- [`PROJECT_CHECKLIST.md`](PROJECT_CHECKLIST.md) — cumulative checklist that feeds the capstone.

## Completion Criteria

A student is ready for the capstone when they can:

- Explain which test layer should cover a behavior and why.
- Write stable Playwright tests through page objects rather than raw selectors in tests.
- Build explicit pytest fixtures with safe scopes and cleanup.
- Use API setup to reduce slow or brittle UI setup.
- Keep test data isolated and repeatable.
- Diagnose common flaky-test causes.
- Produce Allure reports that are useful to non-engineers.
- Run the suite locally, in Docker, and in CI.
- Run and observe automation through Docker Compose, Prometheus, and Grafana.
- Build a realistic automation learning plan based on framework gaps and feedback.
- Use AI agents for bounded testing workflows while keeping deterministic tests as release gates.
- Use the Playwright CLI for discovery and debugging, then refactor useful output into the framework.
- Choose stable Playwright locators according to official best practices and keep locator details inside page objects.
- Add focused database tests for persistence risks without coupling every UI/API test to SQL.

## Capstone Rule

Capstone deliverables must be implemented in the production directories (`pages/`, `services/`, `flows/`, `tests/`, `data/`, and configuration files as needed). Changes made only inside `course/framework/` or a session folder are reference work and do not count as production deliverables.
