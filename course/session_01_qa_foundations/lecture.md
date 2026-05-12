# Session 1 — QA Foundations & Manual Testing

## Learning Objectives

By the end of this session you will be able to:

- Write a complete, atomic test case with all seven required fields.
- Choose the right test type (smoke, functional, negative, edge case) for a given scenario.
- Apply equivalence partitioning, boundary value analysis, and decision tables to derive test cases.
- Define severity and priority independently and explain why they can differ.
- Write a structured bug report that a developer can reproduce without follow-up questions.
- Identify when automation adds value and when manual or exploratory testing is more appropriate.

---

## What Is a Test Case?

A test case is a documented procedure to verify one specific behaviour.
Every test case has exactly **seven fields**: ID, title, priority, type, precondition, steps, and expected result.

- **Steps** must be atomic — one physical action per step.
- **Expected result** must be concrete and measurable — never "it works" or "the page loads".
- **Precondition** must describe system state before step 1 — never assume the reader knows.

**Common mistakes:**

| Mistake | Wrong | Correct |
| --- | --- | --- |
| Compound step | "Log in and check the cart" | Two separate steps |
| Vague action | "Fill in the form" | "Enter 'John' in the First Name field" |
| Missing precondition | Steps assume a logged-in user | State it explicitly |
| Vague expected | "The page works correctly" | "URL is /inventory.html and 6 products are visible" |
| Testing two things | One case verifies login AND cart | Split into two cases |

---

## Test Types

| Type | When to write |
|---|---|
| **Smoke** | After every deploy — does the happy path work at all? |
| **Functional** | For each acceptance criterion in the user story |
| **Negative** | For every input that should be rejected |
| **Edge Case** | At boundaries: min, max, empty, zero, overflow |
| **Security** | XSS, SQLi, auth bypass, sensitive data in responses |
| **Performance** | When a page or API must respond within an SLA |
| **Usability** | Can a real user complete the task without reading docs? |
| **Regression** | Any area touched by the current change |

---

## The Test Pyramid

```
        /\  E2E / UI    (10%)  — slow, expensive, few
       /  \ Integration (20%)  — moderate speed and cost
      /    \ Unit       (70%)  — fast, cheap, many
```

Invert the pyramid (more E2E than unit) and your suite becomes slow, fragile, and expensive.
If an E2E test covers logic that a unit test could cover, the E2E test is in the wrong layer.

---

## Test Design Techniques

### Equivalence Partitioning (EP)

Divide inputs into groups that should behave identically. Test **one value per group**.

**Login password — partitions:**

| Partition | Example | Expected |
| --- | --- | --- |
| Valid | `secret_sauce` | Login succeeds |
| Wrong | `wrong_password` | Credential error |
| Empty | `""` | Validation error |
| Injected | `' OR 1=1 --` | Standard error, no bypass |

### Boundary Value Analysis (BVA)

Test at the **exact edge** of each partition: min, min−1, max, max+1.
Most bugs hide at boundaries because developers write `>` instead of `>=`.

**Password length (8–72 chars):**

| Value | Length | Expected |
| --- | --- | --- |
| `""` | 0 | Rejected — empty |
| `"a" * 7` | 7 | Rejected — too short |
| `"a" * 8` | **8** | **Accepted — minimum** |
| `"a" * 72` | **72** | **Accepted — maximum** |
| `"a" * 73` | 73 | Rejected — too long |

### Decision Tables

Use when the expected result depends on a **combination** of conditions. Each column is one test case.

**Login (username valid × password valid):**

| Condition | C1 | C2 | C3 | C4 |
| --- | --- | --- | --- | --- |
| Username valid | Y | Y | N | N |
| Password valid | Y | N | Y | N |
| **Result** | **Login OK** | **Error** | **Error** | **Error** |

Four conditions → four test cases. No combination is left untested.

### State Transition Testing

Model the system as **states** connected by **transitions**. Cover every valid transition and every invalid one.

```
LOGGED_OUT --login--> LOGGED_IN
                           |
                        checkout
                           |
                           v
                    CHECKOUT_STEP1 --continue--> CHECKOUT_STEP2 --finish--> ORDER_PLACED
                           |                          |
                         cancel                     cancel
                           v                          v
                          CART                      EMPTY
```

**Invalid transitions to test:** skip step 1, submit empty cart, double-click Finish, navigate directly to step URL.

### Pairwise (All-Pairs) Testing

Full combinatorial coverage of N factors = M^N test cases.
Pairwise reduces this by covering every **pair** of values at least once (roughly 30–70% fewer cases, catches ~75% of bugs).

Use when: 3+ independent variables and full combinatorial is too expensive. Tools: `pairwisepy`, `allpairs`.

---

## Defect Lifecycle

```
New --> Assigned --> In Progress --> Fixed --> Verified --> Closed
                                                              ^
                                               (or Reopened if fix was incomplete)
```

### Severity vs Priority

| | Severity | Priority |
| --- | --- | --- |
| Question | How badly does it break the system? | How urgently must it be fixed? |
| Scale | Critical / Major / Minor / Trivial | High / Medium / Low |
| Set by | QA | Product Owner |

**They are independent.** A cosmetic typo on the CEO dashboard: Severity = Trivial, Priority = High.

### What makes a good bug report?

1. **Title** — `<Component>: <observed> instead of <expected>`
2. **Steps** — atomic, numbered, reproducible 100% of the time
3. **Actual** — exactly what happened (paste error text verbatim)
4. **Expected** — what the spec or common sense says should happen
5. **Environment** — OS, browser version, user account, URL
6. **Attachments** — screenshot, console log, network trace

See `bug_report.py` for five real examples from saucedemo.com.

