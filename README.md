# Playwright Python Test Suite

UI and API test automation for the TutorialsNinja demo store, built with:

- `pytest`
- `playwright`
- `pytest-xdist`
- `allure-pytest`

## Prerequisites

- Python 3.12+ recommended
- Node.js 18+ for the Allure 3 report CLI
- A virtual environment with the project dependencies installed
- Playwright Chromium installed

## Course Materials

This repository also includes a twenty-eight-session automation QA course under [`course/`](course/README.md). Start there for the learning path, session order, exercise workflow, and guidance on when to use the teaching scaffold versus the production framework.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
npm install
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

Or use the helper script, which builds the image, mounts `docker-artifacts/`, mounts `data/secrets.json` when present, and runs the full suite:

```bash
./scripts/run_all_tests_docker.sh
```

Run the Compose stack with database, automation server, Prometheus, Grafana, all tests, and a fresh Allure report:

```bash
./scripts/run_compose_tests_with_allure.sh
```

Or through npm:

```bash
npm run test:compose:report
```

Useful URLs after the Compose script starts the support containers:

```text
Grafana:    http://localhost:3000/d/automation/automation-runs
Prometheus: http://localhost:9090
Server:     http://localhost:8000/docs
Allure:     opened automatically from docker-artifacts/allure-report
```

Pass pytest arguments after the script name:

```bash
./scripts/run_compose_tests_with_allure.sh tests/api tests/contract -q
./scripts/run_compose_tests_with_allure.sh -m cart
```

Pass extra pytest arguments after the script name:

```bash
./scripts/run_all_tests_docker.sh -m cart
./scripts/run_all_tests_docker.sh tests/web-ui/test_add_to_cart.py
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

This project uses Allure Report 3 through the local npm `allure` package. Avoid the global `allure` command if it reports a `2.x` version.

```bash
npm run allure:version
npm run allure:generate
npm run allure:open
```

For live report updates while rerunning tests:

```bash
npm run allure:watch
```

## FastAPI Automation Service

Start the local API:

```bash
uvicorn server.app:app --reload
```

Open the interactive docs at:

```text
http://127.0.0.1:8000/docs
```

Also view the architecture documentation at:

[http://127.0.0.1:8000/architecture](http://127.0.0.1:8000/architecture)

Useful endpoints:

```text
GET    /health
GET    /automation/config
GET    /automation/test-data
GET    /automation/test-data/{key}
GET    /automation/external/search?query=MacBook
POST   /automation/external/cart
POST   /runs/pytest
GET    /runs/{job_id}
GET    /reports/allure/status
GET    /reports/allure/summary
POST   /reports/allure/generate
GET    /reports/allure/view/index.html
GET    /mock/products/search?query=MacBook
POST   /mock/cart/add
GET    /mock/cart
DELETE /mock/cart
```
