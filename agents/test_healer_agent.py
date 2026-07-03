"""
AI Test Automation Healer Agent
-------------------------------
Repairs failing Playwright + pytest automation. It runs the failing test, reads
the trace, and heals it — preferring to fix the Page Object selector over the
test itself. When an in-place repair isn't enough it regenerates the test from
its STD by delegating to the **test writer agent** (the previous stage).

Pipeline position:  planner (STD) → writer (tests) → **healer (fixes failures)**

Tools available to Claude:
  run_test(target)                 – pytest a file or node id; returns pass/fail + trace
  list_tests()                     – test files under tests/web-ui/
  read_test(filename)              – source of one test file
  read_page_objects()              – every pages/ + pages/components/ class
  save_test(filename, content)     – overwrite a test file
  save_page_object(path, content)  – overwrite a Page Object (heal a drifted selector)
  list_stds() / read_std(name)     – the STDs behind the tests
  regenerate_from_std(std)         – rebuild the test from its STD via the writer agent
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
        "name": "run_test",
        "description": (
            "Run pytest on a single test file or node id (e.g. 'test_login.py' or "
            "'test_login.py::TestLogin::test_valid'). Returns the pass/fail status and the "
            "captured output/traceback. Use it to reproduce the failure and to verify a fix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"target": {"type": "string", "description": "test file name or pytest node id under tests/web-ui/"}},
            "required": ["target"],
        },
    },
    {
        "name": "list_tests",
        "description": "List the test files under tests/web-ui/.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_test",
        "description": "Read the source of one test file under tests/web-ui/.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"],
        },
    },
    {
        "name": "read_page_objects",
        "description": "Read every Page Object class under pages/ and pages/components/.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "save_test",
        "description": "Overwrite a test file under tests/web-ui/ with repaired content.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
            "required": ["filename", "content"],
        },
    },
    {
        "name": "save_page_object",
        "description": (
            "Overwrite a Page Object file to heal a drifted selector or add a missing method. "
            "Path is relative to pages/, e.g. 'login_page.py' or 'components/nav_bar.py'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_stds",
        "description": "List the STD filenames in stds/.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_std",
        "description": "Read one STD's Markdown from stds/.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"],
        },
    },
    {
        "name": "regenerate_from_std",
        "description": (
            "Last resort: rebuild the test from its STD by invoking the test writer agent. "
            "Use only when an in-place fix to the test or Page Object cannot recover the test."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"std": {"type": "string", "description": "e.g. STD_Login.md"}},
            "required": ["std"],
        },
    },
]


def _read_dir(root: Path, pattern: str) -> dict[str, str]:
    return {
        str(p.relative_to(_ROOT)): p.read_text(encoding="utf-8")
        for p in sorted(root.rglob(pattern))
        if "__pycache__" not in p.parts
    }


def _resolve_target(target: str) -> str:
    """Turn 'test_x.py[::node]' into a path under tests/web-ui/ that pytest accepts."""
    file_part = target.split("::", 1)[0]
    node = target[len(file_part):]
    name = Path(file_part).name
    return f"{(_WEB_UI_DIR / name).relative_to(_ROOT)}{node}"


def _tool_run_test(target: str) -> str:
    rel = _resolve_target(target)
    print(f"  [tool] run_test → {rel}", flush=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", rel, "-p", "no:xdist", "-o", "addopts=", "-q"],
        cwd=_ROOT, capture_output=True, text=True,
    )
    out = (proc.stdout + proc.stderr).strip()[-6000:]
    return json.dumps({"target": rel, "passed": proc.returncode == 0, "returncode": proc.returncode, "output": out})


def _tool_read_test(filename: str) -> str:
    path = _WEB_UI_DIR / Path(filename).name
    if not path.exists():
        return json.dumps({"error": f"test not found: {path.name}"})
    return path.read_text(encoding="utf-8")


def _tool_save_test(filename: str, content: str) -> str:
    dest = _WEB_UI_DIR / Path(filename).name
    dest.write_text(content, encoding="utf-8")
    print(f"  [tool] save_test → {dest}", flush=True)
    return json.dumps({"saved": str(dest.relative_to(_ROOT))})


def _tool_save_page_object(path: str, content: str) -> str:
    # keep the write inside pages/ (allow the components/ subdir)
    dest = (_PAGES_DIR / path).resolve()
    if _PAGES_DIR.resolve() not in dest.parents and dest != _PAGES_DIR.resolve():
        return json.dumps({"error": "path must be inside pages/"})
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"  [tool] save_page_object → {dest}", flush=True)
    return json.dumps({"saved": str(dest.relative_to(_ROOT))})


def _tool_read_std(filename: str) -> str:
    path = _STDS_DIR / Path(filename).name
    if not path.exists():
        return json.dumps({"error": f"STD not found: {path.name}"})
    return path.read_text(encoding="utf-8")


def _tool_regenerate_from_std(std: str) -> str:
    print(f"  [tool] regenerate_from_std → {std} (delegating to test writer agent)", flush=True)
    from agents import test_writer_agent
    try:
        test_writer_agent.run([Path(std).name])
        return json.dumps({"regenerated": std})
    except Exception as exc:  # noqa: BLE001 - surface any delegation error to the model
        return json.dumps({"error": f"writer agent failed: {exc}"})


def _dispatch(name: str, tool_input: dict) -> str:
    if name == "run_test":
        return _tool_run_test(tool_input["target"])
    if name == "list_tests":
        return json.dumps(sorted(p.name for p in _WEB_UI_DIR.glob("test_*.py")))
    if name == "read_test":
        return _tool_read_test(tool_input["filename"])
    if name == "read_page_objects":
        return json.dumps(_read_dir(_PAGES_DIR, "*.py"), indent=2, ensure_ascii=False)
    if name == "save_test":
        return _tool_save_test(tool_input["filename"], tool_input["content"])
    if name == "save_page_object":
        return _tool_save_page_object(tool_input["path"], tool_input["content"])
    if name == "list_stds":
        return json.dumps(sorted(p.name for p in _STDS_DIR.glob("*.md")))
    if name == "read_std":
        return _tool_read_std(tool_input["filename"])
    if name == "regenerate_from_std":
        return _tool_regenerate_from_std(tool_input["std"])
    return json.dumps({"error": f"Unknown tool: {name}"})


SYSTEM_PROMPT = """You are a senior SDET who heals failing Playwright + pytest automation for the
TutorialsNinja demo store.

