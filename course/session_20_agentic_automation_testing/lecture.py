"""
Session 20 - Agentic Automation Testing
Key concepts: supervised workflows, guardrails, failure investigation, CI analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentWorkflow:
    goal: str
    inputs: tuple[str, ...]
    tools: tuple[str, ...]
    write_scope: str
    stop_condition: str
    output: str


@dataclass(frozen=True)
class QualityGate:
    name: str
    required: bool
    reason: str


FAILURE_INVESTIGATION_WORKFLOW = AgentWorkflow(
    goal="Investigate one failing web UI test and produce a verified investigation record.",
    inputs=(
        "test name",
        "traceback",
        "screenshot path",
        "trace artifact",
        "recent changed files",
    ),
    tools=(
        "read files",
        "run narrow pytest command",
        "inspect artifacts",
    ),
    write_scope="Read-only during investigation. Code edits require a separate approved task.",
    stop_condition="Root cause verified or three plausible hypotheses rejected.",
    output="Root cause, evidence, fix recommendation, verification command, residual risk.",
)


AGENT_TEST_QUALITY_GATES = [
    QualityGate(
        name="No raw selectors in tests",
        required=True,
        reason="UI structure belongs in page objects or components.",
    ),
    QualityGate(
        name="Concrete assertion",
        required=True,
        reason="The test must fail for a meaningful product regression.",
    ),
    QualityGate(
        name="Stable data",
        required=True,
        reason="Parallel execution and repeated runs need isolated inputs.",
    ),
    QualityGate(
        name="No sleeps",
        required=True,
        reason="Fixed delays hide timing bugs and slow the suite.",
    ),
    QualityGate(
        name="Readable report output",
        required=True,
        reason="Failures must be diagnosable from CI artifacts.",
    ),
]


TASK_CLASSIFICATION = {
    "summarize pytest traceback": "safe_read_only",
    "group Allure failures by feature": "safe_read_only",
    "draft a new test": "human_approval_required",
    "edit a page object": "human_approval_required",
    "change CI deployment rules": "not_safe_for_agent",
    "update credentials": "not_safe_for_agent",
}


def print_workflow(workflow: AgentWorkflow) -> None:
    print(f"Goal: {workflow.goal}")
    print("\nInputs:")
    for item in workflow.inputs:
        print(f"  - {item}")
    print("\nTools:")
    for tool in workflow.tools:
        print(f"  - {tool}")
    print(f"\nWrite scope: {workflow.write_scope}")
    print(f"Stop condition: {workflow.stop_condition}")
    print(f"Output: {workflow.output}")


def print_quality_gates(gates: list[QualityGate]) -> None:
    print("\nQuality gates:")
    for gate in gates:
        required = "required" if gate.required else "optional"
        print(f"  - {gate.name} ({required}): {gate.reason}")


def print_task_classification() -> None:
    print("\nTask classification:")
    for task, classification in TASK_CLASSIFICATION.items():
        print(f"  - {task}: {classification}")


if __name__ == "__main__":
    print_workflow(FAILURE_INVESTIGATION_WORKFLOW)
    print_quality_gates(AGENT_TEST_QUALITY_GATES)
    print_task_classification()
