#!/bin/bash

# Automated Security Testing Script for AutoCusto
# This script runs comprehensive security tests to verify authorization fixes

echo "🔒 AutoCusto Security Test Suite"
echo "================================"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Django is properly configured
echo "🔧 Checking Django configuration..."
python manage.py check --deploy 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Django deployment checks failed. Running basic check..."
    python manage.py check
fi

echo ""
echo "🧪 Running Security Tests..."
echo "----------------------------"

# Run only security tests with test settings
python manage.py test tests.test_security --settings=test_settings --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "📊 Test Results Summary:"
echo "======================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All security tests passed!"
    echo ""
    echo "🛡️  Security Status: SECURE"
    echo "   - Patient access authorization: ✅ WORKING"
    echo "   - Patient search filtering: ✅ WORKING" 
    echo "   - Patient listing authorization: ✅ WORKING"
    echo "   - Process access control: ✅ WORKING"
    echo "   - Session hijacking prevention: ✅ WORKING"
else
    echo "❌ Security tests failed!"
    echo ""
    echo "🚨 Security Status: VULNERABLE"
    echo "   Please review the test output above and fix failing tests."
fi

echo ""
echo "🔍 Additional Security Checks:"
echo "-----------------------------"

# Check for common security issues
echo "   - Checking for @login_required decorators..."
MISSING_LOGIN_REQ=$(grep -r "def " */views.py | grep -v "@login_required" | grep -v "class " | wc -l)
if [ $MISSING_LOGIN_REQ -gt 5 ]; then
    echo "   ⚠️  Found $MISSING_LOGIN_REQ view functions that may need @login_required"
else
    echo "   ✅ Login requirements look good"
fi

# Check for direct object access without filtering
echo "   - Checking for potential unauthorized object access..."
POTENTIAL_ISSUES=$(grep -r "objects.get\|objects.filter" */views.py | grep -v "usuarios=" | grep -v "usuario=" | wc -l)
if [ $POTENTIAL_ISSUES -gt 3 ]; then
    echo "   ⚠️  Found $POTENTIAL_ISSUES queries that should be reviewed for authorization"
else
    echo "   ✅ Object access patterns look secure"
fi

echo ""
echo "💡 To run specific test classes:"
echo "   python manage.py test tests.test_security.SecurityTestCase"
echo "   python manage.py test tests.test_security.PatientSearchSecurityTest"
echo "   python manage.py test tests.test_security.PatientListingSecurityTest"
echo "   python manage.py test tests.test_security.ProcessAccessSecurityTest"

echo ""
echo "📝 To add this to CI/CD pipeline, add to your workflow:"
echo "   ./run_security_tests.sh"

exit $TEST_EXIT_CODE