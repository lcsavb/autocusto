#!/bin/bash

# Prescription Form Testing Script using Selenium
# Tests complex prescription form workflows and functionality

echo "💊 AutoCusto Prescription Form Test Suite"
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

# Create screenshots directory
echo "📸 Setting up screenshots directory..."
mkdir -p tests/screenshots

echo ""
echo "🧪 Running Prescription Form Tests..."
echo "-----------------------------------"
echo ""
echo "🚨 CRITICAL: Testing med.js medication management logic"
echo "   • Add/remove medication functionality"
echo "   • 'Nenhum' selection validation" 
echo "   • Form submission prevention with no valid medications"
echo ""

# Run prescription form tests with detailed output
python manage.py test tests.test_prescription_forms --settings=test_settings --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "📊 Prescription Test Results Summary:"
echo "===================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All prescription form tests passed!"
    echo ""
    echo "🎯 Prescription Form Test Coverage:"
    echo "   - Form navigation workflow: ✅ WORKING"
    echo "   - Basic patient data filling: ✅ WORKING"
    echo "   - Medication section functionality: ✅ WORKING"
    echo "   - Clinical data entry: ✅ WORKING"
    echo "   - Complete form workflow: ✅ WORKING"
    echo "   - Form validation errors: ✅ WORKING"
    echo ""
    echo "🚨 CRITICAL: Medication Management (med.js) Tests:"
    echo "   - Add/remove medication tabs: ✅ WORKING"
    echo "   - 'Nenhum' selection field clearing: ✅ WORKING"
    echo "   - Form submission validation: ✅ WORKING"
    echo "   - Medical prescription safety: ✅ PROTECTED"
    echo ""
    echo "📸 Screenshots saved in: tests/screenshots/"
else
    echo "❌ Prescription form tests failed!"
    echo ""
    echo "🚨 Prescription Form Test Status: ISSUES DETECTED"
    echo "   Please review the test output above and screenshots."
    echo ""
    echo "📸 Debug screenshots available in: tests/screenshots/"
fi

echo ""
echo "🔍 Prescription Testing Notes:"
echo "-----------------------------"
echo "   - Tests run in headless Chrome browser"
echo "   - Screenshots taken at each major step"
echo "   - Character-by-character form filling simulates real usage"
echo "   - Tests cover complete prescription workflow"

echo ""
echo "💡 To run specific prescription test methods:"
echo "   python manage.py test tests.test_prescription_forms.PrescriptionFormTest.test_prescription_form_navigation --settings=test_settings"
echo "   python manage.py test tests.test_prescription_forms.PrescriptionFormTest.test_prescription_form_complete_workflow --settings=test_settings"

echo ""
echo "📝 To view screenshots after test run:"
echo "   ls -la tests/screenshots/"
echo "   # Open screenshots with your preferred image viewer"

echo ""
echo "🔧 Troubleshooting:"
echo "   - If tests fail, check screenshots for visual debugging"
echo "   - Ensure test data is properly set up in database"
echo "   - Verify prescription form URLs are accessible"

exit $TEST_EXIT_CODE