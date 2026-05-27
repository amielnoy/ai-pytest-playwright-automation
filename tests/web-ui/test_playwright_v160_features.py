"""
tests/web-ui/test_playwright_v160_features.py

One integration test per new Playwright 1.60.0 feature:

  1. Playwright MCP          — AI-agent browser control via Model Context Protocol.
                               Validates the project's .claude/settings.json wires
                               the @playwright/mcp server correctly.

  2. CLI for Coding Agents   — playwright CLI optimised for coding assistants.
                               Drives `python -m playwright screenshot` via subprocess.

  3. HAR Recording (Tracing) — tracing.start_har() / stop_har() new first-class API.
                               Records network traffic as HAR during navigation.

  4. Drop API                — locator.drop() drops local files or clipboard data.
                               Verifies the DataTransfer.files payload reaches the
                               drop-event handler.

  5. Aria Snapshots (Page)   — expect(page).to_match_aria_snapshot() now targets an
                               entire Page, not just a Locator.
"""
import json
import subprocess
import sys
from pathlib import Path

import allure
import pytest
from playwright.sync_api import BrowserContext, Page, expect


# ---------------------------------------------------------------------------
# 1. Playwright MCP
# ---------------------------------------------------------------------------

@allure.feature("Playwright 1.60 Features")
@allure.story("Playwright MCP")
class TestPlaywrightMCP:

    @allure.title("Project MCP config wires @playwright/mcp with --headless flag")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mcp_playwright_server_configured(self):
        """Playwright MCP exposes a JSON-RPC server so AI agents (Claude Code, Copilot)
        can drive the browser without Python boilerplate.  This test validates the
        project's .claude/settings.json declares the server correctly.
        """
        config_path = Path(".claude/settings.json")

        with allure.step("Read project MCP configuration"):
            assert config_path.exists(), (
                "Missing .claude/settings.json — create it with mcpServers.playwright"
            )
            config = json.loads(config_path.read_text())

        with allure.step("Verify 'playwright' MCP server entry exists"):
            servers = config.get("mcpServers", {})
            assert "playwright" in servers, (
                f"'playwright' key missing from mcpServers. Found: {list(servers)}"
            )

        with allure.step("Verify command is npx and @playwright/mcp is in args"):
            pw = servers["playwright"]
            assert pw.get("command") == "npx", (
                f"Expected command='npx', got '{pw.get('command')}'"
            )
            args = pw.get("args", [])
            assert "@playwright/mcp" in args, (
                f"@playwright/mcp not found in args: {args}"
            )

        with allure.step("Verify --headless flag is present for CI compatibility"):
            assert "--headless" in args, (
                f"--headless flag missing from args: {args}"
            )

        allure.attach(
            json.dumps(pw, indent=2),
            name="mcp-playwright-config",
            attachment_type=allure.attachment_type.JSON,
        )


# ---------------------------------------------------------------------------
# 2. CLI for Coding Agents
# ---------------------------------------------------------------------------

