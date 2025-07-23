#!/bin/bash
# Backend-only test suite for CI/CD deployment
# Excludes browser-dependent tests (Selenium/Playwright)

set -e  # Exit on any error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
    echo -e "$1$2${NC}"
}

# Test tracking variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
ERROR_TESTS=0
SKIPPED_TESTS=0

# Function to parse and update test counts
update_test_counts() {
    local category=$1
    local output="$2"
    local exit_code=$3
    
    # Parse test results from output
    local results=$(echo "$output" | grep -E "Ran [0-9]+ test")
    local failures=$(echo "$output" | grep -E "FAILED.*failures=([0-9]+)" | sed -n 's/.*failures=\([0-9]\+\).*/\1/p')
    local errors=$(echo "$output" | grep -E "errors=([0-9]+)" | sed -n 's/.*errors=\([0-9]\+\).*/\1/p')
    local skipped=$(echo "$output" | grep -E "skipped=([0-9]+)" | sed -n 's/.*skipped=\([0-9]\+\).*/\1/p')
    
    if [[ -n "$results" ]]; then
        local test_count=$(echo "$results" | sed -n 's/.*Ran \([0-9]\+\) test.*/\1/p')
        TOTAL_TESTS=$((TOTAL_TESTS + test_count))
        
        # Default values
        failures=${failures:-0}
        errors=${errors:-0}  
        skipped=${skipped:-0}
        
        FAILED_TESTS=$((FAILED_TESTS + failures))
        ERROR_TESTS=$((ERROR_TESTS + errors))
        SKIPPED_TESTS=$((SKIPPED_TESTS + skipped))
        
        local passed=$((test_count - failures - errors - skipped))
        PASSED_TESTS=$((PASSED_TESTS + passed))
        
        echo "  📊 $category Results: $test_count tests, $passed passed, $failures failed, $errors errors, $skipped skipped"
    fi
}

# Function to run test category
run_backend_test_category() {
    local category=$1
    local test_path=$2
    local description=$3
    
    print_status $BLUE "🔄 Running $description..."
    echo ""
    
    # Use timeout to prevent hanging tests
    local output
    local exit_code=0
    
    if [[ "$ENVIRONMENT" == "container" ]]; then
        print_status $YELLOW "   Running inside container"
        output=$(timeout 300 python manage.py test $test_path --settings=test_settings --verbosity=1 2>&1) || exit_code=$?
    elif [[ "$ENVIRONMENT" == "docker" ]]; then
        print_status $YELLOW "   Using Docker environment"
        output=$(timeout 300 docker-compose exec -T web python manage.py test $test_path --settings=test_settings --verbosity=1 2>&1) || exit_code=$?
    else
        print_status $YELLOW "   Using local environment"
        # Check if virtual environment exists
        if [[ -d "venv/bin" ]]; then
            source venv/bin/activate
        fi
        output=$(timeout 300 python manage.py test $test_path --settings=test_settings --verbosity=1 2>&1) || exit_code=$?
    fi
    
    # Parse results and show summary
    update_test_counts "$category" "$output" $exit_code
    
    if [[ $exit_code -eq 0 ]]; then
        print_status $GREEN "   ✅ $category tests completed successfully"
    else
        print_status $RED "   ❌ $category tests failed (exit code: $exit_code)"
        
        print_status $YELLOW "   🔍 Last few lines of output:"
        echo "$output" | tail -10
    fi
    
    echo ""
}

# Header
print_status $BLUE "🧪 AutoCusto Backend Test Suite (CI/CD)"
echo "======================================"
echo ""

# Environment detection
if [[ -f /.dockerenv ]] || [[ -n "${CONTAINER}" ]]; then
    print_status $GREEN "✅ Running inside Docker container"
    ENVIRONMENT="container"
elif command -v docker-compose &> /dev/null && docker-compose ps | grep -q "web.*Up"; then
    print_status $GREEN "✅ Docker environment detected"
    ENVIRONMENT="docker"
else
    print_status $YELLOW "📍 Using local environment"
    ENVIRONMENT="local"
fi
echo ""

# Backend-only test categories (NO browser dependencies)
print_status $BLUE "🧪 Backend Tests (No Browser Required)"
echo "====================================="

# 1. Forms Tests (fastest, foundational)
run_backend_test_category "Forms" "tests.forms" "Form Validation Tests"

# 2. Authentication Tests (critical for medical app)
run_backend_test_category "Authentication" "tests.test_authentication" "Authentication & Security Tests"

# 3. Backend Security Tests
run_backend_test_category "Security" "tests.test_security" "Backend Security Tests"

# 4. Integration Tests (newly fixed)
run_backend_test_category "Integration" "tests.integration" "Cross-App Integration Tests"

# 5. Session Functionality Tests
run_backend_test_category "Session" "tests.session_functionality" "Session Functionality Tests"

# 6. Views Tests
run_backend_test_category "Views" "tests.views" "View Logic Tests"

# 7. PDF Generation Tests (core business logic)
run_backend_test_category "PDF-Generation" "tests.test_pdf_generation" "PDF Generation Tests"

# 8. PDF Strategies Tests
run_backend_test_category "PDF-Strategies" "tests.test_pdf_strategies" "PDF Strategy Tests"

# Final Summary
echo ""
print_status $BLUE "📊 Backend Test Results Summary"
echo "==============================="
echo ""

# Calculate success rate
success_rate=0
if [[ $TOTAL_TESTS -gt 0 ]]; then
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo "📈 Backend Test Statistics:"
echo "   Total Tests Run: $TOTAL_TESTS"
echo "   ✅ Passed: $PASSED_TESTS"
echo "   ❌ Failed: $FAILED_TESTS"
echo "   🔥 Errors: $ERROR_TESTS"
echo "   ⏭️  Skipped: $SKIPPED_TESTS"
echo "   📊 Success Rate: ${success_rate}%"
echo ""

# Overall status
if [[ $FAILED_TESTS -eq 0 && $ERROR_TESTS -eq 0 ]]; then
    print_status $GREEN "🎉 ALL BACKEND TESTS PASSED! Ready for deployment."
    echo ""
    echo "✅ Core Business Logic: Forms, PDF Generation, Authentication"
    echo "✅ Security & Access Control: Backend security validated"  
    echo "✅ Integration Workflows: Cross-app functionality verified"
    echo "✅ Session Management: User workflow integrity confirmed"
    echo ""
    echo "🚀 Backend is deployment-ready!"
    exit 0
else
    print_status $RED "🚨 BACKEND TESTS FAILED! Deployment blocked."
    echo ""
    echo "❌ Failed Tests: $FAILED_TESTS"
    echo "🔥 Error Tests: $ERROR_TESTS"
    echo ""
    echo "🔧 Fix failing tests before deployment."
    exit 1
fi