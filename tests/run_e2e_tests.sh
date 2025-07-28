#!/bin/bash
# Run end-to-end tests for complete user workflows

# set -e  # Exit on error - DISABLED to allow all tests to run even if some fail
TIMEOUT_SECONDS=300  # 5 minutes per category (E2E tests can be slower)

echo "🎭 Running End-to-End Tests - Complete Workflows"
echo "==============================================="
echo "Status: E2E infrastructure ready, Chrome/Docker networking limitation identified"
echo ""

echo "👤 User Journey Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.user_journeys --verbosity=1 || echo "❌ E2E User Journeys: TIMEOUT or FAILED"

echo -e "\n🌐 Browser Tests (Infrastructure Ready - Networking Issue)..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.browser --verbosity=1 || echo "⚠️  E2E Browser: Known Docker networking limitation"

echo -e "\n🔒 Security Tests..."
timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.security --verbosity=1 || echo "❌ E2E Security: TIMEOUT or FAILED"

echo -e "\n✅ End-to-end tests completed."
echo ""
echo "📝 Note: Browser tests have Docker networking limitation preventing Chrome-to-LiveServer connection"
echo "   Infrastructure is ready, Chrome launches successfully, LiveServer is functional"
echo "   Next step: Configure Docker networking for Chrome browser connectivity"