## Process
1. `run_test` the failing target to reproduce it and read the traceback.
2. Diagnose the failure category:
   - **DOM / selector drift** — a locator no longer matches. Fix it in the PAGE OBJECT
     (`save_page_object`), not the test. Prefer stable locators (role/label/id) and, where the
     project supports it, add a fallback via the existing self-healing helper.
   - **Automation bug** — wrong step order, bad wait, or a mis-scoped assertion. Fix the test or
     the page object method as appropriate.
   - **Real product bug** — the app genuinely misbehaves. Do NOT paper over it; leave the test
     failing and clearly report it as a product defect in your final summary.
3. Re-`run_test` after every change and iterate until it passes (or you've confirmed a product bug).
4. Only if in-place repair cannot recover the test, call `regenerate_from_std` to rebuild it from
   its STD via the writer agent, then `run_test` again.

## Rules
- Keep raw selectors in Page Objects, never in tests.
- Make the smallest change that fixes the root cause; don't weaken assertions to force a pass.
- Preserve the test's intent and its Allure decorators/markers.
- End with a short report: what failed, the category, what you changed, and the final status.
"""


def run(target: str) -> None:
    user_message = (
        f"Heal the failing automation test: {target}\n\n"
        "Reproduce it with run_test, read the page objects, diagnose the root cause, fix it "
        "(prefer the Page Object over the test), and re-run until it passes — or confirm it's a "
        "real product bug. Use regenerate_from_std only as a last resort."
    )
    print(f"Starting test healer agent for: {target}\n", flush=True)
    run_agent(system_prompt=SYSTEM_PROMPT, tools=TOOLS, dispatch=_dispatch, user_message=user_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Heal a failing Playwright+pytest test.")
    parser.add_argument("target", help="failing test file or node id, e.g. test_login.py::TestLogin::test_valid")
    args = parser.parse_args()
    run(args.target)
