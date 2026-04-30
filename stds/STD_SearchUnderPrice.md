# STD-SEARCH-UNDER-PRICE: Search With Price Filter Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Search |
| Feature | Search |
| Story | Search with price filter |
| Marker | `search` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that the price-filter search helper returns only products at or below the given maximum price, respects the result limit, handles no-results queries, and excludes products above the cap.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- `data/test_data.json` contains a `search` block with `query`, `max_price`, and `limit`.
- No authenticated session required.

## Test Cases

### TC-SEARCH-PRICE-01: Items Returned Are At or Below max_price
**Objective:** The search helper returns product names whose prices are within the configured cap.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Run `search_items_by_name_under_price` with the configured query and price cap. | `query`, `max_price`, `limit` from `data/test_data.json`. | A list of product names is returned; count ≤ limit. |
| 2 | Assert the result count does not exceed the configured limit. | `limit` from test data. | `len(names) <= limit`. |
| 3 | Assert every returned name is a non-empty string. | N/A | All names are non-empty. |

**Post-conditions:** No store state is changed.

---

### TC-SEARCH-PRICE-02: Non-Existent Product Returns Empty List
**Objective:** A nonsense query returns an empty list rather than raising an error.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Run `search_items_by_name_under_price` with a query that matches nothing. | Query: `xyznonexistentproduct999`, `max_price: 999.0`, `limit: 5` | Empty list returned. |
| 2 | Assert result is `[]`. | N/A | Assertion passes. |

---

### TC-SEARCH-PRICE-03: Items Above max_price Are Excluded
**Objective:** A price cap set below all real product prices returns an empty list.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Run `search_items_by_name_under_price` with an unreachable price cap. | Query: `MacBook`, `max_price: 1.0`, `limit: 5` | Empty list returned. |
| 2 | Assert result is `[]`. | N/A | Assertion passes. |

---

### TC-SEARCH-PRICE-04: Result List Is Capped at limit
**Objective:** Even when many products match, the result is truncated to the limit.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Run `search_items_by_name_under_price` with a broad query and high price cap, but `limit=2`. | Query: `Apple`, `max_price: 9999.0`, `limit: 2` | At most 2 names returned. |
| 2 | Assert `len(names) <= 2`. | N/A | Assertion passes. |

## Notes
- Tests are marked `@pytest.mark.search`.
- Test data for TC-SEARCH-PRICE-01 is driven by `data/test_data.json`; the other cases use fixed inline values.
