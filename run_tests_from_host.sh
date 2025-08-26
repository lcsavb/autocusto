#!/bin/bash
# Host Machine Test Runner for AutoCusto - Enhanced Version
# Runs all tests inside the Docker container but executed from host for convenience
# DO NOT ADD TO DEPLOYMENT WORKFLOW - this is for local development only
#
# ⚡ IMPROVEMENTS IN THIS VERSION:
# - E2E/Browser tests run ONE BY ONE with real-time feedback (expert approach)
# - No more batching issues - each test gets full resources and clean state
# - Immediate feedback - see results as each test completes
# - Better debugging - pinpoint exact failing tests instantly
# - Reduced timeout risk - each test isolated with appropriate timeout

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

# Function to run test category with proper Docker exec and better feedback
run_container_test() {
    local category=$1
    local test_path=$2
    local description=$3
    local timeout_seconds=${4:-120}
    
    print_status $BLUE "🔄 Running $description..."
    echo ""
    
    local exit_code=0
    local temp_output="/tmp/test_output_$$"
    local start_time=$(date +%s)
    
    # Run tests and capture output to temporary file
    timeout ${timeout_seconds} docker exec autocusto-web-1 python manage.py test $test_path --keepdb --noinput --verbosity=2 --debug-mode > "$temp_output" 2>&1 || exit_code=$?
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Extract test count and individual results for better feedback
    local test_count=$(grep -E "^Ran [0-9]+ tests" "$temp_output" | grep -o '[0-9]\+' | head -1)
    local individual_results=$(grep -E "^test_[a-zA-Z_0-9]+ \(" "$temp_output" | sed 's/^test_/  ✓ test_/' | head -10)
    
    if [[ $exit_code -eq 0 ]]; then
        print_status $GREEN "   ✅ $category completed successfully (${duration}s)"
        if [[ -n "$test_count" ]]; then
            print_status $GREEN "   📊 Ran $test_count tests - all passed"
        fi
        # Show first few individual test results for feedback
        if [[ -n "$individual_results" ]]; then
            echo "$individual_results"
        fi
        
        # Log success summary
        echo "=== $category PASSED (${duration}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        grep -E "^Ran [0-9]+ tests|^OK" "$temp_output" >> "$CONSOLIDATED_ERROR_FILE" 2>/dev/null || echo "All tests passed" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    elif [[ $exit_code -eq 124 ]]; then
        print_status $YELLOW "   ⏰ $category timed out after ${timeout_seconds} seconds"
        echo "=== $category TIMEOUT (${timeout_seconds}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        # For timeouts, include the last part of output which might have useful info
        tail -50 "$temp_output" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    else
        print_status $RED "   ❌ $category failed (exit code: $exit_code, ${duration}s)"
        if [[ -n "$test_count" ]]; then
            local failed_count=$(grep -E "^FAILED \(" "$temp_output" | grep -o 'failures=[0-9]\+\|errors=[0-9]\+' | grep -o '[0-9]\+' | head -1)
            if [[ -n "$failed_count" ]]; then
                print_status $RED "   📊 Ran $test_count tests - $failed_count failed"
            fi
        fi
        
        echo "=== $category FAILED (exit code: $exit_code, ${duration}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
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

# Function to run individual test with real-time feedback
run_individual_test() {
    local test_path=$1
    local test_name=$2
    local timeout_seconds=${3:-120}
    
    print_status $BLUE "🧪 Running: $test_name"
    echo "   📍 Test: $test_path"
    echo "   ⏱️  Timeout: ${timeout_seconds}s"
    echo ""
    
    local start_time=$(date +%s)
    local exit_code=0
    
    # Run single test with real-time output (no temp file - direct output)
    timeout ${timeout_seconds} docker exec autocusto-web-1 python manage.py test $test_path --keepdb --noinput --verbosity=2 || exit_code=$?
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        print_status $GREEN "✅ PASSED: $test_name (${duration}s)"
        echo "=== $test_name PASSED (${duration}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    elif [[ $exit_code -eq 124 ]]; then
        print_status $YELLOW "⏰ TIMEOUT: $test_name (${timeout_seconds}s)"
        echo "=== $test_name TIMEOUT (${timeout_seconds}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    else
        print_status $RED "❌ FAILED: $test_name (${duration}s, exit code: $exit_code)"
        echo "=== $test_name FAILED (exit code: $exit_code, ${duration}s) ===" >> "$CONSOLIDATED_ERROR_FILE"
        echo "" >> "$CONSOLIDATED_ERROR_FILE"
    fi
    
    echo ""
    echo "=================================================================================================="
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

print_status $BLUE "📍 PHASE 3: End-to-End Tests (Individual Real-Time)"
echo "=================================================="

print_status $BLUE "🎭 User Journey Tests (One-by-One with Real-Time Feedback)"
echo "=========================================================="

# Check if Playwright browser container is running first
if ! docker exec autocusto-playwright-browsers-1 echo "Browser container accessible" > /dev/null 2>&1; then
    print_status $YELLOW "   ⚠️  Playwright browser container not running - starting it..."
    if ! docker compose up -d playwright-browsers > /dev/null 2>&1; then
        print_status $RED "   ❌ Failed to start Playwright browser container"
        print_status $YELLOW "   Skipping browser-dependent tests"
    else
        print_status $GREEN "   ✅ Playwright browser container started"
        sleep 3  # Give browser container time to initialize
    fi
fi

# Individual E2E Test Classes with Real-Time Feedback (Reliable Approach)
print_status $BLUE "🎭 Process Registration Tests"
echo "============================="

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.user_journeys.test_process_registration.ProcessRegistrationWorkflowTest" "Process Registration Workflow" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "💊 Renovation & Renewal Tests"
echo "============================="

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.user_journeys.test_renovation_workflows.RenovationWorkflowTest" "Renovation Workflow Tests" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.user_journeys.test_quick_renewal.RenovacaoRapidaVersioningBugTest" "Quick Renewal Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "👤 User Journey Tests"
echo "===================="

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.user_journeys.test_setup_flow.PreProcessoSetupFlowTest" "Setup Flow Tests" 150; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.user_journeys.test_crm_cns_functionality.CRMCNSValidationTest" "CRM/CNS Validation Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "🌐 Browser Integration Tests"
echo "============================"

((TOTAL_CATEGORIES++))
if run_individual_test "tests.integration.forms.test_prescription_forms.PrescriptionFormTest.test_prescription_form_navigation" "Form Navigation Test" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))  
if run_individual_test "tests.integration.forms.test_prescription_forms.PrescriptionFormTest.test_prescription_form_basic_patient_data" "Basic Patient Data Entry Test" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_individual_test "tests.integration.services.test_pdf_workflows.PDFContentValidationTest.test_pdf_contains_patient_data" "PDF Content Validation Test" 180; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

