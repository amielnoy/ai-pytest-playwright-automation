# Session 23 — Exercises

## Exercise 1: Layer Audit

For each file listed below, identify which of the five architecture layers it belongs to (Tests / Pages / API clients / AI utilities / Fixtures & data). If it belongs to more than one layer, explain the violation and propose a refactor.

- `tests/web-ui/test_add_to_cart.py`
- `pages/cart_page.py`
- `course/session_14_ai_tools/cli.py`
- `conftest.py`
- `data/test_data.json`
- `course/framework/analysis/failures.py`

---

## Exercise 2: Write an ADR

Write `docs/adrs/ADR-006-parallel-execution.md` using the format from the lecture (Status / Context / Decision / Consequences).

The decision to record: "Use `pytest-xdist` with `-n auto` and `--dist loadgroup`, grouping `tests/web-ui` via `pytest.mark.xdist_group('web-ui')` (see `pytest.ini` and root `conftest.py`)."

Your ADR must explain:
- Why `--dist loadgroup` plus an explicit web-ui group was chosen over `--dist loadscope`, `--dist each`, or `--dist load`.
- What breaks if parallel workers split shared browser or session state incorrectly (and how grouping avoids it).
- The consequence: tests in the same `xdist_group` run on the same worker; ungrouped tests still distribute across workers.

---

## Exercise 3: Pre-Commit Hook Setup

1. Create `.pre-commit-config.yaml` with hooks for `ruff` (linting) and `ruff-format` (formatting).
2. Run `pre-commit install`.
3. Introduce a deliberate style violation (unused import, wrong indentation).
4. Attempt `git commit` and confirm the hook blocks it.
5. Fix the violation and confirm the commit succeeds.

---

## Exercise 4: Complete the Capstone Checklist

Work through every item in the Capstone Checklist from `lecture.md`. For each unchecked item, either complete it or write a one-sentence explanation of what is blocking it.

---

## Exercise 5: Framework Mapping

Draw (on paper or in a tool) a diagram showing which directory maps to which architecture layer and how a test call flows through the layers at runtime.

Annotate with the names of three actual files at each layer from this project.
