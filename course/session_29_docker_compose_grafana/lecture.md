# Session 29 - Running Automation With Docker Compose And Grafana

## Learning Objectives

By the end of this session you will be able to:

- Explain why Docker Compose is useful for local automation stacks.
- Run tests as a dedicated Compose service through the production helper script.
- Keep Allure results and Playwright artifacts in mounted volumes.
- Add Prometheus and Grafana services for automation observability.
- Define useful automation metrics for dashboards.
- Separate monitoring signals from release gates.

---

## Why Docker Compose

Docker runs one container well. Docker Compose runs a small system well.

For automation this means the test runner, mock services, report artifacts,
Prometheus, Grafana, and the automation server can start from one command with
repeatable networking and volumes.

Use Compose when you need:

- the same test environment on every machine
- mounted Allure results and browser artifacts
- a local monitoring stack
- a realistic CI-like run before pushing
- clear service names instead of localhost guessing between containers

---

## Production Stack In This Repository

This repository now includes the production Compose stack in
`docker-compose.automation.yml` and a wrapper script in
`scripts/run_compose_tests_with_allure.sh`.

| Service | Responsibility |
|---|---|
| `db` | PostgreSQL database service for DB-backed automation scenarios. |
| `automation-server` | FastAPI automation service running `server.app:app`. |
| `automation-tests` | Builds the test image and runs `pytest` with Allure results. |
| `postgres-exporter` | Exposes database metrics for Prometheus. |
| `prometheus` | Scrapes database/exporter metrics. |
| `grafana` | Shows automation run dashboards. |

The reusable Python reference lives in `course/framework/observability/`.

---

## Compose Shape

This is the shape students should understand in the real Compose file:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: automation

  automation-server:
    build: .
    command: ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
    depends_on:
      db:
        condition: service_healthy

  automation-tests:
    build: .
    environment:
      CI: "true"
      PW_RECORD_ARTIFACTS: "true"
      AUTOMATION_SERVER_URL: http://automation-server:8000
    volumes:
      - ./docker-artifacts:/app/test-artifacts
      - ./data:/app/data:ro
    command:
      - pytest
      - tests/
      - --alluredir=/app/test-artifacts/allure-results

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:v0.15.0

  prometheus:
    image: prom/prometheus:v2.54.1
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro

  grafana:
    image: grafana/grafana:11.1.4
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

---

## Commands

```bash
# Recommended: start stack, run all tests, generate Allure, open Allure
./scripts/run_compose_tests_with_allure.sh

# Same command through npm
npm run test:compose:report

# Start support services manually
docker compose -f docker-compose.automation.yml up -d --build \
  db automation-server postgres-exporter prometheus grafana

# Re-run only the test service manually
docker compose -f docker-compose.automation.yml run --rm automation-tests pytest tests/api -q

# Open dashboards
open http://localhost:3000/d/automation/automation-runs
open http://localhost:9090
open http://localhost:8000/docs
```

---

## Grafana Signals

Useful automation dashboards focus on run health, not vanity metrics.

Start with:

- passed tests
- failed tests
- skipped tests
- run duration
- failure rate
- flaky test count
- top failing suites
- artifact availability: Allure report, screenshots, video, trace

Grafana is for visibility. Pytest, Allure, and CI status are still the release
gates.

---

## Allure Flow

The Compose runner keeps pytest failures visible while still generating a report:

1. Start support containers.
2. Run `automation-tests` with `--alluredir=/app/test-artifacts/allure-results`.
3. Mount results back to `docker-artifacts/allure-results`.
4. Generate `docker-artifacts/allure-report`.
5. Open Allure locally.
6. Return the original pytest exit code.

This matters because a failing suite should still produce evidence.

---

## Runnable Example

```bash
python course/session_29_docker_compose_grafana/lecture.py
pytest course/session_29_docker_compose_grafana -q
```

The examples build commands and monitoring contracts without starting Docker.
That keeps the session fast and deterministic while still teaching the Compose
and Grafana architecture. The production runner is available when students are
ready to run containers:

```bash
OPEN_ALLURE=false ./scripts/run_compose_tests_with_allure.sh tests/api tests/contract -q
```

---

## Session Completion Checklist

- [ ] I can explain when Docker Compose is better than `docker run`.
- [ ] I can run `npm run test:compose:report`.
- [ ] I can mount Allure results and Playwright artifacts from a test container.
- [ ] I can describe the role of Prometheus and Grafana in automation monitoring.
- [ ] I can list the dashboard metrics that matter for test run health.
- [ ] I can explain why dashboards do not replace deterministic test gates.
- [ ] I completed the exercises in `EXERCISES.md`.
