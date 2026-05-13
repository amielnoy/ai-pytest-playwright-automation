# Session 20 - Exercises

## Exercise 1: Design a Supervised Agent Workflow

Design an agent workflow for one of these goals:

- Investigate a failing web UI test.
- Propose tests for a changed page.
- Review a generated test for framework violations.
- Summarize an Allure report.

Define:

- Goal.
- Inputs.
- Tools.
- Write scope.
- Stop condition.
- Required output.

---

## Exercise 2: Classify Agent Tasks

Create a table with at least ten testing tasks.

For each task, classify it as:

- Safe for read-only agent work.
- Safe with human approval.
- Not safe for agent work.

Include one sentence explaining the guardrail.

---

## Exercise 3: Build a Failure Investigation Record

Use a real failing test, or intentionally break a small assertion.

Create an investigation record with:

- Test name.
- Command run.
- Failure message.
- Evidence inspected.
- Top three hypotheses.
- Verified root cause.
- Fix.
- Verification command.
- Residual risk.

Restore any intentional break before finishing.

---

## Exercise 4: Review an Agent-Created Test

Ask an AI tool to draft a test for cart, search, login, or registration.

Review it against these gates:

- No raw selectors in test files.
- Concrete assertion.
- Stable data.
- Correct layer.
- No sleeps.
- Useful report output.

Mark each gate as pass or fail, then rewrite the weakest part of the test.

---

## Exercise 5: Agentic CI Proposal

Write a short proposal for adding read-only agent analysis to CI.

Include:

- When the analysis job runs.
- What artifacts it reads.
- What output it publishes.
- What it is not allowed to do.
- Who makes the final release decision.
