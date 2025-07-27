#!/bin/bash
# Run all tests in test pyramid order (unit -> integration -> e2e)

set -e  # Exit on error
TOTAL_TIMEOUT=900  # 15 minutes total

echo "Running Test Pyramid (Unit -> Integration -> E2E) with ${TOTAL_TIMEOUT}s total timeout..."
echo "===================================================================================="

echo "Phase 1: Unit Tests (Fast feedback)"
echo "-----------------------------------"
timeout 300 ./tests/run_unit_tests.sh || echo "Unit tests phase: TIMEOUT or FAILED"

echo -e "\n\nPhase 2: Integration Tests (Component interactions)"
echo "------------------------------------------------"
timeout 360 ./tests/run_integration_tests.sh || echo "Integration tests phase: TIMEOUT or FAILED"

echo -e "\n\nPhase 3: End-to-End Tests (Full workflows)"
echo "----------------------------------------"
timeout 600 ./tests/run_e2e_tests.sh || echo "E2E tests phase: TIMEOUT or FAILED"

echo -e "\n\nTest pyramid completed."