---

## Risk-Based Testing

When time is limited, test where **risk = likelihood × impact** is highest first.

| Area | Likelihood | Impact | Score | Action |
| --- | --- | --- | --- | --- |
| Checkout / payment | Medium | High | 6 | Run every sprint |
| Login / auth | Medium | High | 6 | Smoke gate on every deploy |
| Cart total | Low | High | 3 | Automated assertion |
| Sort dropdown | Medium | Low | 2 | Regression suite only |
| UI cosmetics | High | Low | 3 | Visual diff in CI |

---

## Exploratory Testing

Exploratory testing is **simultaneous learning, design, and execution** — not random clicking.
It is structured through **charters** and time-boxed sessions.

### Charter format

```
Area:     Shopping Cart
Mission:  Explore the cart's state management across page navigation
          to find inconsistencies in the badge count and item persistence.
Time box: 45 minutes
```

One charter per session. Broad charters produce shallow coverage.

### SFDIPOT — structured exploration heuristic

| Letter | Question |
|---|---|
| **S**tructure | What is the product made of? (pages, forms, APIs) |
| **F**unction | What does it do? (features, workflows, rules) |
| **D**ata | What data flows through? (inputs, outputs, formats) |
| **I**nterfaces | How does it connect? (APIs, browser, OS) |
| **P**latform | Where does it run? (browsers, screen sizes) |
| **O**perations | How is it used in production? (load, error recovery) |
| **T**ime | How does time affect it? (expiry, race conditions) |

### FEW HICCUPS — rapid edge-case discovery

| | What to try |
|---|---|
| **F**unny characters | Unicode, emoji, RTL text, null bytes, very long strings |
| **E**mpty / null | Empty fields, empty lists, missing JSON keys |
| **W**rong type | String where number expected, negative IDs |
| **H**uge values | Max int, enormous strings, large file uploads |
| **I**nvalid boundaries | One below min, one above max |
| **C**ombinations | Two valid inputs that conflict |
| **C**oncurrency | Two users doing the same action at once |
| **U**ndo / cancel | Browser Back, Cancel mid-flow |
| **P**ermissions | Access another user's resource |
| **S**tates | Double-submit, reload during submit, expired session |

### Session note structure

Take notes **as you explore** — not after. Record what you did, what you saw, and what surprised you.
After the session: list bugs found, questions raised, areas covered, areas missed, and coverage %.

See `exploratory.py` for five charters and one fully completed session note (EX-001, Authentication).

---

## Test Plan — the six questions

A test plan answers: **what** is tested, **how**, by **whom**, by **when**, **where**, and **under what conditions**.

| Section | Key content |
|---|---|
| Scope | In-scope features and explicit out-of-scope items |
| Approach | Manual vs automated, tools, environments, browsers |
| Resources | Who does what (QA Lead, QA Engineer, PO) |
| Schedule | Milestones and owners, day by day |
| Risks | What can go wrong and how to mitigate it |
| Entry/Exit | When testing starts and when it is done |
| Coverage matrix | Feature to test case IDs to automation percentage |

See `test_plan.py` for the complete plan for saucedemo.com v1.0.

---

## Coverage Summary (this session)

| Feature | Manual cases | Automated (later sessions) | Known gaps |
| --- | --- | --- | --- |
| Authentication | 11 | 4 | Mobile viewport layout |
| Product Inventory | 8 | 3 | Search (out of scope) |
| Shopping Cart | 8 | 4 | Second-tab behaviour |
| Checkout | 8 | 2 | Tax rounding edge cases |
| **Total** | **35** | **13** | |

---

## When NOT to Automate

Automation is an investment. It only pays off when the test runs frequently enough to recoup the authoring and maintenance cost.

**Automate when:**
- The test must run on every commit or every deploy.
- The same steps are repeated across many data combinations (`@pytest.mark.parametrize`).
- Manual execution is slow, error-prone, or requires precise timing.
- The feature is stable — the UI or API contract is unlikely to change next sprint.

**Do NOT automate when:**
- The feature is changing rapidly (you will rewrite the test more often than you run it).
- The test requires human judgement — visual design, tone of error messages, usability.
- The cost of writing and maintaining the test exceeds the cost of manual execution over the feature's lifetime.
- You need to explore an unfamiliar area first; write the exploratory session note, then automate the cases that survived review.

**The automation ROI formula (rough guide):**

```
savings = (manual_time_per_run × runs_per_year) - (authoring_time + maintenance_time_per_year)
```

If `savings` is negative, keep it manual.

---

## Session Completion Checklist

Before moving to Session 2, verify you can answer yes to each item:

- [ ] I can write a test case with all seven fields from memory.
- [ ] I can name all eight test types and give a one-sentence definition of each.
- [ ] I can apply EP, BVA, and decision tables to a new feature without looking at notes.
- [ ] I have read `test_cases.py` and can explain why each case belongs to its test type.
- [ ] I have read `bug_report.py` and written at least one original bug report using the template.
- [ ] I can explain the difference between severity and priority with a concrete example.
- [ ] I can decide whether a given test scenario is worth automating and explain why.

---

## Files in this session

| File | Purpose |
|---|---|
| `lecture.py` | Concepts: all techniques as executable Python reference |
| `lecture.md` | This document — human-readable summary |
| `test_cases.py` | 35 structured test cases across 4 features |
| `bug_report.py` | Template + 5 real saucedemo bug examples |
| `test_plan.py` | Full test plan: scope, schedule, risks, coverage matrix |
| `exploratory.py` | 5 charters + session note template + 1 completed session |
| `EXERCISES.md` | Hands-on practice tasks for this session |
