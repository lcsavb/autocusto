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

### Memory-Optimized Architecture
This is the most technically complex part of the system. The PDF generation uses:

- **RAM Filesystem**: `/dev/shm` (tmpfs) for all PDF operations
- **Memory Streaming**: PDFs generated directly to BytesIO objects
- **UTF-8 Handling**: Custom FDF generation for special characters
- **Template Caching**: PDF templates stored in memory mount

### Key Technical Components
- **`processos/manejo_pdfs_memory.py`** - Core PDF generator class `GeradorPDF`
- **`processos/pdf_strategies.py`** - `DataDrivenStrategy` (new architecture)
- **`startup.sh`** - Copies PDF templates to `/dev/shm` on container start
- **Template Directory**: `static/autocusto/protocolos/` and `static/autocusto/processos/`

### Memory Mount System
```bash
# Container startup copies templates to RAM
mkdir -p /dev/shm/autocusto/static/processos
mkdir -p /dev/shm/autocusto/static/protocolos
cp -r /static/templates/* /dev/shm/autocusto/static/
```

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
- **PDF Core Logic**: `processos/manejo_pdfs_memory.py`
- **PDF Strategies**: `processos/pdf_strategies.py`
- **Business Models**: `processos/models.py`
- **Form Handling**: `processos/forms.py`
- **View Logic**: `processos/views.py`

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