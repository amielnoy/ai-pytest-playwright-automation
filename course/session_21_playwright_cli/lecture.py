"""
Session 21 - Playwright CLI
Key concepts: codegen, screenshots, trace viewer, CLI-to-framework workflow.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CliCommand:
    command: str
    purpose: str
    course_use: str


PLAYWRIGHT_CLI_COMMANDS = [
    CliCommand(
        command="python3 -m playwright install chromium",
        purpose="Install Chromium browser binaries.",
        course_use="Run once during setup or when browser binaries are missing.",
    ),
    CliCommand(
        command="python3 -m playwright codegen https://tutorialsninja.com/demo",
        purpose="Generate actions while manually using the browser.",
        course_use="Discover locators and flow order, then refactor into page objects.",
    ),
    CliCommand(
        command="python3 -m playwright open https://tutorialsninja.com/demo",
        purpose="Open a page for quick manual inspection.",
        course_use="Check current page state before writing a test.",
    ),
    CliCommand(
        command="python3 -m playwright screenshot https://tutorialsninja.com/demo artifacts/home.png",
        purpose="Capture a screenshot from the command line.",
        course_use="Collect quick visual evidence for notes or bug reports.",
    ),
    CliCommand(
        command="python3 -m playwright show-trace path/to/trace.zip",
        purpose="Open a saved trace file.",
        course_use="Debug failed Playwright runs through action snapshots and network data.",
    ),
]


CODEGEN_REVIEW_RULES = [
    "Keep locator ideas, not raw generated tests.",
    "Move Playwright calls into page objects or components.",
    "Keep assertions concrete and behavior-focused.",
    "Remove sleeps and replace them with state-based waits.",
    "Run the narrowest pytest command after refactoring.",
]


def print_cli_reference() -> None:
    print("Playwright CLI reference:")
    for item in PLAYWRIGHT_CLI_COMMANDS:
        print(f"  {item.command}")
        print(f"    Purpose: {item.purpose}")
        print(f"    Course use: {item.course_use}")

    print("\nCodegen review rules:")
    for rule in CODEGEN_REVIEW_RULES:
        print(f"  - {rule}")


if __name__ == "__main__":
    print_cli_reference()
