# AutoCusto Project Technical Infrastructure Guide

This prompt is to make you aware of my project infrastructure, so you can help me effectively with development, deployment, debugging, and maintenance tasks.

## Project Overview

You are working with **AutoCusto**, a Django-based web application that specializes in automated PDF generation. The system's core technical challenge is efficiently generating complex PDFs with UTF-8 support while maintaining high performance through memory optimization.

## Tech Stack & Architecture

### Core Technologies
- **Backend**: Django 5.2.4 (Python 3.11)
- **Database**: PostgreSQL 17.4
- **PDF Engine**: pypdftk with custom memory optimization
- **Frontend**: Bootstrap 4 + Django Crispy Forms
- **Containerization**: Docker + Docker Compose
- **Web Server**: uWSGI + Nginx with SSL
- **CI/CD**: GitHub Actions with container registry
- **Backup**: GPG-encrypted automated backups to Nextcloud

### Django Application Structure

When working with this project, you'll encounter these main Django apps:

- **`usuarios/`** - Custom email-based authentication system
- **`medicos/`** - Doctor profile management 
- **`clinicas/`** - Medical facility management
- **`pacientes/`** - Patient record management
- **`processos/`** - **Core business logic** (main app you'll work with most)
- **`logica_raw/`** - Legacy disease-specific modules (being refactored)

### Key Models You Should Know

The database schema centers around these relationships:
```
Usuario (Custom User) ←→ Medico ←→ Clinica
                          ↓
                       Emissor (Doctor-Clinic combo)
                          ↓
                       Processo (Central business entity)
                          ↓
                   Paciente + Doenca + Medicamento
```

**Critical Model**: `Processo` in `processos/models.py` - This is the central entity with a unique constraint: `['usuario', 'paciente', 'doenca']`

## PDF Generation System (Core Technical Feature)

### Clean Service Architecture (Updated 2025)
The PDF generation system follows SOLID principles with proper separation of concerns:

### **📁 Architecture Layers**

#### **1. Pure PDF Infrastructure (`processos/pdf_operations.py`)**
- **`PDFGenerator`** - Core pypdftk operations (fill forms, concatenate)
- **`PDFResponseBuilder`** - HTTP response creation with security headers
- **Zero business logic** - completely domain-agnostic
- **Memory Optimized**: Uses `/dev/shm` (tmpfs) for all PDF operations
- **UTF-8 Support**: Leverages pypdftk's custom FDF generation for special characters

#### **2. Medical Business Logic (`processos/prescription_services.py`)**
- **`PrescriptionDataFormatter`** - Medical data privacy rules & Brazilian date formatting
- **`PrescriptionTemplateSelector`** - Protocol-based template selection for diseases/medications
- **`PrescriptionPDFService`** - Complete prescription PDF generation workflow
- **`PrescriptionService`** - Full prescription business workflow (database + PDF coordination)
- **`RenewalService`** - Prescription renewal business logic with specific medical rules

#### **3. Utility Functions (`processos/dados.py`)**
- **Database Operations**: `registrar_db()`, `checar_paciente_existe()`
- **Data Transformations**: `gera_med_dosagem()`, `vincula_dados_emissor()`
- **Medical Business Logic**: `listar_med()`, `gerar_dados_renovacao()`
- **Helper Functions**: Called by services for specific data operations

#### **4. View Layer (HTTP Infrastructure)**
- **File I/O Operations**: `_save_pdf_for_serving()` in views
- **HTTP Request/Response**: Handles web requests and JSON responses
- **URL Generation**: Creates serving URLs for PDF downloads

### **🔧 Critical PDF Generation Fix**
**Problem Solved**: `pypdftk.concat()` flattens forms by default, removing fillable fields.

**Solution**: 
1. **Fill each PDF template individually** with form data
2. **Concatenate the filled PDFs** into final document
3. Ensures consentimento, exames, and relatorio forms are properly filled

### **Key Technical Components**
- **`processos/pdf_operations.py`** - Pure PDF infrastructure (no business logic)
- **`processos/prescription_services.py`** - Medical prescription business logic
- **`processos/dados.py`** - Utility functions for data operations
- **`processos/pdf_strategies.py`** - `DataDrivenStrategy` for protocol-based template selection
- **`processos/manejo_pdfs_memory.py`** - Legacy (kept for safety during migration)
- **`startup.sh`** - Copies PDF templates to `/dev/shm` on container start
- **Template Directory**: `static/autocusto/protocolos/` and `static/autocusto/processos/`

### Memory Mount System
```bash
# Container startup copies templates to RAM
mkdir -p /dev/shm/autocusto/static/processos
mkdir -p /dev/shm/autocusto/static/protocolos
cp -r /static/templates/* /dev/shm/autocusto/static/
```

### **🏗️ Working with the New Architecture**

#### **Creating New Prescription Workflows**
```python
# In views - use PrescriptionService
from processos.prescription_services import PrescriptionService

prescription_service = PrescriptionService()
pdf_response, processo_id = prescription_service.create_or_update_prescription(
    form_data=dados_formulario,
    user=usuario,
    medico=medico,
    clinica=clinica,
    patient_exists=paciente_existe,
    process_id=None  # None for new, ID for updates
)

# View layer handles file I/O
if pdf_response:
    pdf_url = _save_pdf_for_serving(pdf_response, dados_formulario)
```

#### **Creating Renewals**
```python
# Use RenewalService for renewals
from processos.prescription_services import RenewalService

renewal_service = RenewalService()
pdf_response = renewal_service.process_renewal(nova_data, processo_id, usuario)
```

#### **Direct PDF Generation** 
```python
# For custom PDF generation
from processos.prescription_services import PrescriptionPDFService

pdf_service = PrescriptionPDFService()
response = pdf_service.generate_prescription_pdf(prescription_data)
```

#### **Adding New Business Logic**
- **Medical logic** → Add to `prescription_services.py`
- **Pure PDF operations** → Add to `pdf_operations.py` 
- **Data utilities** → Add to `dados.py`
- **File I/O** → Handle in views with `_save_pdf_for_serving()`

#### **Architecture Rules**
1. **PDF operations** must be domain-agnostic (no medical knowledge)
2. **Services** contain business logic but no file I/O
3. **Views** handle HTTP concerns and file operations
4. **Utilities** provide reusable data transformation functions

## Development Environment

### Local Setup Commands
```bash
# Start development stack
docker-compose up -d

# Access application
http://localhost:8001

# Container access
docker-compose exec web bash
docker-compose exec db psql -U lucas autocusto

# Common Django commands
python manage.py migrate
python manage.py shell
python manage.py collectstatic
```

### Key Configuration Files
- **Django Settings**: `autocusto/settings.py`
- **Docker Development**: `docker-compose.yml`
- **Container Build**: `Dockerfile`
- **Web Server**: `uwsgi.ini`
- **Startup Logic**: `startup.sh`
- **Dependencies**: `requirements.txt`

### Development Workflow Tools
```bash
# Testing
make test-all
make test-security 
make test-frontend
python manage.py test tests.session_functionality

# PDF System
python manage.py cleanup_pdfs

# Database Operations
python manage.py dbbackup
python manage.py upload_backup

# Cron Jobs (django-crontab)
python manage.py crontab add
python manage.py crontab show
python manage.py crontab remove
```

## Production Deployment Architecture

### Container Infrastructure
- **Registry**: GitHub Container Registry (`ghcr.io`)
- **VPS Location**: `/opt/autocusto`
- **Web Server**: Nginx reverse proxy with SSL termination
- **Database**: Containerized PostgreSQL with persistent volumes

### CI/CD Pipeline (.github/workflows/deploy.yml)
1. **Test Stage**: PostgreSQL service + dependency installation
2. **Build Stage**: Multi-stage Docker build to registry
3. **Deploy Stage**: SSH to VPS + dynamic docker-compose generation
4. **Production Setup**: GPG key import + container restart + migrations

### Production Environment Configuration

**Environment Files**:
- **Development**: `.backupenv` (debug mode, local settings)
- **Production**: `.prodenv` (SSL enforced, security headers)

**Key Production Settings**:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### Production Docker Compose (Auto-generated)
```yaml
services:
  web:
    image: ghcr.io/repo:commit-sha
    volumes:
      - static_volume:/home/appuser/app/static_root
      - /var/backups/autocusto:/var/backups/autocusto
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
  db:
    image: postgres:17.4-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
```

## Automated Backup System

### Cron Configuration (django-crontab)
```python
# In settings.py
CRONJOBS = [
    ('0 3 * * *', 'django.core.management.call_command', ['cleanup_pdfs']),
    ('0 2 * * *', 'django.core.management.call_command', ['dbbackup']),
    ('15 2 * * *', 'django.core.management.call_command', ['upload_backup']),
]
```

### Backup Process Technical Flow
1. **Database Dump**: PostgreSQL backup to `/var/backups/autocusto/`
2. **GPG Encryption**: Files encrypted with `lcsavb@gmail.com` public key
3. **Nextcloud Upload**: WebDAV upload via `webdav4` client
4. **Local Cleanup**: Encrypted files removed after successful upload
5. **Retention**: 7 days local, permanent remote storage

### GPG Key Management
- **Host Location**: `/root/lucas-backup-public.asc`
- **Container Import**: Done during deployment via SSH
- **Encryption Command**: `gpg --encrypt -r lcsavb@gmail.com --output file.gpg file`

## Important Technical Patterns

### Memory Management for PDFs
```python
# PDF generation uses memory optimization
def preencher_formularios_memory(template_path, fields_dict):
    # Uses /dev/shm for temporary files
    # Immediate cleanup after generation
    # UTF-8 FDF generation for special characters
```

### Database Transactions
```python
# Critical operations use atomic transactions
@transaction.atomic
def create_processo(user, patient, disease):
    # Ensures data consistency
```

### Container Security
- **Non-root user**: `appuser` (UID/GID management)
- **Tmpfs mounts**: `/tmp` and `/dev/shm` with security flags
- **Volume permissions**: Proper ownership for backup directories

## Development Guidelines When Working With This Project

### PDF Generation Development
1. **Always test memory mount**: Check `/dev/shm` availability
2. **UTF-8 handling**: Use specialized FDF functions for special characters
3. **Template paths**: Verify templates exist in memory mount
4. **Cleanup**: Ensure temporary files are removed

### Database Development
1. **Migration safety**: Test with production-like data
2. **Model constraints**: Respect unique constraints on core models
3. **Transaction boundaries**: Use atomic decorators for multi-model operations

### Container Development
1. **Layer efficiency**: Minimize Docker layer changes
2. **Security**: Maintain non-root user execution
3. **Volume mounts**: Consider development vs production differences

### Deployment Considerations
1. **Environment parity**: Test with production-like settings
2. **SSL certificates**: Verify certificate paths and renewal
3. **Backup validation**: Test GPG encryption and Nextcloud connectivity

## Troubleshooting Reference

### PDF Generation Issues
```bash
# Check memory mount status
df -h /dev/shm
ls -la /dev/shm/autocusto/static/

# Test PDF templates accessibility
docker-compose exec web ls -la /dev/shm/autocusto/static/protocolos/

# Debug PDF generation
docker-compose exec web python manage.py shell
>>> from processos.manejo_pdfs_memory import GeradorPDF
```

### Database Issues
```bash
# Check PostgreSQL connectivity
docker-compose exec db pg_isready
docker-compose exec web python manage.py dbshell

# Migration status
python manage.py showmigrations
python manage.py migrate --plan
```

### Backup System Issues
```bash
# Test GPG setup
docker-compose exec web gpg --list-keys lcsavb@gmail.com

# Manual backup test
docker-compose exec web python manage.py dbbackup
docker-compose exec web python manage.py upload_backup

# Check cron status
python manage.py crontab show
```

### SSL/Nginx Issues
```bash
# Verify certificate files (production)
ls -la /opt/autocusto/ssl/

# Test Nginx configuration
docker-compose exec nginx nginx -t

# Check SSL connectivity
curl -I https://domain.com
```

### Container Issues
```bash
# Container resource usage
docker stats

# Service logs
docker-compose logs web
docker-compose logs nginx
docker-compose logs db

# Container access for debugging
docker-compose exec web bash
```

## Key File Locations You'll Work With

### Core Application Files
- **Main Settings**: `autocusto/settings.py`
- **URL Configuration**: `autocusto/urls.py`
- **Pure PDF Infrastructure**: `processos/pdf_operations.py` ⭐ *New Clean Architecture*
- **Medical Business Logic**: `processos/prescription_services.py` ⭐ *New Clean Architecture*
- **Utility Functions**: `processos/dados.py`
- **PDF Template Selection**: `processos/pdf_strategies.py`
- **Business Models**: `processos/models.py`
- **Form Handling**: `processos/forms.py`
- **View Logic**: `processos/views.py`
- **Legacy PDF Logic**: `processos/manejo_pdfs_memory.py` *(kept for safety)*

### Infrastructure Files
- **Docker Config**: `docker-compose.yml`, `Dockerfile`
- **CI/CD Pipeline**: `.github/workflows/deploy.yml`
- **Web Server**: `nginx.conf`, `uwsgi.ini`
- **Container Startup**: `startup.sh`
- **Dependencies**: `requirements.txt`

### Data and Templates
- **PDF Templates**: `static/autocusto/protocolos/`, `static/autocusto/processos/`
- **Test Suite**: `tests/` (security, frontend, integration)
- **Database Seeding**: `processos/db/` (diseases, protocols, medications)

## Performance Considerations

### Memory Usage
- **PDF Operations**: Monitor `/dev/shm` utilization (100MB allocated)
- **Database Connections**: PostgreSQL connection pooling
- **Static Files**: WhiteNoise for production serving

### Optimization Strategies
- **PDF Caching**: Short-lived cache for immediate serving
- **Memory Mount**: Eliminates disk I/O during PDF generation
- **Container Resources**: uWSGI worker configuration

## Security Awareness

### Sensitive Data Handling
- **Healthcare Data**: Ensure proper access controls
- **Document Validation**: Validate all input data
- **Backup Encryption**: GPG encryption for all backups
- **Session Security**: CSRF protection and secure cookies

### Production Security
- **SSL Enforcement**: HTTPS required in production
- **Security Headers**: XSS protection, frame options, HSTS
- **Input Validation**: Extensive form validation
- **Container Security**: Non-root execution, tmpfs isolation

## Development Best Practices

### Exception Handling
- **Always add django messages**: When handling exceptions, use Django's messaging framework to provide user-friendly feedback

Remember: This system handles sensitive data and must maintain high security, performance, and reliability standards. Always consider the memory-optimized PDF generation as the core technical challenge when making changes.

---

# 🏗️ Major Architecture Refactoring (2025)

## Overview of Changes

A comprehensive refactoring was completed to implement clean architecture principles, following SOLID design patterns and proper separation of concerns. The changes transformed a monolithic, tightly-coupled system into a maintainable, testable service-oriented architecture.

## 🎯 Key Achievements

### ✅ **Clean Service Architecture Implementation**
- **Before**: Mixed business logic, PDF operations, and HTTP concerns in views
- **After**: Proper separation with dedicated service layers following Single Responsibility Principle

### ✅ **Critical PDF Bug Fix** 
- **Issue**: `pypdftk.concat()` was flattening PDF forms, preventing form filling
- **Solution**: Fill forms individually first, then concatenate filled PDFs
- **Impact**: Fixed broken consentimento forms and other fillable PDFs

### ✅ **View Simplification**
- **Before**: Views with 100+ lines of complex setup logic
- **After**: Clean views with ~25 lines focused only on HTTP concerns

### ✅ **Comprehensive Test Coverage**
- Created test suite for new service architecture
- Added smoke tests to verify refactored views work correctly
- All tests passing with proper error handling validation

### ✅ **Improved Code Organization**
- Renamed `dados.py` → `helpers.py` for better clarity and intent
- Updated all import statements across the codebase
- Maintained all English translation comments and functionality

## 📁 New Architecture Files Created

### **Core Service Files**
```
processos/
├── pdf_operations.py         # Pure PDF infrastructure (no business logic)
├── prescription_services.py  # Medical business logic services  
├── view_services.py          # View setup and data preparation services
└── pdf_strategies.py         # Existing - Protocol-based template selection
```

### **Test Files**  
```
tests/
├── test_pdf_services_basic.py    # Basic service functionality tests
└── test_refactoring_smoke.py     # Integration and smoke tests
```

## 🔧 Service Layer Architecture

### **1. PDF Operations Layer** (`pdf_operations.py`)
**Pure infrastructure with zero business logic**
```python
class PDFGenerator:
    def fill_and_concatenate(self, template_paths: List[str], form_data: dict) -> Optional[bytes]:
        """CRITICAL: Fill each PDF individually, then concatenate filled PDFs
        (pypdftk.concat flattens forms by default)"""

class PDFResponseBuilder:
    def build_response(self, pdf_bytes: bytes, filename: str) -> HttpResponse:
        """Build HTTP response for PDF serving"""
```

### **2. Prescription Services Layer** (`prescription_services.py`)
**Medical business logic with healthcare domain knowledge**
```python
class PrescriptionDataFormatter:
    """Brazilian healthcare privacy rules and date formatting"""
    
class PrescriptionTemplateSelector:
    """Disease protocol-based template selection"""
    
class PrescriptionPDFService:
    """Complete prescription PDF generation workflow"""
    
class PrescriptionService:
    """Full prescription business workflow (database + PDF)"""
    
class RenewalService:
    """Prescription renewal business logic"""
```

### **3. View Services Layer** (`view_services.py`)
**View setup and data preparation services**
```python
class PrescriptionViewSetupService:
    def setup_for_new_prescription(self, request) -> SetupResult
    def setup_for_edit_prescription(self, request) -> SetupResult
    """Handles all complex setup logic extracted from views"""
```

## 🔄 Refactored Views

### **Before & After Transformation**

#### **`cadastro` View (New Prescriptions)**
**Before** (~120 lines of complex setup):
```python
def cadastro(request):
    # 50+ lines of user/doctor validation
    # 20+ lines of clinic choices with versioning  
    # 15+ lines of session validation
    # 10+ lines of CID and medication logic
    # 15+ lines of form model creation
    # Complex try/catch blocks throughout
```

**After** (~25 lines of clean logic):
```python
def cadastro(request):
    """Clean view delegating setup to PrescriptionViewSetupService."""
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_new_prescription(request)
    
    if not setup.success:
        messages.error(request, setup.error_message)
        return redirect(setup.error_redirect)
    
    # Extract setup data and focus on HTTP concerns only
```

#### **`edicao` View (Edit Prescriptions)**
**Before** (~130 lines of complex setup):
```python
def edicao(request):
    # All the same complex setup as cadastro
    # Plus process ownership verification
    # Plus initial data preparation from existing process
    # Multiple exception handling blocks
```

**After** (~25 lines of clean logic):
```python  
def edicao(request):
    """Clean view delegating setup to PrescriptionViewSetupService."""
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_edit_prescription(request)
    
    # Same clean pattern as cadastro
```

#### **`renovacao_rapida` View (Quick Renewals)**
**Before** (~80 lines with debug prints):
```python
def renovacao_rapida(request):
    print(f"DEBUG: GET request to renovacao_rapida")
    print(f"DEBUG: busca parameter = '{busca}'") 
    # Multiple print() statements throughout
    # Broad exception handling
    # Duplicated AJAX/non-AJAX response logic
```

**After** (~60 lines with proper logging):
```python
def renovacao_rapida(request):
    """Clean view with proper logging and error handling."""
    logger.info(f"GET request from user: {request.user}")
    # Proper logger statements
    # Clean validation error collection
    # Consolidated response handling
    # All English translation comments preserved
```

## 🧪 Testing Strategy

### **Test Files Overview**
1. **`test_pdf_services_basic.py`** - Unit tests for service functionality
2. **`test_refactoring_smoke.py`** - Integration tests for refactored architecture

### **Test Coverage Results**
- ✅ All service imports and instantiation (6/6 tests)  
- ✅ Basic service functionality (6/6 tests)
- ✅ Service integration (8/8 smoke tests)
- ✅ All refactored views accessible and functional

## 🔍 Debugging Guide for Future Development

### **Key Files for Debugging Issues**

#### **PDF Generation Problems**
1. **Check**: `processos/pdf_operations.py` - Pure PDF infrastructure
2. **Check**: `processos/prescription_services.py` - Business logic coordination
3. **Log**: `processos.pdf` logger for detailed PDF generation logs
4. **Critical**: Ensure templates exist in `/dev/shm` memory mount

#### **View Setup Problems** 
1. **Check**: `processos/view_services.py` - All setup logic centralized here
2. **Check**: Session data validation in `PrescriptionViewSetupService` methods
3. **Log**: Standard Django logger for view-level debugging

#### **Service Layer Problems**
1. **Run**: `python manage.py test tests.test_pdf_services_basic`  
2. **Run**: `python manage.py test tests.test_refactoring_smoke`
3. **Check**: Service instantiation and method availability

### **Legacy vs New Architecture**

#### **Old Files** (⚠️ Gradually being deprecated)
```
processos/
└── manejo_pdfs_memory.py     # Old PDF generation - still used by helpers.py
```

#### **Current Files** (✅ Active architecture)
```
processos/
├── pdf_operations.py         # Pure PDF infrastructure
├── prescription_services.py  # Medical business logic  
├── view_services.py          # View setup services
├── helpers.py                # Utility functions - bridges old/new architecture
└── views.py                  # Clean views using services
```

### **Migration Status**
- ✅ **Views**: `cadastro`, `edicao`, `renovacao_rapida` - Fully refactored
- ✅ **Services**: All new services implemented and tested
- ✅ **PDF Generation**: Critical concatenation bug fixed
- ⚠️ **Legacy Functions**: Kept temporarily in `helpers.py` for compatibility  
- 🔄 **Gradual Migration**: `transfere_dados_gerador` bridges old/new architecture
- ✅ **File Rename**: `dados.py` renamed to `helpers.py` for better clarity

## 💡 Development Guidelines Post-Refactoring

### **For New Features**
1. **Always use the service layer** - Don't put business logic in views
2. **Follow the established patterns** - Use existing services as templates
3. **Write tests first** - Add to `test_pdf_services_basic.py` or create new test files
4. **Keep views thin** - Views should only handle HTTP concerns

### **For Bug Fixes**
1. **Identify the layer** - Is it infrastructure (PDF ops), business logic (services), or HTTP (views)?
2. **Check service tests** - Run relevant tests to ensure services work correctly
3. **Use proper logging** - Follow established logging patterns in each layer

### **For Understanding the System**
1. **Start with service layer** - `prescription_services.py` contains main business workflows
2. **Check view services** - `view_services.py` handles all view setup complexity  
3. **Reference architecture docs** - This section explains the separation of concerns

Remember: The new architecture prioritizes maintainability, testability, and clear separation of concerns. Always consider which layer your changes belong in before implementing.