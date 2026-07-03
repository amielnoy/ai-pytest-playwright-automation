"""Shared Anthropic tool-use loop for the repo's AI agents.

Extracts the streaming agentic loop that test_planner_agent.py established so the
test-writer and test-healer agents don't duplicate it. Each agent supplies its
own system prompt, tool schemas, and a `dispatch(name, input) -> str` callback.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Callable, cast

import anthropic

# Same model the planner agent standardised on, kept consistent across the pipeline.
DEFAULT_MODEL = "claude-opus-4-7"


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable is not set.")
    return anthropic.Anthropic(api_key=api_key)


def run_agent(
    *,
    system_prompt: str,
    tools: list[dict],
    dispatch: Callable[[str, dict], str],
    user_message: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 16000,
    client: anthropic.Anthropic | None = None,
) -> str:
    """Drive an Anthropic tool-use conversation to completion.

    Streams assistant text to stdout, executes every requested tool via
    `dispatch`, and loops until the model stops requesting tools. Returns the
    final assistant text.
    """
    client = client or get_client()
    messages: list[dict] = [{"role": "user", "content": user_message}]
    final_text = ""

    while True:
        collected_tool_uses: list[dict] = []

        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=cast(Any, tools),
            messages=cast(Any, messages),
        ) as stream:
            for event in stream:
                if getattr(event, "type", None) == "content_block_delta":
                    delta = event.delta
                    if getattr(delta, "type", None) == "text_delta":
                        print(delta.text, end="", flush=True)
            final = stream.get_final_message()

        for block in final.content:
            if block.type == "text":
                final_text = block.text
            elif block.type == "tool_use":
                collected_tool_uses.append(
                    {"id": block.id, "name": block.name, "input": block.input}
                )

        messages.append({"role": "assistant", "content": final.content})

        if final.stop_reason == "end_turn" or not collected_tool_uses:
            print("\n\nAgent finished.", flush=True)
            return final_text

        tool_results = []
        for tu in collected_tool_uses:
            print(f"\n→ Calling tool: {tu['name']}", flush=True)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": dispatch(tu["name"], tu["input"]),
                }
            )
        messages.append({"role": "user", "content": tool_results})
