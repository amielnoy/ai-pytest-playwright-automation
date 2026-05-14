"""Docker Compose and Grafana monitoring patterns for automation runs.

The helpers in this module do not start Docker. They model the commands,
services, and monitoring contract students should understand before wiring a
real automation stack to Docker Compose, Prometheus, and Grafana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from shlex import quote


@dataclass(frozen=True)
class AutomationService:
    """A service that participates in an automation run."""

    name: str
    image: str
    command: tuple[str, ...]
    ports: tuple[str, ...] = ()
    volumes: tuple[str, ...] = ()
    environment: dict[str, str] = field(default_factory=dict)

    @property
    def exposes_metrics(self) -> bool:
        return any(port.endswith(":8000") or port.endswith(":9090") for port in self.ports)


@dataclass(frozen=True)
class GrafanaDashboard:
    """Minimal dashboard contract for automation run monitoring."""

    uid: str
    title: str
    panels: tuple[str, ...]

    def tracks_required_signals(self) -> bool:
        required = {"passed tests", "failed tests", "run duration", "flake rate"}
        normalized = {panel.lower() for panel in self.panels}
        return required.issubset(normalized)


@dataclass(frozen=True)
class MonitoringStack:
    """Services and dashboard definitions for the automation monitoring stack."""

    services: tuple[AutomationService, ...]
    dashboard: GrafanaDashboard

    def service_names(self) -> tuple[str, ...]:
        return tuple(service.name for service in self.services)


@dataclass(frozen=True)
class DockerComposeAutomationPlan:
    """A runnable plan for executing tests through Docker Compose."""

    compose_file: str
    test_service: str
    test_path: str
    allure_results_dir: str
    grafana_url: str
    prometheus_url: str


def build_compose_command(
    compose_file: str = "docker-compose.automation.yml",
    services: tuple[str, ...] = ("db", "automation-server", "postgres-exporter", "prometheus", "grafana"),
    detach: bool = True,
) -> str:
    """Build the command that starts the Compose support stack."""

    parts = ["docker", "compose", "-f", compose_file]
    parts.extend(["up"])
    if detach:
        parts.append("-d")
    parts.append("--build")
    parts.extend(services)
    return " ".join(quote(part) for part in parts)


def build_compose_test_command(
    compose_file: str = "docker-compose.automation.yml",
    test_path: str = "tests/",
    allure_dir: str = "/app/test-artifacts/allure-results",
    extra_args: tuple[str, ...] = (),
) -> str:
    """Build the command that runs pytest inside the Compose test service."""

    pytest_command = build_pytest_service_command(test_path, allure_dir, extra_args)
    parts = ["docker", "compose", "-f", compose_file, "run", "--rm", "automation-tests", *pytest_command]
    return " ".join(quote(part) for part in parts)


def build_compose_allure_script_command(script: str = "./scripts/run_compose_tests_with_allure.sh") -> str:
    """Return the production script that runs Compose tests and opens Allure."""

    return script


def build_pytest_service_command(
    test_path: str = "tests/",
    allure_dir: str = "/app/test-artifacts/allure-results",
    extra_args: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Return the pytest command the test container should execute."""

    return ("pytest", test_path, f"--alluredir={allure_dir}", *extra_args)


def build_grafana_url(host: str = "localhost", port: int = 3000, dashboard_uid: str = "automation") -> str:
    """Return the URL for the automation dashboard."""

    return f"http://{host}:{port}/d/{dashboard_uid}/automation-runs"


def create_monitoring_stack() -> MonitoringStack:
    """Create the reference Docker Compose monitoring stack."""

    database = AutomationService(
        name="db",
        image="postgres:16-alpine",
        command=(),
        ports=("5432:5432",),
        environment={
            "POSTGRES_DB": "automation",
            "POSTGRES_USER": "automation",
            "POSTGRES_PASSWORD": "automation",
        },
    )
    server = AutomationService(
        name="automation-server",
        image="ai-automation-testing:latest",
        command=("uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"),
        ports=("8000:8000",),
        volumes=("./docker-artifacts:/app/test-artifacts",),
        environment={"CI": "true", "DATABASE_URL": "postgresql://automation:automation@db:5432/automation"},
    )
    tests = AutomationService(
        name="automation-tests",
        image="ai-automation-testing:latest",
        command=build_pytest_service_command(),
        volumes=("./docker-artifacts:/app/test-artifacts", "./data:/app/data:ro"),
        environment={
            "CI": "true",
            "PW_RECORD_ARTIFACTS": "true",
            "DATABASE_URL": "postgresql://automation:automation@db:5432/automation",
            "AUTOMATION_SERVER_URL": "http://automation-server:8000",
        },
    )
    postgres_exporter = AutomationService(
        name="postgres-exporter",
        image="prometheuscommunity/postgres-exporter:v0.15.0",
        command=(),
        ports=("9187:9187",),
        environment={"DATA_SOURCE_NAME": "postgresql://automation:automation@db:5432/automation?sslmode=disable"},
    )
    prometheus = AutomationService(
        name="prometheus",
        image="prom/prometheus:v2.54.1",
        command=("--config.file=/etc/prometheus/prometheus.yml",),
        ports=("9090:9090",),
        volumes=("prometheus.yml:/etc/prometheus/prometheus.yml:ro",),
    )
    grafana = AutomationService(
        name="grafana",
        image="grafana/grafana:11.1.4",
        command=(),
        ports=("3000:3000",),
        volumes=("grafana-data:/var/lib/grafana",),
        environment={"GF_SECURITY_ADMIN_PASSWORD": "admin"},
    )
    dashboard = GrafanaDashboard(
        uid="automation",
        title="Automation Runs",
        panels=("Passed Tests", "Failed Tests", "Run Duration", "Flake Rate"),
    )
    return MonitoringStack(services=(database, server, tests, postgres_exporter, prometheus, grafana), dashboard=dashboard)


def render_prometheus_scrape_config(stack: MonitoringStack) -> str:
    """Render a compact Prometheus scrape config for services exposing metrics."""

    targets = [f"{service.name}:9187" for service in stack.services if service.name == "postgres-exporter"]
    targets.extend(f"{service.name}:9090" for service in stack.services if service.name == "prometheus")
    target_list = ", ".join(f'"{target}"' for target in targets)
    return "\n".join(
        [
            "scrape_configs:",
            "  - job_name: automation",
            f"    static_configs: [{{ targets: [{target_list}] }}]",
        ]
    )


def validate_monitoring_plan(plan: DockerComposeAutomationPlan, stack: MonitoringStack) -> list[str]:
    """Return validation errors for a compose-based automation monitoring plan."""

    errors: list[str] = []
    if plan.test_service not in stack.service_names():
        errors.append(f"Unknown test service: {plan.test_service}")
    if not plan.allure_results_dir:
        errors.append("Allure results directory is required")
    if "grafana" not in plan.grafana_url and ":3000" not in plan.grafana_url:
        errors.append("Grafana URL should point to the Grafana service or host")
    if "prometheus" not in plan.prometheus_url and ":9090" not in plan.prometheus_url:
        errors.append("Prometheus URL should point to Prometheus")
    if not stack.dashboard.tracks_required_signals():
        errors.append("Dashboard is missing required automation signals")
    return errors
