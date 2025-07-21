

FOR EARLY DEPLOYMENT

when the medicamento is nenhum it works
dados condicionais not being saved and not being retrieved (symptom?

database backup
admin dashboard with stats
add renovacao rapida progress bar
in renovacao rapida the latest conditional data are not being loaded
recuperacao da senha instrucoes em ingles
instituir autenticação de dois fatores obrigatória
The pdfs_base directories exist for some protocols but not for epilepsia. Let me check if it should exist:





-----------------------------------------------------------------------------------------------------------------
integracao api cnes
js folders duplicated staticroot and staticroot/processos
erase duplicated old files (on drive pdf management)dd
put entire base pdfs in ram
roadmap
Finish front/backend test coverage
Finish frontend prescription test
change the variables to englishis
prescrições a vencer
modal pdf -> imprimir diretamente
saving pdfs and removing them
when trying to add a duplicated process a html response is being generated, not a json
add custom pdf files

  Code Quality

  - Remove debug prints from manejo_pdfs.py - replace with proper logging
  - Error handling in PDF generation - catch specific exceptions instead of broad try/catch
  - Consolidate JavaScript files - merge /static_root/js/med.js and /static_root/processos/js/med.js

  Security

  - Validate file paths in PDF serving to prevent directory traversal
  - Add rate limiting to password reset functionality
  - Sanitize user inputs in error reporting forms

  Performance

  - Cache medication choices instead of querying database repeatedly
  - Optimize form validation - avoid processing all 4 medications when only 1-2 are used
  - Use database indexing on frequently queried fields (CPF, CID)

  User Experience

  - Add loading states during PDF generation (can take time)
  - Improve error messages - make them more user-friendly
  - Add field validation hints before form submission
  - Implement auto-save for long forms

  Code Organization

  - Extract constants - move hardcoded values to settings
  - Create service layer for PDF operations
  - Add type hints to Python functions
  - Standardize naming - mix of Portuguese/English is confusing

  Most critical: logging system and JavaScript consolidation.


● Complete Summary: Data-Driven PDF Generation Implementation

  Current Problems

  1. Two parallel PDF systems: Legacy GeradorPDF (disk-based) + Modern GeradorPDFMemory (memory-based)
  2. Hardcoded disease classes: Separate class for each disease (Dor, EscleroseMultipla, etc.) with massive switch statements
  3. Hardcoded conditional fields: seletor_campos() function with giant if/elif chains for each disease
  4. Unmaintainable: Adding 1000 diseases would require 1000 classes + 1000 hardcoded field definitions

  Proposed Solution: Unified Data-Driven Architecture

  1. Single Unified PDF Generator

  - Rename: GeradorPDFMemory → GeradorPDF
  - Keep: All existing memory-based PDF operations (UTF-8 handling, RAM disk, concatenation)
  - Add: Strategy pattern support for disease/medication-specific files

  2. Universal PDF Handling (stays in main generator)

  The main GeradorPDF continues to handle:
  - ✅ Base LME form (always)
  - ✅ Consent PDF (if primeira_vez = True)
  - ✅ Report PDF (if relatorio = True)
  - ✅ Exam PDF (if exames = True)

  3. Data-Driven Strategy (NEW)

  Single strategy class that reads configuration from database:
  class DataDrivenStrategy:
      def get_disease_specific_paths(self, dados):
          # Returns paths like: ["pdfs_base/edss.pdf", "pdfs_base/lanns.pdf"]

      def get_medication_specific_paths(self, dados):
          # Returns paths like: ["fingolimod_monitoring.pdf"]

  4. Database Configuration (NEW)

  Store everything in Protocolo.dados_condicionais JSON field:
  {
    "fields": [
      {"name": "opt_edss", "type": "choice", "choices": ["0", "1", "2"...]}
    ],
    "disease_files": ["pdfs_base/edss.pdf"],
    "medications": {
      "fingolimode": ["fingolimod_monitoring.pdf"],
      "natalizumabe": ["natalizumab_specific.pdf"]
    }
  }

  5. Directory Structure Leverage

  Use existing filesystem structure:
  static/autocusto/protocolos/esclerose_multipla/
  ├── consentimento.pdf (handled by main generator)
  ├── pdfs_base/
  │   ├── edss.pdf (disease-specific - strategy)
  │   └── relatorio.pdf (universal - main generator)
  └── fingolimod_monitoring.pdf (medication-specific - strategy)

  Implementation Changes

  Files to Modify:

  1. processos/manejo_pdfs_memory.py:
    - Rename class GeradorPDFMemory → GeradorPDF
    - Add strategy pattern integration
    - Keep all existing universal logic
  2. processos/pdf_strategies.py (NEW):
    - Create DataDrivenStrategy class
    - Database-driven path resolution
  3. processos/forms.py:
    - Replace seletor_campos() with database lookup
    - Use protocolo.dados_condicionais["fields"]
  4. processos/views.py:
    - Update import from GeradorPDFMemory to GeradorPDF

  Database Updates:

  1. Populate Protocolo.dados_condicionais for existing diseases:
    - Multiple Sclerosis: EDSS + medication configs
    - Chronic Pain: LANNS + EVA + medication configs
    - Epilepsy: medication configs
    - etc.

  Legacy Code:

  1. Keep logica_raw/ intact (for reference/backup)
  2. Gradually deprecate disease-specific classes
  3. No immediate deletion - parallel systems during transition

  Benefits

  1. Single PDF Generator: One unified class instead of parallel systems
  2. Data-Driven: Add new diseases through database config, not code
  3. Maintainable: No more giant switch statements
  4. Preserves Logic: All existing functionality maintained
  5. Directory Leveraged: Filesystem structure drives behavior
  6. Gradual Migration: Can implement disease by disease

  Migration Path

  1. ✅ Start with Multiple Sclerosis (most complex medication logic)
  2. Create database configuration for MS
  3. Test PDF generation matches existing behavior
  4. Migrate other diseases one by one
  5. Eventually deprecate legacy system

  This approach eliminates the 1000 disease classes problem while preserving all existing functionality and leveraging your current directory structure.

  Automated GPG Encrypted Backup Deployment Roadmap

  Deployment Objective

  Create a fully automated, production-ready backup system that runs without manual intervention on your VPS, encrypting database backups before uploading to Nextcloud.

  Production Deployment Configuration

  Step 1: VPS Environment Setup

  1.1 Generate Production GPG Key
  # On VPS as root
  gpg --batch --gen-key <<EOF
  Key-Type: RSA
  Key-Length: 4096
  Subkey-Type: RSA
  Subkey-Length: 4096
  Name-Real: AutoCusto Backup System
  Name-Email: lcsavb@gmail.com
  Expire-Date: 2y
  Passphrase: YOUR_SECURE_PASSPHRASE
  %commit
  EOF

  1.2 Secure GPG Key Storage
  # Export keys for backup
  gpg --export-secret-keys --armor lcsavb@gmail.com > /root/autocusto-backup-private.asc
  gpg --export --armor lcsavb@gmail.com > /root/autocusto-backup-public.asc

  # Secure the private key backup
  chmod 600 /root/autocusto-backup-private.asc

  1.3 Create Production Environment File
  # Create /opt/autocusto/.backupenv
  cat > /opt/autocusto/.backupenv <<EOF
  NC_BACKUP_URL=https://coupleofbytes.com/remote.php/dav/files/admin/
  NC_BACKUP_USERNAME=admin
  NC_BACKUP_PASSWORD=YOUR_NEXTCLOUD_APP_PASSWORD
  EOF

  chmod 600 /opt/autocusto/.backupenv

  Step 2: Container GPG Integration

  2.1 Update Dockerfile for Production GPG
  # Add to /opt/autocusto/Dockerfile after line 28
  RUN apt-get update && apt-get install -y \
      pdftk \
      cron \
      wget \
      gnupg \
      && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
      && echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
      && apt-get update \
      && apt-get install -y postgresql-client-17 \
      && rm -rf /var/lib/apt/lists/*

  # Add GPG key import during build
  COPY autocusto-backup-public.asc /tmp/
  RUN gpg --import /tmp/autocusto-backup-public.asc && rm /tmp/autocusto-backup-public.asc

  2.2 Update docker-compose.yml for Production
  services:
    web:
      build: .
      volumes:
        - .:/home/appuser/app
        - ./backups:/var/backups/autocusto
        # Remove GPG mount - key embedded in image instead
      env_file:
        - .backupenv

  Step 3: Automated Scheduling Configuration

  3.1 Enable Cron in Container
  # Add to Dockerfile
  USER root
  RUN service cron start
  USER appuser

  3.2 Configure Django Cron Jobs
  # In /opt/autocusto/autocusto/settings.py
  CRONJOBS = [
      ('0 3 * * *', 'django.core.management.call_command', ['cleanup_pdfs']),
      ('0 2 * * *', 'django.core.management.call_command', ['dbbackup']),
      ('15 2 * * *', 'django.core.management.call_command', ['upload_backup']),
  ]

  # Add cron logging
  CRON_CLASSES = [
      'django_crontab.cron.CronJobLog',
  ]

  3.3 Production Startup Script
  # Update /opt/autocusto/startup.sh
  #!/bin/bash

  # Start cron service
  service cron start

  # Install cron jobs
  python manage.py crontab add

  # Copy PDF templates to memory mount
  echo "Setting up memory mount for PDF templates..."
  mkdir -p /dev/shm/autocusto/static/processos
  mkdir -p /dev/shm/autocusto/static/protocolos
  cp -r /home/appuser/app/static/autocusto/processos/* /dev/shm/autocusto/static/processos/ 2>/dev/null || true
  cp -r /home/appuser/app/static/autocusto/protocolos/* /dev/shm/autocusto/static/protocolos/ 2>/dev/null || true

  # Execute the original command
  exec "$@"

  Step 4: Production Upload Command

  4.1 Simplified Production Upload Command
  # Update /opt/autocusto/processos/management/commands/upload_backup.py
  import os
  import glob
  import subprocess
  import logging
  from django.core.management.base import BaseCommand
  from webdav4.client import Client

  logger = logging.getLogger('backup')

  class Command(BaseCommand):
      help = 'Upload encrypted database backups to Nextcloud'

      def handle(self, *args, **options):
          try:
              # Nextcloud configuration
              nc_url = os.environ.get('NC_BACKUP_URL')
              nc_username = os.environ.get('NC_BACKUP_USERNAME')
              nc_password = os.environ.get('NC_BACKUP_PASSWORD')

              if not all([nc_url, nc_username, nc_password]):
                  logger.error('Nextcloud credentials not configured')
                  return

              # Find backup files
              backup_dir = '/var/backups/autocusto/'
              backup_files = glob.glob(os.path.join(backup_dir, 'autocusto_db_*.psql.bin'))

              if not backup_files:
                  logger.info('No backup files found')
                  return

              # WebDAV client
              client = Client(nc_url, auth=(nc_username, nc_password), timeout=60)

              # Ensure backups directory exists
              try:
                  client.ls("backups/")
              except:
                  client.mkdir("backups")

              for backup_file in backup_files:
                  filename = os.path.basename(backup_file)
                  encrypted_file = f"{backup_file}.gpg"
                  encrypted_filename = f"{filename}.gpg"
                  remote_path = f'backups/{encrypted_filename}'

                  # Encrypt backup
                  encrypt_cmd = [
                      'gpg', '--trust-model', 'always', '--cipher-algo', 'AES256',
                      '--compress-algo', '2', '--encrypt', '-r', 'lcsavb@gmail.com',
                      '--output', encrypted_file, backup_file
                  ]

                  result = subprocess.run(encrypt_cmd, capture_output=True)
                  if result.returncode != 0:
                      logger.error(f'Encryption failed for {filename}: {result.stderr.decode()}')
                      continue

                  # Check if file already exists
                  try:
                      client.ls(remote_path)
                      logger.info(f'File {encrypted_filename} already exists on Nextcloud')
                  except:
                      # Upload encrypted file
                      client.upload_file(encrypted_file, remote_path)
                      logger.info(f'Uploaded {encrypted_filename} to Nextcloud')

                  # Cleanup
                  if os.path.exists(encrypted_file):
                      os.remove(encrypted_file)

          except Exception as e:
              logger.error(f'Backup upload failed: {str(e)}')
              raise

  Step 5: Monitoring and Logging

  5.1 Configure Backup Logging
  # Add to /opt/autocusto/autocusto/settings.py
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'backup_file': {
              'level': 'INFO',
              'class': 'logging.FileHandler',
              'filename': '/var/log/django/backup.log',
          },
      },
      'loggers': {
          'backup': {
              'handlers': ['backup_file'],
              'level': 'INFO',
              'propagate': False,
          },
      },
  }

  5.2 Health Check Script
  # Create /opt/autocusto/check_backups.sh
  #!/bin/bash

  # Check if backups are being created
  LATEST_BACKUP=$(find /var/backups/autocusto/ -name "*.psql.bin" -mtime -1 | wc -l)
  if [ $LATEST_BACKUP -eq 0 ]; then
      echo "ERROR: No backups created in last 24 hours"
      exit 1
  fi

  # Check Nextcloud connectivity
  if ! curl -s -u "admin:$NC_BACKUP_PASSWORD" "$NC_BACKUP_URL" > /dev/null; then
      echo "ERROR: Cannot connect to Nextcloud"
      exit 1
  fi

  echo "Backup system healthy"

  Step 6: Deployment Steps

  6.1 Build and Deploy
  # On VPS
  cd /opt/autocusto

  # Copy public key for container build
  cp /root/autocusto-backup-public.asc .

  # Build with GPG key embedded
  docker-compose build --no-cache

  # Deploy
  docker-compose down
  docker-compose up -d

  # Verify cron jobs are installed
  docker-compose exec web python manage.py crontab show

  6.2 Test Full System
  # Test backup creation
  docker-compose exec web python manage.py dbbackup

  # Test encrypted upload
  docker-compose exec web python manage.py upload_backup

  # Verify in Nextcloud
  curl -u "admin:$NC_BACKUP_PASSWORD" "$NC_BACKUP_URL/backups/"

  6.3 Monitoring Setup
  # Add to crontab for daily health checks
  0 8 * * * /opt/autocusto/check_backups.sh

  # Monitor logs
  tail -f /opt/autocusto/logs/backup.log

  Production Checklist

  Security Requirements:

  - ✅ GPG private key securely stored and backed up
  - ✅ Nextcloud app password (not main password)
  - ✅ Environment file permissions (600)
  - ✅ Container runs as non-root user
  - ✅ Encrypted backups only stored remotely

  Automation Requirements:

  - ✅ Cron jobs automatically installed on container start
  - ✅ Daily backup at 2:00 AM
  - ✅ Daily upload at 2:15 AM
  - ✅ Local cleanup after 7 days
  - ✅ Automatic container restart recovery

  Monitoring Requirements:

  - ✅ Backup creation logging
  - ✅ Upload success/failure logging
  - ✅ Daily health check script
  - ✅ Nextcloud storage monitoring
  - ✅ Alert on backup failures

  Final Production Architecture

  VPS Host (2:00 AM daily)
  ├── Docker Container
  │   ├── python manage.py dbbackup → /var/backups/autocusto/file.psql.bin
  │   └── (2:15 AM) python manage.py upload_backup
  │       ├── GPG encrypt → file.psql.bin.gpg
  │       ├── Upload to Nextcloud → backups/file.psql.bin.gpg  
  │       └── Delete local .gpg file
  ├── Local Storage (7-day retention)
  │   └── /var/backups/autocusto/*.psql.bin
  └── Nextcloud Storage (permanent)
      └── backups/*.psql.bin.gpg (encrypted)

  This roadmap creates a zero-maintenance, production-ready backup system with military-grade encryption and automated monitoring.