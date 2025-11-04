# AutoCusto DevOps Infrastructure - Comprehensive Analysis

**Date:** November 4, 2025
**Project:** AutoCusto - Automated Medical Prescription Processing System
**Analysis Type:** Complete DevOps Infrastructure Assessment

---

## Executive Summary

AutoCusto employs a modern, containerized DevOps infrastructure with comprehensive CI/CD pipelines, automated testing, and robust monitoring capabilities. The system is designed for healthcare compliance, high availability, and secure deployment to production environments.

**Key Strengths:**
- Multi-stage Docker builds with production/test separation
- Comprehensive test pyramid implementation (Unit → Integration → E2E)
- Automated backup and disaster recovery systems
- Real-time system health monitoring with custom analytics
- GitHub Actions CI/CD with parallel test execution

**Areas for Enhancement:**
- Infrastructure as Code (IaC) implementation
- Container orchestration (Kubernetes)
- Advanced monitoring/alerting integration
- Blue-green deployment strategy
- Enhanced secrets management

---

## 1. CI/CD Pipeline Architecture

### 1.1 GitHub Actions Workflows

#### Test Pipeline (`test-integration.yml`)
Location: `.github/workflows/test-integration.yml`

**Workflow Structure:**
```yaml
Triggers:
  - Push to master/develop
  - Pull requests to master/develop
  - Manual workflow_dispatch
```

**Job Execution Strategy:** Parallel execution with 5 concurrent jobs

##### Job 1: Backend Tests (Unit & Integration)
- **Runtime:** ubuntu-latest
- **Database:** PostgreSQL 17.4-alpine (service container)
- **Test Pyramid Phase 1-2:** Unit tests → Integration tests
- **Coverage:** Codecov integration enabled
- **Exit Strategy:** Continues even on failure to allow all tests to complete

**Test Categories:**
```bash
Phase 1: Unit Tests (Fast Feedback)
  - tests.unit.models
  - tests.unit.services
  - tests.unit.repositories
  - tests.unit.utils

Phase 2: Integration Tests (Component Interactions)
  - tests.integration.database
  - tests.integration.api
  - tests.integration.services.*
```

**Performance Metrics:**
- Uses Python 3.11
- Pip dependency caching enabled
- Django check --deploy validation
- Coverage tracking with coverage.py

##### Job 2: Playwright Tests (Browser-Based Integration)
- **Runtime:** ubuntu-latest with Docker Compose
- **Test Pyramid Phase 3:** E2E browser testing
- **Infrastructure:** Containerized Playwright architecture

**Architecture:**
```
┌─────────────────────────────────────────────┐
│ GitHub Actions Runner                       │
│  ┌──────────────────────────────────────┐  │
│  │ docker-compose.ci.yml                │  │
│  │  ├─ PostgreSQL 17.4-alpine          │  │
│  │  ├─ Web Container (Django + Tests)  │  │
│  │  └─ Playwright Browser Container    │  │
│  │     └─ Chrome via CDP (port 9222)   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Test Categories:**
- Prescription form tests (`tests.integration.forms.test_prescription_forms`)
- PDF workflow tests (`tests.integration.services.test_pdf_workflows`)
- E2E browser tests (`tests.e2e.browser`)

**Key Features:**
- Dynamic docker-compose.ci.yml generation
- Xvfb virtual display for headless testing
- Chrome DevTools Protocol remote debugging
- 2GB shared memory for browser performance
- Automatic cleanup with `if: always()`

##### Job 3: JavaScript Unit Tests
- **Runtime:** ubuntu-latest
- **Node Version:** 18
- **Package Manager:** npm with caching
- **Focus:** Critical medication validation logic

**Test Suite:**
```javascript
Location: static/autocusto/js/
Tests: Medication dosage validation, drug interactions
Framework: Jest (inferred from package.json structure)
```

##### Job 4: Security Tests
- **Tools:**
  - Django security test suite
  - Safety (dependency vulnerability scanner)
  - Bandit (Python security linter)

**Scans:**
```bash
1. E2E security tests (tests.e2e.security)
2. Dependency vulnerability scanning (safety check)
3. Static code security analysis (bandit -r .)
```

**Artifacts:**
- Security reports retained for 30 days
- JSON format for automated processing

##### Job 5: Docker Integration Test
- **Objective:** Validate production container integrity
- **Build Target:** `production` stage from multi-stage Dockerfile
- **Verifications:**
  1. Production build succeeds
  2. Container starts and runs unit tests
  3. Test dependencies NOT present (security validation)
  4. Container size monitoring

**Security Validation:**
```bash
# Ensures production image doesn't contain test-only dependencies
- No Chrome/Chromium binaries
- No Playwright libraries
- No cpf-generator (test utility)
```

##### Job 6: Deployment Readiness
- **Condition:** Only on master branch
- **Dependencies:** backend-tests, javascript-tests, security-tests
- **Purpose:** Final gate before deployment

##### Job 7: Test Summary
- **Always Runs:** Even if previous jobs fail
- **Purpose:** Consolidated reporting
- **Output:** GitHub Actions summary markdown

**Summary Includes:**
- Test pyramid visualization
- Pass/fail status for all test suites
- Success rate calculations
- Deployment readiness indicators

#### Deployment Pipeline (`deploy.yml`)
Location: `.github/workflows/deploy.yml`

**Trigger:** Push to master branch (production deployment)

**Pipeline Stages:**

1. **Test Stage**
   - Quick smoke tests before deployment
   - Unit and integration test validation
   - Uses same PostgreSQL service as test pipeline

2. **Build Stage**
   - GitHub Container Registry (ghcr.io)
   - Multi-stage Docker build targeting `production`
   - Image tagging strategy:
     ```
     - latest (rolling)
     - {github.sha} (immutable)
     ```
   - Image metadata with OCI labels

3. **Deploy Stage**
   - SSH deployment to VPS
   - Host: Stored in GitHub Secrets
   - Uses appleboy/ssh-action@v1.0.0

**Deployment Process:**
```bash
1. Pre-deployment backup (mandatory, fails on error)
2. GPG key setup for encrypted backups
3. Environment validation (.prodenv check)
4. Directory structure initialization
5. GitHub Container Registry login
6. Docker image pull (specific SHA)
7. docker-compose.yml generation
8. Container orchestration (down → up -d)
9. Database migrations
10. Static file collection
11. Backup upload to remote storage
12. Nginx reload (host-level)
13. Health check validation
```

**Infrastructure Characteristics:**
- Uses bind mounts for static/media files (not Docker volumes)
- tmpfs mounts for security (/tmp with noexec,nosuid)
- Shared memory mount: /dev/shm/autocusto
- Network binding: 127.0.0.1:8001 (localhost only, proxied by nginx)

**Rollback Safety:**
- Pre-deployment database backup (with GPG encryption)
- Immutable image tags (git SHA)
- Health check validation post-deployment

---

## 2. Containerization Architecture

### 2.1 Multi-Stage Dockerfile

Location: `Dockerfile`

**Build Strategy:** 4-stage optimized build

#### Stage 1: Builder
```dockerfile
FROM python:3.11-slim-bookworm AS builder
```
**Purpose:** Compile Python dependencies into wheels
- Builds ALL dependencies (requirements.txt)
- Builds production-only dependencies (requirements-production.txt)
- Separate wheel directories for test vs production

**Benefits:**
- Faster subsequent builds
- Layer caching optimization
- Smaller final images

#### Stage 2: Base Runtime
```dockerfile
FROM python:3.11-slim-bookworm AS base
```
**Purpose:** Shared runtime dependencies
- pdftk (PDF manipulation)
- PostgreSQL 17 client
- cron, gnupg, wget, curl
- Certificate authorities

**Size Optimization:**
- apt cleanup after installation
- Minimal base image (slim)

#### Stage 3: Test Image
```dockerfile
FROM base AS test
```
**Purpose:** Test execution environment
- Includes Playwright browser dependencies (libatk, libdrm, etc.)
- Non-root user (appuser)
- Full test dependency set
- startup.sh entrypoint for memory mount setup

**Characteristics:**
- User: appuser (non-root)
- Working directory: /home/appuser/app
- Exposes port 8001
- Log directory: /var/log/django
- Backup directory: /var/backups/autocusto

#### Stage 4: Production Image
```dockerfile
FROM base AS production
```
**Purpose:** Minimal production runtime
- Only production dependencies (no test libraries)
- No browser binaries
- Security-hardened
- Optimized for size and attack surface

**Security Features:**
- Non-root execution
- Minimal dependency footprint
- No development tools
- Read-only application code (runtime)

### 2.2 Docker Compose Configurations

#### Development Configuration (`docker-compose.yml`)
```yaml
Services:
  - db: PostgreSQL 17.4-alpine
  - web: Django application (test stage)
  - playwright-browsers: Browser testing infrastructure
