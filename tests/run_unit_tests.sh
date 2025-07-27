#!/bin/bash
# Run only unit tests for fast feedback during development

set -e  # Exit on error
TIMEOUT_SECONDS=120  # 2 minutes per category

echo "Running Unit Tests with ${TIMEOUT_SECONDS}s timeout per category..."
echo "=================================================================="

# Run unit tests with timeouts
echo "Unit Model Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.unit.models --verbosity=1 || echo "Unit Models: TIMEOUT or FAILED"

echo -e "\nUnit Service Tests..."  
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.unit.services --verbosity=1 || echo "Unit Services: TIMEOUT or FAILED"

echo -e "\nUnit Repository Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.unit.repositories --verbosity=1 || echo "Unit Repositories: TIMEOUT or FAILED"

echo -e "\nUnit Utility Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.unit.utils --verbosity=1 || echo "Unit Utils: TIMEOUT or FAILED"

echo -e "\nUnit tests completed."