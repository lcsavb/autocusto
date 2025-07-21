#!/bin/bash

# Master Test Execution Script for AutoCusto
# Runs all tests with proper categorization and reporting

set -e  # Exit on any error

echo "🧪 AutoCusto Master Test Suite"
echo "============================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
ERROR_TESTS=0
SKIPPED_TESTS=0

# Function to display colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to parse test results
parse_test_results() {
    local output="$1"
    local category="$2"
    
    # Extract test results from Django output
    local results=$(echo "$output" | grep -E "Ran [0-9]+ test.*in [0-9]+\.[0-9]+s")
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
run_test_category() {
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
    
    parse_test_results "$output" "$category"
    
    if [[ $exit_code -eq 0 ]]; then
        print_status $GREEN "   ✅ $category tests completed successfully"
    else
        print_status $RED "   ❌ $category tests failed (exit code: $exit_code)"
        
        # Show last few lines of output for debugging
        echo ""
        print_status $YELLOW "   🔍 Last few lines of output:"
        echo "$output" | tail -10
    fi
    
    echo ""
}

# Function to install Chrome if needed (for Selenium tests)
install_chrome_if_needed() {
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
        print_status $YELLOW "🔧 Chrome/Chromium not found. Attempting to install..."
        
        if [[ "$ENVIRONMENT" == "container" ]]; then
            # Already inside container, try to install directly
            print_status $BLUE "   Installing Chromium in container..."
            apt-get update && apt-get install -y chromium-browser 2>/dev/null || print_status $RED "   ⚠️  Could not install Chrome (permission denied)"
        elif [[ "$ENVIRONMENT" == "docker" ]]; then
            # Install in Docker container via docker-compose
            print_status $BLUE "   Installing Chromium in Docker container..."
            docker-compose exec web bash -c "apt-get update && apt-get install -y chromium-browser" || true
        else
            # Install locally
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y chromium-browser
            elif command -v yum &> /dev/null; then
                sudo yum install -y chromium
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y chromium
            else
                print_status $RED "   ⚠️  Could not install Chrome/Chromium automatically."
                print_status $YELLOW "   Please install Chrome or Chromium manually for Selenium tests."
            fi
        fi
    else
        print_status $GREEN "   ✅ Chrome/Chromium found"
    fi
}

# Main execution
print_status $BLUE "📦 Environment Check"
echo "==================="

# Check if we're running inside Docker container or using docker-compose
if [[ -f /.dockerenv ]] || [[ -n "${CONTAINER}" ]]; then
    print_status $GREEN "✅ Running inside Docker container"
    ENVIRONMENT="container"
elif command -v docker-compose &> /dev/null && docker-compose ps | grep -q "web.*Up"; then
    print_status $GREEN "✅ Docker environment detected and running"
    ENVIRONMENT="docker"
else
    print_status $YELLOW "📍 Using local environment"
    ENVIRONMENT="local"
    
    # Check for virtual environment
    if [[ -d "venv" ]]; then
        print_status $GREEN "   ✅ Virtual environment found"
    else
        print_status $YELLOW "   ⚠️  No virtual environment found at ./venv"
    fi
fi

echo ""

# Install Chrome if needed for Selenium tests
print_status $BLUE "🌐 Browser Setup for Selenium Tests"
echo "==================================="
install_chrome_if_needed
echo ""

# Run test categories
print_status $BLUE "🧪 Executing Test Suite"
echo "======================="

# 1. Forms Tests (fastest, foundational)
run_test_category "Forms" "tests.forms" "Form Validation Tests"

# 2. Authentication Tests (core security)
run_test_category "Authentication" "tests.test_authentication" "Authentication & Security Tests"

# 3. Backend Security Tests
run_test_category "Security" "tests.test_security" "Backend Security Tests"

# 4. Session Functionality Tests
run_test_category "Session" "tests.session_functionality" "Session Functionality Tests"

# 5. Integration Tests
run_test_category "Integration" "tests.integration" "Cross-App Integration Tests"

# 6. Views Tests
run_test_category "Views" "tests.views" "View Logic Tests"

# 7. Frontend Tests (Selenium - may fail without Chrome)
print_status $BLUE "🌐 Frontend Tests (Selenium-based)"
echo "================================="
print_status $YELLOW "   Note: These tests require Chrome/Chromium and may be skipped if not available"

run_test_category "Frontend-Login" "tests.test_login_frontend" "Frontend Login UI Tests"
run_test_category "Frontend-Registration" "tests.test_user_registration" "Frontend Registration Tests"  
run_test_category "Frontend-Security" "tests.test_frontend_security" "Frontend Security Tests"
run_test_category "Clinic-Management" "tests.test_clinic_management" "Clinic Management Tests"
run_test_category "Prescription-Forms" "tests.test_prescription_forms" "Prescription Form Tests"

# Final Summary
echo ""
print_status $BLUE "📊 Final Test Results Summary"
echo "============================="
echo ""

# Calculate success rate
success_rate=0
if [[ $TOTAL_TESTS -gt 0 ]]; then
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo "📈 Overall Statistics:"
echo "   Total Tests Run: $TOTAL_TESTS"
echo "   ✅ Passed: $PASSED_TESTS"
echo "   ❌ Failed: $FAILED_TESTS" 
echo "   🔥 Errors: $ERROR_TESTS"
echo "   ⏭️  Skipped: $SKIPPED_TESTS"
echo "   📊 Success Rate: ${success_rate}%"
echo ""

# Status determination
if [[ $FAILED_TESTS -eq 0 && $ERROR_TESTS -eq 0 ]]; then
    print_status $GREEN "🎉 ALL TESTS PASSED! System is ready for deployment."
    exit 0
elif [[ $success_rate -ge 80 ]]; then
    print_status $YELLOW "⚠️  Most tests passed ($success_rate% success rate)"
    print_status $YELLOW "   Some issues need attention before deployment."
    exit 1
else
    print_status $RED "🚨 SIGNIFICANT TEST FAILURES ($success_rate% success rate)"
    print_status $RED "   System needs fixes before deployment."
    exit 2
fi