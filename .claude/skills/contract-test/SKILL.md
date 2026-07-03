---
name: contract-test
description: Conventions for writing or changing API/page-structure contract tests in this repo (tests/contract/, map-driven cases). Use when adding or editing contract tests.
---

# Contract Test Skill

- Put API/page structure contract tests under `tests/contract/`.
- Validate stable contracts: status codes, required fields, parseable product IDs, prices, and page markers.
- Keep contract cases map-driven when multiple endpoints or queries share the same assertion shape.
- Do not import reusable data from `conftest.py`; move shared cases to a normal module if they grow.
