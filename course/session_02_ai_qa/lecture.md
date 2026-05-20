# Session 2 — QA in the AI Era

## Learning Objectives

By the end of this session you will be able to:

- Explain where LLMs add value in QA and where they fail.
- Write zero-shot, few-shot, chain-of-thought, and role+constraints prompts for test generation.
- Construct a prompt with all six anatomy components.
- Review AI-generated test cases against a validation checklist and reject hallucinated output.
- Identify at least four common hallucination risks in AI-generated test suites.

> **New to coding?** This session focuses on prompting and reviewing AI output — no Python required yet.
> If you find the prompt examples abstract, come back after Session 6 once you have written real tests
> and the patterns will be much more concrete.

---

## Session Flow

| Time | Activity | Output |
| --- | --- | --- |
| 0:00-0:15 | AI strengths and failure modes in QA | Shared risk model for AI use |
| 0:15-0:40 | Prompt anatomy and prompting patterns | First prompt draft |
| 0:40-1:05 | Zero-shot vs few-shot comparison | Improved prompt with example |
| 1:05-1:30 | Validation and hallucination review | Rejected or corrected AI output |
| 1:30-1:50 | Prompt iteration workflow | Review-ready generated test set |
| 1:50-2:00 | Checklist and handoff to Python | Completion evidence |

---

## Why AI for QA?

Large language models can read a user story and produce structured test cases in seconds.
They excel at breadth — suggesting negative cases and edge cases a human might skip.
They fail at depth — hallucinating endpoint names, inventing business rules, or producing duplicate cases with different wording.
The engineer's job shifts from *writing* cases to *prompting well* and *reviewing AI output critically*.

Use AI as a draft generator and critic, not as an authority.
The source of truth remains the spec, code, product behaviour, logs, and conversations with product or development.

---

## Safe AI Workflow for QA

1. **Ground** — paste the exact user story, acceptance criteria, API contract, or relevant code.
2. **Constrain** — specify output format, counts, required test types, and forbidden assumptions.
3. **Generate** — ask for a draft only.
4. **Validate** — compare every case against the source material.
5. **Repair** — ask AI to fix only the issues you identified, or rewrite manually.
6. **Trace** — map each final test case to a requirement, risk, or discovered behaviour.

Never commit an AI-generated test case that cannot be traced back to a real requirement or observed product behaviour.

---

## Four Prompting Patterns

**Zero-shot** — give the task with no examples. Fast but output format varies.

**Few-shot** — provide one or two example input/output pairs before the real task. Guides structure and detail level.

**Chain-of-thought** — ask the model to reason step by step (actors → happy paths → failures → edge cases → security) before writing cases. Produces deeper coverage.

**Role + constraints** — assign a role ("You are a senior SDET") and hard rules ("5 cases minimum, at least 1 negative, output JSON only"). Most reliable for CI pipelines.

### Pattern selection guide

| Need | Pattern | Example instruction |
| --- | --- | --- |
| Fast brainstorming | Zero-shot | "List likely test scenarios for this story." |
| Consistent review format | Few-shot | "Use the exact structure in this example." |
| Deeper risk discovery | Chain-of-thought | "First identify actors, failure modes, edge cases, and security risks." |
| CI-ready output | Role + constraints | "Return valid JSON only; do not invent endpoints." |

---

## Prompt Anatomy

A well-formed QA prompt has six components:

1. **Role** — who the model is.
2. **Task** — what to produce.
3. **Context** — the user story, spec, or code snippet.
4. **Format** — JSON array, Markdown table, pytest file, etc.
5. **Constraints** — minimum counts, required test types, no invented fields.
6. **Examples** — (few-shot only) one reference input/output pair.

---

## Validating AI Output

Before committing AI-generated test cases, check:

- At least one positive, one negative, and one edge-case test.
- Steps are atomic (one action per step).
- Expected results are concrete (`"Error 'Password is required' appears"`), not vague (`"it shows an error"`).
- No two cases share an identical expected result (duplicates).
- No endpoints, fields, or business rules invented outside the spec.

### Validation table template

Use this table when reviewing AI output:

