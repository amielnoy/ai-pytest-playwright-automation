# STD-IPOD-STORAGE: iPod Product Storage Test

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Search |
| Feature | Search |
| Story | iPod product storage |
| Marker | `search` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that searching for iPod products returns results, that the stored product name strips the "iPod" prefix, and that the minimum and maximum prices are correctly identified.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- The iPod product category contains at least two products with distinct prices.
- No authenticated session required.

## Test Cases

### TC-IPOD-01: iPod Product Data Is Stored and Validated
**Objective:** Confirm iPod search results are captured (name, picture URL, description, price), the stored name has the "iPod" prefix removed, and min/max prices are correctly computed.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Home page loads. |
| 2 | Search for `iPod`. | Query: `iPod` | Search results page loads with iPod products. |
| 3 | Switch to list view. | N/A | Products are displayed in list layout. |
| 4 | Collect stored product information (name, picture URL, description, price) for all cards. | N/A | At least one product record is returned; data is attached to Allure report. |
| 5 | Assert no stored product name contains the word `ipod` (case-insensitive). | N/A | All stored names have "iPod" stripped. |
| 6 | Find the product with the maximum price and log its details. | N/A | Max-price product is identified; details attached to Allure report. |
| 7 | Find the product with the minimum price and log its details. | N/A | Min-price product is identified; details attached to Allure report. |
| 8 | Assert that the identified max price equals `max(all prices)`. | N/A | Assertion passes. |
| 9 | Assert that the identified min price equals `min(all prices)`. | N/A | Assertion passes. |

**Post-conditions:** No store state is changed.

## Notes
- Tests are marked `@pytest.mark.search`.
- Product name cleaning strips the "iPod" prefix so that only the model suffix (e.g., "Classic", "Nano") is stored.
- Allure attachments include the full JSON record for every product and separate attachments for the max/min price products.
