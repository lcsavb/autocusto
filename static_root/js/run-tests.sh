#!/bin/bash

# AutoCusto JavaScript Tests - CRITICAL MEDICATION VALIDATION LOGIC
# Tests the core med.js functionality without requiring browsers

echo "🧪 AutoCusto JavaScript Unit Tests"
echo "=================================="
echo ""
echo "🚨 CRITICAL: Testing medication validation logic (med.js)"
echo "   • Form submission prevention with no valid medications"
echo "   • Medication value validation logic"
echo "   • Field name attribute management"
echo "   • Integration with FormHandler"
echo ""

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run from the js directory."
    echo "   Expected location: /static/autocusto/js/"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    echo "   Node.js is required to run JavaScript unit tests"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH"
    echo "   npm is required to install test dependencies"
    exit 1
fi

echo "🔧 Installing test dependencies..."
npm install --quiet

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install npm dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

echo "🧪 Running JavaScript Unit Tests..."
echo "-----------------------------------"

# Run the tests with verbose output
npm test -- --verbose

TEST_EXIT_CODE=$?

echo ""
echo "📊 JavaScript Test Results Summary:"
echo "==================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All JavaScript unit tests passed!"
    echo ""
    echo "🎯 JavaScript Test Coverage:"
    echo "   - Medication validation logic: ✅ TESTED"
    echo "   - Form submission prevention: ✅ TESTED"
    echo "   - Field name management: ✅ TESTED"
    echo "   - Edge case handling: ✅ TESTED"
    echo "   - FormHandler integration: ✅ TESTED"
    echo ""
    echo "🚨 CRITICAL: Medical Safety Logic:"
    echo "   - Prevents invalid prescriptions: ✅ PROTECTED"
    echo "   - Allows valid prescriptions: ✅ VERIFIED"
    echo "   - Handles edge cases safely: ✅ ROBUST"
    echo ""
    echo "💡 To run specific test suites:"
    echo "   npm run test:med      # Run only medication tests"
    echo "   npm run test:coverage # Run with coverage report"
    echo "   npm run test:watch    # Run in watch mode"
else
    echo "❌ JavaScript unit tests failed!"
    echo ""
    echo "🚨 CRITICAL: JavaScript Test Status: ISSUES DETECTED"
    echo "   Please review the test output above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check that med.js logic hasn't been changed"
    echo "   - Verify jQuery mock is working correctly"
    echo "   - Ensure test cases match current med.js implementation"
    echo ""
    echo "💡 Debug commands:"
    echo "   npm test -- --verbose        # Detailed test output"
    echo "   npm test -- --detectOpenHandles # Debug hanging tests"
fi

echo ""
echo "🏥 MEDICAL SAFETY NOTE:"
echo "----------------------"
echo "These tests validate CRITICAL medication validation logic."
echo "Any test failures could indicate medical prescription safety issues."
echo "Do not deploy if tests are failing without thorough investigation."

echo ""
echo "Test completed with exit code: $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE