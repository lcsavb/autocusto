# AutoCusto Test Suite

This directory contains the centralized test suite for the AutoCusto application, organized by functionality rather than by Django app.

## Structure

```
tests/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── session_functionality/      # Tests for current session features
│   ├── __init__.py
│   ├── test_crm_cns_functionality.py
│   └── test_setup_flow.py
├── integration/                 # Cross-app integration tests
│   ├── __init__.py
│   ├── test_clinic_setup.py
│   └── test_process_setup.py
├── forms/                       # Form validation tests
│   ├── __init__.py
│   └── test_medico_forms.py
├── views/                       # View logic tests
│   ├── __init__.py
│   └── test_medico_views.py
└── utils/                       # Test utilities and runners
    ├── __init__.py
    └── test_runners.py
```

## Test Categories

### Session Functionality Tests
- CRM/CNS confirmation and immutability
- Setup flow with session preservation
- Form improvements and validation
- Navigation and UI enhancements

### Integration Tests
Cross-app integration tests covering:
- Setup flow redirects and session preservation
- Multi-step workflow completion
- User experience continuity

### Form Tests
Form validation and behavior tests:
- Field validation and error handling
- Confirmation field logic
- Immutability enforcement
- Data persistence

### View Tests
View logic and response tests:
- Authentication requirements
- Request/response handling
- Redirect logic
- Message framework integration

## Running Tests

### Run All Tests
```bash
# Run all centralized tests
python manage.py test tests

# Or using the test runner utility
python tests/utils/test_runners.py all
```

### Run by Category
```bash
# Session functionality tests only
python manage.py test tests.session_functionality
python tests/utils/test_runners.py session

# Integration tests only
python manage.py test tests.integration
python tests/utils/test_runners.py integration

# Form tests only
python manage.py test tests.forms
python tests/utils/test_runners.py forms

# View tests only
python manage.py test tests.views
python tests/utils/test_runners.py views
```

### Run Specific Test Files
```bash
# Run specific test file
python manage.py test tests.session_functionality.test_crm_cns_functionality

# Run specific test class
python manage.py test tests.session_functionality.test_crm_cns_functionality.CRMCNSConfirmationTest

# Run specific test method
python manage.py test tests.session_functionality.test_crm_cns_functionality.CRMCNSConfirmationTest.test_crm_confirmation_validation
```

## Test Configuration

The tests use the `test_settings.py` configuration which:
- Uses an in-memory SQLite database for speed
- Disables migrations for faster test setup
- Configures logging for test debugging
- Sets up test-specific middleware

## Test Utilities

The `utils/` directory provides:
- Custom test runners for different test categories
- Helper functions for running specific test suites
- Common test fixtures and utilities (can be extended)

## Docker Testing

To run tests in Docker containers:
```bash
# Run all tests in Docker
docker-compose exec web python manage.py test tests

# Run specific test category in Docker
docker-compose exec web python manage.py test tests.session_functionality
```

## Coverage

To run tests with coverage reporting:
```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test tests
coverage report
coverage html  # Generate HTML coverage report
```

## Test Organization Benefits

1. **Functionality-based**: Tests are organized by what they test, not where the code lives
2. **Easier maintenance**: Related tests are grouped together
3. **Better discoverability**: Clear structure makes finding relevant tests easier
4. **Reduced duplication**: Common test utilities are centralized
5. **Flexible execution**: Can run tests by category or functionality
6. **Clear separation**: Session-specific tests are clearly identified

## Adding New Tests

When adding new tests:
1. Determine the appropriate category (session_functionality, integration, forms, views)
2. Add tests to the relevant directory
3. Follow existing naming conventions
4. Update test runners if needed for new categories
5. Document any new test utilities or patterns


