#!/usr/bin/env python3
"""CLI entry point for the Allure failure analysis agent."""

import argparse
import sys

from agents.allure_failure_agent import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Allure results and classify failed tests as product bugs, DOM changes, or automation issues."
    )
    parser.add_argument(
        "--allure-dir",
        default="",
        help="Path to the allure-results directory.",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Use heuristic classification only; do not call Anthropic.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Anthropic model to use for classification (default: claude-sonnet-4-6).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Anthropic API key to use instead of ANTHROPIC_API_KEY.",
    )
    args = parser.parse_args()

    sys.exit(
        run(
            allure_dir=args.allure_dir,
            no_ai=args.no_ai,
            model=args.model or None,
            api_key=args.api_key,
        )
    )


if __name__ == "__main__":
    main()
