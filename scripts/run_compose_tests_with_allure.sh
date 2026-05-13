#!/usr/bin/env bash
# run_compose_tests_with_allure.sh
#
# Run tests via Docker Compose and produce a full Allure report that matches
# the GitHub Actions pipeline output:
#   • Rolling archive of previous runs → full step/attachment detail in retries
#   • Allure history in ./allure-history/ for trend charts (CI-identical pattern)
#   • architecture.html embedded in the report (same as CI deploy step)
#   • Coloured summary printed to the terminal
#
# History pattern (mirrors .github/workflows/playwright-tests.yml exactly):
#   Allure 3 reads  ./allure-history/  from CWD before generating the report
#   Allure 3 writes ./allure-history/  in-place during generation (updates trends)
#   No copy in / copy out required — the directory persists naturally between runs.
#
# Archive layout (git-ignored, persists between runs):
#   allure-results-archive/
#     run_20260513_101500/   ← full result JSONs + attachments (oldest kept)
#     run_20260513_180000/   ← most recent previous run
#   allure-history/          ← managed by Allure 3 automatically
#
# Environment variables (all optional):
#   COMPOSE_FILE   docker-compose file              default: docker-compose.automation.yml
#   ARTIFACTS_DIR  host artifact root               default: docker-artifacts
#   ARCHIVE_DIR    rolling archive root             default: allure-results-archive
#   HISTORY_DIR    allure history dir (in CWD)      default: allure-history
#   MAX_RUNS       past runs to keep for detail     default: 5
#   OPEN_ALLURE    open browser after report        default: true
#   COMPOSE_DOWN   stop stack after tests           default: false

set -Eeuo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.automation.yml}"

# Keep these as RELATIVE paths from PROJECT_ROOT — Allure 3 CLI requires
# relative paths; absolute paths cause the CWD to be prepended a second time.
ARTIFACTS_DIR_REL="${ARTIFACTS_DIR:-docker-artifacts}"
ALLURE_RESULTS_REL="${ARTIFACTS_DIR_REL}/allure-results"
ALLURE_REPORT_REL="${ARTIFACTS_DIR_REL}/allure-report"
ARCHIVE_DIR_REL="${ARCHIVE_DIR:-allure-results-archive}"
HISTORY_DIR_REL="${HISTORY_DIR:-allure-history}"          # read/written by Allure 3 in CWD
MAX_RUNS="${MAX_RUNS:-5}"

# Absolute equivalents for shell operations (cp, mkdir, find, etc.)
ALLURE_RESULTS_DIR="${PROJECT_ROOT}/${ALLURE_RESULTS_REL}"
ALLURE_REPORT_DIR="${PROJECT_ROOT}/${ALLURE_REPORT_REL}"
ARCHIVE_DIR="${PROJECT_ROOT}/${ARCHIVE_DIR_REL}"
HISTORY_DIR="${PROJECT_ROOT}/${HISTORY_DIR_REL}"

