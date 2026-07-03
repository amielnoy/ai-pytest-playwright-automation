"""
AI Test Writer Agent
--------------------
Consumes the Software Test Documents (STDs) produced by test_planner_agent.py
and writes runnable pytest + Playwright test files that follow this project's
conventions: Page Object Model, shared fixtures, Allure decorators and markers.

Pipeline position:  planner (STD) → **writer (tests)** → healer (fixes failures)

Tools available to Claude:
  list_stds()                     – names of the STDs under stds/
  read_std(filename)              – full Markdown of one STD
  read_page_objects()            – every pages/ + pages/components/ class (reuse, never invent selectors)
  read_existing_tests()          – existing tests/web-ui + conftest.py for patterns/fixtures
  save_test(filename, content)    – write a test file into tests/web-ui/
  validate_test(filename)         – pytest --collect-only on the new file
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from agents._agent_loop import run_agent

_ROOT = Path(__file__).parent.parent
_STDS_DIR = _ROOT / "stds"
_PAGES_DIR = _ROOT / "pages"
_WEB_UI_DIR = _ROOT / "tests" / "web-ui"

TOOLS: list[dict] = [
    {
        "name": "list_stds",
        "description": "List the available Software Test Document (STD) filenames in stds/.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_std",
        "description": "Read the full Markdown content of one STD file from stds/.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "e.g. STD_Registration.md"}},
            "required": ["filename"],
        },
    },
    {
        "name": "read_page_objects",
        "description": (
            "Read every Page Object class under pages/ and pages/components/. Use these to drive "
            "the browser via business methods — NEVER put raw selectors in a test. If a needed "
            "method does not exist, note it rather than inventing selectors."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_existing_tests",
        "description": (
            "Read existing tests/web-ui test files and the root conftest.py so you follow the same "
            "fixtures (e.g. registration_pages, api_cart), Allure decorators and markers."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "save_test",
        "description": "Save a pytest + Playwright test file into tests/web-ui/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "e.g. test_registration.py"},
                "content": {"type": "string", "description": "Full Python source of the test module."},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "validate_test",
        "description": (
            "Run `pytest --collect-only` on a test file to confirm it imports and collects cleanly. "
            "Returns collection output; fix any errors before finishing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "e.g. test_registration.py"}},
            "required": ["filename"],
        },
    },
]


def _read_dir(root: Path, pattern: str) -> dict[str, str]:
    return {
        str(p.relative_to(_ROOT)): p.read_text(encoding="utf-8")
        for p in sorted(root.rglob(pattern))
        if "__pycache__" not in p.parts
    }


def _tool_list_stds() -> str:
    return json.dumps(sorted(p.name for p in _STDS_DIR.glob("*.md")))


def _tool_read_std(filename: str) -> str:
    path = _STDS_DIR / Path(filename).name
    if not path.exists():
        return json.dumps({"error": f"STD not found: {path.name}"})
    return path.read_text(encoding="utf-8")


def _tool_read_page_objects() -> str:
    files = _read_dir(_PAGES_DIR, "*.py")
    return json.dumps(files, indent=2, ensure_ascii=False)


def _tool_read_existing_tests() -> str:
    files = _read_dir(_WEB_UI_DIR, "test_*.py")
    conftest = _ROOT / "conftest.py"
    if conftest.exists():
        files["conftest.py"] = conftest.read_text(encoding="utf-8")
    return json.dumps(files, indent=2, ensure_ascii=False)


def _safe_test_name(filename: str) -> str:
    name = Path(filename).name
    if not name.startswith("test_"):
        name = "test_" + name
    if not name.endswith(".py"):
        name += ".py"
    return name


def _tool_save_test(filename: str, content: str) -> str:
    _WEB_UI_DIR.mkdir(parents=True, exist_ok=True)
    dest = _WEB_UI_DIR / _safe_test_name(filename)
    dest.write_text(content, encoding="utf-8")
    print(f"  [tool] save_test → {dest}", flush=True)
    return json.dumps({"saved": str(dest.relative_to(_ROOT))})


def _tool_validate_test(filename: str) -> str:
    dest = _WEB_UI_DIR / _safe_test_name(filename)
    if not dest.exists():
        return json.dumps({"error": f"file not found: {dest.name} — save it first"})
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", str(dest)],
        cwd=_ROOT, capture_output=True, text=True,
    )
    tail = (proc.stdout + proc.stderr).strip()[-3000:]
    return json.dumps({"returncode": proc.returncode, "collected_ok": proc.returncode == 0, "output": tail})


def _dispatch(name: str, tool_input: dict) -> str:
    if name == "list_stds":
        return _tool_list_stds()
    if name == "read_std":
        return _tool_read_std(tool_input["filename"])
    if name == "read_page_objects":
        return _tool_read_page_objects()
    if name == "read_existing_tests":
        return _tool_read_existing_tests()
    if name == "save_test":
        return _tool_save_test(tool_input["filename"], tool_input["content"])
    if name == "validate_test":
        return _tool_validate_test(tool_input["filename"])
    return json.dumps({"error": f"Unknown tool: {name}"})


SYSTEM_PROMPT = """You are a senior SDET who writes Playwright + pytest automation for the
TutorialsNinja demo store, turning Software Test Documents (STDs) into runnable test files.

## Process
1. `read_std` the target STD(s) (use `list_stds` if you need the names).
2. `read_page_objects` to learn the available Page Object methods.
3. `read_existing_tests` to copy the exact fixture names, Allure decorators and markers already in use.
4. Write ONE test module per STD and `save_test` it under tests/web-ui/.
5. `validate_test` the file and fix anything until it collects cleanly.

## Hard rules (this project's conventions)
- NO raw Playwright selectors in tests. Drive the browser only through Page Object business
  methods from pages/. If the STD needs an interaction no Page Object exposes, add a short note
  in a comment at the top of the test — do NOT invent selectors inline.
- Use the shared fixtures from conftest.py (e.g. page/context/app_url and the page-object fixtures);
  prefer API setup fixtures (e.g. api_cart) when UI setup would be slow or flaky.
- Every test class/function carries Allure decorators: @allure.feature / @allure.story /
  @allure.title / @allure.severity, and wraps logical steps in `with allure.step(...)`.
- Tag each test with the correct pytest marker (registration / search / cart / api / contract / sanity)
  matching the STD's Marker field.
- Read test data via utils/data_loader (get_test_data) — never hard-code credentials or read files directly.
- Mirror the structure, naming and imports of the existing tests exactly.

Keep going until every requested STD has a saved, cleanly-collecting test file.
"""


def run(stds: list[str] | None = None) -> None:
    available = sorted(p.name for p in _STDS_DIR.glob("*.md"))
    if stds:
        targets = "\n".join(f"- {s}" for s in stds)
        user_message = (
            f"Write pytest + Playwright test files for these STDs:\n{targets}\n\n"
            "Read each STD, read the page objects and existing tests, then save and validate a "
            "test module for each."
        )
    else:
        listing = "\n".join(f"- {s}" for s in available) or "(none found)"
        user_message = (
            "Write pytest + Playwright test files for every STD in stds/:\n"
            f"{listing}\n\n"
            "For each STD: read it, read the page objects and existing tests, then save and validate "
            "a matching test module under tests/web-ui/."
        )

    print("Starting test writer agent...\n", flush=True)
    run_agent(system_prompt=SYSTEM_PROMPT, tools=TOOLS, dispatch=_dispatch, user_message=user_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pytest+Playwright tests from STDs.")
    parser.add_argument("stds", nargs="*", help="STD filenames to write tests for (default: all).")
    args = parser.parse_args()
    run(args.stds or None)
