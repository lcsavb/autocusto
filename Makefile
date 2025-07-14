# AutoCusto Testing Makefile

.PHONY: help test test-security test-frontend test-all test-coverage clean

help:
	@echo "AutoCusto Testing Commands:"
	@echo ""
	@echo "  make test-security    Run backend security tests only"
	@echo "  make test-frontend    Run frontend security tests with Selenium"
	@echo "  make test-all         Run all tests (backend + frontend)"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make clean           Clean test artifacts"
	@echo ""

# Run security tests only
test-security:
	@echo "Running backend security tests..."
	./run_security_tests.sh

# Run frontend tests with Selenium
test-frontend:
	@echo "Running frontend security tests..."
	./run_frontend_tests.sh

# Run all tests
test-all:
	@echo "Running all tests..."
	@echo "Backend tests:"
	./run_security_tests.sh
	@echo ""
	@echo "Frontend tests:"
	./run_frontend_tests.sh

# Run tests with coverage (install coverage first: pip install coverage)
test-coverage:
	@echo "Running tests with coverage..."
	source venv/bin/activate && \
	pip install coverage >/dev/null 2>&1 && \
	coverage run --source='.' manage.py test && \
	coverage report && \
	coverage html

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -f .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Quick security check (for development)
quick-security:
	@echo "Quick security check..."
	source venv/bin/activate && python manage.py test tests.test_security --failfast