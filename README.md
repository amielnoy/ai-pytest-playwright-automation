# Playwright Python Test Suite

UI and API test automation for the TutorialsNinja demo store, built with:

- `pytest`
- `playwright`
- `pytest-xdist`
- `allure-pytest`

## Prerequisites

- Python 3.12+ recommended
- A virtual environment with the project dependencies installed
- Playwright Chromium installed

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

If you want to run registration tests, create `data/secrets.json` from `data/secrets.json.example`.

## Default Test Behavior

`pytest.ini` is configured to run tests in parallel by default:

- `-n auto`
- `--dist loadscope`

So a plain `pytest` run will use multiple workers automatically.

## Run Tests In Parallel

Run the full suite with the default parallel configuration:

```bash
pytest
```

## Run Tests With Docker

Build the test image:

```bash
docker build -t ness-automation-tests .
```

Run the full suite:

```bash
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ness-automation-tests pytest tests/ --alluredir=/app/test-artifacts/allure-results
```

Run a specific test file or marker by passing pytest arguments:

```bash
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ness-automation-tests pytest tests/web-ui/test_search_under_price.py --alluredir=/app/test-artifacts/allure-results
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ness-automation-tests pytest -m cart --alluredir=/app/test-artifacts/allure-results
```

If registration tests need private data, mount your local secrets file:

```bash
docker run --rm \
  -v "$PWD/data/secrets.json:/app/data/secrets.json:ro" \
  -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ness-automation-tests pytest tests/ --alluredir=/app/test-artifacts/allure-results
```

Run a specific file in parallel:

```bash
pytest tests/web-ui/test_search_under_price.py
```

Run a subset of tests in parallel:

```bash
pytest tests/web-ui/test_search_under_price.py tests/web-ui/test_add_to_cart.py
```

Run only API tests:

```bash
pytest tests/api
```

Run only contract tests:

```bash
pytest tests/contract
```

Run only UI tests:

```bash
pytest tests/web-ui
```

## Run Tests Serially

Override the default xdist behavior and run in a single process:

```bash
pytest -n 0
```

Run a specific file serially:

```bash
pytest -n 0 tests/web-ui/test_registration.py
```

Run a single test serially:

```bash
pytest -n 0 tests/web-ui/test_cart_total.py -k cart_total_not_exceeds
```

## Useful Options

Verbose output:

```bash
pytest -n 0 -v
```

Run only tests with a marker:

```bash
pytest -m search
pytest -n 0 -m cart
```

## Reports

Allure results are written to:

```text
allure-results/
```

Generate and open a local Allure report if Allure CLI is installed:

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```