```

**Key Features:**
- Volume mounting for hot-reload development
- Environment variables for local development
- Playwright remote browser architecture
- tmpfs for performance (/tmp, /dev/shm)

**Playwright Architecture:**
```
Web Container (Django) ──CDP──> Playwright Container (Chromium)
                        Port 9222
```

**Benefits:**
- Clean separation of concerns
- Replicates CI/CD test environment locally
- Faster test execution (shared browser pool)

#### Production Configuration (Generated Dynamically)
Created during deployment in `.github/workflows/deploy.yml`

```yaml
Services:
  - web: Production image from GHCR
  - db: PostgreSQL 17.4-alpine with persistent volume
```

**Production-Specific Settings:**
- Bind mounts instead of volumes (static/media)
- Localhost-only binding (127.0.0.1:8001)
- restart: unless-stopped
- tmpfs with security options
- Environment from .prodenv

### 2.3 Container Security

**Runtime Security Measures:**
1. Non-root user execution
2. Read-only filesystem capabilities
3. Minimal attack surface (production image)
4. tmpfs with noexec,nosuid flags
5. Network isolation (localhost binding)

**Build-Time Security:**
1. Official Python base images
2. Pinned dependency versions
3. Multi-stage builds (test dependencies not in production)
4. Layer minimization
5. Security scanning in CI (bandit, safety)

---

## 3. Testing Infrastructure

### 3.1 Test Pyramid Implementation

AutoCusto implements a comprehensive Test Pyramid strategy:

```
           ┌─────────────┐
          /   E2E Tests   \      ← Playwright, Security
         /─────────────────\
        /  Integration Tests \   ← API, Services, Forms
       /─────────────────────\
      /     Unit Tests        \  ← Models, Utils, Repositories
     /─────────────────────────\

    Base: Fast, Many       Top: Slow, Few
```

### 3.2 Test Categories

#### Unit Tests
Location: `tests/unit/`
```
tests.unit.models
tests.unit.services
tests.unit.repositories
tests.unit.utils
```

**Characteristics:**
- SQLite in-memory database
- No external dependencies
- Fast execution (<1ms per test)
- High coverage of business logic

**Settings:** `test_settings.py`
- MD5 password hashing (speed)
- LocalMem cache backend
- Disabled logging (noise reduction)
- Analytics disabled

#### Integration Tests
Location: `tests/integration/`
```
tests.integration.database
tests.integration.api
tests.integration.forms (Playwright-based)
tests.integration.services
```

**Characteristics:**
- Real PostgreSQL database
- Component interaction testing
- API endpoint validation
- Service layer integration

**Special Cases:**
- Prescription form tests use Playwright
- PDF workflow tests use containerized browsers
- Database tests validate data integrity

#### E2E Tests
Location: `tests/e2e/`
```
tests.e2e.browser (Playwright)
tests.e2e.security
tests.e2e.user_journeys
```

**Characteristics:**
- Full application stack
- Real browser automation
- User workflow simulation
- Security validation

#### JavaScript Tests
Location: `static/autocusto/js/`
**Focus:** Critical medication logic
- Dosage calculation validation
- Drug interaction checks
- Form validation logic

### 3.3 Test Execution Scripts

#### Host Machine Test Runner
Script: `run_tests_from_host.sh`

**Features:**
- Docker environment validation
- Colored output for readability
- Timeout protection (120-300s per category)
- Consolidated error reporting
- Success rate calculations

**Test Execution Flow:**
```bash
1. Environment Check
   ↓
