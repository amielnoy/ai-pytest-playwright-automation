#!/usr/bin/env python3
"""
CLI entry point for the AI test planner agent.

Usage:
    python run_agent.py
    python run_agent.py --pages https://tutorialsninja.com/demo/index.php?route=account/register

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
"""
import argparse
import sys

from agents.test_planner_agent import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate STDs for TutorialsNinja using a Playwright + Claude agent."
    )
    parser.add_argument(
        "--pages",
        nargs="*",
        metavar="URL",
        help="One or more page URLs to analyse. Omit to run the full default set.",
    )
    args = parser.parse_args()
    run(pages=args.pages or None)


if __name__ == "__main__":
    sys.exit(main())
