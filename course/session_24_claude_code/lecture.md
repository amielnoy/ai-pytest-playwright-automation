# Session 24 — Claude Code Integration for QA

## Learning Objectives

By the end of this session you will be able to:

- Invoke project-specific slash commands from Claude Code to generate tests, review code, and analyze failures.
- Configure the Playwright MCP server so Claude can control a real browser inside your chat session.
- Write a custom slash command (`/your-command`) tailored to a new QA workflow.
- Configure `.claude/settings.json` to allow the tools your commands need without prompting.
- Explain how Claude Code slash commands differ from the `cli.py` approach in Session 14.

---

## What Is Claude Code?

Claude Code is a CLI (and IDE extension) that runs Claude in your terminal with direct access to your file system, shell, and git. Unlike a chat interface, it can read files, edit code, run commands, and call MCP tools — all in one turn.

For QA teams this means:
- Generate a full test file, run it, and review the output without leaving the terminal.
- Ask Claude to find a broken selector, navigate to the real page to inspect it, and patch the page object — automatically.
- Analyze CI failures, propose fixes, and open a PR — in one command.

---

## Slash Commands

Project-specific slash commands live in `.claude/commands/`. Each command is a `.md` file whose content is sent to Claude as a system prompt when you invoke `/command-name`.

### Commands in this project

| Command | Invoke | What it does |
|---|---|---|
| `/generate-test` | `/generate-test user can add to cart` | Generates a complete pytest + Playwright test file |
| `/review-tests` | `/review-tests tests/web-ui/` | Scans for 8 anti-patterns and reports findings |
| `/create-page-object` | `/create-page-object product detail page` | Inspects the live page and writes a page object |
| `/analyze-failures` | `/analyze-failures results.xml` | Buckets failures and produces a root-cause report |
| `/add-allure` | `/add-allure tests/web-ui/test_cart.py` | Adds all Allure decorators to an existing test file |
| `/fix-selectors` | `/fix-selectors pages/` | Audits and replaces brittle selectors across page objects |

### How commands work

```
.claude/commands/generate-test.md   ← prompt template
                                        ↓
you type: /generate-test add to cart
                                        ↓
Claude receives: [file content] + "add to cart" substituted for $ARGUMENTS
                                        ↓
Claude reads project files, writes test, runs collection check
```

The `$ARGUMENTS` placeholder is replaced with whatever you type after the command name.

---

## The Playwright MCP Server

The Playwright MCP server (`@playwright/mcp`) exposes browser control as MCP tools — no Playwright code required inside Claude Code. Claude can navigate, click, fill forms, take screenshots, and read the accessibility tree of any live page.

### Install

```bash
npm install -g @playwright/mcp
```

### Configure in `.claude/settings.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp", "--headless"]
    }
  }
}
```

Remove `--headless` to watch the browser in real time while Claude navigates.

### What you can do with it

- `/create-page-object` navigates to the real page and inspects elements before writing code.
- `/fix-selectors` opens each page to confirm the new locator actually finds the element.
- Ask Claude to "explore the checkout flow and tell me what accessibility issues it finds" — no test code needed.
- Ask Claude to "reproduce bug report BUG-42 on the live demo site and screenshot each step."

---

## Writing Your Own Slash Command

A slash command is a plain `.md` file. The only special syntax is `$ARGUMENTS`.

**Template:**

```markdown
Do the following for: $ARGUMENTS

## Context
This project uses pytest + Playwright with the POM pattern.
Tests live in `tests/`, page objects in `pages/`.

## Steps
1. ...
2. ...

## Output format
...
```

**Tips for effective commands:**

- Be explicit about file placement — Claude should not guess where to put output.
- State the output format precisely — if you want Python, say "Output ONLY Python, no markdown fences."
- Include a verification step — "run `pytest --collect-only -q` after writing the file."
- Reference project conventions — "follow the patterns in `pages/base_page.py`."

---

## Claude Code vs `cli.py` (Session 14)

| | `cli.py` (Session 14) | Claude Code Slash Commands |
|---|---|---|
| **Invoked** | `python cli.py test "feature"` in terminal | `/generate-test feature` in Claude Code |
| **Context** | Only what you pass in the prompt | Full project file access — Claude reads your actual page objects |
| **Output** | Writes a file | Writes, runs, checks, and reports in one turn |
| **MCP tools** | No browser access | Can navigate the live site to inspect elements |
| **Best for** | CI pipelines, headless automation | Interactive development, ad-hoc generation |

Use `cli.py` in CI (Session 16 pipeline) and slash commands during local development.

---

## Configuring Allowed Tools in `.claude/settings.json`

By default, Claude Code asks for permission before running shell commands. You can pre-approve safe read-only commands to reduce prompts:

```json
{
  "permissions": {
    "allow": [
      "Bash(pytest --collect-only*)",
      "Bash(pytest --lf*)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)"
    ]
  },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp", "--headless"]
    }
  }
}
```

Do not pre-approve write operations (file edits, git commits, git push) — these should always require explicit confirmation.

---

## Session Completion Checklist

- [ ] I ran `/generate-test` for a real feature and the output passes `pytest --collect-only -q`.
- [ ] I ran `/review-tests` on at least one test file and evaluated each finding.
- [ ] I ran `/create-page-object` and Claude navigated the live site before writing the file.
- [ ] I ran `/analyze-failures` after a real test failure and used the report to fix the test.
- [ ] I ran `/fix-selectors` and at least one brittle selector was replaced.
- [ ] I wrote one custom slash command for a QA workflow specific to this project.
- [ ] The Playwright MCP server is configured in `.claude/settings.json` and Claude can navigate the demo site.
- [ ] I completed the exercises in `EXERCISES.md`.
