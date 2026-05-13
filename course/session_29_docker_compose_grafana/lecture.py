"""
Session 29 - Running Automation With Docker Compose And Grafana

Runnable examples for planning a Docker Compose automation run and monitoring
the run through Prometheus and Grafana.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.observability import (  # noqa: E402
    DockerComposeAutomationPlan,
    build_compose_allure_script_command,
    build_compose_command,
    build_compose_test_command,
    build_grafana_url,
    create_monitoring_stack,
    render_prometheus_scrape_config,
    validate_monitoring_plan,
)


def demo() -> None:
    stack = create_monitoring_stack()
    plan = DockerComposeAutomationPlan(
        compose_file="docker-compose.automation.yml",
        test_service="automation-tests",
        test_path="tests/",
        allure_results_dir="/app/test-artifacts/allure-results",
        grafana_url=build_grafana_url(),
        prometheus_url="http://localhost:9090",
    )

    print("Services:", ", ".join(stack.service_names()))
    print("Start stack:", build_compose_command(plan.compose_file))
    print("Run tests:", build_compose_test_command(plan.compose_file, "tests/"))
    print("Full runner:", build_compose_allure_script_command())
    print("Grafana:", plan.grafana_url)
    print("Prometheus config:")
    print(render_prometheus_scrape_config(stack))
    print("Validation errors:", validate_monitoring_plan(plan, stack))


if __name__ == "__main__":
    demo()


__all__ = [
    "DockerComposeAutomationPlan",
    "build_compose_allure_script_command",
    "build_compose_command",
    "build_compose_test_command",
    "build_grafana_url",
    "create_monitoring_stack",
    "render_prometheus_scrape_config",
    "validate_monitoring_plan",
]
