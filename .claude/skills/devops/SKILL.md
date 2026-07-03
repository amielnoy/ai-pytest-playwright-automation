---
name: devops
description: Conventions for changing Docker, Compose, CI, monitoring, or the OpenAPI spec in this repo. Use when editing the Dockerfile, docker-compose, GitHub Actions, Prometheus/Grafana, or docs/openapi.yaml.
---

# DevOps Skill

- Keep Docker, README commands, and GitHub Actions aligned.
- If Docker is changed, verify with `docker build` and a containerized `pytest` run.
- Keep generated outputs out of git: `allure-results/`, `allure-report/`, `docker-artifacts/`, caches, and secrets.
- Prefer pinned dependency versions for reproducible CI.
- When adding new Compose services, update: `docker-compose.automation.yml`, `monitoring/prometheus.yml` (scrape targets), both compose scripts (`compose_test_report.sh` and `run_compose_tests_with_allure.sh`), and `README.md`.
- The OpenAPI spec lives in `docs/openapi.yaml` and is served by the `swagger-ui` Compose service on port 8090. Update it when adding or changing API endpoints.
- HTTP metrics (request rate, latency, error rate) are auto-collected via `prometheus-fastapi-instrumentator` in `server/app.py` and visualised in the *Infrastructure & Network* Grafana dashboard.
