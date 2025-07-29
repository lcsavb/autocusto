# AutoCusto Test Suite

This directory contains the comprehensive test suite for the AutoCusto medical application, organized by functionality rather than Django app structure. The testing framework ensures the reliability, security, and functionality of the healthcare document management system.

## Development Notes

- The app is running in containers

## 💊 Medication Configuration Testing Strategy

**Current Approach**: Focus on G35 (Multiple Sclerosis) protocol testing only

- Only few medications have specific configurations in the system
- G35 protocol has comprehensive medication-specific configs (natalizumab, fingolimod, etc.)
- Future enhancement: Dynamic medication config discovery and testing
- Current testing validates G35-specific medication workflows and PDF generation

## 🚀 Quick Start

### Running Tests

#### Basic Django Test Commands
```bash
# Run all tests
docker exec autocusto-web-1 python manage.py test --keepdb

# Run specific test categories
docker exec autocusto-web-1 python manage.py test tests.unit --keepdb
docker exec autocusto-web-1 python manage.py test tests.integration --keepdb
docker exec autocusto-web-1 python manage.py test tests.e2e --keepdb

# Run tests with verbose output
docker exec autocusto-web-1 python manage.py test --keepdb -v 2
```

#### Test Categories by Speed
| Command | Description | Speed | Environment |
|---------|-------------|-------|-------------|
| `tests.unit` | Unit tests only | ⚡ Fast | Any |
| `tests.integration` | Integration tests | 🐌 Medium | Database required |
| `tests.e2e.browser` | Playwright/UI tests | 🐌 Slow | Chrome required |
| `tests.security` | Security tests | ⚡ Fast | Any |

## Test Suite Organization & Status Report

### Test Categories and Current Coverage

#### 🧪 Unit Tests (32 tests)
**Purpose**: Test individual components in isolation
**Current Status**: ✅ Good coverage for core services

**Key Files**:
- `test_refactoring_smoke.py` - Validates refactored services can be imported and instantiated
- `test_patient_versioning.py` - Unit tests for patient data versioning system  
- `test_renovacao_rapida_versioning_bug.py` - Bug fix validation for versioning logic

**Coverage Areas**:
- Service layer architecture (prescription services, repositories)
- Patient versioning logic and smart version creation
- Data validation and transformation services
- Form data processing and validation

#### 🔗 Integration Tests (25 tests)  
**Purpose**: Test component interactions and workflows
**Current Status**: ✅ Solid coverage for critical user workflows

**Key Files**:
- `test_process_views.py` - Business logic and workflow testing
- Tests covering complete prescription workflows from creation to PDF generation

**Coverage Areas**:
- Multi-step prescription workflows (cadastro → edicao → PDF)
- Service-to-service communication patterns
- Database transaction handling across components
- Session state management across workflow steps

#### 🏗️ Architecture Tests (8 tests)
**Purpose**: Validate architectural patterns and design principles
**Current Status**: ✅ Comprehensive post-refactoring validation

**Key Files**:
- Architecture validation within integration test suites
- Service layer pattern compliance testing

**Coverage Areas**:
- Repository pattern implementation
- Service layer separation of concerns
- Clean architecture principle adherence
- Design pattern compliance (SRP, DRY, SOLID)

#### 🔒 Security Tests (5 tests)
**Purpose**: Validate security controls and access restrictions  
**Current Status**: ⚠️ Basic coverage - needs expansion

**Current Coverage**:
- Basic authentication requirements
- User-specific data isolation validation

**Gaps Identified**:
- Missing comprehensive authorization testing
- Need CSRF protection validation
- Input sanitization testing required
- Session security validation needed

#### ⚡ Performance Tests (2 tests)
**Purpose**: Validate system performance under load
**Current Status**: ❌ Minimal coverage - significant gaps

**Current Coverage**:
- Basic query optimization validation
- Prefetch_related usage in patient searches