@allure.feature("Playwright 1.60 Features")
@allure.story("CLI for Coding Agents")
class TestPlaywrightCLIForCodingAgents:

    @allure.title("playwright CLI captures a full-page screenshot via subprocess")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cli_screenshot_for_coding_agent(self, app_url: str, tmp_path: Path):
        """Playwright 1.60 optimises the CLI for coding agents: lower latency,
        structured output, no Python boilerplate required.
        This test drives the CLI via subprocess, the same way Claude Code uses it.
        """
        screenshot_path = tmp_path / "agent_view.png"

        with allure.step("Run: python -m playwright screenshot --full-page"):
            result = subprocess.run(
                [
                    sys.executable, "-m", "playwright",
                    "screenshot",
                    "--browser", "chromium",
                    "--full-page",
                    f"{app_url}/index.php?route=account/register",
                    str(screenshot_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0, (
                f"playwright CLI exited {result.returncode}.\nstderr: {result.stderr}"
            )

        with allure.step("Verify screenshot file exists with meaningful content"):
            assert screenshot_path.exists(), "Screenshot file was not created"
            size_kb = screenshot_path.stat().st_size / 1024
            assert size_kb > 20, f"Screenshot too small ({size_kb:.1f} KB) — likely blank"

        with allure.step("Attach screenshot to Allure report"):
            allure.attach.file(
                str(screenshot_path),
                name="cli-agent-screenshot",
                attachment_type=allure.attachment_type.PNG,
            )


# ---------------------------------------------------------------------------
# 3. HAR Recording via Tracing API
# ---------------------------------------------------------------------------

@allure.feature("Playwright 1.60 Features")
@allure.story("HAR Recording via Tracing")
class TestHARRecordingViaTracing:

    @allure.title("tracing.start_har() records search page network traffic as HAR")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_har_via_tracing_api(self, context: BrowserContext, app_url: str, tmp_path: Path):
        """New in 1.60: HAR generation is a first-class Tracing API alongside screenshots
        and snapshots.  tracing.start_har(path) is a context manager; the HAR is flushed
        when the block exits — no explicit stop_har() call needed.
        """
        har_path = tmp_path / "search_traffic.har"
        page = context.new_page()

        with allure.step("Start HAR recording via tracing.start_har()"):
            with context.tracing.start_har(path=str(har_path)):
                with allure.step("Navigate to MacBook search to generate network traffic"):
                    page.goto(
                        f"{app_url}/index.php?route=product/search&search=MacBook",
                        wait_until="networkidle",
                    )

        with allure.step("Verify HAR file was created"):
            assert har_path.exists(), "tracing.start_har() did not write a HAR file"

        with allure.step("Verify HAR structure and network entries"):
            har = json.loads(har_path.read_text(encoding="utf-8"))
            entries = har["log"]["entries"]
            assert len(entries) > 0, "HAR has no network entries"
            urls = [e["request"]["url"] for e in entries]
            assert any("route=product" in u or "tutorialsninja" in u for u in urls), (
                f"Expected search request not found. Sample URLs: {urls[:3]}"
            )

        with allure.step("Attach HAR summary to Allure report"):
            summary = {
                "entry_count": len(entries),
                "sample_urls": urls[:5],
            }
            allure.attach(
                json.dumps(summary, indent=2),
                name="har-summary",
                attachment_type=allure.attachment_type.JSON,
            )

        page.close()


# ---------------------------------------------------------------------------
# 4. Drop API
# ---------------------------------------------------------------------------

@allure.feature("Playwright 1.60 Features")
@allure.story("Drop API")
class TestDropAPI:

    @allure.title("locator.drop() delivers a local file payload to an HTML5 drop zone")
    @allure.severity(allure.severity_level.NORMAL)
    def test_drop_file_onto_drop_zone(self, page: Page, tmp_path: Path):
        """New in 1.60: locator.drop(DropPayload) simulates dragging local files or
        arbitrary clipboard data into any element — not just <input type=file>.
        DropPayload.files accepts a path string; DropPayload.data accepts key-value pairs.
        """
        # Minimal HTML5 drop zone that writes the dropped filename to a <span>.
        page.set_content(
            """
            <html><body>
              <div id="zone"
                   style="width:300px;height:150px;border:3px dashed #ccc;
                          display:flex;align-items:center;justify-content:center"
                   ondragover="event.preventDefault()"
                   ondrop="
                       event.preventDefault();
                       const f = event.dataTransfer.files[0];
                       document.getElementById('result').textContent = f ? f.name : '';
                   ">
                Drop a file here
              </div>
              <span id="result"></span>
            </body></html>
            """
        )

        sample_file = tmp_path / "report.txt"
        sample_file.write_text("Playwright 1.60 Drop API — file transfer payload")

        with allure.step("Drop the local file onto the drop zone via locator.drop()"):
            # DropPayload: {"files": [...], "data": {...}}
            page.locator("#zone").drop({"files": [str(sample_file)]})

        with allure.step("Verify the drop handler received the correct filename"):
            result = page.locator("#result").inner_text()
            assert result == sample_file.name, (
                f"Drop handler received '{result}', expected '{sample_file.name}'"
            )


# ---------------------------------------------------------------------------
# 5. Aria Snapshots on Page
# ---------------------------------------------------------------------------

@allure.feature("Playwright 1.60 Features")
@allure.story("Aria Snapshots on Page")
class TestAriaSnapshotsOnPage:

    @allure.title("expect(page).to_match_aria_snapshot() validates full-page ARIA structure")
    @allure.severity(allure.severity_level.NORMAL)
    def test_full_page_aria_snapshot(self, page: Page):
        """New in 1.60: to_match_aria_snapshot() can target an entire Page, not just a
        Locator.  page.aria_snapshot() returns a YAML-like string; the matcher performs
        partial matching so only the declared nodes need to be present.

        Aria snapshot format:
            - role "accessible name" [attribute=value]

        Regex names are supported: /pattern/i
        """
        page.set_content(
            """
            <html><body>
              <h1>Register Account</h1>
              <form>
                <label>First Name <input type="text" aria-label="First Name"></label>
                <label>Last Name  <input type="text" aria-label="Last Name"></label>
                <label>E-Mail     <input type="email" aria-label="E-Mail"></label>
                <label>Telephone  <input type="tel"   aria-label="Telephone"></label>
                <label>Password   <input type="password" aria-label="Password"></label>
                <button type="submit">Continue</button>
              </form>
            </body></html>
            """
        )

        with allure.step("Capture full-page ARIA snapshot for diagnostics"):
            snapshot = page.aria_snapshot()
            allure.attach(
                snapshot,
                name="aria-snapshot",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Assert page-level ARIA snapshot contains the registration form"):
            # expect(page) — targeting the FULL PAGE — is new in 1.60
            expect(page).to_match_aria_snapshot(
                '- heading "Register Account" [level=1]\n'
                '- textbox "First Name"\n'
                '- textbox "Last Name"\n'
                '- textbox "E-Mail"\n'
                '- textbox "Telephone"\n'
                '- textbox "Password"\n'
                '- button "Continue"'
            )
