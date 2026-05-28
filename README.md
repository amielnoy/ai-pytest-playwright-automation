# AI_AUTOMATION_TESTING

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

This repository also includes a 30-session automation QA course plus a Git basics bridge under [`course/`](course/README.md). Start there for the learning path, session order, exercise workflow, and guidance on when to use the teaching scaffold versus the production framework. For a visual browser overview, open [`course_overview.html`](course_overview.html).

## Project Layout

```text
agents/       Agent runners and planning helpers
config/       Runtime configuration
data/         Test data, parametrize corpora, and local-only secrets
flows/        Business-level UI/API workflows
mcp_servers/  Local MCP tools, including the test reporter
pages/        Playwright page objects and components
scripts/      Test, Docker, Compose, and report helper scripts
server/       FastAPI automation service
services/     API service clients
stds/         Test standards and generated page snapshot source docs
tests/        API, contract, unit, and web UI tests
utils/        Shared utilities
course/       Training material and teaching examples
artifacts/    Generated or captured artifacts kept out of core code paths
monitoring/   Prometheus and Grafana configuration
```

Generated outputs such as `allure-results/`, `allure-report/`, `docker-artifacts/`, `logs/`, `.playwright-mcp/`, `outputs/`, `test-results/`, `playwright-report/`, and `artifacts/reports/*.html` are ignored by git.

## Production Page Object Rules

Production UI tests use `pages/`, `pages/components/`, and `flows/`.

- Page objects initialize stable locator members in `__init__`.
- Methods reuse those members instead of rebuilding the same locator repeatedly.
- Dynamic locators that depend on runtime input, such as a product name, stay inside the method that receives that input.
- CSS-heavy locators use deterministic self-healing fallbacks through `pages/self_healing.py`.
- Self-healing does not call AI or invent selectors. Fallbacks are explicitly owned by the page object and recorded through `self_heal_events()` so stale primary locators can be fixed.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
npm install
```

If you want to run registration tests, create `data/secrets.json` from `data/secrets.json.example`.

## Secrets (local and CI)

Credentials live in `data/secrets.json`, which is **runtime-only** — never commit it.

| Where | How secrets are supplied |
| ----- | ------------------------ |
| Local | Copy `data/secrets.json.example` → `data/secrets.json` and fill in real values. The file is listed in `.gitignore`. |
| CI | GitHub Actions secret `TEST_SECRETS_JSON` (full JSON body). The workflow writes it to `data/secrets.json` on the runner only; the step does not print the secret. |
| Docker | Mount `data/secrets.json` read-only at run time (`scripts/run_all_tests_docker.sh`); the image excludes it via `.dockerignore`. |

`utils/data_loader.py` merges `secrets.json` over `data/test_data.json` when the file exists. Registration tests skip via `registration_data` if secrets are missing — they do not fail the whole suite.

Data-driven tests load their parametrize corpus via `get_data_file(filename)`, which reads any JSON file from `data/` by name. The corpora shipped with the project are:

| File | Used by |
| ---- | ------- |
| `data/api_test_cases.json` | `tests/api/test_api_data_driven.py` — search, price, cart, empty-search cases |
| `data/pentest_cases.json` | `tests/api/test_pentest_data_driven.py` — injection, auth, ACL, and file-exposure vectors |

**Capstone / course rule:** deliverables must not include real passwords or API keys in git. Use the example file for shape only; store real values locally or in GitHub repository secrets.

Before pushing, confirm nothing leaked: `git check-ignore -v data/secrets.json` and `git status` should not list `data/secrets.json`.

## Default Test Behavior

`pytest.ini` is configured to run tests in parallel by default:

- `-n auto`
- `--dist loadgroup` — API, contract, and unit tests are distributed across workers; **all web-UI tests share a single worker** (via `xdist_group("web-ui")` in `tests/web-ui/conftest.py`) to avoid concurrent headless-browser bot-protection triggers.

So a plain `pytest` run uses multiple workers automatically.

### Offline Fallback for Live-Site Tests

All HTTP requests to `tutorialsninja.com` are transparently intercepted by `services/api/opencart_fallback.py` via `services/rest_client.py`. The fallback simulates a complete OpenCart store — search results, cart state, home page, login, and registration — without a real network connection. This makes the API, contract, and pentest suites instant and network-independent.

Web-UI tests (Playwright) still use a real browser. When the site is accessible, tests run against live pages. When unreachable, the browser's connection attempt times out and those tests are retried or skipped by the CI `--reruns=1` policy.

CI runs `pytest tests/ -m "not demo"` so teaching-only tests (intentional failure, flaky Allure demo) do not fail the pipeline. Run them locally with `pytest -m demo`.

## Run Tests In Parallel

Run the full suite with the default parallel configuration:

```bash
pytest
```

## Run Tests With Docker

Build the test image:

```bash
docker build -t ai-automation-testing .
```

Run the full suite:

```bash
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ai-automation-testing pytest tests/ --alluredir=/app/test-artifacts/allure-results
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
Grafana — Test Runs:      http://localhost:3000/d/automation/automation-runs
Grafana — Infrastructure: http://localhost:3000/d/infra-network/infrastructure-network
Prometheus:               http://localhost:9090
Swagger UI:               http://localhost:8090
cAdvisor:                 http://localhost:8082
node-exporter:            http://localhost:9100/metrics
Server API docs:          http://localhost:8000/docs
Allure:                   opened automatically from docker-artifacts/allure-report
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
  ai-automation-testing pytest tests/web-ui/test_search_under_price.py --alluredir=/app/test-artifacts/allure-results
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ai-automation-testing pytest -m cart --alluredir=/app/test-artifacts/allure-results
```

If registration tests need private data, mount your local secrets file:

```bash
docker run --rm \
  -v "$PWD/data/secrets.json:/app/data/secrets.json:ro" \
  -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ai-automation-testing pytest tests/ --alluredir=/app/test-artifacts/allure-results
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