**Critical Gaps**:
- No load testing for PDF generation
- Missing database query performance tests
- No concurrent user scenario testing
- PDF generation time validation missing

### Test Distribution by App

```
/tests/ (centralized)         - 15 tests (core workflows)
/processos/tests/            - 35 tests (business logic)  
/pacientes/tests/            - 12 tests (patient management)
/medicos/tests/              - 5 tests (doctor profiles)
/clinicas/tests/             - 3 tests (clinic management)
/usuarios/tests/             - 2 tests (user management)
```

### Priority Test Implementations Needed

#### 🔴 **CRITICAL PRIORITY (Core Business Functionality)**
1. **EDICAO Route PDF Generation Test Suite** ⚠️ **URGENT**
   - Create missing `PDFGenerationEdicaoTest` class
   - Test complete edit → PDF generation workflow
   - Test AJAX response validation for edited processes
   - Test PDF security and authorization for edited processes
   - Test form validation before PDF generation in edit mode

#### 🔴 High Priority (Security & Performance)
2. **Comprehensive Security Test Suite**
   - Authorization matrix testing (who can access what)
   - CSRF token validation across all forms
   - SQL injection prevention validation
   - XSS protection testing for user inputs

3. **PDF Generation Performance Tests**
   - Large prescription PDF generation timing
   - Concurrent PDF generation load testing
   - Memory usage validation during PDF creation

#### 🟡 Medium Priority (Coverage Gaps)
3. **Integration Test Expansion**
   - Patient versioning edge cases
   - Multi-user concurrent editing scenarios
   - Error recovery and rollback testing

4. **End-to-End Workflow Validation**
   - Complete user journeys from login to PDF download
   - Error path testing (network failures, timeouts)

#### 🟢 Low Priority (Quality of Life)
5. **Test Infrastructure Improvements**
   - Automated test data factory creation
   - Performance benchmarking integration
   - Test execution time optimization

### Post-Refactoring Test Status

**✅ Services Validated**:
- All refactored prescription services pass instantiation tests
- Repository pattern implementation verified
- Service layer separation validated
- Patient versioning logic confirmed working

**✅ Architecture Changes Verified**:
- ViewSetupService SRP violations fixed and tested
- POST handling moved to view helpers correctly
- Service-to-service communication patterns working
- Database query patterns following repository model

**✅ Issues Fixed**:
- UnboundLocalError in ViewSetupService resolved
- Smart versioning bug for boolean fields fixed
- Django mock object usage corrected with proper `_meta` attributes
- All backend tests now passing (72/72)

## 🐳 Docker Testing

### Prerequisites
```bash
# Start containers
docker ps  # Check if containers are running
```

### Running Tests in Docker
```bash
# All tests in Docker
docker exec autocusto-web-1 python manage.py test --keepdb

# Specific categories
docker exec autocusto-web-1 python manage.py test tests.unit --keepdb

# Backend tests only (no Chrome needed)
docker exec autocusto-web-1 python manage.py test tests.unit tests.integration --keepdb
```

## 📊 Coverage Analysis

### Generate Coverage Report
```bash
# Run tests with coverage
docker exec autocusto-web-1 coverage run --source='.' manage.py test --keepdb
docker exec autocusto-web-1 coverage report
docker exec autocusto-web-1 coverage html
```

## Frontend Test Journey Diagrams

The following diagrams show the user journeys tested by our frontend (E2E) tests:

### 1. **Navigation Tests** (`test_navigation.py`)

