# Session 19 - Exercises

## Exercise 1: Write an Agent Input Contract

Choose one feature from the demo store: search, cart, registration, login, or checkout.

Write an agent input contract with:

- Feature name.
- Requirement summary.
- Known risks.
- Out-of-scope items.
- Existing files the agent should inspect.
- Required output format.

Keep the scope narrow enough that a human could review the output in 15 minutes.

---

## Exercise 2: Generate a Risk-Based Coverage Inventory

Using your input contract, ask an AI agent to produce:

- Risk table.
- Functional tests.
- Negative tests.
- Edge cases.
- Automation candidates.
- Open questions.

Review the output and mark each item as:

- Accept.
- Revise.
- Reject.

For each rejected item, write one sentence explaining why.

---

## Exercise 3: Convert One Agent Finding Into Work

Pick one accepted automation candidate.

Create a task breakdown with:

- Production file to change.
- Test file to add or update.
- Test data needed.
- Assertion.
- Verification command.

Then implement it only if the task is small and safe. Otherwise, leave the breakdown as the deliverable.

---

## Exercise 4: Hallucination Check

Find at least three claims in the agent output that require verification.

For each claim, record:

- Claim.
- How you verified it.
- Result: true, false, or unclear.
- Action taken.

Examples: exact error text, URL path, available sort options, required fields, or API behavior.

---

## Exercise 5: Human-Owned QA Decisions

Write a short note answering:

- Which parts of the agent output helped?
- Which parts were unsafe or too generic?
- Which final decisions did you keep human-owned?
- What context would make the next agent run better?
