# Session 12 - Mini Project: One Complete Feature Slice

## Goal

Build one complete automation slice before moving into advanced AI and CI topics.

Your slice must include:

- One page object improvement.
- One explicit fixture.
- One data-loader or factory usage.
- One concrete UI test.
- One Allure title or step.
- One focused verification command.

---

## Suggested Feature Slices

| Feature | Expected work |
|---|---|
| Search under price | Data from JSON, search page behavior, concrete price assertions. |
| Add to cart | Product-card method, cart fixture, badge and total assertions. |
| Registration | Unique data, validation assertions, secret-safe handling. |
| Sort products | Locator filtering, page method, ordered-name assertion. |

---

## Acceptance Criteria

- No raw selectors in the test body.
- Test data is not hardcoded unless it is truly local to the assertion.
- The test can run alone.
- The test can run in parallel.
- Failure output explains what behavior broke.

---

## Session Completion Checklist

- [ ] I chose one feature slice.
- [ ] I implemented or improved page behavior.
- [ ] I used a fixture intentionally.
- [ ] I used structured test data.
- [ ] I ran the narrowest test command and recorded the result.
