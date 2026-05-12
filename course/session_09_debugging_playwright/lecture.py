"""Session 9 - debugging Playwright tests."""

FAILURE_CLASSES = {
    "selector": "Locator no longer matches the intended element.",
    "timing": "The test observes state before the app is ready.",
    "data": "Input or precondition is invalid, stale, or shared.",
    "environment": "Browser, network, config, or CI differs from local.",
    "product": "The application behavior changed or regressed.",
}


if __name__ == "__main__":
    for name, desc in FAILURE_CLASSES.items():
        print(f"{name}: {desc}")
