#!/bin/bash

# Prescription Form Testing Script using Selenium
# Tests complex prescription form workflows and functionality

echo "💊 AutoCusto Prescription Form Test Suite"
echo "========================================"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Chrome is installed
echo "🔧 Checking Chrome installation..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "⚠️  Chrome/Chromium not found. Installing Chromium..."
    
    # Try to install Chromium (works on most Linux systems)
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

# Create screenshots directory
echo "📸 Setting up screenshots directory..."
mkdir -p tests/screenshots

echo ""
echo "🧪 Running Prescription Form Tests..."
echo "-----------------------------------"

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