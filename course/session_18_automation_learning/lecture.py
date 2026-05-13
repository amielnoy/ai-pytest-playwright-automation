"""
Session 18 - Automation Learning
Key concepts: deliberate practice, automation backlog, learning plan, portfolio evidence.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LearningTask:
    """A small automation practice task with measurable output."""

    title: str
    focus: str
    output: str
    verification: str


LEARNING_LOOP = [
    "Observe product behavior manually",
    "Design the test idea and expected result",
    "Script the smallest useful path",
    "Refactor into the correct framework layer",
    "Verify with a focused test command",
    "Report with readable names and debug artifacts",
    "Reflect on the failure, fix, and next skill",
]


FOUR_WEEK_PLAN = {
    "Week 1": LearningTask(
        title="Selectors and smoke coverage",
        focus="Stable locators, clear assertions, and one isolated browser test.",
        output="One automated smoke test and three manual test cases.",
        verification="pytest tests/web-ui -q -k smoke",
    ),
    "Week 2": LearningTask(
        title="Page objects and fixtures",
        focus="Move browser interactions out of tests.",
        output="Two tests with no raw selectors in the test body.",
        verification="pytest tests/web-ui -q",
    ),
    "Week 3": LearningTask(
        title="API setup and contracts",
        focus="Use service classes to create state and validate fast contracts.",
        output="One shortened UI test plus two API or contract tests.",
        verification="pytest tests/api tests/contract -q",
    ),
    "Week 4": LearningTask(
        title="Debugging and reporting",
        focus="Diagnose a failing test through screenshots, traces, and Allure.",
        output="One documented failure analysis and one improved report.",
        verification="pytest -q --alluredir=allure-results",
    ),
}


AUTOMATION_BACKLOG = [
    LearningTask(
        title="Cart quantity update",
        focus="Page object behavior and exact assertions.",
        output="A test that updates quantity and verifies subtotal.",
        verification="pytest tests/web-ui -q -k cart",
    ),
    LearningTask(
        title="Search contract",
        focus="Service layer and parseable product data.",
        output="A contract test for search result product fields.",
        verification="pytest tests/contract -q -k search",
    ),
    LearningTask(
        title="Failure report quality",
        focus="Allure steps and screenshot attachments.",
        output="A failed run that explains the root cause from the report.",
        verification="npm run allure:generate",
    ),
]


def print_plan() -> None:
    print("Automation learning loop:")
    for index, step in enumerate(LEARNING_LOOP, start=1):
        print(f"  {index}. {step}")

    print("\nFour-week plan:")
    for week, task in FOUR_WEEK_PLAN.items():
        print(f"  {week}: {task.title}")
        print(f"    Focus: {task.focus}")
        print(f"    Output: {task.output}")
        print(f"    Verify: {task.verification}")

    print("\nBacklog ideas:")
    for task in AUTOMATION_BACKLOG:
        print(f"  - {task.title}: {task.output}")


if __name__ == "__main__":
    print_plan()