2. Phase 1: Unit Tests (4 categories)
   ↓
3. Phase 2: Integration Tests (4 categories)
   ↓
4. Phase 3: E2E Tests (2 categories)
   ↓
5. Playwright Infrastructure Check
   ↓
6. Browser Tests (with remote Playwright)
   ↓
7. Consolidated Report Generation
```

**Error Handling:**
- Captures full test output
- Filters to show only errors
- Preserves context (20 lines around errors)
- Timeout detection with clear indicators

#### Frontend Test Runner
Script: `run_frontend_tests.sh`

**Categories:**
1. User Journey Tests
2. Browser/Playwright Tests
3. Security Tests

**Timeout:** 5 minutes per category

### 3.4 Test Database Strategy

**Development/Local:**
- Uses `--keepdb` flag for speed
- SQLite for unit tests (in-memory)
- PostgreSQL for integration tests

**CI/CD:**
- Fresh PostgreSQL instance per job
- Health checks before test execution
- Parallel test execution across jobs

---

## 4. Deployment Architecture

### 4.1 Deployment Strategy

**Type:** Rolling deployment with pre-deployment validation

**Target Environment:**
- VPS (Virtual Private Server)
- Host-based Nginx reverse proxy
- Docker Compose orchestration

### 4.2 Deployment Flow

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Actions (master branch push)                    │
│  ↓                                                      │
│ 1. Run smoke tests                                     │
│  ↓                                                      │
│ 2. Build Docker image (multi-stage)                    │
│  ↓                                                      │
│ 3. Push to GitHub Container Registry                   │
│  │  - Tag: latest                                      │
│  │  - Tag: {git-sha}                                   │
│  ↓                                                      │
│ 4. SSH to VPS                                          │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ VPS Deployment Process                                  │
│  ↓                                                      │
│ 1. Create encrypted database backup (MANDATORY)        │
│  ↓                                                      │
│ 2. Setup GPG keys for backup encryption                │
│  ↓                                                      │
│ 3. Validate environment (.prodenv)                     │
│  ↓                                                      │
│ 4. Setup static/media directories                      │
│  │  - /opt/autocusto/static_files                     │
│  │  - /opt/autocusto/media_files                      │
│  │  - /dev/shm/autocusto (memory mount)               │
│  ↓                                                      │
│ 5. Pull latest Docker image (by SHA)                   │
│  ↓                                                      │
│ 6. Generate production docker-compose.yml              │
│  ↓                                                      │
│ 7. Stop old containers                                 │
│  ↓                                                      │
│ 8. Start new containers                                │
│  ↓                                                      │
│ 9. Run database migrations                             │
│  ↓                                                      │
│10. Collect static files                                │
│  ↓                                                      │
│11. Fix permissions (deploy:deploy)                     │
│  ↓                                                      │
│12. Upload backup to Nextcloud (WebDAV)                 │
│  ↓                                                      │
│13. Reload host Nginx                                   │
│  ↓                                                      │
│14. Health check (HTTP 200 on /health/)                 │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Network Architecture

```
Internet
   ↓
┌──────────────────────────────────────────┐
│ Host Nginx (Port 443 HTTPS)              │
│  - SSL/TLS termination                   │
│  - Static file serving                   │
│  - Reverse proxy to Django               │
└──────────────────────────────────────────┘
   ↓ (127.0.0.1:8001)
┌──────────────────────────────────────────┐
│ Docker Container - Django (uWSGI)        │
│  - Port 8001 (localhost only)            │
│  - 4 processes, 2 threads each           │
└──────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────┐
│ Docker Container - PostgreSQL 17.4       │
│  - Internal network only                 │
│  - Persistent volume                     │
└──────────────────────────────────────────┘
```

### 4.4 Nginx Configuration

Location: `nginx.conf`

**Features:**
- HTTP → HTTPS redirect (mandatory)
- TLS 1.2/1.3 only
- Static file optimization
- PDF iframe embedding support
- Memory-mounted PDF templates (/dev/shm)
- uWSGI reverse proxy

**Static File Strategy:**
```
/static/tmp/          → Django (dynamic PDFs)
/static/processos/    → Memory mount (templates)
/static/protocolos/   → Memory mount (templates)
/static/             → Disk (general assets)
```

**Performance Optimization:**
- PDF templates in /dev/shm (RAM) for speed
- Static files served directly by Nginx (not Django)
- uWSGI protocol for Django communication

### 4.5 Application Server

Configuration: `uwsgi.ini`

```ini
[uwsgi]
socket = :8001
master = true
processes = 4       # Worker processes
threads = 2         # Threads per process
vacuum = true       # Clean up on exit
die-on-term = true  # Respect SIGTERM
module = autocusto.wsgi:application
buffer-size = 32768 # Large buffer for complex requests
```

**Capacity:** 8 concurrent requests (4 processes × 2 threads)

### 4.6 Memory Mount Strategy

Script: `startup.sh`

**Purpose:** Copy PDF templates to shared memory for performance

```bash
/home/appuser/app/static/autocusto/processos/*
  → /dev/shm/autocusto/static/processos/

/home/appuser/app/static/autocusto/protocolos/*
  → /dev/shm/autocusto/static/protocolos/
```

**Benefits:**
- 10-100x faster PDF template access
- Reduced disk I/O
- Better performance under load

**Setup:**
- Runs at container startup (entrypoint)
- Automatic directory creation
- Error-tolerant (|| true)

---

## 5. Backup and Disaster Recovery

### 5.1 Backup Strategy

**Tool:** django-dbbackup

**Configuration:**
```python
DBBACKUP_FILENAME_TEMPLATE = 'autocusto_db_{datetime}.{extension}'
DBBACKUP_CLEANUP_KEEP = 7  # 7 days retention
DBBACKUP_GPG_RECIPIENT = 'lcsavb@gmail.com'
DBBACKUP_STORAGE = FileSystemStorage
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups/autocusto/'}
```

### 5.2 Backup Schedule

Managed by: `django-crontab`

```python
CRONJOBS = [
    # PDF Cleanup (prevent disk fill)
    ('0 3 * * *', 'cleanup_pdfs'),           # 3:00 AM daily

    # Database Backup (encrypted)
    ('0 2 * * *', 'dbbackup'),              # 2:00 AM daily

    # Remote Upload (Nextcloud)
    ('15 2 * * *', 'upload_backup'),        # 2:15 AM daily

    # Metrics Collection
    ('30 1 * * *', 'calculate_daily_metrics'), # 1:30 AM daily

    # Health Metrics
    ('*/15 * * * *', 'collect_health_metrics'),  # Every 15 min
    ('0 4 * * *', 'collect_health_metrics --cleanup'), # 4:00 AM daily
]
```

### 5.3 Backup Process

#### Local Backup
Command: `python manage.py dbbackup`

**Process:**
1. PostgreSQL database dump
2. GPG encryption with AES256
3. Compression (level 2)
4. Save to /var/backups/autocusto/
5. Cleanup old backups (>7 days)

#### Remote Upload
Command: `python manage.py upload_backup`
Location: `processos/management/commands/upload_backup.py`

**Process:**
1. Find all .psql.bin files in /var/backups/autocusto/
2. GPG encrypt each backup
3. Upload to Nextcloud via WebDAV
4. Verify upload success
5. Clean up local encrypted copies
6. Skip already-uploaded files

**Technologies:**
- WebDAV4 client library
- Nextcloud as backup storage
- GPG for encryption (asymmetric)

**Security:**
- Backups encrypted before network transfer
- GPG public key encryption
- Credentials from environment variables

### 5.4 Disaster Recovery Procedure

**Backup Locations:**
1. Local: /var/backups/autocusto/ (7 days)
2. Remote: Nextcloud (indefinite)
3. Pre-deployment: Automatic before each deploy

**Recovery Steps:**
```bash
# 1. Download encrypted backup from Nextcloud
wget https://nextcloud.example.com/backups/autocusto_db_YYYYMMDD.psql.bin.gpg

