#!/bin/bash
# Host Machine Test Runner for AutoCusto
# Runs all tests inside the Docker container but executed from host for convenience
# DO NOT ADD TO DEPLOYMENT WORKFLOW - this is for local development only

# set -e  # Exit on any error - disabled to allow test failures to be handled gracefully

echo "🏠 AutoCusto Host Machine Test Runner"
echo "===================================="
echo "Running tests inside Docker container from host machine"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check Docker environment
check_docker_environment() {
    print_status $BLUE "🐳 Checking Docker Environment"
    echo "=============================="
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_status $RED "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if AutoCusto container is running
    if ! docker exec autocusto-web-1 echo "Container accessible" > /dev/null 2>&1; then
        print_status $RED "❌ AutoCusto container (autocusto-web-1) is not running."
        print_status $YELLOW "   Please start the container with: docker-compose up -d"
        exit 1
    fi
    
    print_status $GREEN "✅ Docker environment is ready"
    print_status $GREEN "✅ AutoCusto container is running"
    echo ""
}

# Function to run test category with proper Docker exec
run_container_test() {
    local category=$1
    local test_path=$2
    local description=$3
    local timeout_seconds=${4:-120}
    
    print_status $BLUE "🔄 Running $description..."
    echo ""
    
    local exit_code=0
    local temp_output="/tmp/test_output_$$"
    
    # Run tests and capture output to temporary file
    timeout ${timeout_seconds} docker exec autocusto-web-1 python manage.py test $test_path --keepdb --noinput --verbosity=2 --debug-mode > "$temp_output" 2>&1 || exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_status $GREEN "   ✅ $category completed successfully"
        # Only log a success summary for passed tests
        echo "=== $category PASSED ===" >> "$CONSOLIDATED_ERROR_FILE"
        # Extract just the final summary line for passed tests
        grep -E "^Ran [0-9]+ tests|^OK" "$temp_output" >> "$CONSOLIDATED_ERROR_FILE" 2>/dev/null || echo "All tests passed" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    elif [[ $exit_code -eq 124 ]]; then
        print_status $YELLOW "   ⏰ $category timed out after ${timeout_seconds} seconds"
        echo "=== $category TIMEOUT (${timeout_seconds}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        # For timeouts, include the last part of output which might have useful info
        tail -50 "$temp_output" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    else
        print_status $RED "   ❌ $category failed (exit code: $exit_code)"
        echo "=== $category FAILED (exit code: $exit_code) ===" >> "$CONSOLIDATED_ERROR_FILE"
        # For failures, use a simpler approach: extract error sections and summary
        {
            # First add test summary
            grep -E "^Ran [0-9]+ tests|^FAILED \(|^OK$|^Using existing test database" "$temp_output"
            echo ""
            # Then add each complete error/failure block
            grep -A 20 -E "^ERROR:|^FAIL:" "$temp_output" | grep -E "^ERROR:|^FAIL:|^Traceback|^  File|^    |Error:|AssertionError:|^------"
        } >> "$CONSOLIDATED_ERROR_FILE" 2>/dev/null
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    fi
    
    # Clean up temporary file
    rm -f "$temp_output"
    
    echo ""
    return $exit_code
}

# Main execution
print_status $BLUE "🚀 Starting Host Machine Test Execution"
echo ""

# Create consolidated error file
CONSOLIDATED_ERROR_FILE="test_errors_$(date +%Y%m%d_%H%M%S).log"
echo "AutoCusto Test Errors - $(date)" > "$CONSOLIDATED_ERROR_FILE"
echo "========================================" >> "$CONSOLIDATED_ERROR_FILE"
echo "" >> "$CONSOLIDATED_ERROR_FILE"

# Check environment
check_docker_environment

# Clean up any existing test databases
print_status $BLUE "🧹 Cleaning up previous test databases..."
docker exec autocusto-web-1 python manage.py flush --noinput > /dev/null 2>&1 || true
echo ""

# Test execution summary
TOTAL_CATEGORIES=0
PASSED_CATEGORIES=0
FAILED_CATEGORIES=0

print_status $BLUE "📍 PHASE 1: Unit Tests (Fast Feedback)"
echo "======================================"

# Unit Tests
((TOTAL_CATEGORIES++))
if run_container_test "Unit-Models" "tests.unit.models" "Model Unit Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Unit-Services" "tests.unit.services" "Service Unit Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Unit-Repositories" "tests.unit.repositories" "Repository Unit Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Unit-Utils" "tests.unit.utils" "Utility Unit Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "📍 PHASE 2: Integration Tests (Component Interactions)"
echo "===================================================="