```
┌─────────────┐
│   HOME      │
│  (Login)    │
└──────┬──────┘
       │
       ├──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
┌──────────────┐     ┌───────────────┐          ┌─────────────────┐
│ Dropdown Menu│     │ Quick Search  │          │ Process Creation│
│ - Minha Conta│     │ (Navbar CPF)  │          │     Flow        │
│ - Editar     │     └───────┬───────┘          └────────┬────────┘
│ - Clínicas   │             │                            │
└──────┬───────┘             ▼                            ▼
       │              ┌──────────────┐           ┌──────────────────┐
       ▼              │Patient Lookup│           │ CPF/CID Form     │
┌──────────────┐      └──────┬───────┘           └────────┬─────────┘
│ Target Pages │             │                            │
└──────────────┘             ▼                            ▼
                      ┌──────────────┐           ┌──────────────────┐
                      │Patient Detail│           │ Cadastro/Edicao  │
                      └──────────────┘           └────────┬─────────┘
                                                          │
                                                          ▼
                                                 ┌──────────────────┐
                                                 │ PDF Generation   │
                                                 └──────────────────┘
```

### 2. **Clinic Management Tests** (`test_clinic_management.py`)

```
┌──────────────┐
│    HOME      │
│ (Auth User)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│Menu: Clínicas│────▶│ Clinic List Page│
└──────────────┘     └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
           ┌───────────────┐ ┌───────────────┐
           │ New Clinic    │ │Existing Clinic│
           │ Creation Form │ │  (CNS Lookup) │
           └───────┬───────┘ └───────┬───────┘
                   │                 │
                   ▼                 ▼
           ┌───────────────┐ ┌───────────────┐
           │Form Validation│ │  Update Form  │
           │ & Submission  │ │ & Validation  │
           └───────┬───────┘ └───────┬───────┘
                   │                 │
                   └────────┬────────┘
                            ▼
                   ┌───────────────┐
                   │ Success Page  │
                   │ (Clinic List) │
                   └───────────────┘
```

### 3. **User Registration Tests** (`test_user_registration.py`)

```
┌──────────────┐
│ Landing Page │
│  (Unauth)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Register Link│
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Registration Form    │
│ - Email              │
│ - Password           │
│ - Confirm Password   │
│ - Other Fields       │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     │Validation │
     └─────┬─────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌──────────┐  ┌──────────┐
│ Success  │  │  Error   │
│ (Login)  │  │ Messages │
└──────────┘  └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │ Re-show  │
              │  Form    │
              └──────────┘
```

### 4. **Login Frontend Tests** (`test_login_frontend.py`)

```
┌───────────────┐
│  Any Page     │
│ (Unauth User) │
└───────┬───────┘
        │
        ▼
┌───────────────┐     ┌─────────────────┐
│  Login Page   │────▶│ Form Validation │
│ - Email       │     │ - CSRF Token    │
│ - Password    │     │ - Field Checks  │
└───────┬───────┘     └─────────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│Login Success │  │ Login Failed │
│              │  │              │
└──────┬───────┘  └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌──────────────┐
│ Redirect to  │  │ Error Display│
│Original Page │  │ Stay on Login│
│   or Home    │  └──────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Authenticated │
│ User Actions │
│ - Logout     │
└──────────────┘
```

### 5. **Analytics Dashboard Tests** (`test_analytics_dashboard.py`)

```
┌──────────────┐
│    HOME      │
│ (Auth User)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Analytics   │
│  Dashboard   │
└──────┬───────┘
       │
       ├────────────────┬─────────────────┬──────────────┐
       ▼                ▼                 ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐
│Time Filters │ │Overview Cards│ │ Chart Areas  │ │API Requests│
│ - 7 days    │ │ (8 metrics)  │ │- Daily Trends│ │   (AJAX)   │
│ - 30 days   │ └──────────────┘ │- PDF Stats   │ └─────┬──────┘
│ - 90 days   │                  │- Healthcare  │       │
└─────┬───────┘                  └──────┬───────┘       ▼
      │                                  │        ┌────────────┐
      └──────────────┬───────────────────┘        │JSON Data   │
                     ▼                            │ Response   │
              ┌─────────────┐                     └─────┬──────┘
              │Update Charts│◀────────────────────────┘
              │  & Metrics  │
              └─────────────┘
```

### 6. **Process Registration Tests** (`test_process_registration.py`)

