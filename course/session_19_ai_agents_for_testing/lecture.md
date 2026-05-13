# Session 19 - AI Agents for Testing: Planning, Exploration, and Review

## Learning Objectives

By the end of this session you will be able to:

- Use AI agents to support test planning without letting them replace QA judgment.
- Turn product requirements into a risk-based test inventory.
- Design a test-planning agent with explicit inputs, outputs, and guardrails.
- Use an exploratory testing agent to produce charters, observations, and follow-up questions.
- Review agent output for coverage gaps, hallucinations, and weak assertions.
- Convert useful agent findings into real tests in the production framework.

---

## Where AI Agents Help QA

AI agents are most useful when they perform bounded work with verifiable output.

| Agent role | Useful for | Human responsibility |
|---|---|---|
| Test planner | Drafting coverage maps from requirements. | Validate risk, priority, and business meaning. |
| Exploratory agent | Navigating product areas and recording observations. | Confirm findings and decide what matters. |
| Bug triage agent | Grouping failures and suggesting likely causes. | Reproduce and verify the root cause. |
| Review agent | Checking tests for selectors, assertions, and isolation. | Approve code only after running it. |
| Data agent | Proposing edge cases and input partitions. | Remove invalid or unrealistic data. |

Agents are assistants. They do not own quality decisions.

---

## Agent Input Contract

Weak prompt:

```text
Test this checkout feature.
```

Strong input contract:

```text
Feature: Checkout with guest user
Requirement: Guest users can add products, enter shipping details, choose shipping, and place an order.
Known risks: cart total accuracy, required fields, payment unavailable in test environment.
Out of scope: real payment processing, email delivery.
Output format: risk table, test cases, automation candidates, open questions.
```

The agent should receive context, boundaries, and an output format. Without those, it will produce generic coverage.

---

## Test Planning Agent Output

A useful test-planning agent should produce:

| Output | Purpose |
|---|---|
| Risk table | Shows why some tests matter more than others. |
| Coverage inventory | Lists functional, negative, edge, integration, and regression tests. |
| Automation candidates | Identifies repeatable checks worth automating first. |
| Data matrix | Suggests realistic input values and boundaries. |
| Open questions | Exposes missing product decisions. |

Every item must be traceable to a requirement, risk, or observed behavior.

---

## Review Checklist for Agent Output

Before using agent output, check:

- Does every test have a concrete expected result?
- Are priorities based on risk, not just feature order?
- Are negative and edge cases realistic?
- Are there missing states, permissions, or data variations?
- Did the agent invent product behavior not present in the requirement?
- Are automation candidates stable and repeatable?
- Is there a clear reason for each test layer: unit, API, contract, or UI?

If an answer is vague, ask the agent to revise with evidence or reject that part.

---

## Agent-Generated Test Case Example

Requirement:

> Product search supports filtering results under a maximum price.

Good agent output:

| Field | Value |
|---|---|
| Risk | Incorrect price parsing can show products above the user's budget. |
| Test type | Functional and boundary. |
| Automation layer | UI plus unit coverage for price parsing. |
| Data | `max_price=100`, `max_price=0`, invalid text, decimal values. |
| Expected result | Every displayed product price is less than or equal to the maximum. |

Poor agent output:

> Verify search works correctly.

That expected result is not measurable and should not become an automated test.

---

## Converting Agent Output Into Framework Work

Use this mapping:

| Agent finding | Framework action |
|---|---|
| New UI behavior | Add or update a page object method in `pages/`. |
| Reusable user journey | Add a flow in `flows/`. |
| API behavior | Add a service method in `services/api/`. |
| Data variation | Add structured data in `data/test_data.json`. |
| Bug risk | Add a focused test in `tests/`. |
| Repeated failure pattern | Add reporting or analysis logic. |

The agent can propose tasks, but the framework structure decides where the code belongs.

---

## Guardrails

Use these guardrails when running AI agents for QA:

- Give agents read-only access first.
- Require structured output.
- Limit the scope to one feature or flow.
- Log the prompt, input files, and output.
- Never commit agent-generated code without review and execution.
- Treat any claim about product behavior as untrusted until verified.
- Prefer small agent tasks that finish in minutes, not broad "test everything" goals.

---

## Session Completion Checklist

- [ ] I wrote an input contract for a test-planning agent.
- [ ] I generated a risk-based coverage inventory for one feature.
- [ ] I reviewed the output and removed weak or invented tests.
- [ ] I converted at least one useful agent finding into a framework task.
- [ ] I can explain which QA decisions must remain human-owned.