# Integration Tests
((TOTAL_CATEGORIES++))
if run_container_test "Integration-Database" "tests.integration.database" "Database Integration Tests" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Integration-API" "tests.integration.api" "API Integration Tests" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Integration-Forms" "tests.integration.forms" "Form Integration Tests" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "Integration-Services" "tests.integration.services" "Service Integration Tests" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "📍 PHASE 3: End-to-End Tests (Complete Workflows)"
echo "=============================================="

# E2E Tests
((TOTAL_CATEGORIES++))
if run_container_test "E2E-User-Journeys" "tests.e2e.user_journeys" "User Journey Tests" 300; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "🌐 Running E2E Browser Tests (Playwright Remote Architecture)"
print_status $GREEN "   ✅ Infrastructure: Web container + Playwright browser container"

# Check if Playwright browser container is running
if ! docker exec autocusto-playwright-browsers-1 echo "Browser container accessible" > /dev/null 2>&1; then
    print_status $YELLOW "   ⚠️  Playwright browser container not running - starting it..."
    if ! docker compose up -d playwright-browsers > /dev/null 2>&1; then
        print_status $RED "   ❌ Failed to start Playwright browser container"
        print_status $YELLOW "   Skipping browser tests for this run"
    else
        print_status $GREEN "   ✅ Playwright browser container started"
        sleep 3  # Give browser container time to initialize
    fi
fi

# E2E Browser Tests (Playwright with remote browser)
((TOTAL_CATEGORIES++))
if run_container_test "E2E-Browser-Playwright" "tests.integration.services.test_pdf_workflows" "Playwright PDF Workflow Tests" 300; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_container_test "E2E-Security" "tests.e2e.security" "Security End-to-End Tests" 300; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

# Final Summary
echo ""
print_status $BLUE "📊 Host Machine Test Results Summary"
echo "==================================="
echo ""

# Calculate success rate
success_rate=0
if [[ $TOTAL_CATEGORIES -gt 0 ]]; then
    success_rate=$((PASSED_CATEGORIES * 100 / TOTAL_CATEGORIES))
fi

echo "📈 Overall Statistics:"
echo "   Total Test Categories: $TOTAL_CATEGORIES"
echo "   ✅ Passed: $PASSED_CATEGORIES"
echo "   ❌ Failed: $FAILED_CATEGORIES" 
echo "   📊 Success Rate: ${success_rate}%"
echo ""

# Show consolidated error file info
if [[ -f "$CONSOLIDATED_ERROR_FILE" ]]; then
    print_status $BLUE "📄 Consolidated Error Log:"
    echo "=========================="
    echo "   📁 File: $CONSOLIDATED_ERROR_FILE"
    
    # Show file size and line count for quick assessment
    local file_size=$(wc -c < "$CONSOLIDATED_ERROR_FILE")
    local line_count=$(wc -l < "$CONSOLIDATED_ERROR_FILE")
    
    if [[ $file_size -gt 100 ]]; then
        echo "   📊 Size: $file_size bytes, $line_count lines"
        print_status $YELLOW "   💡 Contains only errors/failures and test summaries"
        print_status $YELLOW "   💡 Use: grep -A 5 -B 5 'FAILED\\|ERROR' $CONSOLIDATED_ERROR_FILE"
    else
        echo "   📊 Size: $file_size bytes (minimal errors logged)"
    fi
    echo ""
fi

# Status determination
if [[ $FAILED_CATEGORIES -eq 0 ]]; then
    print_status $GREEN "🎉 ALL TEST CATEGORIES PASSED!"
    print_status $GREEN "   Backend tests are working correctly"
    print_status $GREEN "   System is stable for development work"
    echo ""
    print_status $BLUE "📝 Development Notes:"
    echo "   - Backend unit tests: ✅ All passing"
    echo "   - Integration tests: ✅ Working properly"  
    echo "   - E2E browser tests: ✅ Playwright remote browser architecture working"
    echo "   - Test infrastructure: ✅ Fully operational with Docker containers"
    exit 0
elif [[ $success_rate -ge 80 ]]; then
    print_status $YELLOW "⚠️  Most test categories passed ($success_rate% success rate)"
    print_status $YELLOW "   Some categories need attention"
    exit 1
else
    print_status $RED "🚨 SIGNIFICANT TEST CATEGORY FAILURES ($success_rate% success rate)"
    print_status $RED "   Multiple categories need fixes"
    exit 2
fi