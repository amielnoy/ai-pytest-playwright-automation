# Added in Session 15 — AI browser exploration agent
from .explorer import run_agent, TOOLS
from agents.playwright_cli_std_agent import StdAgentResult, run as run_playwright_cli_std_agent

__all__ = [
    "run_agent",
    "TOOLS",
    "StdAgentResult",
    "run_playwright_cli_std_agent",
]
