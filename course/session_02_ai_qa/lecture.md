# Session 2 — QA in the AI Era

## Learning Objectives

By the end of this session you will be able to:

- Explain where LLMs add value in QA and where they fail.
- Write zero-shot, few-shot, chain-of-thought, and role+constraints prompts for test generation.
- Construct a prompt with all six anatomy components.
- Review AI-generated test cases against a validation checklist and reject hallucinated output.
- Identify at least four common hallucination risks in AI-generated test suites.

> **New to coding?** This session focuses on prompting and reviewing AI output — no Python required yet.
> If you find the prompt examples abstract, come back after Session 5 once you have written real tests
> and the patterns will be much more concrete.

---

## Why AI for QA?

Large language models can read a user story and produce structured test cases in seconds.
They excel at breadth — suggesting negative cases and edge cases a human might skip.
They fail at depth — hallucinating endpoint names, inventing business rules, or producing duplicate cases with different wording.
The engineer's job shifts from *writing* cases to *prompting well* and *reviewing AI output critically*.

---

## Four Prompting Patterns

**Zero-shot** — give the task with no examples. Fast but output format varies.

**Few-shot** — provide one or two example input/output pairs before the real task. Guides structure and detail level.

**Chain-of-thought** — ask the model to reason step by step (actors → happy paths → failures → edge cases → security) before writing cases. Produces deeper coverage.

**Role + constraints** — assign a role ("You are a senior SDET") and hard rules ("5 cases minimum, at least 1 negative, output JSON only"). Most reliable for CI pipelines.

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

---

## Common Hallucination Risks

- Endpoint paths that do not exist in the spec (e.g. `/api/v2/coupon/validate`).
- Field names borrowed from similar APIs (`discount_code` instead of `coupon`).
- Security tests that only cover SQL injection and miss IDOR or auth bypass.
- Acceptance criteria contradicted by the AI's own assumed rules.

Always cross-reference AI output against the actual spec before adding cases to the suite.

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
