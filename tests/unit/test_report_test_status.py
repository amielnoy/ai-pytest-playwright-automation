"""
Unit tests for the report_test_status MCP tool.

Covers: result loading, status classification (including flaky detection),
terminal report content, HTML report creation, Allure entry writing,
and the end-to-end report_test_status() call.
"""

import json
from collections import Counter
from pathlib import Path

import allure
import pytest

from mcp_servers.test_reporter import (
    _classify,
    _html_report,
    _load_results,
    _overall_status,
    _terminal_report,
    _write_allure_entry,
    report_test_status,
)
from utils.logger import get_logger

LOGGER = get_logger("unit.test_report_test_status")

# --------------------------------------------------------------------------- #
# Shared fixture data                                                           #
# --------------------------------------------------------------------------- #

_LABELS_A = [{"name": "feature", "value": "Feature A"}, {"name": "suite", "value": "suite_a"}]
_LABELS_B = [{"name": "feature", "value": "Feature B"}, {"name": "suite", "value": "suite_b"}]


def _make_result(
    name: str,
    status: str,
    history_id: str,
    labels: list | None = None,
    message: str = "",
    start: int = 1000,
    stop: int = 2000,
) -> dict:
    r: dict = {
        "name": name,
        "status": status,
        "historyId": history_id,
        "uuid": history_id + "-uuid",
        "fullName": f"tests.example#{name}",
        "start": start,
        "stop": stop,
        "labels": labels or _LABELS_A,
    }
    if message:
        r["statusDetails"] = {"message": message}
    return r


@pytest.fixture()
def mixed_results() -> list[dict]:
    return [
        _make_result("test_pass",    "passed",  "h-pass"),
        _make_result("test_fail",    "failed",  "h-fail",  message="AssertionError: expected True"),
        _make_result("test_broken",  "broken",  "h-broken", message="RuntimeError: db down"),
        _make_result("test_skip",    "skipped", "h-skip"),
        _make_result("test_flaky_1", "passed",  "h-flaky", start=1000, stop=1500),
        _make_result("test_flaky_2", "failed",  "h-flaky", start=2000, stop=2500),
    ]


