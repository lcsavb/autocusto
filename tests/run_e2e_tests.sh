#!/bin/bash
# Run end-to-end tests for complete user workflows

set -e  # Exit on error
TIMEOUT_SECONDS=300  # 5 minutes per category (E2E tests can be slower)

echo "Running End-to-End Tests with ${TIMEOUT_SECONDS}s timeout per category..."
echo "======================================================================="

echo "User Journey Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.user_journeys --verbosity=1 || echo "E2E User Journeys: TIMEOUT or FAILED"

echo -e "\nBrowser Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.browser --verbosity=1 || echo "E2E Browser: TIMEOUT or FAILED"

echo -e "\nSecurity Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.security --verbosity=1 || echo "E2E Security: TIMEOUT or FAILED"

echo -e "\nEnd-to-end tests completed."