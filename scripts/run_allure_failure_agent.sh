#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}" || exit 1

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="python3"
fi

ALLURE_DIR="${ALLURE_DIR:-allure-results}"
NO_AI_FLAG=""
MODEL=""
API_KEY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allure-dir)
      shift
      ALLURE_DIR="$1"
      ;;
    --no-ai)
      NO_AI_FLAG="--no-ai"
      ;;
    --model)
      shift
      MODEL="$1"
      ;;
    --api-key)
      shift
      API_KEY="$1"
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--allure-dir DIR] [--no-ai] [--model MODEL] [--api-key KEY]"
      exit 1
      ;;
  esac
  shift
done

export ANTHROPIC_API_KEY="${API_KEY:-${ANTHROPIC_API_KEY:-}}"

CMD=("${PYTHON_BIN}" "run_failure_agent.py" "--allure-dir" "${ALLURE_DIR}")
if [[ -n "${NO_AI_FLAG}" ]]; then
  CMD+=("${NO_AI_FLAG}")
fi
if [[ -n "${MODEL}" ]]; then
  CMD+=("--model" "${MODEL}")
fi

printf "Running failure analysis agent with:\n  allure dir: %s\n  no-ai: %s\n  model: %s\n" "${ALLURE_DIR}" "${NO_AI_FLAG}" "${MODEL:-default}"
exec "${CMD[@]}"
