#!/bin/bash
# Run integration tests that test component interactions

set -e  # Exit on error
TIMEOUT_SECONDS=180  # 3 minutes per category

echo "Running Integration Tests with ${TIMEOUT_SECONDS}s timeout per category..."
echo "========================================================================"

echo "Database Integration Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.integration.database --verbosity=1 || echo "Integration Database: TIMEOUT or FAILED"

echo -e "\nAPI Integration Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.integration.api --verbosity=1 || echo "Integration API: TIMEOUT or FAILED"

echo -e "\nForm Integration Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.integration.forms --verbosity=1 || echo "Integration Forms: TIMEOUT or FAILED"

echo -e "\nService Integration Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.integration.services --verbosity=1 || echo "Integration Services: TIMEOUT or FAILED"

echo -e "\nIntegration tests completed."