@pytest.fixture()
def allure_dir(tmp_path: Path, mixed_results: list[dict]) -> Path:
    """Temp allure-results directory pre-populated with mixed result files."""
    for i, r in enumerate(mixed_results):
        (tmp_path / f"result-{i:02d}-result.json").write_text(
            json.dumps(r), encoding="utf-8"
        )
    # Extra non-result file that must be ignored
    (tmp_path / "something-container.json").write_text("{}", encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------------------- #
# Tests                                                                         #
# --------------------------------------------------------------------------- #

@pytest.mark.security
def test_load_results_reads_only_result_json_files(tmp_path: Path):
    with allure.step("Populate tmp dir with two result files and one non-result file"):
        LOGGER.info("Step: Write result JSONs and a container JSON to tmp_path")
        (tmp_path / "aaa-result.json").write_text('{"name":"t","status":"passed"}')
        (tmp_path / "bbb-result.json").write_text('{"name":"u","status":"failed"}')
        (tmp_path / "ccc-container.json").write_text('{"ignored":true}')
        (tmp_path / "ddd-result.json").write_text("NOT JSON {{{")  # invalid — must be skipped

    with allure.step("Call _load_results and verify only valid result files are loaded"):
        LOGGER.info("Step: Call _load_results and assert count == 2")
        results = _load_results(tmp_path)

    with allure.step("Assert exactly 2 valid results loaded and invalid JSON is silently skipped"):
        LOGGER.info("Step: Assert len == 2, invalid JSON ignored")
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        names = {r["name"] for r in results}
        assert names == {"t", "u"}, f"Unexpected names: {names}"


def test_classify_maps_statuses_correctly(mixed_results: list[dict]):
    with allure.step("Classify the mixed result list"):
        LOGGER.info("Step: Call _classify on passed/failed/broken/skipped/flaky set")
        classified = _classify(mixed_results)

    with allure.step("Assert each expected status is present in classified output"):
        LOGGER.info("Step: Assert passed, failed, broken, skipped, flaky all appear")
        status_counts = Counter(r["status"] for r in classified)
        assert status_counts["passed"]  >= 1, "Expected at least one passed"
        assert status_counts["failed"]  >= 1, "Expected at least one failed"
        assert status_counts["broken"]  >= 1, "Expected at least one broken"
        assert status_counts["skipped"] >= 1, "Expected at least one skipped"

    with allure.step("Assert the flaky test is promoted from failed/passed to flaky"):
        LOGGER.info("Step: Assert h-flaky historyId is classified as flaky")
        assert status_counts["flaky"] >= 1, (
            "Test with mixed pass/fail results for same historyId must be classified as flaky"
        )


def test_classify_detects_flaky_when_same_history_has_mixed_statuses():
    results = [
        _make_result("run_1", "passed", "hid-x", start=100, stop=200),
        _make_result("run_2", "failed", "hid-x", start=300, stop=400),
    ]

    with allure.step("Classify two results sharing historyId with one pass and one fail"):
        LOGGER.info("Step: Call _classify on pass+fail pair with same historyId")
        classified = _classify(results)

    with allure.step("Assert the pair is collapsed into a single flaky entry"):
        LOGGER.info("Step: Assert exactly one entry with status=flaky")
        assert len(classified) == 1, f"Expected 1 deduplicated entry, got {len(classified)}"
        assert classified[0]["status"] == "flaky", (
            f"Expected status=flaky, got {classified[0]['status']!r}"
        )


def test_terminal_report_contains_status_icons_for_all_non_zero_statuses(
    mixed_results: list[dict],
):
    classified = _classify(mixed_results)

    with allure.step("Generate terminal report from mixed classified results"):
        LOGGER.info("Step: Call _terminal_report on mixed classified results")
        report = _terminal_report(classified)

    with allure.step("Assert all expected status icons appear in the report"):
        LOGGER.info("Step: Assert ✅ ❌ ⚠️ ⏭️ 🔁 all present in terminal output")
        for icon in ("✅", "❌", "⚠️", "⏭️", "🔁"):
            assert icon in report, f"Icon {icon!r} missing from terminal report"

    with allure.step("Assert the report contains a summary line with status counts"):
        LOGGER.info("Step: Assert PASSED, FAILED, BROKEN, SKIPPED, FLAKY appear in report")
        upper = report.upper()
        for label in ("PASSED", "FAILED", "BROKEN", "SKIPPED", "FLAKY"):
            assert label in upper, f"Status label {label!r} absent from terminal report"


def test_html_report_creates_file_with_badge_per_status(
    mixed_results: list[dict], tmp_path: Path
):
    classified = _classify(mixed_results)
    html_path = tmp_path / "report.html"

    with allure.step("Generate the HTML report to a temp file"):
        LOGGER.info("Step: Call _html_report and write to %s", html_path)
        _html_report(classified, html_path)

    with allure.step("Assert the HTML file was created and is non-empty"):
        LOGGER.info("Step: Assert file exists and size > 0")
        assert html_path.exists(), "HTML report file was not created"
        assert html_path.stat().st_size > 0, "HTML report file is empty"

    with allure.step("Assert the HTML contains badge colours for each active status"):
        LOGGER.info("Step: Assert red, green, yellow badge colours present in HTML")
        html = html_path.read_text(encoding="utf-8")
        assert "#28a745" in html, "Green badge colour for 'passed' missing"
        assert "#dc3545" in html, "Red badge colour for 'failed'/'flaky' missing"
        assert "#ffc107" in html, "Yellow badge colour for 'broken'/'skipped' missing"


def test_write_allure_entry_creates_result_json_and_both_attachments(
    mixed_results: list[dict], tmp_path: Path
):
    classified = _classify(mixed_results)
    terminal = _terminal_report(classified)
    html_path = tmp_path / "report.html"
    _html_report(classified, html_path)

    with allure.step("Call _write_allure_entry and write artifacts to tmp allure dir"):
        LOGGER.info("Step: Call _write_allure_entry, expect 3 new files in allure dir")
        before = set(tmp_path.iterdir())
        _write_allure_entry(classified, terminal, html_path, tmp_path)
        after = set(tmp_path.iterdir())

    new_files = after - before

    with allure.step("Assert a result JSON and two attachment files were written"):
        LOGGER.info("Step: Assert exactly 3 new files: *-result.json, *txt*, *html*")
        result_files = [f for f in new_files if f.name.endswith("-result.json")]
        txt_files    = [f for f in new_files if "txt-attachment" in f.name]
        html_files   = [f for f in new_files if "html-attachment" in f.name]
        assert len(result_files) == 1, f"Expected 1 result JSON, got {result_files}"
        assert len(txt_files)    == 1, f"Expected 1 txt attachment, got {txt_files}"
        assert len(html_files)   == 1, f"Expected 1 html attachment, got {html_files}"

    with allure.step("Assert the result JSON references both attachment files"):
        LOGGER.info("Step: Parse result JSON and check attachments list")
        result_data = json.loads(result_files[0].read_text(encoding="utf-8"))
        sources = {a["source"] for a in result_data.get("attachments", [])}
        assert txt_files[0].name in sources,  "Text attachment not referenced in result JSON"
        assert html_files[0].name in sources, "HTML attachment not referenced in result JSON"

    with allure.step("Assert result JSON status reflects overall outcome of classified tests"):
        LOGGER.info("Step: Assert overall status is 'failed' (has failed/flaky tests)")
        assert result_data["status"] == "failed", (
            f"Expected overall status 'failed' for mixed results, got {result_data['status']!r}"
        )


def test_report_test_status_returns_error_message_when_dir_does_not_exist(tmp_path: Path):
    missing = str(tmp_path / "no-such-dir")

    with allure.step(f"Call report_test_status with non-existent dir: {missing}"):
        LOGGER.info("Step: Call report_test_status with missing allure_dir=%s", missing)
        result = report_test_status(allure_dir=missing, write_allure_entry=False)

    with allure.step("Assert the return value contains an error indicator"):
        LOGGER.info("Step: Assert '❌' present in error response")
        assert "❌" in result, f"Expected error indicator in response, got: {result!r}"


def test_report_test_status_end_to_end_with_mixed_results(allure_dir: Path, tmp_path: Path):
    html_out = str(tmp_path / "status.html")

    with allure.step("Run report_test_status end-to-end against the pre-populated allure dir"):
        LOGGER.info(
            "Step: Call report_test_status(allure_dir=%s, html_out=%s, write_allure_entry=True)",
            allure_dir, html_out,
        )
        output = report_test_status(
            allure_dir=str(allure_dir),
            html_out=html_out,
            write_allure_entry=True,
        )

    with allure.step("Assert terminal output confirms HTML and Allure entry were written"):
        LOGGER.info("Step: Assert HTML and Allure notes in output")
        assert "📄" in output, "HTML report note missing from output"
        assert "📊" in output, "Allure entry note missing from output"

    with allure.step("Assert the standalone HTML file was created"):
        LOGGER.info("Step: Assert %s exists on disk", html_out)
        assert Path(html_out).exists(), "Standalone HTML report file was not created"

    with allure.step("Assert a new Allure result entry was written into allure_dir"):
        LOGGER.info("Step: Assert new *-result.json with fullName mcp.test_reporter exists")
        reporter_results = [
            f for f in allure_dir.glob("*-result.json")
            if "mcp.test_reporter" in f.read_text(encoding="utf-8")
        ]
        assert reporter_results, "No MCP reporter result entry found in allure_dir"

    with allure.step("Assert all five status types appear in the terminal output"):
        LOGGER.info("Step: Assert PASSED, FAILED, BROKEN, SKIPPED, FLAKY in output")
        for label in ("PASSED", "FAILED", "BROKEN", "SKIPPED", "FLAKY"):
            assert label in output.upper(), f"Status {label!r} missing from report output"


def test_overall_status_reflects_worst_case():
    with allure.step("Test _overall_status with counts containing failed tests"):
        LOGGER.info("Step: Assert overall=failed when failed>0")
        assert _overall_status({"passed": 5, "failed": 1}) == "failed"

    with allure.step("Test _overall_status with only broken tests (no failed/flaky)"):
        LOGGER.info("Step: Assert overall=broken when broken>0 and no failed/flaky")
        assert _overall_status({"passed": 3, "broken": 1}) == "broken"

    with allure.step("Test _overall_status when all tests pass"):
        LOGGER.info("Step: Assert overall=passed when only passed/skipped")
        assert _overall_status({"passed": 10, "skipped": 2}) == "passed"

    with allure.step("Test _overall_status promotes flaky to failed"):
        LOGGER.info("Step: Assert overall=failed when flaky>0")
        assert _overall_status({"passed": 8, "flaky": 1}) == "failed"
