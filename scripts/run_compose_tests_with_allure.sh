#!/usr/bin/env bash
# run_compose_tests_with_allure.sh
#
# Run tests via Docker Compose and produce a full Allure report that matches
# the GitHub Actions pipeline output:
#   • Rolling archive of previous runs → full step/attachment detail in retries
#   • Allure history restored for trend charts
#   • architecture.html embedded in the report (same as CI deploy)
#   • Coloured summary printed to the terminal
#
# Archive layout (persisted between runs, git-ignored):
#   allure-results-archive/
#     run_20260513_101500/   ← oldest kept run
#     run_20260513_180000/   ← most recent previous run
#   allure-history/          ← history/ dir for trend charts
#
# Environment variables (all optional):
#   COMPOSE_FILE   docker-compose file               default: docker-compose.automation.yml
#   ARTIFACTS_DIR  host artifact root                default: docker-artifacts
#   ARCHIVE_DIR    rolling archive root              default: allure-results-archive
#   HISTORY_DIR    allure history/ for trends        default: allure-history
#   MAX_RUNS       past runs to keep for detail      default: 5
#   OPEN_ALLURE    open browser after report         default: true
#   COMPOSE_DOWN   stop stack after tests            default: false

set -Eeuo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.automation.yml}"
ARTIFACTS_DIR="${PROJECT_ROOT}/${ARTIFACTS_DIR:-docker-artifacts}"
ALLURE_RESULTS_DIR="${ARTIFACTS_DIR}/allure-results"
ALLURE_REPORT_DIR="${ARTIFACTS_DIR}/allure-report"
ARCHIVE_DIR="${PROJECT_ROOT}/${ARCHIVE_DIR:-allure-results-archive}"
HISTORY_DIR="${PROJECT_ROOT}/${HISTORY_DIR:-allure-history}"
MAX_RUNS="${MAX_RUNS:-5}"

cd "${PROJECT_ROOT}" || exit 1

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[32m'; YELLOW='\033[33m'; CYAN='\033[36m'
BOLD='\033[1m'; RESET='\033[0m'

step() { echo -e "\n${CYAN}${BOLD}▶ $*${RESET}"; }
ok()   { echo -e "${GREEN}  ✔ $*${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠ $*${RESET}"; }

# ── 1. Prepare directories ────────────────────────────────────────────────────
step "Preparing artifact directories..."
mkdir -p "${ARTIFACTS_DIR}" "${ARCHIVE_DIR}" "${HISTORY_DIR}"

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
  -n auto --dist loadscope
pytest_exit_code=$?
set -e

if [[ ${pytest_exit_code} -eq 0 ]]; then
  ok "Tests finished — all passed"
else
  warn "Tests finished with exit code ${pytest_exit_code}"
fi

# ── 5. Archive the current run (pure results, before any merging) ─────────────
step "Archiving current run → ${ARCHIVE_DIR}..."
RUN_LABEL="run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${ARCHIVE_DIR}/${RUN_LABEL}"
cp -r "${ALLURE_RESULTS_DIR}/." "${ARCHIVE_DIR}/${RUN_LABEL}/"
ok "Archived as ${RUN_LABEL}"

# Prune runs older than MAX_RUNS
TOTAL_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
if [[ ${TOTAL_RUNS} -gt ${MAX_RUNS} ]]; then
  TO_DELETE=$(( TOTAL_RUNS - MAX_RUNS ))
  ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort | head -n "${TO_DELETE}" | xargs rm -rf
  ok "Pruned ${TO_DELETE} old run(s) — keeping last ${MAX_RUNS}"
fi

# ── 6. Merge current + all kept previous runs ─────────────────────────────────
# Allure groups files by testCaseId → shows as Retries with full step details.
step "Merging last ${MAX_RUNS} run(s) for full historical detail..."
MERGED="${ARTIFACTS_DIR}/allure-results-merged"
rm -rf "${MERGED}"
mkdir -p "${MERGED}"
for run_dir in $(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort); do
  cp -r "${run_dir}/." "${MERGED}/" 2>/dev/null || true
done
KEPT=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
ok "Merged ${KEPT} run(s)"

# ── 7. Restore allure history for trend charts ────────────────────────────────
step "Restoring Allure history for trend charts..."
HISTORY_DEST="${MERGED}/history"
mkdir -p "${HISTORY_DEST}"
if [[ -d "${HISTORY_DIR}" && "$(ls -A "${HISTORY_DIR}" 2>/dev/null)" ]]; then
  cp -r "${HISTORY_DIR}/." "${HISTORY_DEST}/"
  ok "History restored ($(ls "${HISTORY_DIR}" | wc -l | tr -d ' ') files)"
else
  ok "No previous history — first run in trend charts"
fi

# ── 8. Generate Allure report ─────────────────────────────────────────────────
step "Generating Allure report → ${ALLURE_REPORT_DIR}"
rm -rf "${ALLURE_REPORT_DIR}"
set +e
npx allure generate "${MERGED}" -o "${ALLURE_REPORT_DIR}"
allure_exit_code=$?
set -e

rm -rf "${MERGED}"

if [[ ${allure_exit_code} -ne 0 ]]; then
  warn "Allure report generation failed (exit ${allure_exit_code})"
  exit "${allure_exit_code}"
fi
ok "Allure report generated"

# ── 9. Embed architecture.html (mirrors the CI deploy step) ──────────────────
step "Embedding architecture.html into report..."
cp "${PROJECT_ROOT}/architecture.html" "${ALLURE_REPORT_DIR}/architecture.html"
ok "architecture.html → ${ALLURE_REPORT_DIR}/architecture.html"

# ── 10. Persist allure history for the next run ───────────────────────────────
step "Saving history for trend charts → ${HISTORY_DIR}"
GENERATED_HISTORY="${ALLURE_REPORT_DIR}/history"
if [[ -d "${GENERATED_HISTORY}" ]]; then
  rm -rf "${HISTORY_DIR}"
  mkdir -p "${HISTORY_DIR}"
  cp -r "${GENERATED_HISTORY}/." "${HISTORY_DIR}/"
  ok "History saved ($(ls "${HISTORY_DIR}" | wc -l | tr -d ' ') files)"
else
  warn "No history directory in generated report"
fi

# ── 11. Coloured summary ──────────────────────────────────────────────────────
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
echo -e "  ${CYAN}History depth:${RESET}    ${KEPT_RUNS} run(s) kept (max ${MAX_RUNS})"
echo -e "  ${CYAN}Grafana:${RESET}          http://localhost:3000/d/automation/automation-runs"
echo -e "  ${CYAN}Prometheus:${RESET}       http://localhost:9090"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ── 12. Optionally stop Compose stack ─────────────────────────────────────────
if [[ "${COMPOSE_DOWN:-false}" == "true" ]]; then
  step "Stopping Compose stack (COMPOSE_DOWN=true)..."
  docker compose -f "${COMPOSE_FILE}" down
fi

# ── 13. Open report ───────────────────────────────────────────────────────────
if [[ "${OPEN_ALLURE:-true}" == "false" ]]; then
  ok "Report ready — skipping browser open (OPEN_ALLURE=false)"
else
  step "Opening Allure report in browser..."
  npx allure open "${ALLURE_REPORT_DIR}"
fi

exit "${pytest_exit_code}"