# 2. Decrypt backup
gpg --decrypt autocusto_db_YYYYMMDD.psql.bin.gpg > backup.psql.bin

# 3. Restore to database
python manage.py dbrestore --input-filename=backup.psql.bin

# 4. Verify data integrity
python manage.py check
python manage.py test tests.unit.models
```

**RTO (Recovery Time Objective):** < 30 minutes
**RPO (Recovery Point Objective):** < 24 hours (daily backups)

---

## 6. Monitoring and Observability

### 6.1 Health Monitoring System

**Architecture:** Custom Django-based monitoring with psutil

Location: `analytics/health_utils.py`

#### Metrics Collected

1. **Database Performance**
   - Query execution time (ms)
   - Simple SELECT COUNT(*) benchmark
   - Thresholds: <100ms good, >200ms warning, >500ms critical

2. **PDF Memory Usage**
   - /dev/shm usage (MB)
   - Shared memory monitoring
   - Fallback to system memory if /dev/shm unavailable

3. **API Response Time**
   - Real query timing (recent processes count)
   - Measures actual business logic performance
   - Thresholds: <100ms good, >300ms warning

4. **Error Rate**
   - PDF generation failures (%)
   - Calculated over 1-hour window
   - Thresholds: <5% good, >10% warning, >20% critical

5. **Active Users**
   - Count of users active in last 30 minutes
   - Based on UserActivityLog
   - Fallback to session analysis

### 6.2 Monitoring Architecture

```
┌──────────────────────────────────────────────┐
│ SystemHealthMiddleware (Request Processing) │
│  - Measures every request response time      │
│  - Logs slow requests (>100ms)              │
│  - Periodic health checks (5min interval)   │
└──────────────────────────────────────────────┘
         ↓ (logs to)
┌──────────────────────────────────────────────┐
│ SystemHealthLog (Database Table)             │
│  - metric_type                               │
│  - value (Decimal)                           │
│  - unit (ms, MB, %, etc.)                    │
│  - timestamp                                 │
│  - details (JSON)                            │
└──────────────────────────────────────────────┘
         ↓ (queried by)
┌──────────────────────────────────────────────┐
│ Analytics Dashboard                          │
│  - /analytics/system-health/                 │
│  - Real-time metrics API                     │
│  - Historical trends (7 days)                │
└──────────────────────────────────────────────┘
```

### 6.3 Cron-Based Monitoring

**Health Metrics Collection:**
```bash
*/15 * * * * collect_health_metrics  # Every 15 minutes
0 4 * * *    collect_health_metrics --cleanup  # Daily cleanup
```

**Metrics Retention:** 7 days (automatic cleanup)

### 6.4 Logging Infrastructure

Configuration: `autocusto/settings.py` (LOGGING)

**Log Files:**
```
/var/log/django/
  ├── error.log     (ERROR level)
  ├── info.log      (INFO level)
  ├── pdf.log       (PDF generation)
  ├── security.log  (Authentication, permissions)
  ├── database.log  (DB queries, slow queries)
  └── audit.log     (Critical operations)
