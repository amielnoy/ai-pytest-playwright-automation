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
| [1](session_1_qa_foundations/lecture.md) | QA Foundations & Manual Testing | Write clear test cases, bug reports, risk analysis, and exploratory charters. |
| [2](session_2_ai_qa/lecture.md) | QA in the AI Era | Use AI for QA work without losing verification discipline. |
| [3](session_3_playwright_basics/lecture.md) | Playwright Basics | Write the first browser tests with fixtures, locators, and assertions. |
| [4](session_4_playwright_locators/lecture.md) | Playwright Locators | Apply Playwright locator best practices for stable, maintainable tests. |
| [5](session_5_pytest_fixtures/lecture.md) | pytest Fixtures | Build explicit, scoped, parallel-safe setup and teardown. |
| [6](session_6_pom_ui_api/lecture.md) | POM + UI + API | Build reusable page objects and combine UI flows with API setup. |
| [7](session_7_test_data_strategy/lecture.md) | Test Data Strategy | Manage static, generated, API-created, and secret data safely. |
| [8](session_8_mini_project/lecture.md) | Mini Project | Build one complete feature slice before advanced topics. |
| [9](session_9_debugging_playwright/lecture.md) | Debugging Playwright | Diagnose selector, timing, data, environment, and product failures. |
| [10](session_10_ai_tools/lecture.md) | AI Tools for QA | Add self-healing and command-line analysis utilities. |
| [11](session_11_mcp_agents/lecture.md) | MCP & AI Agents | Explore agent-driven regression planning and codebase inspection. |
| [12](session_12_ci_cd_ai_analysis/lecture.md) | CI/CD & Failure Analysis | Analyze flaky tests and CI failures with repeatable tooling. |
| [13](session_13_reporting_ci/lecture.md) | Allure 3 + GitHub Pages | Publish readable reports with trend history through CI. |
| [14](session_14_automation_learning/lecture.md) | Automation Learning | Turn course work into a structured learning plan and portfolio. |
| [15](session_15_ai_agents_for_testing/lecture.md) | AI Agents for Testing | Use agents for test planning, exploration, and QA review with guardrails. |
| [16](session_16_agentic_automation_testing/lecture.md) | Agentic Automation Testing | Design supervised agent workflows for failure investigation and CI analysis. |
| [17](session_17_playwright_cli/lecture.md) | Playwright CLI | Use codegen, screenshots, and trace viewer as learning and debugging tools. |
| [18](session_18_automation_code_review/lecture.md) | Automation Code Review | Review tests for reliability, layering, fixtures, data, and report quality. |
| [19](session_19_capstone/lecture.md) | Capstone Framework | Deliver production-level framework changes in the real project structure. |

## How To Use Each Session

1. Read `lecture.md` and run the examples in `lecture.py` where present.
2. Inspect the supporting files in the same session directory.
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

## Suggested Session Workflow

Use this rhythm for every session:

```bash
# 1. Run examples or tests for the current session
pytest course/session_3_playwright_basics -q

# 2. Run the related production test slice
pytest tests/web-ui -q

# 3. Check collection before broader runs
pytest --collect-only -q
```

Adjust the paths for the current topic. For example, Session 12 maps mostly to CI and failure analysis, while Session 13 maps to Allure reporting and pipeline validation.

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
- Build a realistic automation learning plan based on framework gaps and feedback.
- Use AI agents for bounded testing workflows while keeping deterministic tests as release gates.
- Use the Playwright CLI for discovery and debugging, then refactor useful output into the framework.
- Choose stable Playwright locators according to official best practices and keep locator details inside page objects.

## Capstone Rule

Capstone deliverables must be implemented in the production directories (`pages/`, `services/`, `flows/`, `tests/`, `data/`, and configuration files as needed). Changes made only inside `course/framework/` or a session folder are reference work and do not count as production deliverables.
