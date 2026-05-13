# Session 27 - Claude Connectors For QA Workflows

## Learning Objectives

By the end of this session you will be able to:

- Explain what Claude connectors are and how they differ from skills, plugins, MCP, and CLI workflows.
- Choose the right connector for a QA task.
- Use connectors to gather project context without over-sharing data.
- Separate read actions from write actions.
- Define confirmation rules before commenting, sending, creating, or updating anything.
- Capture connector evidence in a QA summary.

---

## What Connectors Are

Connectors give Claude permissioned access to real work systems such as GitHub, Google Drive, Gmail, Calendar, Slack, Outlook, SharePoint, or Teams.

They are powerful because they connect QA work to live project context:

- pull requests and CI results
- bug reports and issue threads
- requirement documents
- release calendars
- stakeholder email or chat discussions

They are risky when permissions and write boundaries are unclear.

---

## Connector Selection

| Connector | QA use |
|---|---|
| GitHub | PR review, issue triage, CI failure investigation. |
| Google Drive | Requirements, test plans, release notes, spreadsheets. |
| Slack / Teams | Bug threads, release coordination, test status. |
| Gmail / Outlook | Stakeholder approvals, QA summaries, incoming defects. |
| Calendar | Test windows, release meetings, availability. |

The reference helper in `course/framework/claude/connectors.py` models this selection.

---

## Read vs Write

Read actions are usually lower risk:

- read a PR
- summarize a document
- inspect a Slack thread
- review a calendar invite

Write actions need confirmation:

- comment on a PR
- send a message
- create a calendar event
- update a document
- send an email

The assistant should summarize what it found before taking a write action.

---

## QA Workflow Pattern

1. Name the QA task.
2. Choose the narrowest connector source.
3. Read only the relevant thread, document, issue, PR, or event.
4. Summarize findings with links or IDs.
5. Ask before writing anything.
6. Record what was changed or sent.

---

## Runnable Example

```bash
python course/session_27_claude_connectors/lecture.py
pytest course/session_27_claude_connectors -q
```

The reusable reference implementation lives in `course/framework/claude/connectors.py`.

---

## Session Completion Checklist

- [ ] I can explain the difference between a connector and a skill.
- [ ] I can choose a connector for PR review, requirements review, and release coordination.
- [ ] I can identify which actions are read-only and which require confirmation.
- [ ] I can write a QA connector prompt with source, task, and output format.
- [ ] I can document evidence links or IDs in a QA summary.
- [ ] I completed the exercises in `EXERCISES.md`.