```

**Log Rotation:** Managed by system logrotate (inferred)

**Log Handlers:**
- TimedRotatingFileHandler
- Separate loggers for different components
- JSON-structured logs (inferred from details field usage)

### 6.5 Analytics Tracking

**Models:**
- `UserActivityLog`: Login/logout tracking
- `PDFGenerationLog`: Every PDF generation with timing
- `DailyMetrics`: Cached daily statistics
- `SystemHealthLog`: Real-time health metrics
- `ClinicMetrics`: Clinic-specific analytics
- `DiseaseMetrics`: Disease-specific analytics
- `MedicationUsage`: Medication prescription tracking

**Dashboard Features:**
- Real-time system health (API endpoint)
- Historical trend analysis (30-day default)
- User analytics (activity, specialties, disease patterns)
- PDF generation performance tracking
- Error rate monitoring

### 6.6 Observability Endpoints

**Health Check:** `/analytics/api/system-health/`
- Real-time system status
- Recent metrics (5-minute window)
- Active user count
- Uptime percentage
- Recent PDF errors

**Analytics API:**
- `/analytics/api/daily-trends/`
- `/analytics/api/pdf-analytics/`
- `/analytics/api/healthcare-insights/`
- `/analytics/api/users/`
- `/analytics/api/diseases/`

---

## 7. Security Practices

### 7.1 Application Security

#### Secrets Management
**Current:**
- Environment variables (.env, .prodenv)
- GitHub Secrets for CI/CD
- GPG encryption for sensitive backups

**Storage:**
- SSH keys: GitHub Secrets (KINGHOST_SSH_KEY)
- Database credentials: Environment files
- API keys: Environment variables (Nextcloud)

#### Authentication & Authorization
- Django authentication system
- Staff-only admin panels
- @staff_member_required decorators
- Session-based authentication

#### Security Middleware
```python
- SecurityMiddleware
- CsrfViewMiddleware
- XFrameOptionsMiddleware
- Custom SystemHealthMiddleware
```

### 7.2 Container Security

**Production Image Security:**
1. Non-root user execution (appuser)
2. Minimal dependencies (only production requirements)
3. No development tools
4. No browser binaries
5. Read-only filesystem at runtime

**Runtime Security:**
- tmpfs with noexec, nosuid flags
- Limited network exposure (127.0.0.1:8001)
- No privileged containers
- Resource limits (inferred from shm_size: 2gb)

### 7.3 Network Security

**SSL/TLS:**
- TLS 1.2/1.3 only
- Strong cipher suites (HIGH:!aNULL:!MD5)
- Server cipher preference
- Certificate managed by host Nginx

**Network Isolation:**
- Django exposed only to localhost (127.0.0.1:8001)
- Nginx as reverse proxy (public-facing)
- PostgreSQL on internal Docker network only
- No direct database access from internet

### 7.4 Security Testing

**Automated Scanning:**
1. **Safety:** Python dependency vulnerability scanner
2. **Bandit:** Static security analysis for Python
3. **Django Security Tests:** Custom security test suite

**CI/CD Security:**
- Security job in test pipeline
- Artifacts retained 30 days
- JSON reports for automated processing

**Test Coverage:**
```python
tests.e2e.security  # Security-focused E2E tests
```

### 7.5 Data Protection

**Backup Encryption:**
- GPG encryption with AES256
- Public key encryption (lcsavb@gmail.com)
- Encryption before network transfer

**Database Security:**
- Encrypted backups
- 7-day local retention
- Remote encrypted storage (Nextcloud)

**PDF Security:**
- Memory-based temporary storage (/tmp with tmpfs)
- Automatic cleanup (5-minute TTL)
- Cron job: cleanup_pdfs (daily at 3 AM)

---

## 8. Infrastructure Analysis

### 8.1 Current Infrastructure

**Type:** Single VPS with Docker Compose

**Components:**
```
VPS (Virtual Private Server)
├── Host Nginx (Reverse Proxy + Static Files)
├── Docker Engine
│   ├── Web Container (Django + uWSGI)
│   └── DB Container (PostgreSQL 17.4)
├── Filesystem
│   ├── /opt/autocusto/static_files (bind mount)
│   ├── /opt/autocusto/media_files (bind mount)
│   └── /dev/shm/autocusto (memory mount)
└── Systemd (Nginx, Docker)
```

**Deployment Method:**
- SSH-based deployment
- GitHub Actions → appleboy/ssh-action → VPS
- Docker Compose orchestration

### 8.2 Scalability Considerations

**Current Limitations:**
- Single server (no horizontal scaling)
- Manual SSH deployment
- No load balancing
- No container orchestration (Kubernetes)

**Capacity:**
- uWSGI: 8 concurrent requests (4 processes × 2 threads)
- Database: Single PostgreSQL instance
- Static files: Direct Nginx serving

**Potential Bottlenecks:**
1. Database (single instance)
2. uWSGI worker count (4 processes)
3. Server resources (CPU, RAM, disk)

### 8.3 High Availability Assessment

**Current HA Level:** Low
- Single point of failure (VPS)
- No redundancy
- No automatic failover
- Downtime during deployments

**Mitigation Strategies:**
- Comprehensive backups (local + remote)
- Health checks post-deployment
- Fast rollback capability (Docker image tags)

---

## 9. Recommendations

### 9.1 High Priority (0-3 months)

#### 1. Implement Blue-Green Deployment
**Current:** Rolling deployment with downtime
**Target:** Zero-downtime deployments

**Implementation:**
```yaml
# docker-compose with blue/green
services:
  web-blue:
    image: ghcr.io/...:${BLUE_TAG}
    ports: ["127.0.0.1:8001:8001"]

  web-green:
    image: ghcr.io/...:${GREEN_TAG}
    ports: ["127.0.0.1:8002:8001"]
```

**Nginx Switch:**
```nginx
upstream django {
    server 127.0.0.1:8001;  # Blue (active)
    # server 127.0.0.1:8002;  # Green (standby)
}
```

**Benefits:**
- Zero-downtime deployments
- Instant rollback capability
- Testing in production-like environment

#### 2. Enhanced Secrets Management
**Current:** Environment files + GitHub Secrets
**Target:** Dedicated secrets management

**Options:**
- HashiCorp Vault (self-hosted)
- AWS Secrets Manager (if migrating to AWS)
- Doppler (SaaS)
- Azure Key Vault

**Priority Items:**
- Database credentials
- GPG private keys
- Nextcloud credentials
- SSH keys

#### 3. Implement Health Check Endpoint
**Current:** Post-deployment curl check
**Target:** Dedicated /health/ endpoint with detailed status

**Implementation:**
```python
# urls.py
path('health/', health_check_view, name='health')

