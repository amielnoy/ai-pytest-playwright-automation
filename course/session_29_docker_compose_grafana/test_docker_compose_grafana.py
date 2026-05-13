from __future__ import annotations

from pathlib import Path

from course.framework.observability import (
    DockerComposeAutomationPlan,
    build_compose_allure_script_command,
    build_compose_command,
    build_compose_test_command,
    build_grafana_url,
    build_pytest_service_command,
    create_monitoring_stack,
    render_prometheus_scrape_config,
    validate_monitoring_plan,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_build_compose_command_starts_real_support_services() -> None:
    command = build_compose_command("docker-compose.automation.yml")

    assert command == (
        "docker compose -f docker-compose.automation.yml up -d --build "
        "db automation-server postgres-exporter prometheus grafana"
    )


def test_build_compose_command_can_run_detached() -> None:
    command = build_compose_command(detach=False)

    assert command.startswith("docker compose -f docker-compose.automation.yml up --build")


def test_build_compose_test_command_runs_automation_tests_service() -> None:
    command = build_compose_test_command("docker-compose.automation.yml", "tests/api", extra_args=("-q",))

    assert command == (
        "docker compose -f docker-compose.automation.yml run --rm automation-tests "
        "pytest tests/api --alluredir=/app/test-artifacts/allure-results -q"
    )


def test_compose_allure_script_command_points_to_production_runner() -> None:
    assert build_compose_allure_script_command() == "./scripts/run_compose_tests_with_allure.sh"


def test_build_pytest_service_command_writes_allure_results() -> None:
    command = build_pytest_service_command("tests/api", extra_args=("-q",))

    assert command == ("pytest", "tests/api", "--alluredir=/app/test-artifacts/allure-results", "-q")


def test_monitoring_stack_contains_tests_prometheus_and_grafana() -> None:
    stack = create_monitoring_stack()

    assert stack.service_names() == (
        "db",
        "automation-server",
        "automation-tests",
        "postgres-exporter",
        "prometheus",
        "grafana",
    )
    assert stack.dashboard.tracks_required_signals() is True


def test_grafana_url_points_to_automation_dashboard() -> None:
    url = build_grafana_url(dashboard_uid="automation")

    assert url == "http://localhost:3000/d/automation/automation-runs"


def test_prometheus_config_scrapes_automation_targets() -> None:
    config = render_prometheus_scrape_config(create_monitoring_stack())

    assert "postgres-exporter:9187" in config
    assert "prometheus:9090" in config


def test_valid_monitoring_plan_has_no_errors() -> None:
    stack = create_monitoring_stack()
    plan = DockerComposeAutomationPlan(
        compose_file="docker-compose.automation.yml",
        test_service="automation-tests",
        test_path="tests/",
        allure_results_dir="/app/test-artifacts/allure-results",
        grafana_url="http://grafana:3000/d/automation/automation-runs",
        prometheus_url="http://prometheus:9090",
    )

    assert validate_monitoring_plan(plan, stack) == []


def test_invalid_monitoring_plan_reports_missing_service() -> None:
    stack = create_monitoring_stack()
    plan = DockerComposeAutomationPlan(
        compose_file="docker-compose.automation.yml",
        test_service="missing-tests",
        test_path="tests/",
        allure_results_dir="",
        grafana_url="http://localhost:3000",
        prometheus_url="http://localhost:8080",
    )

    errors = validate_monitoring_plan(plan, stack)

    assert "Unknown test service: missing-tests" in errors
    assert "Allure results directory is required" in errors


def test_production_compose_file_contains_required_services() -> None:
    compose_text = (PROJECT_ROOT / "docker-compose.automation.yml").read_text()

    for service in ("db:", "automation-server:", "automation-tests:", "postgres-exporter:", "prometheus:", "grafana:"):
        assert service in compose_text


def test_production_runner_generates_allure_from_docker_artifacts() -> None:
    script = (PROJECT_ROOT / "scripts/run_compose_tests_with_allure.sh").read_text()

    assert "docker compose -f" in script
    assert "automation-tests" in script
    assert "npx allure generate" in script
    assert "docker-artifacts" in script


def test_package_json_exposes_compose_report_command() -> None:
    package_json = (PROJECT_ROOT / "package.json").read_text()

    assert '"test:compose:report": "./scripts/run_compose_tests_with_allure.sh"' in package_json
