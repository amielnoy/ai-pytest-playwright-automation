# Session 2 — QA in the AI Era

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