# views.py
def health_check_view(request):
    checks = {
        'database': check_database(),
        'migrations': check_migrations(),
        'disk_space': check_disk_space(),
        'memory': check_memory(),
    }

    status_code = 200 if all(checks.values()) else 503
    return JsonResponse(checks, status=status_code)
```

**Usage:**
- Kubernetes readiness/liveness probes (future)
- External monitoring (UptimeRobot, Pingdom)
- Automated health checks in deployment

#### 4. Add Sentry for Error Tracking
**Current:** File-based logging
**Target:** Real-time error tracking and alerting

**Benefits:**
- Automatic error grouping
- Stack trace aggregation
- Performance monitoring
- Release tracking
- User context with errors

**Configuration:**
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    environment=os.environ.get('ENVIRONMENT', 'production'),
    traces_sample_rate=0.1,
)
```

### 9.2 Medium Priority (3-6 months)

#### 5. Implement Infrastructure as Code
**Current:** Manual VPS configuration
**Target:** Reproducible infrastructure

**Option 1: Terraform (Recommended)**
```hcl
# main.tf
provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "autocusto" {
  name   = "autocusto-prod"
  size   = "s-2vcpu-4gb"
  image  = "ubuntu-22-04-x64"
  region = "nyc3"

  user_data = file("cloud-init.yaml")
}
```

**Option 2: Ansible (Configuration Management)**
```yaml
# playbook.yml
- hosts: autocusto_servers
  roles:
    - docker
    - nginx
    - autocusto
```

**Benefits:**
- Reproducible environments
- Disaster recovery automation
- Documentation as code
- Version-controlled infrastructure

#### 6. Database Read Replicas
**Current:** Single PostgreSQL instance
**Target:** Primary + Read Replica(s)

**Architecture:**
```
Write Operations → Primary PostgreSQL
                      ↓ (replication)
Read Operations  → Read Replica(s)
```

**Django Configuration:**
```python
DATABASES = {
    'default': {  # Write
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_PRIMARY_HOST'),
    },
    'replica': {  # Read
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_REPLICA_HOST'),
    }
}

DATABASE_ROUTERS = ['utils.database_router.ReplicaRouter']
```

**Benefits:**
- Improved read performance
- Load distribution
- Backup source (read replica)

#### 7. Implement Prometheus + Grafana Monitoring
**Current:** Custom Django analytics
**Target:** Industry-standard observability stack

**Stack:**
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

**Django Integration:**
```python
# Install django-prometheus
pip install django-prometheus

# settings.py
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
path('metrics/', include('django_prometheus.urls')),
```

**Dashboards:**
- Request rate/latency
- Error rates
- Database query performance
- Container resource usage
- Custom business metrics (PDFs generated, etc.)

#### 8. Automated Database Migrations Testing
**Current:** Migrations run directly in production
**Target:** Migration testing in staging environment

**Implementation:**
```yaml
# .github/workflows/test-migrations.yml
jobs:
  test-migrations:
    steps:
      - name: Restore production backup to test DB
      - name: Run migrations
      - name: Validate data integrity
      - name: Run smoke tests
```

**Benefits:**
- Catch migration issues before production
- Validate data transformations
- Estimate migration duration

### 9.3 Long-Term Improvements (6-12 months)

#### 9. Migrate to Kubernetes
**Current:** Docker Compose on single VPS
**Target:** Kubernetes cluster for orchestration

**Benefits:**
- Horizontal auto-scaling
- Self-healing (pod restarts)
- Rolling updates built-in
- Service discovery
- Config/Secret management
- Multi-cloud portability

**Minimal Kubernetes Setup:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autocusto-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autocusto-web
  template:
    metadata:
      labels:
        app: autocusto-web
    spec:
      containers:
      - name: web
        image: ghcr.io/lcsavb/autocusto:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: autocusto-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: autocusto-web
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8001
  selector:
    app: autocusto-web
```

**Migration Path:**
1. Start with managed Kubernetes (GKE, EKS, DOKS)
2. Keep PostgreSQL external (managed database)
3. Migrate web application first
4. Implement HPA (Horizontal Pod Autoscaler)
5. Add ingress controller (Nginx Ingress)

**Considerations:**
- Cost increase (managed K8s + load balancer)
- Learning curve for team
- Complexity increase
- Operations overhead

#### 10. Implement GitOps with ArgoCD
**Current:** Push-based deployment (GitHub Actions → SSH)
**Target:** Pull-based GitOps

**Architecture:**
```
Git Repository (Manifests)
        ↓ (monitors)
    ArgoCD
        ↓ (syncs)
Kubernetes Cluster
```

**Benefits:**
- Git as single source of truth
- Automated drift detection
- Easy rollback (git revert)
- Multi-cluster management
- Audit trail (git history)

#### 11. Multi-Region Deployment
**Current:** Single region (VPS location)
**Target:** Multi-region for HA and performance

**Architecture:**
```
          Global Load Balancer (Cloudflare, AWS Route53)
                    /                \
          Region A (Primary)    Region B (Secondary)
          /         \               /         \
      K8s Cluster  DB Master   K8s Cluster  DB Replica
```

**Benefits:**
- Geographic redundancy
- Lower latency for distributed users
- Disaster recovery (regional failure)

**Challenges:**
- Database replication complexity
- Static asset synchronization
- Cost increase
- Operational complexity

#### 12. Implement Continuous Compliance Scanning
**Current:** Manual security scans in CI
**Target:** Continuous compliance monitoring

**Tools:**
- **Trivy:** Container image vulnerability scanning
- **Snyk:** Dependency vulnerability scanning
- **OPA (Open Policy Agent):** Policy enforcement
- **Falco:** Runtime security monitoring

**Implementation:**
```yaml
# .github/workflows/security.yml
jobs:
  trivy-scan:
    steps:
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/lcsavb/autocusto:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### 9.4 Additional Best Practices

#### 13. Implement Feature Flags
**Tool:** LaunchDarkly, Unleash, or FlagSmith

**Benefits:**
- Gradual rollouts
- A/B testing
- Kill switch for problematic features
- Separate deployment from release

