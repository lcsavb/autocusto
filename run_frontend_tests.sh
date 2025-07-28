#!/bin/bash
# Run all frontend/E2E tests from host into container
# Usage: ./run_frontend_tests.sh

set -e  # Exit on error

echo "🎭 AutoCusto Frontend Test Runner"
echo "================================="
echo "Running all E2E and Playwright tests inside Docker container..."
echo ""

# Check if container is running
if ! docker ps | grep -q "autocusto-web-1"; then
    echo "❌ Error: autocusto-web-1 container is not running"
    echo "   Please start the container first with: docker compose up -d"
    exit 1
fi

echo "✅ Container is running"
echo ""

# Set timeout for each test category (E2E tests can be slow)
TIMEOUT_SECONDS=300  # 5 minutes per category

echo "📋 Running Test Categories:"
echo "  1. User Journey Tests (workflow testing)"
echo "  2. Browser/Playwright Tests (UI automation)" 
echo "  3. Security Tests (frontend security)"
echo ""

# Track test results
FAILED_CATEGORIES=()

echo "👤 [1/3] User Journey Tests..."
echo "-----------------------------"
if timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.user_journeys --verbosity=1; then
    echo "✅ User Journey Tests: PASSED"
else
    echo "❌ User Journey Tests: FAILED or TIMEOUT"
    FAILED_CATEGORIES+=("User Journeys")
fi

echo ""
echo "🌐 [2/3] Browser/Playwright Tests..."
echo "-----------------------------------"
if timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.browser --verbosity=1; then
    echo "✅ Browser/Playwright Tests: PASSED"
else
    echo "⚠️  Browser/Playwright Tests: FAILED or TIMEOUT"
    echo "   Note: May have Docker networking limitations with Chrome connectivity"
    FAILED_CATEGORIES+=("Browser/Playwright")
fi

echo ""
echo "🔒 [3/3] Security Tests..."
echo "-------------------------"
if timeout ${TIMEOUT_SECONDS} docker exec autocusto-web-1 python manage.py test --keepdb --noinput tests.e2e.security --verbosity=1; then
    echo "✅ Security Tests: PASSED"
else
    echo "❌ Security Tests: FAILED or TIMEOUT"
    FAILED_CATEGORIES+=("Security")
fi

echo ""
echo "🏁 Test Results Summary"
echo "======================"

if [ ${#FAILED_CATEGORIES[@]} -eq 0 ]; then
    echo "🎉 ALL FRONTEND TESTS PASSED!"
    exit 0
else
    echo "⚠️  Some test categories failed:"
    for category in "${FAILED_CATEGORIES[@]}"; do
        echo "   ❌ $category"
    done
    echo ""
    echo "💡 Troubleshooting:"
    echo "   - Check container logs: docker logs autocusto-web-1"
    echo "   - Run individual categories: docker exec autocusto-web-1 python manage.py test tests.e2e.browser"
    echo "   - Browser tests may need Docker networking configuration for Chrome"
    exit 1
fi