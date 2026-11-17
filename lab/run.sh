#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-loom-190-adk-a2a-hitl}"

PIN_TAG="v1.9.0"
PIN_SHA="a3050669f5b4c83210a44ed4346f17e01641e82f"
SRC_DEST="src-v1.9.0"
LABEL="LOOM-190-ADK-A2A-HITL"
WITNESS="LOOM-190-ADK-A2A-HITL-WITNESS"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail() {
  echo "FAIL ${LABEL} $* ${WITNESS}" | tee poc-last-run.txt
  exit 1
}


trap down EXIT

copy_pin() {
  local tmp got
  tmp="$(mktemp -d)"
  GIT_TERMINAL_PROMPT=0 git clone --depth 1 --branch "${PIN_TAG}" --filter=blob:none --sparse \
    https://github.com/awslabs/loom.git "${tmp}"
  git -C "${tmp}" sparse-checkout set agents/adk_agent agents/strands_agent
  got="$(git -C "${tmp}" rev-parse HEAD)"
  echo "checkout tag=${PIN_TAG} sha=${got} expect=${PIN_SHA}"
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    GIT_TERMINAL_PROMPT=0 git -C "${tmp}" fetch --depth 1 origin "${PIN_SHA}"
    git -C "${tmp}" checkout -f "${PIN_SHA}"
    got="$(git -C "${tmp}" rev-parse HEAD)"
    echo "checkout-forced sha=${got}"
  fi
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    rm -rf "${tmp}"
    echo "FAIL ${LABEL} unexpected-commit got=${got} expect=${PIN_SHA}" | tee poc-last-run.txt
    exit 1
  fi
  rm -rf "src-v1.9.0"
  mkdir -p "src-v1.9.0/agents"
  cp -a "${tmp}/agents/adk_agent" "src-v1.9.0/agents/"
  cp -a "${tmp}/agents/strands_agent" "src-v1.9.0/agents/"
  rm -rf "${tmp}"
  find "src-v1.9.0" -type d -name '__pycache__' -exec rm -rf {} + || true
  echo "checkout-ok tag=${PIN_TAG} sha=${got} source=public-tag"
}

echo "== pin ${PIN_TAG} ${PIN_SHA} =="
copy_pin
if [[ ! -f "${SRC_DEST}/agents/adk_agent/src/integrations/a2a_client.py" ]]; then
  fail "missing-adk-a2a-client"
fi
if [[ ! -f "${SRC_DEST}/agents/strands_agent/src/integrations/approval.py" ]]; then
  fail "missing-strands-approval"
fi

python3 -m py_compile poc.py

echo "== docker compose down (clean) =="
down

echo "== docker compose up --build =="
if ! docker compose -p "${COMPOSE_PROJECT_NAME}" up --build -d; then
  fail "compose-up-failed"
fi

echo "== poc.py =="
set +e
docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T lab python /lab/poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if ! grep -qE "FAIL ${LABEL}|SUCCESS ${LABEL}" poc-last-run.txt; then
  echo "FAIL ${LABEL} poc-no-verdict exit=${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi
exit "${rc}"
