# Session 29 Exercises - Docker Compose And Grafana

## Exercise 1 - Compose Command Review

Run:

```bash
python course/session_29_docker_compose_grafana/lecture.py
```

Identify:

- the test service name
- the generated support-stack command
- the generated test-service command
- the production wrapper script
- the Grafana dashboard URL
- the Prometheus scrape targets

## Exercise 2 - Production Runner Dry Run

Write the command you would use to run API and contract tests through the
production Compose runner without opening Allure.

Expected shape:

```bash
OPEN_ALLURE=false ./scripts/run_compose_tests_with_allure.sh tests/api tests/contract -q
```

## Exercise 3 - Manual Compose Service Run

Write the manual command that runs only API tests in the `automation-tests`
service.

Expected shape:

```bash
docker compose -f docker-compose.automation.yml run --rm automation-tests pytest tests/api -q
```

## Exercise 4 - Inspect The Production Files

Open these files and write one sentence about the purpose of each:

- `docker-compose.automation.yml`
- `scripts/run_compose_tests_with_allure.sh`
- `monitoring/prometheus.yml`
- `monitoring/grafana/provisioning/datasources/prometheus.yml`
- `monitoring/grafana/dashboards/automation-runs.json`

## Exercise 5 - Dashboard Design

Design a Grafana dashboard with at least six panels:

- 3 panels for run result health
- 2 panels for duration or trend
- 1 panel for artifact/report availability

Explain which panel would make you stop a release.

## Exercise 6 - Failure Investigation

A Compose run fails with 1 UI failure and 110 passing tests.

Document the investigation order:

1. pytest summary
2. Allure failed test page
3. screenshot
4. video
5. trace
6. Grafana trend

Explain what Grafana can show that a single Allure report cannot.

## Exercise 7 - Monitoring Is Not A Gate

Write a short rule for your team:

- Which tool decides pass/fail?
- Which tool shows trends?
- Which artifacts are mandatory on UI failure?
