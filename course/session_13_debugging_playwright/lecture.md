# Session 13 - Debugging Playwright Tests

## Learning Objectives

- Diagnose selector, timing, data, environment, and product failures.
- Use headed mode, slow motion, screenshots, videos, traces, console logs, and network logs.
- Re-run the narrowest failing test.
- Write a failure note that identifies evidence and root cause.

---

## Debugging Order

1. Re-run one failing test.
2. Read the assertion and traceback.
3. Inspect screenshot or trace.
4. Decide failure class: selector, timing, data, environment, or product.
5. Fix the smallest responsible layer.
6. Re-run the same focused command.

---

## Commands

```bash
pytest -k test_name -vv
pytest -n 0 -k test_name
pytest --lf
python3 -m playwright show-trace trace.zip
```

---

## Before / After

Weak:

```python
time.sleep(3)
page.locator(".btn").click()
```

Better:

```python
page.get_by_role("button", name="Add to Cart").click()
expect(cart_page.badge).to_have_text("1")
```

Do not patch timing with sleeps. Wait for specific state.

---

## Session Completion Checklist

- [ ] I reproduced one failure with a narrow command.
- [ ] I inspected at least one artifact.
- [ ] I classified the failure cause.
- [ ] I fixed the responsible layer.
- [ ] I recorded the verification command.
