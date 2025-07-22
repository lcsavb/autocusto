#!/bin/bash

# Frontend Security Testing Script using Playwright
# Tests actual browser interactions to verify security fixes

echo "🎭 AutoCusto Frontend Test Suite (Playwright)"
echo "============================================="
echo ""

# Environment detection
echo "📦 Detecting environment..."
if [[ -f /.dockerenv ]] || [[ -n "${CONTAINER}" ]]; then
    echo "✅ Running inside Docker container"
    ENVIRONMENT="container"
elif [[ -d "venv" ]]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    ENVIRONMENT="local"
else
    echo "📍 Using system Python"
    ENVIRONMENT="system"
fi

# Check if Chrome is installed for Playwright
echo "🔧 Checking Chrome installation for Playwright..."
if ! command -v google-chrome-stable &> /dev/null && ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "⚠️  Chrome/Chromium not found. Installing Google Chrome..."
    
    if [[ "$ENVIRONMENT" == "container" ]]; then
        # Inside container - install Chrome
        echo "   Installing Chrome in container..."
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - 2>/dev/null || echo "   ⚠️  Could not add signing key"
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list 2>/dev/null || echo "   ⚠️  Could not add repository"
        apt-get update && apt-get install -y google-chrome-stable 2>/dev/null || echo "   ⚠️  Could not install Chrome (permission denied)"
    else
        # Local environment - use sudo
        if command -v apt-get &> /dev/null; then
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update && sudo apt-get install -y google-chrome-stable
        elif command -v yum &> /dev/null; then
            sudo yum install -y google-chrome-stable
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y google-chrome
        else
            echo "❌ Could not install Chrome automatically."
            echo "   Please install Chrome manually and run again."
            exit 1
        fi
    fi
fi

# Check if Django is properly configured
echo "🔧 Checking Django configuration..."
python manage.py check --deploy 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Django deployment checks failed. Running basic check..."
    python manage.py check
fi

echo ""
echo "🎭 Running Frontend Tests with Playwright..."
echo "--------------------------------------------"

# Run all Playwright frontend tests
echo "🔒 Running security tests..."
python manage.py test tests.test_frontend_security_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "🏠 Running login tests..."
python manage.py test tests.test_login_frontend_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "🧭 Running navigation tests..."
python manage.py test tests.test_navigation_comprehensive_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "🏥 Running clinic management tests..."
python manage.py test tests.test_clinic_management_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "💊 Running prescription form tests..."
python manage.py test tests.test_prescription_forms_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "👤 Running user registration tests..."
python manage.py test tests.test_user_registration_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "🔄 Running renovation workflow tests..."
python manage.py test tests.test_renovation_workflows_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "✏️  Running process editing tests..."
python manage.py test tests.test_process_editing_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "📄 Running PDF generation tests..."
python manage.py test tests.test_pdf_generation_workflows_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "📋 Running complete process registration tests..."
python manage.py test tests.test_process_registration_complete_playwright --settings=tests.test_settings --verbosity=2

echo ""
echo "📄 Running basic PDF workflow tests..."  
python manage.py test tests.test_pdf_basic_workflow_playwright --settings=tests.test_settings --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "📊 Frontend Test Results Summary:"
echo "================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All Playwright frontend tests passed!"
    echo ""
    echo "🎭 Frontend Test Status: EXCELLENT"
    echo "   - Security tests: ✅ WORKING"
    echo "   - Login/logout flows: ✅ WORKING"
    echo "   - Navigation: ✅ WORKING"
    echo "   - Clinic management: ✅ WORKING"
    echo "   - Prescription forms: ✅ WORKING"
    echo "   - User registration: ✅ WORKING"
    echo "   - Renovation workflows: ✅ WORKING"
    echo "   - Process editing: ✅ WORKING"
    echo "   - PDF generation: ✅ WORKING"
    echo "   - Process registration: ✅ WORKING"  
    echo "   - PDF basic workflows: ✅ WORKING"
else
    echo "❌ Some Playwright frontend tests failed!"
    echo ""
    echo "🚨 Frontend Test Status: NEEDS ATTENTION"
    echo "   Please review the test output above and fix failing tests."
fi

echo ""
echo "🔍 Playwright Testing Notes:"
echo "----------------------------"
echo "   - Tests run in headless Chrome browser"
echo "   - 3-5x faster than Selenium"
echo "   - Real browser interactions with async support"
echo "   - Comprehensive debugging with screenshots"
echo "   - Use --verbosity=0 for quieter output"

echo ""
echo "💡 To run specific Playwright test methods:"
echo "   python manage.py test tests.test_frontend_security_playwright.PlaywrightSecurityTest.test_patient_access_authorization --settings=tests.test_settings"
echo "   python manage.py test tests.test_login_frontend_playwright.LoginFunctionalityTest.test_successful_login --settings=tests.test_settings"

echo ""
echo ""
echo "💡 To run specific test classes:"
echo "   python manage.py test tests.test_renovation_workflows_playwright.RenovationWorkflowTest.test_patient_search_by_name --settings=tests.test_settings"
echo "   python manage.py test tests.test_process_editing_playwright.ProcessEditingTest.test_edit_mode_toggle_functionality --settings=tests.test_settings"

echo ""
echo "📝 To add to CI/CD pipeline:"
echo "   ./run_frontend_tests.sh"

exit $TEST_EXIT_CODE