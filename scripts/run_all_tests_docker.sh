#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE_NAME="${IMAGE_NAME:-ness-automation-tests}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-docker-artifacts}"
ALLURE_RESULTS_DIR="/app/test-artifacts/allure-results"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_ARTIFACTS_DIR="${PROJECT_ROOT}/${ARTIFACTS_DIR}"
SECRETS_FILE="${PROJECT_ROOT}/data/secrets.json"

mkdir -p "${HOST_ARTIFACTS_DIR}"

echo "Building Docker image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" "${PROJECT_ROOT}"

docker_args=(
  run
  --rm
  -e CI=true
  -v "${HOST_ARTIFACTS_DIR}:/app/test-artifacts"
)

if [[ -f "${SECRETS_FILE}" ]]; then
  docker_args+=(
    -v "${SECRETS_FILE}:/app/data/secrets.json:ro"
  )
fi

pytest_args=(
  pytest
  tests/
  --alluredir="${ALLURE_RESULTS_DIR}"
)

if [[ $# -gt 0 ]]; then
  pytest_args+=("$@")
fi

echo "Writing Allure results to: ${HOST_ARTIFACTS_DIR}/allure-results"
echo "Running: docker ${docker_args[*]} ${IMAGE_NAME} ${pytest_args[*]}"

docker "${docker_args[@]}" "${IMAGE_NAME}" "${pytest_args[@]}"