| Check | Pass/Fail | Evidence | Fix |
| --- | --- | --- | --- |
| Requirement traceability | | Which story/spec line supports it? | |
| Positive/negative/edge coverage | | Which case IDs cover each type? | |
| Atomic steps | | Which step is compound? | |
| Concrete expected result | | What exact UI/API signal is asserted? | |
| No hallucinated fields or rules | | Which source confirms the field/rule? | |
| No duplicate cases | | Which IDs overlap? | |

---

## Common Hallucination Risks

- Endpoint paths that do not exist in the spec (e.g. `/api/v2/coupon/validate`).
- Field names borrowed from similar APIs (`discount_code` instead of `coupon`).
- Security tests that only cover SQL injection and miss IDOR or auth bypass.
- Acceptance criteria contradicted by the AI's own assumed rules.

Always cross-reference AI output against the actual spec before adding cases to the suite.

## Prompt Iteration Example

Weak prompt:

```
Create checkout tests.
```

Better prompt:

```
You are a senior QA engineer.
Task: Generate checkout test cases for the spec below.
Context: Checkout has Step One (first name, last name, postal code), Step Two (order summary), and Finish. Empty required fields show inline errors. Cart must contain at least one item.
Format: Markdown table with ID, title, type, priority, precondition, steps, expected.
Constraints: 8 cases; include 2 positive, 2 negative, 2 edge, 1 state transition, 1 regression. Do not mention payment, coupons, shipping methods, or APIs.
```

Repair prompt after review:

```
Revise only TC-004 and TC-006.
Problems found:
- TC-004 mentions payment, which is out of scope.
- TC-006 has compound steps and vague expected result.
Keep all other cases unchanged.
```

The repair prompt is narrow on purpose. Broad "improve this" prompts often introduce new hallucinations while fixing old ones.

---

## Worked Example: Zero-Shot vs Few-Shot

**User story:** "As a shopper I can search for products by name so that I find what I want quickly."

**Zero-shot prompt (weak):**

```
Write test cases for product search.
```

Typical output: vague steps like "Search for a product" with expected result "Results are shown." No negative cases. No edge cases.

**Few-shot prompt (strong):**

```
You are a senior QA engineer. Generate test cases in this exact format:

ID | Title | Steps | Expected
TC-001 | Search returns matching products | 1. Navigate to /search. 2. Enter "MacBook" in the search field. 3. Click Search. | At least one result with "MacBook" in the title is shown.

Now generate test cases for:
Feature: Product search on tutorialsninja.com/demo
Spec: The search field is on the homepage. Results page shows matching products. Searching for an unknown term shows "There is no product that matches the search criteria."
Requirements: 1 positive, 1 no-results, 1 empty-query, 1 special-characters edge case.
```

Typical output: four cases with concrete steps and expected results, matching the spec's exact error message.

**What changed:** the format constraint, the explicit spec, and the count requirements eliminated vague output and hallucinated endpoints.

---

## AI Review Exercise

Given this AI-generated test case, identify all the problems:

```
TC-010 | Coupon code discount applies | 1. Log in. 2. Add item to cart. 3. Enter coupon code "SAVE10" in the coupon field. 4. Click Apply. | Discount of 10% is applied.
```

Problems to find:
1. The spec never mentions a coupon field — this endpoint is hallucinated.
2. "Discount of 10% is applied" is vague — what element confirms it? What is the new total?
3. Step 1 "Log in" is compound — missing precondition (user must already exist) and missing the actual login steps.
4. No teardown — what happens to the applied coupon after the test?

---

## Session Completion Checklist

Before moving to Session 3, verify you can answer yes to each item:

- [ ] I can write a zero-shot and a few-shot prompt for the same user story and explain what the few-shot adds.
- [ ] I can name all six components of a well-formed QA prompt.
- [ ] I reviewed `prompt_engineering.py` and ran at least one prompt against a real user story.
- [ ] I applied the validation checklist to a piece of AI-generated output and found at least one issue.
- [ ] I can explain hallucination risk with a concrete example from a QA context.
- [ ] I completed the exercises in `EXERCISES.md`.