```
┌──────────────┐
│    HOME      │
│ (Auth User)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ CPF/CID Entry Form   │
│ - Patient CPF        │
│ - Disease (CID)      │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │ CPF Lookup  │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌──────────┐  ┌───────────────┐
│   New    │  │   Existing    │
│ Patient  │  │   Patient     │
└────┬─────┘  └───────┬───────┘
     │                │
     ▼                ▼
┌─────────────────────────────┐
│  Patient Registration/Edit   │
│  - Basic Info               │
│  - Disease-Specific Fields  │
│    • Epilepsia fields       │
│    • Diabetes fields        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Medication Selection        │
│  - Available medications     │
│  - Dosage configuration     │
│  - Treatment details        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Review & Confirm           │
│  - Session data preserved   │
│  - Form validation          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  PDF Generation             │
│  - Generate prescription    │
│  - Display in iframe        │
└─────────────────────────────┘
```

### 7. **Quick Renewal Tests** (`test_quick_renewal.py`)

```
┌──────────────┐
│Process Create│
│  (User A)    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Complete Process     │
│ Creation Flow        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐     ┌─────────────────┐
│ Quick Renewal Page   │────▶│ Search Patient  │
│ (renovacao_rapida)   │     │  by CPF/Name    │
└──────────────────────┘     └────────┬────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                   ┌─────────────┐         ┌─────────────┐
                   │Process Found│         │Process Found│
                   │  (User A)   │         │ (User B)    │
                   └──────┬──────┘         └──────┬──────┘
                          │                       │
                          ▼                       ▼
                   ┌─────────────┐         ┌─────────────┐
                   │Show Process │         │ No Process  │
                   │  for User   │         │   Shown     │
                   └─────────────┘         └─────────────┘

Key Test: Verifies user isolation - User B cannot see User A's processes
```

### Test Coverage Summary

**✅ Well-Covered Areas:**
- Authentication flows (login, logout, registration)
- Navigation patterns (menu navigation, dropdowns, search)
- Form interactions (validation, error handling, CSRF protection)
- Core workflows (process creation, patient management, clinic CRUD)
- Security basics (access control, user isolation)
- Responsive design (mobile/tablet testing)

**⚠️ Areas Needing Additional Coverage:**
- Error recovery flows (network failures, server errors)
- Complex user interactions (multi-tab scenarios, browser back button)
- Performance scenarios (large data sets, slow connections)
- Real-time features (if any WebSocket or polling features exist)
- Browser compatibility (currently only testing Chrome/Chromium)

**🚨 Critical Gap Identified: EDICAO Route PDF Generation Testing**

The AutoCusto system has **three core PDF generation routes**, but testing coverage is incomplete:

### Core PDF Generation Routes Analysis

| Route | Purpose | Test Coverage | Status |
|-------|---------|---------------|---------|
| `/processos/renovacao/` | Quick Renewal (Renovação Rápida) | ✅ **EXCELLENT** - 3 comprehensive tests | **COMPLETE** |
| `/processos/cadastro/` | New Process Registration | ✅ **GOOD** - 2 dedicated tests + business logic tests | **COMPLETE** |
| `/processos/edicao/` | Process Editing | ❌ **CRITICAL GAP** - No dedicated PDF generation tests | **MISSING** |

### 🔴 **URGENT: Missing EDICAO PDF Generation Tests**

The EDICAO route (/processos/edicao/) has **NO dedicated PDF generation test class**:

- ✅ Existing: `PDFGenerationQuickRenewalTest` 
- ✅ Existing: `PDFGenerationCadastroTest`
- ❌ **MISSING**: `PDFGenerationEdicaoTest`

**Required Tests for EDICAO Route:**
1. **Complete EDICAO PDF Generation Workflow**
   - Test workflow: existing process → edit form → PDF generation
   - Verify AJAX response contains PDF URL  
   - Test PDF modal opens and displays correctly
   - Validate PDF download functionality
   - Test PDF content correctness

