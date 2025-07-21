#!/bin/bash

# Frontend Security Testing Script using Selenium
# Tests actual browser interactions to verify security fixes

echo "🌐 AutoCusto Frontend Security Test Suite"
echo "========================================"
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

# Check if Chrome is installed
echo "🔧 Checking Chrome installation..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "⚠️  Chrome/Chromium not found. Installing Chromium..."
    
    if [[ "$ENVIRONMENT" == "container" ]]; then
        # Inside container - try without sudo
        echo "   Installing in container..."
        apt-get update && apt-get install -y chromium-browser 2>/dev/null || echo "   ⚠️  Could not install (permission denied)"
    else
        # Local environment - use sudo
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y chromium-browser
        elif command -v yum &> /dev/null; then
            sudo yum install -y chromium
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y chromium
        else
            echo "❌ Could not install Chrome/Chromium automatically."
            echo "   Please install Chrome or Chromium manually and run again."
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
echo "🧪 Running Frontend Security Tests..."
echo "------------------------------------"

# Run frontend tests with settings
python manage.py test tests.test_frontend_security --settings=test_settings --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "📊 Frontend Test Results Summary:"
echo "================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All frontend security tests passed!"
    echo ""
    echo "🛡️  Frontend Security Status: SECURE"
    echo "   - Login/logout flow security: ✅ WORKING"
    echo "   - Patient access authorization: ✅ WORKING"
    echo "   - Patient search filtering: ✅ WORKING"
    echo "   - Cross-user session isolation: ✅ WORKING"
    echo "   - Invalid login rejection: ✅ WORKING"
    echo "   - Unauthenticated access blocking: ✅ WORKING"
else
    echo "❌ Frontend security tests failed!"
    echo ""
    echo "🚨 Frontend Security Status: VULNERABLE"
    echo "   Please review the test output above and fix failing tests."
fi

echo ""
echo "🔍 Frontend Testing Notes:"
echo "-------------------------"
echo "   - Tests run in headless Chrome browser"
echo "   - Real browser interactions verify security"
echo "   - Tests complement backend unit tests"
echo "   - Use --verbosity=0 for quieter output"

echo ""
echo "💡 To run specific frontend test methods:"
echo "   python manage.py test tests.test_frontend_security.FrontendSecurityTest.test_patient_cpf_access_authorization --settings=test_settings"
echo "   python manage.py test tests.test_frontend_security.FrontendSecurityTest.test_login_logout_flow --settings=test_settings"

echo ""
echo "📝 To add to CI/CD pipeline:"
echo "   ./run_frontend_tests.sh"

exit $TEST_EXIT_CODE