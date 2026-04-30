# STD-SORT: Sort Search Results Alphabetically Test

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Search |
| Feature | Search |
| Story | Sort search results |
| Marker | `search` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that after selecting "Name (A - Z)" sort order on the search results page, the displayed products are in ascending alphabetical order.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- The iPod search returns more than one product (required for a meaningful sort assertion).
- No authenticated session required.

## Test Cases

### TC-SORT-01: Search Results Are Sorted Alphabetically Ascending
**Objective:** After explicitly choosing "Name (A - Z)", product names are in case-insensitive ascending order.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Home page loads. |
| 2 | Assert the currency dropdown is visible (sanity guard). | N/A | Currency dropdown is visible. |
| 3 | Search for `iPod`. | Query: `iPod` | Search results page loads with iPod products. |
| 4 | Switch to list view. | N/A | Products are displayed in list layout. |
| 5 | Select sort option "Name (A - Z)" from the Sort By combobox. | Label: `Name (A - Z)` | Page reloads with the new sort applied. |
| 6 | Collect all product names. | N/A | Names are attached to the Allure report. |
| 7 | Assert the product list is non-empty. | N/A | At least one product is present. |
| 8 | Assert product names match their case-insensitive sorted order. | N/A | `names == sorted(names, key=str.casefold)`. |

**Post-conditions:** Browser remains on the search results page; no cart or account changes.

## Notes
- Tests are marked `@pytest.mark.search`.
- The sort assertion is case-insensitive (`str.casefold`) to handle mixed-case product names.
