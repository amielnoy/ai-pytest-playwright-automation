# Session 20 - Agentic Automation Testing: From Scripts to Supervised Workflows

## Learning Objectives

By the end of this session you will be able to:

- Design supervised agent workflows for automation testing.
- Decide which testing tasks are safe for agents and which require human approval.
- Build a workflow that turns a failure into a reproducible investigation record.
- Use agents to propose test changes while keeping code review and execution mandatory.
- Add quality gates for agent-created tests.
- Explain how agentic testing fits into CI without making CI unpredictable.

---

## What Is Agentic Automation Testing?

Traditional automation runs a fixed script:

```text
Given this test code, run the same steps every time.
```

Agentic automation runs a supervised workflow:

```text
Given this goal, current app state, tools, and guardrails, decide the next useful action.
```

The goal is not to replace deterministic tests. The goal is to add agent workflows around the test suite:

- Generate candidate tests.
- Investigate failures.
- Explore changed pages.
- Suggest framework refactors.
- Summarize risk after a release.

Deterministic tests remain the release gate. Agents help create, maintain, and explain them.

---

## Safe vs Risky Agent Tasks

| Task | Safe for agent autonomy? | Required guardrail |
|---|---|---|
| Read test failure logs | Yes | Read-only access. |
| Summarize failed tests | Yes | Include source file and error lines. |
| Suggest likely root cause | Yes | Mark as hypothesis until verified. |
| Generate a test draft | Partial | Human review and local execution. |
| Edit page objects | Partial | Scoped files, diff review, tests. |
| Change CI pipeline | No | Human approval before commit. |
| Update secrets or credentials | No | Never give agent access. |
| Mark a release as safe | No | Human-owned decision. |

Agents can move fast. Guardrails decide whether fast is useful or dangerous.

---

## Failure Investigation Workflow

Use this workflow when a CI test fails:

```
1. Collect failure context:
   - test name
   - traceback
   - screenshot
   - trace
   - recent diff

2. Ask the agent for hypotheses:
   - product regression
   - selector drift
   - test data issue
   - timing or environment problem

3. Verify the top hypothesis:
   - rerun one test
   - inspect page object
   - compare expected and actual state

4. Produce an investigation record:
   - root cause
   - fix
   - verification command
   - residual risk
```

The agent may propose hypotheses, but the engineer must verify the cause.

---

## Agent Workflow Design

Every agent workflow should define:

| Field | Example |
|---|---|
| Goal | Investigate one failing web UI test. |
| Inputs | Test name, traceback, screenshot path, changed files. |
| Tools | Read files, run narrow pytest command, inspect report artifact. |
| Write scope | None for investigation, or one page object plus one test file. |
| Stop condition | Root cause found or three hypotheses rejected. |
| Output | Investigation record with verification command. |

Do not run open-ended agents in CI. CI workflows should be bounded, repeatable, and cheap.

---

## Quality Gates for Agent-Created Tests

Before accepting an agent-created test, require:

- No raw Playwright selectors in test files.
- Clear test name and Allure title.
- Concrete expected result.
- Stable test data.
- No sleeps.
- Narrow verification command passes.
- Test belongs to the correct layer.
- Failure output would be useful to a human.

If a generated test fails these gates, revise it before adding it to the suite.

---

## Agentic CI Pattern

Recommended pattern:

```text
test job
  run deterministic tests
  upload results, traces, screenshots

analysis job
  if tests failed
  run read-only agent analysis
  publish summary as artifact or PR comment

human review
  decide whether to fix product, fix test, quarantine, or rerun
```

Avoid pipelines where an agent silently edits code or changes test results during the same release gate.

---

## Practical Use Cases

| Use case | Agent output | Human follow-up |
|---|---|---|
| New feature lands | Coverage gaps and candidate tests. | Choose high-risk tests to implement. |
| UI selector changes | Affected page object methods. | Patch and run focused tests. |
| Flaky test detected | Pattern summary across failures. | Confirm timing, data, or environment cause. |
| Regression report | Failed areas grouped by feature. | Decide release risk. |
| Refactor planning | Duplicate selectors or repeated flows. | Implement scoped framework cleanup. |

---

## Session Completion Checklist

- [ ] I designed one supervised agent workflow for automation testing.
- [ ] I classified safe and risky agent tasks for my project.
- [ ] I wrote quality gates for agent-created tests.
- [ ] I created a failure investigation record from a real or simulated failure.
- [ ] I can explain why deterministic tests remain the release gate.
