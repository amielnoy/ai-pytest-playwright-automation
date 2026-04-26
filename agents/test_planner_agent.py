"""
AI Test Planner Agent
---------------------
Uses Playwright to crawl live pages on tutorialsninja.com/demo, then asks
Claude (claude-opus-4-7 with adaptive thinking) to produce detailed STDs
(Software Test Documents) based on what it actually finds on the page.

Tools available to Claude:
  analyze_page(url)          – Playwright crawl → structured page data JSON
  read_existing_tests()      – Returns all existing test files as context
  save_std(filename, content) – Writes the STD to stds/
"""
import json
import os
import sys
from pathlib import Path

import anthropic

from agents.page_crawler import crawl_page_as_json

_ROOT = Path(__file__).parent.parent
_STDS_DIR = _ROOT / "stds"
_TESTS_DIR = _ROOT / "tests"

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "analyze_page",
        "description": (
            "Navigate to a URL using a real browser and extract the page structure: "
            "title, headings, all HTML forms with field names/types/labels/required flags, "
            "buttons, navigation links, and any visible alert or error messages. "
            "Use this to understand what is on the page before writing test steps."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL to crawl (e.g. https://tutorialsninja.com/demo/index.php?route=account/register)",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "read_existing_tests",
        "description": (
            "Read all existing Playwright pytest test files in the project. "
            "Returns their filenames and source code so you can understand what is "
            "already covered and follow the same patterns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "save_std",
        "description": (
            "Save a completed Software Test Document (STD) as a Markdown file "
            "in the stds/ directory."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename without path, e.g. STD_Registration.md",
                },
                "content": {
                    "type": "string",
                    "description": "Full Markdown content of the STD.",
                },
            },
            "required": ["filename", "content"],
        },
    },
]

# ── Tool implementations ──────────────────────────────────────────────────────

def _tool_analyze_page(url: str) -> str:
    print(f"  [tool] analyze_page → {url}", flush=True)
    try:
        return crawl_page_as_json(url)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_read_existing_tests() -> str:
    print("  [tool] read_existing_tests", flush=True)
    files: dict[str, str] = {}
    for path in sorted(_TESTS_DIR.glob("test_*.py")):
        files[path.name] = path.read_text(encoding="utf-8")
    return json.dumps(files, indent=2, ensure_ascii=False)


def _tool_save_std(filename: str, content: str) -> str:
    _STDS_DIR.mkdir(exist_ok=True)
    # Sanitise filename
    safe = "".join(c if (c.isalnum() or c in "._- ") else "_" for c in filename).strip()
    if not safe.endswith(".md"):
        safe += ".md"
    dest = _STDS_DIR / safe
    dest.write_text(content, encoding="utf-8")
    print(f"  [tool] save_std → {dest}", flush=True)
    return json.dumps({"saved": str(dest)})


def _dispatch_tool(name: str, tool_input: dict) -> str:
    if name == "analyze_page":
        return _tool_analyze_page(tool_input["url"])
    if name == "read_existing_tests":
        return _tool_read_existing_tests()
    if name == "save_std":
        return _tool_save_std(tool_input["filename"], tool_input["content"])
    return json.dumps({"error": f"Unknown tool: {name}"})

# ── System prompt (cached) ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior QA engineer and test architect specialising in web application testing.

Your task is to produce detailed Software Test Documents (STDs) for the TutorialsNinja demo
e-commerce site (https://tutorialsninja.com/demo).

## Process
1. Call `analyze_page` on each relevant URL to obtain real, live page structure.
2. Call `read_existing_tests` to understand what is already automated and what patterns are used.
3. Write one STD per feature/flow, then call `save_std` to persist it.

## STD Format
Each STD must follow this exact structure:

---
# STD-<ID>: <Feature Name>

## Overview
| Field | Value |
|---|---|
| Test Suite | <suite name> |
| Feature | <feature name> |
| Priority | High / Medium / Low |
| Author | QA Agent |
| Date | <today> |

## Objective
<One or two sentences describing what the test suite validates.>

## Preconditions
- <List every precondition needed before the first step executes>

## Test Cases

### TC-<ID>-01: <Scenario Name>
**Objective:** <what this specific case proves>
**Severity:** Critical / High / Normal / Low

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | <concrete UI action> | <exact value or N/A> | <observable outcome> |
| 2 | ... | ... | ... |

**Post-conditions:** <system state after the test>

### TC-<ID>-02: <Next Scenario>
...

## Notes
- <Any important notes about environment, test data generation, or known limitations>
---

## Rules
- Steps must be concrete: name the exact field, button, or link the tester clicks.
- Test data must be explicit (e.g. "email: test_{ts}@example.com" for dynamic data).
- Cover both happy paths and key negative/edge cases.
- Do not invent page structure — only reference elements you found with `analyze_page`.
- Generate one STD file per major feature (registration, login, search, cart, checkout, etc.).
"""

# ── Agent loop ────────────────────────────────────────────────────────────────

def run(pages: list[str] | None = None) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable is not set.")

    client = anthropic.Anthropic(api_key=api_key)

    # Build the initial user message listing which pages to analyse
    if pages:
        page_list = "\n".join(f"- {u}" for u in pages)
        user_message = (
            f"Please analyse the following pages and generate detailed STDs for each feature:\n\n"
            f"{page_list}\n\n"
            "For each feature, crawl the relevant page(s), read the existing tests for context, "
            "then write and save a complete STD."
        )
    else:
        user_message = (
            "Analyse the TutorialsNinja demo site and generate comprehensive STDs for all "
            "major features: registration, login, search, add-to-cart, and cart checkout.\n\n"
            "Relevant URLs:\n"
            "- https://tutorialsninja.com/demo (home)\n"
            "- https://tutorialsninja.com/demo/index.php?route=account/register\n"
            "- https://tutorialsninja.com/demo/index.php?route=account/login\n"
            "- https://tutorialsninja.com/demo/index.php?route=product/search&search=macbook\n"
            "- https://tutorialsninja.com/demo/index.php?route=checkout/cart\n\n"
            "For each feature, crawl the page, read existing tests, then save the STD."
        )

    messages: list[dict] = [{"role": "user", "content": user_message}]

    print("Starting test planner agent...\n", flush=True)

    # ── Agentic loop ──────────────────────────────────────────────────────────
    while True:
        # Collect the full streamed response
        collected_text = ""
        collected_tool_uses: list[dict] = []
        stop_reason: str | None = None

        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # Cache the stable system prompt — saves tokens on every loop iteration
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                # Print text deltas as they arrive
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        delta = event.delta
                        if hasattr(delta, "text"):
                            print(delta.text, end="", flush=True)
                            collected_text += delta.text

            final = stream.get_final_message()
            stop_reason = final.stop_reason

            # Collect all content blocks
            for block in final.content:
                if block.type == "text":
                    collected_text = block.text  # use final authoritative text
                elif block.type == "tool_use":
                    collected_tool_uses.append(
                        {"id": block.id, "name": block.name, "input": block.input}
                    )

        # Append assistant turn to history (preserve all content blocks)
        messages.append({"role": "assistant", "content": final.content})

        if stop_reason == "end_turn" or not collected_tool_uses:
            print("\n\nAgent finished.", flush=True)
            break

        # Execute every tool call and collect results
        tool_results = []
        for tu in collected_tool_uses:
            print(f"\n→ Calling tool: {tu['name']}", flush=True)
            result = _dispatch_tool(tu["name"], tu["input"])
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": result,
                }
            )

        # Feed results back as a user turn
        messages.append({"role": "user", "content": tool_results})
