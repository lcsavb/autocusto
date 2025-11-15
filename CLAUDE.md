# AutoCusto Project - Claude Code Instructions

## Project Overview

**AutoCusto** is a medical prescription automation system for Brazil's SUS (Sistema Único de Saúde) healthcare system. It automates complex bureaucratic forms for high-cost medication prescriptions, particularly focusing on neurological disorders. The system has served 400+ unique patients over 3 years, significantly reducing errors and patient wait times.

## Technology Stack

### Core Framework
- **Django 5.2.8 LTS** - Python web framework (updated Nov 2025 for security fixes)
- **Python 3.11** - Running in Debian Bookworm containers
- **PostgreSQL 17.4** - Production database
- **SQLite** - In-memory testing database

### Key Libraries
- **django-crispy-forms** + crispy-bootstrap4 - Form rendering
- **pypdftk** - PDF manipulation for medical forms
- **uwsgi** - Application server (4 processes, 2 threads each)
- **whitenoise** - Static file serving
- **django-crontab** - Scheduled tasks
- **django-dbbackup** - Automated database backups
- **psutil** - System resource monitoring

### Testing Stack
- **pytest** + pytest-django - Test framework
- **playwright** 1.40.0 - Browser automation (E2E tests)
- **cpf-generator** - Brazilian CPF generation for tests
- Containerized Playwright architecture with separate browser container

### Frontend
- **Bootstrap 4** - CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- Vanilla JavaScript for custom interactions

## Container Infrastructure

**CRITICAL**: The application runs entirely in Docker containers. Always use `docker exec` to run commands:

```bash
# Run Django management commands
docker exec autocusto-web-1 python manage.py <command>

# Run tests
docker exec autocusto-web-1 pytest tests/

# Access Django shell
docker exec -it autocusto-web-1 python manage.py shell

# Access database
docker exec -it autocusto-db-1 psql -U postgres -d defaultdb
```

**Container Services:**
- `autocusto-web-1` - Django application (test stage in development)
- `autocusto-db-1` - PostgreSQL database
- `autocusto-playwright-browsers-1` - Chromium browser for E2E tests

**Memory Mounts:**
- `/dev/shm` - PDF templates are copied here on startup (200MB tmpfs)
- `/tmp` - Temporary files (200MB tmpfs)

## Project Structure (Django Apps)

### Core Applications

1. **processos** - Medical prescription workflows (CORE BUSINESS LOGIC)
   - Central app managing medical processes, diseases (CID codes), medications, protocols
   - Contains repository pattern, service layer, and domain logic
   - PDF generation strategies for various medical forms

2. **medicos** - Doctor management
   - CRM (medical license) and CNS registration
   - Medical specialties (60+ Brazilian specialties)

3. **pacientes** - Patient management with versioning
   - Sophisticated versioning system for multi-user scenarios
   - CPF validation, CNS validation
   - User-specific patient data views

4. **clinicas** - Clinic management with versioning
   - Creates Emissor (doctor-clinic combinations)
   - User-specific clinic data views
   - CEP (Brazilian postal code) handling

5. **usuarios** - Custom user authentication
   - Email-based authentication (no username)
   - Custom User model extending AbstractBaseUser
   - AUTH_USER_MODEL: `usuarios.Usuario`

6. **analytics** - System metrics and monitoring
   - PDF generation tracking
   - User activity logging
   - Daily metrics calculation
   - System health monitoring (every 15 minutes)

## Architectural Patterns

### Repository Pattern
Location: `/processos/repositories/`

**Purpose**: Data access abstraction layer separating business logic from database operations.

Files:
- `domain_repository.py` - Disease/clinic lookups
- `medication_repository.py` - Medication queries
- `patient_repository.py` - Patient data access
- `process_repository.py` - Process CRUD operations

**When to use**: Always access data through repositories in services, not directly through Django ORM in views.

### Service Layer
Location: `/processos/services/`

**Purpose**: Encapsulate business logic, coordinate between repositories and domain objects.

