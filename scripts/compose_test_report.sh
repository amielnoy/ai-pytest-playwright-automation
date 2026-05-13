#!/usr/bin/env bash
# compose_test_report.sh
#
# Run all tests via Docker Compose and produce a full Allure report
# that mirrors the GitHub Actions pipeline:
#   ① Start support services (db, server, monitoring)
#   ② Run pytest inside the automation-tests container
#   ③ Archive the current run's results (for retries/history detail view)
#   ④ Merge current + previous runs so Allure shows full step details of old runs
#   ⑤ Restore allure history so trend charts carry over between runs
#   ⑥ Generate the Allure HTML report from the merged results
#   ⑦ Embed architecture.html inside the report (same as CI deploy)
#   ⑧ Save the new history for the next run
#   ⑨ Print a coloured summary (pass / fail / broken / skip)
#   ⑩ Open the report in the browser (set OPEN_ALLURE=false to skip)
#
# History archive layout (persisted between runs):
#   allure-results-archive/
#     run_20260513_101500/   ← oldest kept
#     run_20260513_141200/
#     run_20260513_180000/   ← most recent previous run
#   allure-history/          ← allure history/ for trend charts
#
# Environment variables (all optional):
#   COMPOSE_FILE   docker-compose file                  default: docker-compose.automation.yml
#   ARTIFACTS_DIR  host artifact root                   default: docker-artifacts
#   ARCHIVE_DIR    rolling archive of past result sets  default: allure-results-archive
#   HISTORY_DIR    allure history/ for trend charts     default: allure-history
#   MAX_RUNS       how many past runs to keep in detail default: 5
#   OPEN_ALLURE    open browser after report            default: true
#   COMPOSE_DOWN   stop stack after tests               default: false

set -Eeuo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.automation.yml}"
ARTIFACTS_DIR="${PROJECT_ROOT}/${ARTIFACTS_DIR:-docker-artifacts}"
ALLURE_RESULTS="${ARTIFACTS_DIR}/allure-results"
ALLURE_REPORT="${ARTIFACTS_DIR}/allure-report"
ARCHIVE_DIR="${PROJECT_ROOT}/${ARCHIVE_DIR:-allure-results-archive}"
HISTORY_DIR="${PROJECT_ROOT}/${HISTORY_DIR:-allure-history}"
MAX_RUNS="${MAX_RUNS:-5}"

