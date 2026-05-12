#!/usr/bin/env python3
"""
CLI entry point for generating a detailed STD from one webpage URL.

Usage:
    python run_playwright_cli_std_agent.py https://tutorialsninja.com/demo
    python run_playwright_cli_std_agent.py https://tutorialsninja.com/demo/index.php?route=account/login --feature Login
"""
from agents.playwright_cli_std_agent import main


if __name__ == "__main__":
    raise SystemExit(main())
