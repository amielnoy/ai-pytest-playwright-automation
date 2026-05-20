# Session 2 — Exercises

## How to Submit

Create one Markdown file named `session_02_answers.md`.
Paste prompts and AI output, but keep the final reviewed test cases separate from the raw AI output.

## Review Criteria

Your work is complete when:

- Each prompt includes role, task, context, format, constraints, and examples when relevant.
- Raw AI output is reviewed against the validation checklist.
- Hallucinations are explicitly marked, not silently fixed.
- Final test cases are traceable to the provided story or observed product behaviour.
- You include at least one prompt iteration based on review findings.

---

## Exercise 1: Zero-Shot vs Few-Shot Comparison

Pick a feature from the TutorialsNinja demo (e.g. "Add to cart", "Search by keyword", "User registration").

1. Write a zero-shot prompt and paste the AI output.
2. Write a few-shot prompt with one example and paste the AI output.
3. List three specific differences in quality (coverage, concreteness, format).

Use this comparison table:

| Dimension | Zero-shot result | Few-shot result | Which is better and why |
| --- | --- | --- | --- |
| Coverage | | | |
| Step quality | | | |
| Expected result specificity | | | |
| Hallucination risk | | | |
| Format consistency | | | |

---

## Exercise 2: Build a Well-Formed Prompt

Write a prompt with all six anatomy components for this user story:

> As a shopper I can filter search results by price range so that I only see products I can afford.

Your prompt must produce at least: 1 positive test, 1 boundary test (exact min/max price), 1 negative test (non-numeric input), 1 edge case.

If the demo site does not actually support price filtering, state that as a product assumption in the prompt. The goal is to practice grounding assumptions instead of hiding them.

---

## Exercise 3: Validate AI Output

Paste the AI output from Exercise 1 or 2 and apply the five-item validation checklist from the lecture. For each item: pass or fail, and if fail, rewrite the offending test case.

Add requirement traceability: for every final case, write the story sentence, spec line, or observed behaviour that justifies it.

---

## Exercise 4: Spot the Hallucination

The following AI output was generated for the TutorialsNinja shopping cart. Find every hallucination and explain what the correct behaviour should be.

```text
TC-H01 | Apply coupon code | 1. Add item to cart. 2. Click "Apply Coupon". 3. Enter "SAVE20". 4. Click Apply. | 20% discount is applied and cart total updates.
TC-H02 | One-click checkout | 1. Log in. 2. Click "Buy Now". | Order is placed immediately without entering shipping info.
TC-H03 | Wishlist to cart | 1. Add item to wishlist. 2. Click "Move to Cart". | Item moves to cart and wishlist count decrements.
```

For each row, classify the issue as one of:

- Invented control.
- Invented business rule.
- Missing precondition.
- Vague expected result.
- Unsupported workflow.

---

## Exercise 5: Chain-of-Thought Prompting

Write a chain-of-thought prompt for the registration feature. The prompt must instruct the model to reason through: actors, happy paths, failure modes, edge cases, security concerns — before writing any test cases.

Compare the output to a direct (zero-shot) prompt for the same feature.

---

## Exercise 6: Prompt Repair

Take one flawed AI-generated test case from any exercise and write a repair prompt that changes only that test case.

Your repair prompt must include:

- The exact case ID to repair.
- The defects found.
- The source of truth the repair must follow.
- A rule to leave unrelated cases unchanged.

Paste the revised case and explain whether the repair introduced any new issue.
