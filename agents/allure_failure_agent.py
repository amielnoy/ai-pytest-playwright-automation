from __future__ import annotations

import json
import os
import re
import textwrap
from pathlib import Path
from typing import Any

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_ALLURE_DIR = _PROJECT_ROOT / "allure-results"
_DEFAULT_MODEL = "llama-3.3-70b-versatile"

_CATEGORIES = (
    "passed",
    "product_bug",
    "dom_change",
    "automation_bug",
    "environment_issue",
    "flaky",
    "unknown",
)

_DOM_PATTERNS = [
    r"locator.*to_have_count",
    r"locator.*resolved to .* elements",
    r"no such element",
    r"element .* not found",
    r"timeout.*locator",
    r"to_have_text",
    r"to_be_visible",
    r"to_have_attribute",
    r"stale element reference",
    r"element not attached",
    r"locator\.resolved",
    r"wait_for.*element",
    r"expect\(self\..*\.resolved\)",
]

_PRODUCT_PATTERNS = [
    r"expected.*to equal",
    r"expected.*to be",
    r"expected.*but got",
    r"price",
    r"total",
    r"quantity",
    r"discount",
    r"tax",
    r"shipping",
    r"checkout",
    r"search",
    r"login",
    r"registration",
    r"response.*status.*200",
    r"response.*contains",
    r"db error",
    r"invalid input",
    r"not found",
]

_AUTOMATION_PATTERNS = [
    r"TypeError",
    r"AttributeError",
    r"ValueError",
    r"NameError",
    r"ImportError",
    r"RuntimeError",
    r"fixture.*not.*found",
    r"invalid syntax",
    r"cannot connect",
    r"connection refused",
    r"timed out",
    r"timeout",
    r"remote error",
    r"session not created",
    r"node is not attached",
]

_ENV_PATTERNS = [
    r"connection refused",
    r"name or service not known",
    r"dns",
    r"network",
    r"proxy",
    r"ssl",
    r"certificate",
    r"timeout",
    r"connection reset",
]

