#!/bin/bash

# Clinic Management Testing Script using Selenium
# Tests clinic creation and editing workflows

echo "🏥 AutoCusto Clinic Management Test Suite"
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
echo "🧪 Running Clinic Management Tests..."
echo "-----------------------------------"

# Run clinic management tests with detailed output
python manage.py test tests.test_clinic_management --settings=test_settings --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "📊 Clinic Management Test Results Summary:"
echo "========================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All clinic management tests passed!"
    echo ""
    echo "🎯 Clinic Management Test Coverage:"
    echo "   - Clinic creation (new): ✅ WORKING"
    echo "   - Clinic updates (existing CNS): ✅ WORKING"
    echo "   - Form validation: ✅ WORKING"
    echo "   - Navigation workflow: ✅ WORKING"
    echo "   - User association: ✅ WORKING"
    echo "   - CNS duplicate prevention: ✅ WORKING"
    echo ""
    echo "📸 Screenshots saved in: tests/screenshots/"
else
    echo "❌ Clinic management tests failed!"
    echo ""
    echo "🚨 Clinic Management Test Status: ISSUES DETECTED"
    echo "   Please review the test output above and screenshots."
    echo ""
    echo "📸 Debug screenshots available in: tests/screenshots/"
fi

echo ""
echo "🔍 Clinic Management Testing Notes:"
echo "----------------------------------"
echo "   - Tests run in headless Chrome browser"
echo "   - Screenshots taken at each major step"
echo "   - Character-by-character form filling simulates real usage"
echo "   - Tests cover complete clinic CRUD operations"
echo "   - Database verification ensures data integrity"

echo ""
echo "💡 To run specific clinic test methods:"
echo "   python manage.py test tests.test_clinic_management.ClinicManagementTest.test_clinic_creation_new_clinic --settings=test_settings"
echo "   python manage.py test tests.test_clinic_management.ClinicManagementTest.test_clinic_creation_update_existing --settings=test_settings"

echo ""
echo "📝 To view screenshots after test run:"
echo "   ls -la tests/screenshots/"
echo "   # Open screenshots with your preferred image viewer"

echo ""
echo "🔧 Troubleshooting:"
echo "   - If tests fail, check screenshots for visual debugging"
echo "   - Ensure test data is properly set up in database"
echo "   - Verify clinic form URLs are accessible"
echo "   - Check for JavaScript errors affecting form submission"

exit $TEST_EXIT_CODE