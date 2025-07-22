# 🧪 AutoCusto Testing Guide

Quick reference for running tests manually and integrating with deployment.

## 🚀 Quick Start

### Option 1: Master Test Script (Recommended)
```bash
# Run all tests with comprehensive reporting
./tests/run_all_tests.sh
```

### Option 2: Make Commands (Easy)
```bash
# Check what's available
make -f Makefile.tests help

# Run backend tests only (fastest)
make -f Makefile.tests test-backend

# Run all tests
make -f Makefile.tests test-all

# Check environment
make -f Makefile.tests check-env
```

### Option 3: Docker Commands (Consistent Environment)
```bash
# Run all tests in Docker
make -f Makefile.tests test-docker

# Or directly
docker-compose exec web ./tests/run_all_tests.sh
```

## 📋 Test Categories

| Command | Description | Speed | Environment |
|---------|-------------|-------|-------------|
| `make -f Makefile.tests test-backend` | Backend tests only | ⚡ Fast | Any |
| `make -f Makefile.tests test-frontend` | Selenium/UI tests | 🐌 Slow | Chrome required |
| `make -f Makefile.tests test-auth` | Authentication tests | ⚡ Fast | Any |
| `make -f Makefile.tests test-security` | Security tests | ⚡ Fast | Any |
| `make -f Makefile.tests test-forms` | Form validation | ⚡ Fast | Any |
| `make -f Makefile.tests test-coverage` | With coverage report | 🐌 Slow | Any |

## 🐳 Docker Testing

### Prerequisites
```bash
# Start containers
docker-compose up -d

# Check status
docker-compose ps
```

### Running Tests
```bash
# All tests in Docker
docker-compose exec web ./tests/run_all_tests.sh

# Specific categories
docker-compose exec web python manage.py test tests.test_authentication --settings=test_settings

# Backend tests only (no Chrome needed)
docker-compose exec web python manage.py test tests.forms tests.test_authentication tests.test_security --settings=test_settings
```

## 🏃‍♂️ Quick Development Testing

### During Development
```bash
# Super fast - just auth backend
make -f Makefile.tests test-quick

# Medium speed - all backend
make -f Makefile.tests test-backend

# Full test suite
make -f Makefile.tests test-all
```

### Debugging Failed Tests
```bash
# Run with verbose output
docker-compose exec web python manage.py test tests.test_authentication --settings=test_settings --verbosity=2

# Run single test class
docker-compose exec web python manage.py test tests.test_authentication.AuthenticationBackendTest --settings=test_settings

# Run single test method
docker-compose exec web python manage.py test tests.test_authentication.AuthenticationBackendTest.test_user_creation_with_email --settings=test_settings
```

## 🌐 Frontend/Selenium Testing

### Requirements
```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser
# or
sudo apt-get install google-chrome-stable

# Install dependencies
make -f Makefile.tests install-deps
```

### Running Frontend Tests
```bash
# All frontend tests
make -f Makefile.tests test-frontend

# Specific frontend tests
docker-compose exec web python manage.py test tests.test_login_frontend --settings=test_settings
docker-compose exec web python manage.py test tests.test_user_registration --settings=test_settings
```

### Screenshots
When Selenium tests fail, screenshots are saved to:
- `tests/screenshots/`
- `test_screenshots/`

## 📊 Coverage Analysis

### Generate Coverage Report
```bash
# With make
make -f Makefile.tests test-coverage

# Manually
coverage run --source='.' manage.py test tests.forms tests.test_authentication tests.test_security --settings=test_settings
coverage report
coverage html
```

View HTML report: `open htmlcov/index.html`

## 🚀 Deployment Integration

### GitHub Actions
The repository includes two GitHub Actions workflows:

1. **`.github/workflows/test-integration.yml`** - Comprehensive test suite
   - Backend tests with PostgreSQL
   - Frontend tests with Chrome
   - Security analysis
   - Docker integration testing

2. **`.github/workflows/deploy.yml`** - Production deployment
   - Currently tests are disabled (line 55-56)
   - Re-enable after fixing failing tests

### Enable Tests in CI/CD
Edit `.github/workflows/deploy.yml`:
```yaml
# Line 54-56: Change from:
run: |
  echo "Skipping tests temporarily - fix test failures first"
  # python manage.py test

# To:
run: |
  python manage.py test tests.forms tests.test_authentication tests.test_security --settings=test_settings
```

### Manual Deployment Testing
```bash
# Test deployment readiness locally
./tests/run_all_tests.sh

# If exit code is 0, deployment is ready
echo $?
```

## 🛠️ Environment Setup

### Check Your Environment
```bash
make -f Makefile.tests check-env
```

### Install Dependencies
```bash
make -f Makefile.tests install-deps
```

### Clean Test Artifacts
```bash
make -f Makefile.tests clean
```

## 🔧 Troubleshooting

### Common Issues

1. **Chrome not found (Selenium tests)**
   ```bash
   # Install Chrome/Chromium
   sudo apt-get update && sudo apt-get install chromium-browser
   ```

2. **No module named 'django'**
   ```bash
   # Activate virtual environment or use Docker
   source venv/bin/activate
   # or
   make -f Makefile.tests test-docker
   ```

3. **Database connection errors**
   ```bash
   # Make sure Docker containers are running
   docker-compose ps
   docker-compose up -d
   ```

4. **Permission errors**
   ```bash
   # Make scripts executable
   chmod +x tests/run_all_tests.sh
   chmod +x tests/run_*.sh
   ```

### Test Status Summary

Current test status:
- ✅ **Authentication tests**: Backend logic working
- ✅ **Security tests**: Most security measures working  
- ⚠️ **Form tests**: Some initialization issues
- ⚠️ **Integration tests**: Some database setup issues
- ❌ **Frontend tests**: Chrome/Selenium setup needed

### Quick Status Check
```bash
# Check which tests are failing
./tests/run_all_tests.sh 2>&1 | grep -E "(FAIL|ERROR|passed|failed)"
```

## 📚 Additional Resources

- **Test Documentation**: `tests/CLAUDE.md`
- **Security Testing**: `tests/run_security_tests.sh` 
- **Frontend Testing**: `tests/run_frontend_tests.sh`
- **Clinic Testing**: `tests/run_clinic_tests.sh`
- **Prescription Testing**: `tests/run_prescription_tests.sh`

## 🎯 Recommended Workflow

### For Development
1. `make -f Makefile.tests test-quick` - Before committing
2. `make -f Makefile.tests test-backend` - Before pushing
3. `make -f Makefile.tests test-all` - Before deployment

### For CI/CD
1. Use GitHub Actions for automated testing
2. Require tests to pass before merging PRs
3. Run full test suite before deployment

### For Production Deployment
1. Run `./tests/run_all_tests.sh`
2. Check exit code is 0
3. Deploy if tests pass

---

🎉 **Happy Testing!** The comprehensive test suite ensures AutoCusto's reliability for healthcare applications.