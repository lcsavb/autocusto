#!/bin/bash
# Debug script to run Playwright tests with proper output

echo "=== DEBUG: Starting Playwright test runner ==="
echo "Environment variables:"
echo "  CI: ${CI}"
echo "  PW_TEST_CONNECT_WS_ENDPOINT: ${PW_TEST_CONNECT_WS_ENDPOINT}"
echo "  DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE}"

# Force unbuffered Python output
export PYTHONUNBUFFERED=1

# Run a single test with verbose output
echo ""
echo "=== Running fixed Playwright test ==="
python manage.py test tests.integration.forms.test_prescription_forms_fixed.PrescriptionFormTestFixed.test_simple_navigation \
    --settings=test_settings \
    --verbosity=3 \
    --keepdb --noinput 2>&1

echo ""
echo "=== Test completed ==="