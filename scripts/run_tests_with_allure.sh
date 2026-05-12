#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLURE_RESULTS_DIR="${ALLURE_RESULTS_DIR:-allure-results}"
ALLURE_REPORT_DIR="${ALLURE_REPORT_DIR:-allure-report}"

cd "${PROJECT_ROOT}" || exit 1

if [[ -x ".venv/bin/pytest" ]]; then
  PYTEST_BIN=".venv/bin/pytest"
else
  PYTEST_BIN="pytest"
fi

pytest_args=("$@")
if [[ ${#pytest_args[@]} -eq 0 ]]; then
  pytest_args=("tests/")
fi

echo "Running tests with Allure results: ${ALLURE_RESULTS_DIR}"
"${PYTEST_BIN}" "${pytest_args[@]}" \
  --alluredir="${ALLURE_RESULTS_DIR}" \
  --clean-alluredir
pytest_exit_code=$?

echo "Generating fresh Allure report: ${ALLURE_REPORT_DIR}"
rm -rf "${ALLURE_REPORT_DIR}"
npx allure generate "${ALLURE_RESULTS_DIR}"
allure_exit_code=$?

if [[ ${allure_exit_code} -ne 0 ]]; then
  echo "Allure report generation failed with exit code ${allure_exit_code}"
  exit "${allure_exit_code}"
fi

if [[ -z "${ALLURE_OPEN_DIR:-}" ]]; then
  if [[ -f "${ALLURE_REPORT_DIR}/summary.json" ]]; then
    ALLURE_OPEN_DIR="${ALLURE_REPORT_DIR}"
  elif [[ -f "${ALLURE_REPORT_DIR}/awesome/summary.json" ]]; then
    ALLURE_OPEN_DIR="${ALLURE_REPORT_DIR}/awesome"
  else
    ALLURE_OPEN_DIR="${ALLURE_REPORT_DIR}"
  fi
fi

echo "Opening Allure report: ${ALLURE_OPEN_DIR}"
if [[ "${OPEN_ALLURE:-true}" == "false" ]]; then
  echo "Skipping Allure open because OPEN_ALLURE=false"
else
  npx allure open "${ALLURE_OPEN_DIR}"
fi

exit "${pytest_exit_code}"