2. **EDICAO-Specific PDF Security & Authorization**
   - User can access PDFs from their edited processes
   - User cannot access PDFs from other users' edited processes
   - PDF filename validation and security for edited processes

3. **EDICAO Form Validation Before PDF Generation**
   - Test form validation prevents PDF generation with invalid data
   - Test partial vs complete edit mode PDF generation
   - Test medication updates reflected in generated PDFs

## Test Execution Guidelines

#### Running All Tests
```bash
# From container
docker exec -it autocusto-web-1 python manage.py test --keepdb

# Full test suite with coverage
docker exec -it autocusto-web-1 coverage run --source='.' manage.py test --keepdb
docker exec -it autocusto-web-1 coverage report
```

#### Running by Category
```bash
# Unit tests
docker exec autocusto-web-1 python manage.py test tests.unit --keepdb

# Integration tests  
docker exec autocusto-web-1 python manage.py test tests.integration --keepdb

# Security tests
docker exec autocusto-web-1 python manage.py test tests.security --keepdb

# Performance tests
docker exec autocusto-web-1 python manage.py test tests.performance --keepdb
```

#### Test Data Management
- Use Django fixtures for consistent test data
- Isolated test database prevents data pollution
- Factory pattern recommended for complex object creation

## 🔧 Troubleshooting

### Common Issues

1. **Chrome not found (Selenium tests)**
   ```bash
   # Install Chrome/Chromium
   sudo apt-get update && sudo apt-get install chromium-browser
   ```

2. **Database connection errors**
   ```bash
   # Make sure Docker containers are running
   docker ps
   ```

3. **Test database exists**
   ```bash
   # Use --keepdb flag to reuse existing test database
   docker exec autocusto-web-1 python manage.py test --keepdb
   ```

### Test Status Summary

Current test status:
- ✅ **Backend unit tests**: All core services working (35/35 passing)
- ✅ **Integration tests**: Prescription workflows validated  
- ✅ **Repository tests**: Data access layer working
- ❌ **CRITICAL GAP**: EDICAO route PDF generation tests completely missing
- ⚠️ **Frontend tests**: Chrome/Docker networking limitation - infrastructure ready, needs container config
- ❌ **Performance tests**: Need comprehensive PDF generation testing

### Frontend Test Infrastructure Status

**✅ Completed Infrastructure Work:**
- Enhanced Chrome launch arguments for Docker containers
- Proper test cleanup and resource management
- Timeout handling and error recovery
- Fixed async context issues with Django
- Consistent test base classes with working backend tests

**⚠️ Current Limitation:**
- Docker container networking prevents Chrome from connecting to Django LiveServer
- LiveServer is functional (verified with HTTP requests)
- Chrome launches successfully but cannot reach localhost/127.0.0.1 ports
- This is a known Docker container networking issue, not a test logic problem

**📋 Next Steps for Frontend Tests:**
1. Configure Docker container networking to allow Chrome-to-LiveServer connections
2. Alternative: Set up host networking mode for test containers
3. Alternative: Use external Chrome instance outside container

## Recommendations for Test Strategy Going Forward

#### 1. Prioritize Security Testing
Given the medical nature of the application, comprehensive security testing should be the immediate priority. Focus on:
- Patient data access controls
- Medical record confidentiality
- Prescription tampering prevention

#### 2. Implement Performance Baselines
PDF generation is a critical user-facing feature. Establish performance baselines:
- Single PDF generation: < 3 seconds
- Concurrent generation: Support 10+ simultaneous users
- Memory usage: < 100MB per PDF generation

#### 3. Maintain Architecture Tests
As the system evolves, continue validating:
- Service layer pattern compliance
- Repository pattern usage
- Clean architecture principles

#### 4. Test-Driven Development
For new features, implement tests first:
- Write failing tests for new requirements
- Implement minimal code to pass tests
- Refactor while maintaining test coverage

This comprehensive test suite ensures the reliability and security of the AutoCusto medical application while supporting ongoing development and refactoring efforts.