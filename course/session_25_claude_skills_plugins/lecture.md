# Session 25 - Claude Skills & Plugins For QA Automation

## Learning Objectives

By the end of this session you will be able to:

- Explain the difference between Claude skills, plugins, MCP servers, and slash commands.
- Choose the right extension mechanism for a QA workflow.
- Design a skill that encodes team testing standards.
- Identify when a plugin or connector needs explicit permissions.
- Document fallback behavior when external tools are unavailable.
- Review AI extension workflows for safety and repeatability.

---

## Why This Comes After Claude Code

Session 24 introduced Claude Code as an interactive development workflow. This session explains how to extend that workflow responsibly:

| Mechanism | Best for | Example |
|---|---|---|
| Skill | Reusable local instructions and standards | A QA review checklist. |
| Plugin | Product integrations and richer tool bundles | GitHub PR and CI workflows. |
| MCP server | Runtime access to external tools | Playwright browser control. |
| Slash command | Project-specific command shortcuts | `/generate-test checkout validation`. |

The goal is to make AI assistance more consistent, not more magical.

---

## Skills

Skills are local instruction bundles. Use them when the workflow is mostly about judgment, standards, or repeatable review logic.

Good skill candidates:

- test review rubric
- bug report quality checklist
- API contract review guidance
- Allure report review guidance

Avoid putting secrets, private credentials, or environment-specific commands inside a skill.

---

## Plugins

Plugins package capabilities such as skills, tools, and connectors. Use plugins when the workflow needs a richer integration surface than instructions alone.

Good plugin candidates:

- GitHub PR review and CI debugging
- document or spreadsheet generation
- browser-driven local testing workflows

Every plugin should have a clear permission story.

---

## MCP Servers

MCP servers expose tools to the model at runtime. For QA, the most useful example is browser control through Playwright MCP.

Use MCP when the assistant needs to inspect a live target instead of guessing from static code.

---

## Slash Commands

Slash commands are project-specific shortcuts. They are useful when a team repeats the same prompt structure often.

Example:

```text
/generate-test user can remove an item from cart
```

A slash command should define:

- expected input
- output format
- files it may edit
- commands it may run
- review boundaries

---

## Runnable Example

```bash
python course/session_25_claude_skills_plugins/lecture.py
pytest course/session_25_claude_skills_plugins -q
```

The reusable reference implementation lives in `course/framework/claude/`.

---

## Session Completion Checklist

- [ ] I can explain when to use a skill instead of a plugin.
- [ ] I can explain when MCP is required.
- [ ] I wrote one skill idea for QA review.
- [ ] I wrote one plugin idea with permissions and fallback behavior.
- [ ] I reviewed one slash command for scope and safety.
- [ ] I completed the exercises in `EXERCISES.md`.
