#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# Trivy base-image vulnerability scanner — MoveInSync
# Adapted from gameapp DevSecOps standards
# ──────────────────────────────────────────────────────────────────────────────

set -e

# Extract the base image from the first FROM line in Dockerfile
DOCKER_IMAGE_NAME=$(grep -m1 '^FROM' Dockerfile | awk '{print $2}')

if [[ -z "${DOCKER_IMAGE_NAME}" ]]; then
    echo "ERROR: Could not determine base image from Dockerfile."
    exit 1
fi

echo "=============================================="
echo "  Trivy Base Image Scan"
echo "  Image : ${DOCKER_IMAGE_NAME}"
echo "=============================================="

# ── Step 1: Scan for HIGH severity (informational — pipeline continues) ────────
echo ""
echo "[1/2] Scanning for HIGH severity vulnerabilities..."
trivy image --exit-code 0 --severity HIGH --no-progress "${DOCKER_IMAGE_NAME}"

# ── Step 2: Scan for CRITICAL severity (blocks pipeline if found) ─────────────
echo ""
echo "[2/2] Scanning for CRITICAL severity vulnerabilities..."
trivy image --exit-code 1 --severity CRITICAL --no-progress "${DOCKER_IMAGE_NAME}"
EXIT_CODE=$?

echo ""
if [[ "${EXIT_CODE}" == 1 ]]; then
    echo "RESULT: FAILED — CRITICAL vulnerabilities found in ${DOCKER_IMAGE_NAME}"
    echo "        Please update the base image or apply fixes before proceeding."
    exit 1
else
    echo "RESULT: PASSED — No CRITICAL vulnerabilities found in ${DOCKER_IMAGE_NAME}"
fi
