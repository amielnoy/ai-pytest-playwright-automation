#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-docker-artifacts}"
ALLURE_RESULTS_DIR="${ARTIFACTS_DIR}/allure-results"
ALLURE_REPORT_DIR="${ARTIFACTS_DIR}/allure-report"

cd "${PROJECT_ROOT}" || exit 1

echo "Running Docker tests and writing results to: ${ALLURE_RESULTS_DIR}"
"${PROJECT_ROOT}/scripts/run_all_tests_docker.sh" "$@"
pytest_exit_code=$?

echo "Generating fresh Docker Allure report: ${ALLURE_REPORT_DIR}"
rm -rf "${ALLURE_REPORT_DIR}"
npx allure generate "${ALLURE_RESULTS_DIR}" -o "${ALLURE_REPORT_DIR}"
allure_exit_code=$?

if [[ ${allure_exit_code} -ne 0 ]]; then
  echo "Allure report generation failed with exit code ${allure_exit_code}"
  exit "${allure_exit_code}"
fi

echo "Opening Docker Allure report: ${ALLURE_REPORT_DIR}"
if [[ "${OPEN_ALLURE:-true}" == "false" ]]; then
  echo "Skipping Allure open because OPEN_ALLURE=false"
else
  npx allure open "${ALLURE_REPORT_DIR}"
fi

exit "${pytest_exit_code}"