Key files:
- `view_services.py` - View setup and context preparation
- `pdf_operations.py` - PDF generation services
- `pdf_strategies.py` - Strategy pattern for different PDF types
- `prescription_services.py` - Prescription workflow orchestration
- `README.md` - Detailed service architecture documentation

**When to use**: All business logic should be in services. Views should be thin and delegate to services.

### Domain-Driven Design
Location: `/processos/domain/`

**Purpose**: Domain models and business rules separated from infrastructure.

Pattern:
- Domain models represent business concepts
- Forms use factories for complex creation logic
- Clear separation between domain logic and infrastructure

### Data Versioning System

**CRITICAL PATTERN**: Patients and clinics use a versioning system for multi-user scenarios.

Models:
- `PacienteVersion` - Tracks patient data changes per user
- `ClinicaVersion` - Tracks clinic data changes per user
- `PacienteUsuarioVersion` - Links users to specific patient versions
- `ClinicaUsuarioVersion` - Links users to specific clinic versions

**Why**: Enables multiple users to maintain their own view of shared data while preserving privacy and data integrity in a medical context.

**Impact**: When working with patients or clinics, always consider the versioning implications.

## Domain-Specific Concepts (Brazilian Healthcare)

### Medical Entities

1. **Doenca** - Disease with CID codes (ICD-10 classification)
2. **Protocolo** - Treatment protocols with conditional data (stored as JSON)
3. **Medicamento** - Approved medications with dosage/presentation info
4. **Processo** - Complete prescription workflow linking patient + doctor + clinic + disease + medications
5. **Emissor** - Doctor-clinic combination authorized to issue prescriptions

### Brazilian-Specific Features

- **CPF**: Brazilian taxpayer ID (11 digits with validation algorithm)
- **CRM**: Medical license number (state-specific)
- **CNS**: National health card number
- **CEP**: Brazilian postal code
- **CID**: Brazilian ICD-10 classification codes
- **27 States + Federal District**: Use `ESTADO_CHOICES` in models
- **60+ Medical Specialties**: Use `ESPECIALIDADE_CHOICES` in medicos app

### Business Rules

1. **Unique constraint**: One process per user-patient-disease combination
2. **Doctor-clinic relationship**: Many-to-many through Emissor model
3. **Versioned data**: Patients/clinics have user-specific views
4. **Audit preservation**: Foreign keys use SET_NULL to preserve audit trails

### PDF Generation Workflow

1. Template-based PDF filling using pdftk
2. Memory-mounted templates in `/dev/shm` for performance
3. Multiple PDF types: LME forms, prescriptions, medical reports, exam requests
4. Caching system for immediate serving (5-minute TTL)
5. Comprehensive logging via analytics app

Location: `/static/autocusto/processos/` - PDF templates (medical forms)

## Testing Guidelines

### Test Organization (Test Pyramid)

```
tests/
├── unit/               # Fast, isolated tests (models, services, repositories, utils)
├── integration/        # Component interaction tests (database, API, forms, services)
├── e2e/               # End-to-end user journeys
│   ├── user_journeys/
│   ├── browser/       # Playwright browser automation
│   └── security/
├── conftest.py        # Pytest configuration
├── playwright_base.py # Browser test base classes
└── container_utils.py # Docker container helpers
```

### Test Execution

**From host machine:**
```bash
# Run all tests (orchestrated)
./run_tests_from_host.sh

# Run frontend/E2E tests only
./run_frontend_tests.sh

# Run specific test file
docker exec autocusto-web-1 pytest tests/unit/models/test_patient.py -v

# Run with coverage
docker exec autocusto-web-1 pytest --cov=processos tests/
```

### Test Markers

Use pytest markers to categorize tests:
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.frontend` - Frontend/browser tests
- `@pytest.mark.security` - Security tests

### Test Settings

- `test_settings.py` - Overrides production settings
- SQLite in-memory database for speed
- Faster password hashing (MD5PasswordHasher)
- Analytics disabled in tests
- Shared memory database for parallel tests

### Playwright E2E Tests

**Architecture:**
- Separate `playwright-browsers` container running Chromium
- CDP (Chrome DevTools Protocol) on port 9222
- Xvfb virtual display for headless operation

**Base URL**: `http://web:8001` (container network)