cd "${PROJECT_ROOT}" || exit 1

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[32m'; YELLOW='\033[33m'; CYAN='\033[36m'
BOLD='\033[1m'; RESET='\033[0m'

step() { echo -e "\n${CYAN}${BOLD}▶ $*${RESET}"; }
ok()   { echo -e "${GREEN}  ✔ $*${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠ $*${RESET}"; }

# ── 1. Prepare directories ────────────────────────────────────────────────────
step "Preparing artifact directories..."
mkdir -p "${ALLURE_RESULTS_DIR}" "${ARCHIVE_DIR}" "${HISTORY_DIR}"
ok "Directories ready  (history: ./${HISTORY_DIR_REL}/)"

# ── 2. Accept custom pytest args ─────────────────────────────────────────────
pytest_args=("$@")
if [[ ${#pytest_args[@]} -eq 0 ]]; then
  pytest_args=("tests/")
fi

# ── 3. Start support services ─────────────────────────────────────────────────
step "Starting Docker Compose support containers..."
docker compose -f "${COMPOSE_FILE}" up -d --build \
  db automation-server postgres-exporter prometheus grafana
ok "Services started"

# ── 4. Run tests ──────────────────────────────────────────────────────────────
step "Running tests in Compose service: automation-tests"
set +e
docker compose -f "${COMPOSE_FILE}" run --rm \
  -e CI=true \
  automation-tests \
  pytest "${pytest_args[@]}" \
  --alluredir=/app/test-artifacts/allure-results \
  --clean-alluredir \
  --override-ini="addopts=-v --strict-config --strict-markers -n auto --dist loadgroup" \
  -n auto --dist loadgroup
pytest_exit_code=$?
set -e

if [[ ${pytest_exit_code} -eq 0 ]]; then
  ok "Tests finished — all passed"
else
  warn "Tests finished with exit code ${pytest_exit_code}"
fi

# ── 5. Archive current run (pure results before merging) ──────────────────────
step "Archiving current run → ${ARCHIVE_DIR_REL}/..."
RUN_LABEL="run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${ARCHIVE_DIR}/${RUN_LABEL}"
cp -r "${ALLURE_RESULTS_DIR}/." "${ARCHIVE_DIR}/${RUN_LABEL}/"
ok "Archived as ${RUN_LABEL}"

# Prune oldest runs beyond MAX_RUNS
TOTAL_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
if [[ ${TOTAL_RUNS} -gt ${MAX_RUNS} ]]; then
  TO_DELETE=$(( TOTAL_RUNS - MAX_RUNS ))
  ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort | head -n "${TO_DELETE}" | xargs rm -rf
  ok "Pruned ${TO_DELETE} old run(s) — keeping last ${MAX_RUNS}"
fi

# ── 6. Merge current + all kept runs (full detail for Retries tab) ─────────────
step "Merging last ${MAX_RUNS} run(s) for full historical step/attachment detail..."
MERGED_REL="${ARTIFACTS_DIR_REL}/allure-results-merged"
MERGED="${PROJECT_ROOT}/${MERGED_REL}"
rm -rf "${MERGED}"
mkdir -p "${MERGED}"
for run_dir in $(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort); do
  cp -r "${run_dir}/." "${MERGED}/" 2>/dev/null || true
done
KEPT=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
ok "Merged ${KEPT} run(s)"

# ── 7. Write run summary as an Allure entry (appears inside the report) ───────
step "Writing run summary entry into merged results..."
VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"
[[ -x "${VENV_PYTHON}" ]] || VENV_PYTHON="python3"
"${VENV_PYTHON}" - "${ALLURE_RESULTS_DIR}" "${MERGED}" "${RUN_LABEL}" << 'PYEOF'
import sys, json, uuid, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

results_dir = Path(sys.argv[1])
merged_dir  = Path(sys.argv[2])
run_label   = sys.argv[3]

counts: Counter = Counter()
for f in results_dir.glob("*-result.json"):
    try:
        counts[json.loads(f.read_text()).get("status", "unknown")] += 1
    except Exception:
        pass

total = sum(counts.values())
ICONS = {"passed": "✅", "failed": "❌", "broken": "⚠️ ", "skipped": "⏭️ ", "flaky": "🔁"}
STEP_STATUS = {"passed": "passed", "skipped": "passed", "broken": "broken",
               "failed": "failed", "flaky": "failed"}

def overall(c):
    if c.get("failed", 0) or c.get("flaky", 0): return "failed"
    if c.get("broken", 0): return "broken"
    return "passed"

now_ms = int(time.time() * 1000)
entry_uuid = str(uuid.uuid4())
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Plain-text summary attachment
lines = [f"Test Run Summary — {ts}", f"Run: {run_label}", ""]
for s in ("passed", "failed", "broken", "skipped", "flaky"):
    n = counts.get(s, 0)
    if n:
        lines.append(f"{ICONS.get(s, '?')}  {s.upper():<8}  {n}")
lines.append(f"\nTotal: {total}")
txt_src = f"{entry_uuid}-txt-attachment.txt"
(merged_dir / txt_src).write_text("\n".join(lines), encoding="utf-8")

# Steps — one per non-zero status
steps = [
    {"name": f"{ICONS.get(s,'?')} {s.capitalize()}: {counts[s]}",
     "status": STEP_STATUS.get(s, "passed"),
     "start": now_ms, "stop": now_ms}
    for s in ("passed", "failed", "broken", "skipped", "flaky")
    if counts.get(s, 0)
]

result = {
    "name": f"Test Run Summary [{run_label}]",
    "status": overall(counts),
    "steps": steps,
    "attachments": [{"name": "Run Summary", "source": txt_src, "type": "text/plain"}],
    "start": now_ms, "stop": now_ms + 1,
    "uuid": entry_uuid,
    "historyId": "compose-run-summary",
    "testCaseId": "compose-run-summary",
    "fullName": "scripts.run_compose#test_run_summary",
    "labels": [
        {"name": "feature",     "value": "Test Run Summary"},
        {"name": "story",       "value": "Docker Compose Run"},
        {"name": "severity",    "value": "normal"},
        {"name": "suite",       "value": "summary"},
        {"name": "parentSuite", "value": "scripts"},
    ],
}
(merged_dir / f"{entry_uuid}-result.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"  ✔ Summary entry written ({overall(counts).upper()} — {total} tests)")
PYEOF

# ── 8. Generate Allure report ─────────────────────────────────────────────────
# Allure 3 automatically reads ./allure-history/ from CWD for trend charts
# and updates it in-place — no explicit restore/save needed (matches CI pattern).
step "Generating Allure report → ${ALLURE_REPORT_REL}/"
rm -rf "${ALLURE_REPORT_DIR}"
set +e
# Use RELATIVE paths — Allure 3 CLI prepends CWD to absolute paths (bug)
npx allure generate "${MERGED_REL}" -o "${ALLURE_REPORT_REL}"
allure_exit_code=$?
set -e

rm -rf "${MERGED}"

if [[ ${allure_exit_code} -ne 0 ]]; then
  warn "Allure report generation failed (exit ${allure_exit_code})"
  exit "${allure_exit_code}"
fi
ok "Allure report generated"

# ── 8. Embed architecture.html (mirrors CI deploy step) ──────────────────────
step "Embedding architecture.html into report..."
cp "${PROJECT_ROOT}/architecture.html" "${ALLURE_REPORT_DIR}/architecture.html"
ok "architecture.html → ${ALLURE_REPORT_REL}/architecture.html"

# ── 9. Coloured summary ───────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  TEST RUN SUMMARY${RESET}   $(date '+%Y-%m-%d %H:%M')   [${RUN_LABEL}]"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if command -v python3 &>/dev/null; then
  python3 - "${ALLURE_RESULTS_DIR}" << 'PYEOF'
import json, sys
from collections import Counter
from pathlib import Path

results_dir = Path(sys.argv[1])
counts = Counter()
for f in results_dir.glob("*-result.json"):
    try:
        counts[json.loads(f.read_text()).get("status", "unknown")] += 1
    except Exception:
        pass

total = sum(counts.values())
ICONS = {"passed": "✅", "failed": "❌", "broken": "⚠️ ", "skipped": "⏭️ "}
COLS  = {"passed": "\033[32m", "failed": "\033[31m", "broken": "\033[33m", "skipped": "\033[33m"}
RST = "\033[0m"; BOLD = "\033[1m"

for status in ("passed", "failed", "broken", "skipped"):
    n = counts.get(status, 0)
    if n:
        print(f"  {COLS.get(status,'')}{ICONS.get(status,'❓')}  {status.upper():<8}  {n:>4}{RST}")

print(f"\n  {BOLD}Total: {total}{RST}")
PYEOF
fi

KEPT_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo -e "  ${CYAN}Allure report:${RESET}    ${ALLURE_REPORT_DIR}"
echo -e "  ${CYAN}Architecture:${RESET}     ${ALLURE_REPORT_DIR}/architecture.html"
echo -e "  ${CYAN}History depth:${RESET}    ${KEPT_RUNS} run(s) in archive (max ${MAX_RUNS})"
echo -e "  ${CYAN}Grafana:${RESET}          http://localhost:3000/d/automation/automation-runs"
echo -e "  ${CYAN}Prometheus:${RESET}       http://localhost:9090"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ── 10. Optionally stop Compose stack ─────────────────────────────────────────
if [[ "${COMPOSE_DOWN:-false}" == "true" ]]; then
  step "Stopping Compose stack (COMPOSE_DOWN=true)..."
  docker compose -f "${COMPOSE_FILE}" down
fi

# ── 11. Open report ───────────────────────────────────────────────────────────
if [[ "${OPEN_ALLURE:-true}" == "false" ]]; then
  ok "Report ready — skipping browser open (OPEN_ALLURE=false)"
else
  step "Opening Allure report in browser..."
  # Use relative path — Allure 3 CLI prepends CWD to absolute paths (bug)
  npx allure open "${ALLURE_REPORT_REL}"
fi

exit "${pytest_exit_code}"