cd "${PROJECT_ROOT}"

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[32m'; RED='\033[31m'; YELLOW='\033[33m'
CYAN='\033[36m';  BOLD='\033[1m'; RESET='\033[0m'

step() { echo -e "\n${CYAN}${BOLD}▶ $*${RESET}"; }
ok()   { echo -e "${GREEN}  ✔ $*${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠ $*${RESET}"; }

# ── 1. Prepare directories ────────────────────────────────────────────────────
step "Preparing artifact directories..."
mkdir -p "${ARTIFACTS_DIR}" "${ARCHIVE_DIR}" "${HISTORY_DIR}"
ok "Directories ready"

# ── 2. Start support services ─────────────────────────────────────────────────
step "Starting support services (db, automation-server, monitoring)..."
docker compose -f "${COMPOSE_FILE}" up -d --build \
  db automation-server postgres-exporter prometheus grafana
ok "Services started — Grafana: http://localhost:3000 | Prometheus: http://localhost:9090"

# ── 3. Run tests ──────────────────────────────────────────────────────────────
step "Running tests inside Docker Compose (automation-tests)..."
set +e
docker compose -f "${COMPOSE_FILE}" run --rm \
  -e CI=true \
  automation-tests \
  pytest tests/ \
    --alluredir=/app/test-artifacts/allure-results \
    --clean-alluredir \
    -n auto --dist loadscope
TEST_EXIT=$?
set -e

if [[ ${TEST_EXIT} -eq 0 ]]; then
  ok "Tests finished — all passed"
else
  warn "Tests finished with exit code ${TEST_EXIT} (failures detected)"
fi

# ── 4. Archive the current run ────────────────────────────────────────────────
# We archive BEFORE merging so the archive only contains the pure current run.
step "Archiving current results → ${ARCHIVE_DIR}..."
RUN_LABEL="run_$(date +%Y%m%d_%H%M%S)"
CURRENT_ARCHIVE="${ARCHIVE_DIR}/${RUN_LABEL}"
mkdir -p "${CURRENT_ARCHIVE}"
cp -r "${ALLURE_RESULTS}/." "${CURRENT_ARCHIVE}/"
ok "Archived as ${RUN_LABEL}"

# Prune runs older than MAX_RUNS (keep the most recent MAX_RUNS directories)
TOTAL_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
if [[ ${TOTAL_RUNS} -gt ${MAX_RUNS} ]]; then
  TO_DELETE=$(( TOTAL_RUNS - MAX_RUNS ))
  OLD_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort | head -n "${TO_DELETE}")
  echo "${OLD_RUNS}" | xargs rm -rf
  ok "Pruned ${TO_DELETE} old run(s) — keeping last ${MAX_RUNS}"
fi

# ── 5. Merge current + all kept previous runs ─────────────────────────────────
# Allure groups result files by testCaseId and shows them as "retries".
# Including old result files gives the full step/attachment detail per prior run.
step "Merging results from last ${MAX_RUNS} run(s) for full historical detail..."
MERGED="${ARTIFACTS_DIR}/allure-results-merged"
rm -rf "${MERGED}"
mkdir -p "${MERGED}"

# Oldest first so the most recent run's files win on any filename collision
for run_dir in $(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | sort); do
  cp -r "${run_dir}/." "${MERGED}/" 2>/dev/null || true
done
KEPT=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
ok "Merged ${KEPT} run(s) into ${MERGED}"

# ── 6. Restore allure history (trend charts) ──────────────────────────────────
step "Restoring Allure history for trend charts..."
HISTORY_DEST="${MERGED}/history"
mkdir -p "${HISTORY_DEST}"
if [[ -d "${HISTORY_DIR}" && "$(ls -A "${HISTORY_DIR}" 2>/dev/null)" ]]; then
  cp -r "${HISTORY_DIR}/." "${HISTORY_DEST}/"
  ok "History restored ($(ls "${HISTORY_DIR}" | wc -l | tr -d ' ') files)"
else
  ok "No previous history — this will be run #1 in trend charts"
fi

# ── 7. Generate Allure report from merged results ─────────────────────────────
step "Generating Allure report → ${ALLURE_REPORT}"
rm -rf "${ALLURE_REPORT}"
npx allure generate "${MERGED}" -o "${ALLURE_REPORT}"
ok "Allure report generated"

# ── 8. Embed architecture.html (matches CI deploy step) ──────────────────────
step "Embedding architecture.html into report..."
cp "${PROJECT_ROOT}/architecture.html" "${ALLURE_REPORT}/architecture.html"
ok "architecture.html → ${ALLURE_REPORT}/architecture.html"

# ── 9. Persist allure history for next run ────────────────────────────────────
step "Saving history for trend charts → ${HISTORY_DIR}"
GENERATED_HISTORY="${ALLURE_REPORT}/history"
if [[ -d "${GENERATED_HISTORY}" ]]; then
  rm -rf "${HISTORY_DIR}"
  mkdir -p "${HISTORY_DIR}"
  cp -r "${GENERATED_HISTORY}/." "${HISTORY_DIR}/"
  ok "History saved ($(ls "${HISTORY_DIR}" | wc -l | tr -d ' ') files)"
else
  warn "No history directory in generated report — trend chart will reset"
fi

# Clean up the temporary merged directory
rm -rf "${MERGED}"

# ── 10. Coloured summary ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  TEST RUN SUMMARY${RESET}   $(date '+%Y-%m-%d %H:%M')   [${RUN_LABEL}]"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if command -v python3 &>/dev/null; then
  python3 - "${ALLURE_RESULTS}" << 'PYEOF'
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
RST   = "\033[0m"; BOLD = "\033[1m"

for status in ("passed", "failed", "broken", "skipped"):
    n = counts.get(status, 0)
    if n:
        print(f"  {COLS.get(status,'')}{ICONS.get(status,'❓')}  {status.upper():<8}  {n:>4}{RST}")

print(f"\n  {BOLD}Total: {total}{RST}")
PYEOF
fi

KEPT_RUNS=$(ls -1d "${ARCHIVE_DIR}"/run_* 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo -e "  ${CYAN}Report:${RESET}           ${ALLURE_REPORT}"
echo -e "  ${CYAN}Architecture:${RESET}     ${ALLURE_REPORT}/architecture.html"
echo -e "  ${CYAN}History depth:${RESET}    ${KEPT_RUNS} run(s) archived (max ${MAX_RUNS})"
echo -e "  ${CYAN}Grafana:${RESET}          http://localhost:3000"
echo -e "  ${CYAN}Prometheus:${RESET}       http://localhost:9090"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ── 11. Optionally stop Compose stack ─────────────────────────────────────────
if [[ "${COMPOSE_DOWN:-false}" == "true" ]]; then
  step "Stopping Compose stack (COMPOSE_DOWN=true)..."
  docker compose -f "${COMPOSE_FILE}" down
  ok "Stack stopped"
fi

# ── 12. Open report ───────────────────────────────────────────────────────────
if [[ "${OPEN_ALLURE:-true}" == "false" ]]; then
  ok "Report ready — skipping browser open (OPEN_ALLURE=false)"
else
  step "Opening Allure report in browser..."
  npx allure open "${ALLURE_REPORT}"
fi

exit "${TEST_EXIT}"