**Example:**
```python
from tests.playwright_base import PlaywrightTestCase

class TestLoginFlow(PlaywrightTestCase):
    def test_login_page_loads(self):
        self.page.goto(f"{self.base_url}/login/")
        assert self.page.title() == "Login - AutoCusto"
```

## Development Workflow

### Running the Application

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f web

# Restart web service
docker compose restart web

# Stop all services
docker compose down
```

### Database Management

```bash
# Run migrations
docker exec autocusto-web-1 python manage.py migrate

# Create migrations
docker exec autocusto-web-1 python manage.py makemigrations

# Access database shell
docker exec -it autocusto-db-1 psql -U postgres -d defaultdb

# Load fixtures
docker exec autocusto-web-1 python manage.py loaddata fixtures/initial_data.json
```

### Collecting Static Files

```bash
docker exec autocusto-web-1 python manage.py collectstatic --noinput
```

### Creating Superuser

```bash
docker exec -it autocusto-web-1 python manage.py createsuperuser
```

### Scheduled Tasks (Cron Jobs)

Managed via django-crontab:
- `0 3 * * *` - Cleanup old PDFs
- `0 2 * * *` - Database backup
- `15 2 * * *` - Upload backup to cloud storage
- `30 1 * * *` - Calculate daily metrics
- `*/15 * * * *` - System health metrics collection
- `0 4 * * *` - Health metrics cleanup

**Manage cron jobs:**
```bash
docker exec autocusto-web-1 python manage.py crontab add
docker exec autocusto-web-1 python manage.py crontab show
docker exec autocusto-web-1 python manage.py crontab remove
```

## Code Style and Conventions

### Django Best Practices

1. **Use repositories for data access** - Don't use ORM directly in views
2. **Service layer for business logic** - Keep views thin
3. **Form factories for complex creation** - See processos/forms/
4. **Docstrings for business logic** - Explain why, not just what
5. **Meaningful variable names** - Portuguese is acceptable for domain terms

### Python Style

- Follow PEP 8
- Use list comprehensions when appropriate
- Type hints where beneficial (especially in services)
- Comprehensive docstrings for complex business logic

### Security Considerations

**CRITICAL**: This is a medical application handling sensitive patient data.

1. **Always preserve audit trails** - Use SET_NULL on foreign keys, never CASCADE on critical relationships
2. **User-specific data access** - Always filter by user when accessing versioned data
3. **No cross-user data leaks** - Validate user permissions before displaying data
4. **Secure cookie flags** - SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE in production
5. **HTTPS enforcement** - All production traffic over SSL
6. **Comprehensive logging** - Use analytics app for audit trails

### Database Patterns

1. **Indexes** - Add indexes for frequently queried fields
2. **Unique constraints** - Use for business rule enforcement
3. **Choices** - Use Django choices for fixed options (states, specialties)
4. **Timestamps** - Use `auto_now_add` and `auto_now` appropriately
5. **SET_NULL with null=True, blank=True** - For audit preservation

## Common Tasks and Patterns

### Adding a New Medical Form (PDF)

1. Place template PDF in `/static/autocusto/processos/`
2. Create strategy in `processos/services/pdf_strategies.py`
3. Register strategy in `pdf_operations.py`
4. Add analytics logging
5. Create tests in `tests/integration/services/`

### Adding a New Disease/Protocol

1. Create Doenca instance with CID code
2. Create Protocolo with conditional data (JSON)
3. Link medications to protocol
4. Update relevant forms to include new protocol fields

### Modifying Patient/Clinic Versioning

**CAUTION**: Versioning system is complex. Consult existing implementation patterns.

1. Understand current version flow
2. Consider impact on existing user data
3. Add migration carefully (data migration may be needed)
4. Update repositories to handle new version fields
5. Add comprehensive tests

### Adding a New Django App

1. Create app: `docker exec autocusto-web-1 python manage.py startapp <app_name>`
2. Add to `INSTALLED_APPS` in settings.py
3. Follow repository + service + domain pattern if applicable
4. Create tests/ directory with conftest.py
5. Add app-specific documentation

## CI/CD and Deployment

### GitHub Actions Workflows

1. **test-integration.yml** - Sequential test pipeline
   - Runs unit, integration, and E2E tests
   - Coverage reporting
   - Runs on push to master

2. **deploy.yml** - Deployment workflow
   - Manual dispatch with test suite selection
   - Builds and deploys to production

### Production Settings

**Environment variables** (via .env):
- `DEBUG=False`
- `ALLOWED_HOSTS` - Comma-separated list
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `SECURE_SSL_REDIRECT=True`
- `SECURE_HSTS_SECONDS=31536000`

### Health Checks

- `/health/` endpoint for monitoring
- PostgreSQL health checks in docker-compose
- System metrics collected every 15 minutes

## Important Files Reference

### Configuration
- `autocusto/settings.py` - Main settings (494 lines)
- `test_settings.py` - Test overrides
- `uwsgi.ini` - uWSGI server configuration
- `nginx.conf` - Nginx reverse proxy
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Multi-stage build (builder, base, test, production)

### Entry Points
- `manage.py` - Django management commands
- `startup.sh` - Container initialization (copies PDF templates)

### Dependencies
- `requirements.txt` - All dependencies (including test)
- `requirements-production.txt` - Production-only

### Documentation
- `/processos/services/README.md` - Service layer architecture
- This file (CLAUDE.md) - Project instructions

## Language and Localization

- **Language**: Portuguese (pt-br)
- **Timezone**: UTC
- **Domain terms**: Often in Portuguese (doenca, paciente, clinica, processo)
- **Code comments**: Mix of English and Portuguese
- **User-facing text**: All Portuguese

## Working with This Codebase

### When Making Changes

1. **Understand the pattern first** - This codebase uses repository + service patterns
2. **Check existing implementations** - Look for similar features before implementing
3. **Consider versioning** - Patient/clinic changes affect versioning system
4. **Write tests** - Follow test pyramid (unit → integration → E2E)
5. **Preserve audit trails** - Never delete data that should be auditable
6. **Run tests in container** - Always use `docker exec` for commands

### When Adding Features

1. **Create todo list** - Use TodoWrite tool to plan work
2. **Use subagents** - Leverage specialized agents for exploration, refactoring, security, etc.
3. **Explain changes** - Clarify WHY changes are being made, not just WHAT
4. **Consider alternatives** - Discuss trade-offs of different approaches
5. **Update tests** - Add tests for new functionality
6. **Update documentation** - Keep CLAUDE.md current

### When Debugging

1. **Check container logs** - `docker compose logs -f web`
2. **Check database state** - Use psql to inspect data
3. **Run specific tests** - Isolate failures with pytest markers
4. **Use Django shell** - `docker exec -it autocusto-web-1 python manage.py shell`
5. **Check analytics logs** - Audit trail may reveal issues

## Technical Debt Notes

Known areas to be aware of:

1. **SET_NULL vs CASCADE** - Some models have questions about appropriate deletion behavior
2. **Fallback mechanisms** - Versioning system has fallbacks with security warnings
3. **Debug logging** - Some ERROR-level logging might be too verbose
4. **JSON conditional data** - Protocolo stores conditional data as JSON (could be normalized)
5. **PDF template caching** - 5-minute TTL may need tuning

## Getting Help

- **Django documentation**: https://docs.djangoproject.com/
- **Playwright documentation**: https://playwright.dev/python/
- **Project context**: This is a mature production application serving real patients
- **Security**: When in doubt, prioritize data security and audit preservation

---

**Remember**: This is a healthcare application. Changes affect real patients. Always prioritize:
1. Data security and privacy
2. Audit trail preservation
3. User-specific data access
4. Comprehensive testing
5. Clear documentation of business logic

When working on this codebase, use subagents frequently for specialized tasks (security audits, testing strategy, refactoring, etc.) and always explain WHY changes are being made, considering the medical/regulatory context.