Run data-driven API tests (inline and JSON-parametrized):

```bash
pytest tests/api/test_api_data_driven.py
```

Run data-driven penetration tests:

```bash
pytest tests/api/test_pentest_data_driven.py
pytest -m pentest
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

Analysis CLI — RAG AI failure classifier
---------------------------------------

There is a small agent that analyzes `allure-results/` and classifies failing tests using retrieval-augmented (RAG) AI by default. It gathers historical result snippets and small text attachments and includes them in the LLM prompt to improve classification accuracy.

Run from the repository root:

```bash
./scripts/run_allure_failure_agent.sh --allure-dir allure-results
```

Options:
- `--no-ai` — run heuristics only (no LLM call)
- `--model MODEL` — pass an Anthropic model name
- `--api-key KEY` — provide an Anthropic API key for this run (or set `ANTHROPIC_API_KEY` in the environment)

There is also an npm shortcut:

```bash
npm run allure:analyze
```

## Monitoring

The Compose stack includes a full observability layer:

| Service | URL | Purpose |
| --- | --- | --- |
| Grafana | <http://localhost:3000> | Dashboards (login: admin / admin) |
| Prometheus | <http://localhost:9090> | Metrics storage and query |
| Push Gateway | <http://localhost:9091> | Receives test run metrics |
| cAdvisor | <http://localhost:8082> | Container CPU / memory / network per service |
| node-exporter | <http://localhost:9100> | Host CPU / memory / disk / network |
| Swagger UI | <http://localhost:8090> | Full API reference (`docs/openapi.yaml`) |

**Grafana dashboards** (provisioned automatically from `monitoring/grafana/dashboards/`):

- **Automation Runs** — test pass/fail/flaky counters, DB health, service uptime
- **Infrastructure & Network** — container network I/O, per-service CPU/memory, HTTP request rate, P95 latency, error rate, host metrics

HTTP metrics are collected automatically from the FastAPI server via `prometheus-fastapi-instrumentator` and appear on the Infrastructure dashboard under the *HTTP API Performance* row.

To start only the monitoring stack (without running tests):

```bash
docker compose -f docker-compose.automation.yml up -d \
  prometheus grafana pushgateway cadvisor node-exporter swagger-ui
```

To open Swagger UI standalone:

```bash
npm run swagger:up
npm run swagger:open
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