print_status $BLUE "🔒 Security Tests"
echo "================="

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.security.test_security.PatientSearchSecurityTest" "Patient Search Security Tests" 90; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.security.test_security.ProcessAccessSecurityTest" "Process Access Security Tests" 120; then
    ((PASSED_CATEGORIES++))
else
    ((FAILED_CATEGORIES++))
fi

((TOTAL_CATEGORIES++))
if run_individual_test "tests.e2e.security.test_frontend_security.PatientAuthorizationTest" "Patient Authorization Tests" 120; then
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
echo "   Total Test Batches: $TOTAL_CATEGORIES"
echo "   ✅ Passed: $PASSED_CATEGORIES"
echo "   ❌ Failed: $FAILED_CATEGORIES" 
echo "   📊 Success Rate: ${success_rate}%"
echo ""

# Show breakdown by test phase
print_status $BLUE "📋 Test Phase Breakdown:"
echo "========================"
echo "   🚀 Phase 1 - Unit Tests: Fast feedback on individual components"
echo "   🔗 Phase 2 - Integration Tests: Component interaction validation"  
echo "   🎭 Phase 3 - E2E User Journeys: Complete workflow validation (one-by-one)"
echo "   🌐 Phase 4 - Browser Tests: Playwright PDF workflows (one-by-one)"
echo "   🔒 Phase 5 - Security Tests: Authentication & data access (one-by-one)"
echo ""

print_status $BLUE "⚡ Expert Testing Approach:"
echo "=========================="
echo "   ✅ E2E/Browser tests run ONE BY ONE with real-time feedback"
echo "   ✅ Each test gets full container resources and clean state"
echo "   ✅ Immediate results - see pass/fail as each test completes"
echo "   ✅ Better debugging - pinpoint exact failing tests instantly"
echo "   ✅ No batch timeout issues - each test properly isolated"
echo ""

# Show consolidated error file info
if [[ -f "$CONSOLIDATED_ERROR_FILE" ]]; then
    print_status $BLUE "📄 Consolidated Error Log:"
    echo "=========================="
    echo "   📁 File: $CONSOLIDATED_ERROR_FILE"
    
    # Show file size and line count for quick assessment
    file_size=$(wc -c < "$CONSOLIDATED_ERROR_FILE")
    line_count=$(wc -l < "$CONSOLIDATED_ERROR_FILE")
    
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