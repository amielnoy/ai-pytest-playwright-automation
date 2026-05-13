# Session 26 - Codex CLI For QA Automation

## Learning Objectives

By the end of this session you will be able to:

- Use Codex CLI as a coding agent for QA automation work.
- Write precise prompts that include goal, scope, constraints, and verification.
- Ask Codex to inspect the codebase before editing.
- Keep file edits scoped to the relevant framework layer.
- Use pytest, Allure, and collection checks as verification gates.
- Review Codex output before accepting it into the production framework.

---

## Why Codex CLI Gets Its Own Session

Claude Code, skills, plugins, and MCP are useful for interactive workflows. Codex CLI is focused on codebase work: reading files, editing tests and framework code, running commands, and reporting what changed.

For QA automation, Codex CLI is strongest when the task is concrete:

- add a missing test
- fix a failing test
- review a test file
- refactor a page object
- update scripts or documentation

Avoid vague requests like "improve the framework" unless you also define scope and verification.

---

## Prompt Shape

A strong Codex CLI prompt includes:

```text
Goal: Add web UI tests for account navigation.
Scope: tests/web-ui, pages/components/nav_bar.py only if needed.
Constraints: Do not duplicate existing scenarios. Use existing fixtures and page objects.
Verification: Run the new test file and collect tests/web-ui.
Output: Summarize files changed and commands run.
```

This gives the agent enough structure to make useful edits without guessing.

---

## Workflow

1. Inspect current tests and framework code.
2. Identify the smallest useful change.
3. Patch files.
4. Run focused verification.
5. Run collection or a broader smoke check.
6. Summarize changes, risks, and any tests not run.

The reference helpers in `course/framework/codex/` model this workflow.

---

## Useful Commands

```bash
codex
codex "review tests/web-ui for duplicate scenarios"
codex "add API contract tests for missing required fields; run pytest tests/contract -q"
```

Inside this repository, the verification commands usually look like:

```bash
.venv/bin/pytest -n 0 tests/web-ui/test_navigation_and_empty_states.py -q
.venv/bin/pytest --collect-only -q tests/web-ui
npm run allure:generate
```

---

## Safety Rules

- Read before editing.
- Keep scope small.
- Do not revert unrelated user changes.
- Avoid destructive git commands.
- Treat browser, Docker, network, and GUI commands as permission-sensitive.
- Prefer focused tests before broad suites.

---

## Runnable Example

```bash
python course/session_26_codex_cli/lecture.py
pytest course/session_26_codex_cli -q
```

The reusable reference implementation lives in `course/framework/codex/`.

---

## Session Completion Checklist

- [ ] I wrote one Codex CLI prompt with goal, scope, constraints, and verification.
- [ ] I asked Codex to inspect existing tests before editing.
- [ ] I used a focused pytest command to verify a change.
- [ ] I explained when Codex should ask for approval.
- [ ] I reviewed the final diff instead of blindly accepting it.
- [ ] I completed the exercises in `EXERCISES.md`.