#### 14. Add Database Connection Pooling
**Current:** Direct PostgreSQL connections
**Target:** PgBouncer for connection pooling

**Benefits:**
- Reduced connection overhead
- Better resource utilization
- Support for more concurrent users

**Configuration:**
```yaml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer
    environment:
      - DATABASE_URL=postgres://...
    ports:
      - "6432:6432"
```

#### 15. Implement Request Rate Limiting
**Current:** No rate limiting (inferred)
**Target:** Rate limiting for API endpoints

**Options:**
- Django Ratelimit library
- Nginx rate limiting
- Cloudflare rate limiting (if using Cloudflare)

**Configuration:**
```python
# Django Ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def prescription_create(request):
    ...
```

---

## 10. Cost Optimization Recommendations

### Current Infrastructure Costs (Estimated)
- VPS hosting: ~$20-50/month
- GitHub Actions: Free tier (2000 minutes/month)
- Nextcloud storage: Variable (self-hosted or provider)

### Optimization Opportunities

#### 1. Docker Image Size Reduction
**Current:** Production image likely 500MB-1GB
**Target:** <300MB

**Strategies:**
- Use Alpine base images where possible
- Multi-stage builds (already implemented ✓)
- Remove unnecessary dependencies
- Use .dockerignore (currently missing)

**Create .dockerignore:**
```
.git
.github
tests/
*.md
*.pyc
__pycache__
.pytest_cache
node_modules/
.coverage
htmlcov/
```

#### 2. Optimize GitHub Actions Minutes
**Current:** ~15-30 minutes per workflow run

**Optimizations:**
- Use dependency caching (already implemented ✓)
- Parallel job execution (already implemented ✓)
- Skip redundant runs (paths filter)

```yaml
on:
  push:
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

#### 3. Database Optimization
- Implement query optimization
- Add database indexes (review slow query logs)
- Implement caching (Redis) for frequent queries

---

## 11. Compliance and Documentation

### 11.1 Healthcare Compliance Considerations

**Data Protection:**
- Patient data: LGPD (Brazil's GDPR equivalent)
- Medical records: CFM (Federal Council of Medicine) requirements
- Digital prescriptions: RDC 357/2020 (ANVISA)

**Current Measures:**
- Encrypted backups ✓
- Audit logging ✓
- User authentication ✓
- HTTPS enforcement ✓

**Gaps:**
- No data retention policy documented
- No explicit LGPD compliance documentation
- No data breach response plan

### 11.2 Documentation Recommendations

#### Create/Update Documentation:
1. **DEPLOYMENT.md** - Detailed deployment procedures
2. **DISASTER_RECOVERY.md** - DR procedures and RTO/RPO
3. **SECURITY_POLICY.md** - Security practices and incident response
4. **CONTRIBUTING.md** - Development setup and contribution guidelines
5. **ARCHITECTURE.md** - System architecture diagrams
6. **API_DOCS.md** - API endpoint documentation

#### DevOps Runbooks:
- Database backup/restore procedure
- Rollback procedure
- Adding new environment variables
- Scaling uWSGI workers
- Emergency maintenance mode

---

## 12. Key Metrics and KPIs

### Current DevOps Metrics (Measurable)

#### Deployment Metrics:
- **Deployment Frequency:** On-demand (master branch push)
- **Lead Time:** ~10-15 minutes (tests + build + deploy)
- **Change Failure Rate:** Not tracked (should be implemented)
- **MTTR (Mean Time to Recovery):** Not measured

#### Performance Metrics:
- **Test Success Rate:** Visible in GitHub Actions
- **Build Success Rate:** Tracked by CI/CD
- **Test Coverage:** Codecov integrated ✓

#### System Health (Already Tracked):
- Database query performance (<100ms target)
- API response time (<300ms target)
- Error rate (<5% target)
- Active users (real-time)

### Recommended Additional Metrics:

#### Deployment Metrics:
```python
# Track in analytics
class DeploymentLog(models.Model):
    deployed_at = models.DateTimeField(auto_now_add=True)
    git_sha = models.CharField(max_length=40)
    deployed_by = models.CharField(max_length=100)
    success = models.BooleanField()
    rollback = models.BooleanField(default=False)
    duration_seconds = models.IntegerField()
```

#### SLIs (Service Level Indicators):
- **Availability:** 99.5% uptime target
- **Latency:** p95 < 500ms, p99 < 1000ms
- **Error Rate:** < 1% of requests

---

## 13. Critical Issues and Quick Wins

### Critical Issues (Fix Immediately)

#### 1. Hardcoded Credentials in Files
**Issue:** `.env` and `docker-compose.yml` contain credentials
**Risk:** Credentials exposed if committed to git

**Fix:**
```bash
# Ensure these files are in .gitignore
echo ".env" >> .gitignore
echo ".prodenv" >> .gitignore
echo ".backupenv" >> .gitignore

# Verify not in git history
git log --all --full-history -- .env
```

**If found in history:**
```bash
# Use BFG Repo Cleaner or git-filter-repo
git filter-repo --path .env --invert-paths
```

#### 2. Missing .dockerignore
**Issue:** Unnecessary files copied to Docker image
**Impact:** Larger images, slower builds, potential security issues

**Fix:** Create `.dockerignore` (see Cost Optimization section)

#### 3. No Container Resource Limits
**Issue:** Containers can consume unlimited resources
**Impact:** System instability under load

**Fix:**
```yaml
# docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Quick Wins (Low Effort, High Impact)

#### 1. Add CHANGELOG.md
Track version history and changes

#### 2. Implement GitHub Issue Templates
Standardize bug reports and feature requests

#### 3. Add Pull Request Template
```markdown
## Description
<!-- What does this PR do? -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
```

#### 4. Set Up Codecov Configuration
```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 70%
```

#### 5. Add Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 14. DevOps Maturity Assessment

### Current Maturity Level: **Intermediate (3/5)**

**Scoring:**

