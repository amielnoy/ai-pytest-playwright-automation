#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running all tests, generating a fresh Allure report, and opening it."
"${PROJECT_ROOT}/scripts/run_tests_with_allure.sh" tests/ "$@"