_JSON_OBJECT_RE = re.compile(r"\{.*\}", flags=re.S)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _load_allure_results(allure_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(allure_dir.glob("*-result.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                results.append(json.load(handle))
        except (OSError, json.JSONDecodeError):
            continue
    return results


def _extract_failure_context(result: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for step in result.get("steps", []) or []:
        steps.append({
            "name": _normalize_text(step.get("name")),
            "status": _normalize_text(step.get("status")),
            "message": _normalize_text((step.get("statusDetails") or {}).get("message")),
            "trace": _normalize_text((step.get("statusDetails") or {}).get("trace")),
        })

    message = _normalize_text((result.get("statusDetails") or {}).get("message"))
    trace = _normalize_text((result.get("statusDetails") or {}).get("trace"))

    return {
        "name": result.get("name", ""),
        "full_name": result.get("fullName", ""),
        "status": _normalize_text(result.get("status")),
        "message": message,
        "trace": trace,
        "steps": steps,
        "labels": result.get("labels", []),
        "attachments": result.get("attachments", []),
    }


def _matches_any(patterns: list[str], text: str) -> bool:
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _result_history_is_flaky(history_map: dict[str, list[dict[str, Any]]], raw: dict[str, Any]) -> bool:
    history_id = raw.get("historyId") or raw.get("uuid") or ""
    results = history_map.get(history_id, [])
    statuses = { _normalize_text(r.get("status")) for r in results }
    if "passed" in statuses and any(s != "passed" for s in statuses):
        return True
    return False


def _result_is_flaky(raw: dict[str, Any], history_map: dict[str, list[dict[str, Any]]]) -> bool:
    details = raw.get("statusDetails") or {}
    if details.get("flaky") is True:
        return True
    return _result_history_is_flaky(history_map, raw)


def _collect_failure_text(context: dict[str, Any]) -> str:
    parts = [
        f"Test: {context['full_name'] or context['name']}",
        f"Status: {context['status']}",
        f"Message: {context['message']}",
        f"Trace: {context['trace']}",
    ]
    for step in context["steps"]:
        if step["name"]:
            parts.append(f"Step: {step['name']}")
        if step["message"]:
            parts.append(f"Step message: {step['message']}")
        if step["trace"]:
            parts.append(f"Step trace: {step['trace']}")
    return "\n".join(parts)


def _classify_failure_heuristic(context: dict[str, Any]) -> str:
    if _normalize_text(context["status"]) == "passed":
        return "passed"

    all_text = "\n".join(
        [
            _normalize_text(context.get("message")),
            _normalize_text(context.get("trace")),
            _normalize_text(_collect_failure_text(context)),
        ]
    )
    if _matches_any(_DOM_PATTERNS, all_text):
        return "dom_change"
    if _matches_any(_ENV_PATTERNS, all_text):
        return "environment_issue"
    if _matches_any(_AUTOMATION_PATTERNS, all_text):
        return "automation_bug"
    if _matches_any(_PRODUCT_PATTERNS, all_text) and "assertionerror" in all_text:
        return "product_bug"

    return "unknown"


def _extract_json(text: str) -> dict[str, Any] | None:
    match = _JSON_OBJECT_RE.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _build_llm_prompt(context: dict[str, Any]) -> str:
    policy = (
        "You are a seasoned QA automation engineer. Classify the root cause of a failing test "
        "into one of these categories: product_bug, dom_change, automation_bug, environment_issue, unknown. "
        "Do not invent additional categories. The category should reflect whether the failure is most likely caused by: "
        "A real product defect (product_bug), a changed DOM/locator or UI structure break (dom_change), "
        "an automation/test code problem such as bad selectors, race conditions, or fixture setup (automation_bug), "
        "or an infrastructure/network environment issue (environment_issue). "
        "Respond in JSON only with keys: category, summary, confidence. "
        "Use high/medium/low for confidence. "
    )
    failure_text = _collect_failure_text(context)
    rag = _normalize_text(context.get("rag") or "")
    attachments = _normalize_text(context.get("attachments_text") or "")
    extra = []
    if rag:
        extra.append("Related historical results:\n" + rag)
    if attachments:
        extra.append("Attachments (excerpts):\n" + attachments)

    extra_text = "\n\n".join(extra)

    return textwrap.dedent(
        f"""
        {policy}

        Failure context:
        {failure_text}

        {extra_text}
        """
    )


def _classify_with_llm(context: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_llm_prompt(context)
    response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
    )

    text = response.content[0].text.strip()
    data = _extract_json(text)
    if isinstance(data, dict) and data.get("category") in _CATEGORIES:
        return {
            "category": data["category"],
            "summary": data.get("summary", ""),
            "confidence": data.get("confidence", "low"),
            "extraction": text,
        }

    return {
        "category": "unknown",
        "summary": text[:1024],
        "confidence": "low",
        "extraction": text,
    }


def analyze_allure_results(
    allure_dir: str = "",
    use_llm: bool = True,
    model: str = _DEFAULT_MODEL,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    resolved_dir = Path(allure_dir) if allure_dir else _DEFAULT_ALLURE_DIR
    if not resolved_dir.exists():
        raise FileNotFoundError(f"Allure results directory not found: {resolved_dir}")

    results = _load_allure_results(resolved_dir)
    history_map: dict[str, list[dict[str, Any]]] = {}
    for raw in results:
        history_id = raw.get("historyId") or raw.get("uuid") or ""
        history_map.setdefault(history_id, []).append(raw)

    outputs: list[dict[str, Any]] = []
    for raw in results:
        context = _extract_failure_context(raw)
        # Build RAG context: include recent history entries and small attachment excerpts
        history_id = raw.get("historyId") or raw.get("uuid") or ""
        related_texts: list[str] = []
        for h in history_map.get(history_id, []):
            if h is raw:
                continue
            try:
                name = h.get("fullName") or h.get("name") or ""
                status = _normalize_text(h.get("status"))
                msg = _normalize_text((h.get("statusDetails") or {}).get("message"))
                related_texts.append(f"{name} | {status} | {msg}")
            except Exception:
                continue

        # Attachments: try to read small text attachments from the allure dir
        attachments_excerpt: list[str] = []
        for att in (raw.get("attachments") or []):
            src = att.get("source") or att.get("name")
            if not src:
                continue
            src_path = Path(resolved_dir) / src
            if not src_path.exists() or src_path.stat().st_size > 20_000:
                continue
            try:
                attachments_excerpt.append(src_path.read_text(encoding="utf-8")[:4096])
            except Exception:
                continue

        if related_texts:
            context["rag"] = "\n".join(related_texts)
        if attachments_excerpt:
            context["attachments_text"] = "\n---\n".join(attachments_excerpt)
        classification = "flaky" if _result_is_flaky(raw, history_map) else _classify_failure_heuristic(context)
        details = {
            "name": context["name"],
            "full_name": context["full_name"],
            "status": context["status"],
            "message": context["message"],
            "trace": context["trace"],
            "classification": classification,
            "confidence": "heuristic",
            "summary": "",
        }

        # By default, when AI is enabled we run the RAG LLM on any failing test
        # (i.e., not `passed`) so that the model can provide a classification
        # and summary informed by historical context/attachments.
        if use_llm and _normalize_text(context.get("status")) != "passed":
            if api_key is None:
                api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if api_key:
                llm_data = _classify_with_llm(context, model=model, api_key=api_key)
                details["classification"] = llm_data["category"]
                details["summary"] = llm_data["summary"]
                details["confidence"] = llm_data["confidence"]
                details["extraction"] = llm_data.get("extraction", "")
            else:
                details["summary"] = "No ANTHROPIC_API_KEY configured."
                details["confidence"] = "low"

        outputs.append(details)
    return outputs


def format_analysis_report(analysis: list[dict[str, Any]]) -> str:
    lines = ["Allure failure classification report:" ]
    for item in analysis:
        lines.append("""
        ----------------------------------------
        Test: {name}
        Full name: {full_name}
        Status: {status}
        Classification: {classification}
        Confidence: {confidence}
        Summary: {summary}
        Message: {message}
        Trace: {trace}
        """.strip().format(**item))
    return "\n".join(lines)


def run(
    allure_dir: str = "",
    no_ai: bool = False,
    model: str = _DEFAULT_MODEL,
    api_key: str | None = None,
) -> int:
    analysis = analyze_allure_results(
        allure_dir=allure_dir,
        use_llm=not no_ai,
        model=model,
        api_key=api_key,
    )
    print(format_analysis_report(analysis))
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Classify Allure failure root causes using heuristics and optional AI.")
    parser.add_argument("--allure-dir", default="", help="Path to allure-results directory")
    parser.add_argument("--no-ai", action="store_true", help="Do not call Anthropic; use heuristic classification only")
    parser.add_argument("--model", default=_DEFAULT_MODEL, help="Anthropic model to use for RAG classification")
    parser.add_argument("--api-key", default=None, help="Anthropic API key to use instead of ANTHROPIC_API_KEY")
    args = parser.parse_args()

    raise SystemExit(run(
        allure_dir=args.allure_dir,
        no_ai=args.no_ai,
        model=args.model,
        api_key=args.api_key,
    ))