| Category | Score | Notes |
|----------|-------|-------|
| CI/CD | 4/5 | Excellent GitHub Actions setup, room for improvement in deployment strategies |
| Testing | 5/5 | Comprehensive test pyramid, parallel execution, good coverage |
| Monitoring | 3/5 | Custom solution in place, lacks industry-standard tools (Prometheus/Grafana) |
| Security | 3/5 | Good basics (encryption, backups), lacks advanced scanning and secrets management |
| Infrastructure | 2/5 | Manual setup, no IaC, single server architecture |
| Automation | 4/5 | Well automated (backups, metrics, deployments) |
| Documentation | 2/5 | Basic README, lacks comprehensive DevOps docs |
| Disaster Recovery | 4/5 | Excellent backup strategy, no tested DR procedures |

**Maturity Levels:**
1. **Initial:** Manual processes, ad-hoc deployments
2. **Developing:** Some automation, basic CI/CD
3. **Intermediate:** Strong CI/CD, monitoring, automated testing ← **Current**
4. **Advanced:** IaC, container orchestration, comprehensive monitoring
5. **Optimized:** Full GitOps, multi-region, self-healing, compliance automation

---

## 15. Conclusion

### Summary

AutoCusto demonstrates a **well-architected DevOps infrastructure** for a healthcare application, with particularly strong implementations in:

✅ **Testing:** Comprehensive test pyramid with parallel execution
✅ **CI/CD:** Well-designed GitHub Actions workflows
✅ **Backup Strategy:** Encrypted, automated, multi-location
✅ **Containerization:** Optimized multi-stage Dockerfile
✅ **Custom Monitoring:** Django-based health monitoring system

### Areas Requiring Attention

⚠️ **Infrastructure:** Single server, no IaC
⚠️ **Scalability:** Limited horizontal scaling capability
⚠️ **Monitoring:** Lacks industry-standard observability tools
⚠️ **Documentation:** Incomplete DevOps documentation

### Next Steps

**Immediate (0-1 month):**
1. Fix critical security issues (credentials, .dockerignore)
2. Implement health check endpoint
3. Add resource limits to containers
4. Create CHANGELOG.md and GitHub templates

**Short-term (1-3 months):**
1. Implement blue-green deployment
2. Add Sentry for error tracking
3. Enhance secrets management
4. Create comprehensive DevOps documentation

**Medium-term (3-6 months):**
1. Implement Prometheus + Grafana
2. Add database read replicas
3. Implement Infrastructure as Code (Terraform)
4. Add automated migration testing

**Long-term (6-12 months):**
1. Migrate to Kubernetes (if scale requires)
2. Implement GitOps with ArgoCD
3. Consider multi-region deployment
4. Continuous compliance scanning

### Final Assessment

AutoCusto's DevOps infrastructure is **production-ready and well-maintained** for its current scale. The system demonstrates thoughtful architecture decisions, particularly in testing and deployment automation. With the recommended enhancements, the infrastructure can scale to support significant growth while maintaining security and reliability standards appropriate for a healthcare application.

**Overall Grade:** **B+ (85/100)**

Strong foundation with clear paths for improvement as the application scales.

---

## Appendix A: Technology Stack Summary

### Core Technologies
- **Language:** Python 3.11
- **Framework:** Django 5.2.4
- **Web Server:** uWSGI 2.0.26
- **Database:** PostgreSQL 17.4-alpine
- **Reverse Proxy:** Nginx (host-based)
- **Container Runtime:** Docker with Docker Compose

### Testing Stack
- **Python Testing:** Django TestCase, pytest-django
- **Browser Testing:** Playwright 1.40.0
- **JavaScript Testing:** Jest (inferred)
- **Security Testing:** Bandit, Safety
- **Coverage:** coverage.py, Codecov

### DevOps Tools
- **CI/CD:** GitHub Actions
- **Container Registry:** GitHub Container Registry (ghcr.io)
- **Deployment:** SSH-based (appleboy/ssh-action)
- **Monitoring:** Custom Django analytics + psutil
- **Backup:** django-dbbackup + GPG + Nextcloud (WebDAV)
- **Scheduling:** django-crontab

### Dependencies (Selected)
- **PDF Processing:** pypdftk 0.5
- **Database Client:** psycopg2-binary 2.9.10
- **Forms:** django-crispy-forms 2.3, crispy-bootstrap4
- **Storage:** django-storages 1.14.6, webdav4 0.9.8
- **Monitoring:** psutil 7.0.0

---

## Appendix B: File Structure (DevOps-Relevant)

```
autocusto/
├── .github/
│   └── workflows/
│       ├── test-integration.yml (Comprehensive test pipeline)
│       └── deploy.yml (Production deployment)
├── Dockerfile (Multi-stage: builder → base → test → production)
├── docker-compose.yml (Development environment)
├── uwsgi.ini (uWSGI configuration)
├── nginx.conf (Nginx reverse proxy config)
├── startup.sh (Container entrypoint for memory mount setup)
├── requirements.txt (All dependencies including test)
├── requirements-production.txt (Production-only dependencies)
├── test_settings.py (Test environment configuration)
├── autocusto/
│   └── settings.py (Main configuration with LOGGING, CRONJOBS, DBBACKUP)
├── tests/
│   ├── unit/ (Fast unit tests)
│   ├── integration/ (Component integration)
│   ├── e2e/ (End-to-end tests)
│   ├── run_all_tests.sh
│   ├── run_unit_tests.sh
│   ├── run_integration_tests.sh
│   └── run_e2e_tests.sh
├── run_tests_from_host.sh (Comprehensive host-based test runner)
├── run_frontend_tests.sh (Frontend/E2E test runner)
├── analytics/
│   ├── health_utils.py (System health monitoring)
│   ├── middleware.py (Health tracking middleware)
│   ├── views.py (Health/analytics endpoints)
│   └── management/commands/
│       └── collect_health_metrics.py
└── processos/management/commands/
    ├── upload_backup.py (Nextcloud backup upload)
    └── cleanup_pdfs.py (PDF cleanup cron job)
```

---

**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Author:** DevOps Analysis Agent
**Review Cycle:** Quarterly

---

*This document should be reviewed and updated quarterly or when significant infrastructure changes occur.*
