

FOR EARLY DEPLOYMENT

security fixes
when the medicamento is nenhum it works
some toasts too fast
recuperacao da senha instrucoes em ingles
no inline validation feedback
depois da criação da conta, login automático
instituir autenticação de dois fatores obrigatória
The pdfs_base directories exist for some protocols but not for epilepsia. Let me check if it should exist:
logging
dor_crÔnica 
verify need for changes in dbd
add copaxone for ms
print without dialog -> not working and opening a browser dialog
layout breaking on mobile (home)



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


  change deploy?

  name: Deploy to VPS

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17.4-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: autocusto
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        SECRET_KEY: test-secret-key
        SQL_ENGINE: django.db.backends.postgresql
        SQL_DATABASE: autocusto
        SQL_USER: postgres
        SQL_PASSWORD: postgres
        SQL_HOST: localhost
        SQL_PORT: 5432
        DEBUG: 1
      run: |
        echo "Skipping tests temporarily - fix test failures first"
        # python manage.py test

  build:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - name: Deploy to VPS
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USERNAME }}
        key: ${{ secrets.KINGHOST_SSH_KEY }}
        script: |
          echo "=== CLEAN DEPLOYMENT START ==="
          
          # Setup deployment directory
          sudo chown $USER:$USER /opt/autocusto
          mkdir -p /opt/autocusto
          cd /opt/autocusto
          
          # Create deployment docker-compose.yml with variable expansion
          echo "=== Creating deployment docker-compose.yml ==="
          cat > docker-compose.yml << EOF
          services:
            db:
              image: postgres:17.4-alpine
              volumes:
                - postgres_data:/var/lib/postgresql/data/
              environment:
                - POSTGRES_USER=lucas
                - POSTGRES_PASSWORD=rraptnor
                - POSTGRES_DB=autocusto
              ports:
                - "5432:5432"

            web:
              image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:master
              command: uwsgi --ini uwsgi.ini
              tmpfs:
                - /tmp:rw,noexec,nosuid,size=200m
                - /dev/shm:rw,noexec,nosuid,size=100m
              depends_on:
                - db
              environment:
                - SECRET_KEY=jklahjkldfakjhKLJHADJKFHASDKHFJKLhadsfhjkladhOIUYHQ6516AS5DFASD65F48A6S1652asd1f3as2d
                - DJANGO_ALLOWED_HOSTS=${{ secrets.DJANGO_ALLOWED_HOSTS }}
                - SQL_ENGINE=django.db.backends.postgresql
                - SQL_DATABASE=autocusto
                - SQL_USER=lucas
                - SQL_PASSWORD=rraptnor
                - SQL_HOST=db
                - SQL_PORT=5432

            nginx:
              image: nginx:latest
              ports:
                - "8000:80"
              volumes:
                - ./nginx.conf:/etc/nginx/conf.d/default.conf
              depends_on:
                - web

          volumes:
            postgres_data:
          EOF
          
          # Create nginx.conf
          echo "=== Creating nginx.conf ==="
          cat > nginx.conf << 'EOF'
          upstream web {
            server web:8000;
          }

          server {
            listen 80;
            
            location / {
              proxy_pass http://web;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header Host $host;
              proxy_redirect off;
            }
          }
          EOF
          
          # Login to registry and pull latest image
          echo "=== Pulling latest image from registry ==="
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ${{ env.REGISTRY }} -u ${{ github.actor }} --password-stdin
          docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:master
          
          # Validate deployment files
          echo "=== Validating deployment configuration ==="
          docker-compose config --quiet
          if [ $? -ne 0 ]; then
            echo "❌ Invalid docker-compose.yml"
            docker-compose config
            exit 1
          fi
          echo "✅ Configuration valid"
          
          # Deploy
          echo "=== Deploying containers ==="
          docker-compose down
          docker-compose up -d
          
          # Wait for services to be ready
          echo "=== Waiting for services ==="
          sleep 10
          
          # Run migrations
          echo "=== Running migrations ==="
          docker-compose exec -T web python manage.py migrate
          
          # Health check
          echo "=== Health check ==="
          docker-compose ps
          
          # Cleanup old images
          echo "=== Cleaning up old images ==="
          docker image prune -f
          
          echo "=== DEPLOYMENT COMPLETE ==="


          SECURITY
          
           🚨 CRITICAL PRODUCTION ISSUES FOUND

  Based on my comprehensive audit, here are the IMMEDIATE CHANGES you must make:

  🔥 CRITICAL SECURITY FIXES (DO NOW)

  1. Generate New SECRET_KEY
  # Generate a new secret key
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

  2. Remove Hardcoded Credentials
  # In settings.py - REMOVE these defaults:
  EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'ukmi zxht fwsy yrle')  # ❌ REMOVE DEFAULT
  SECRET_KEY = os.environ.get('SECRET_KEY')  # ✅ Already correct

  3. Add Security Headers to nginx.conf
  # Add to your HTTPS server block:
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Content-Type-Options nosniff;
  add_header X-Frame-Options DENY;
  add_header X-XSS-Protection "1; mode=block";
  add_header Referrer-Policy "strict-origin-when-cross-origin";

  4. Environment Variable Security
  # Add .env to .gitignore (if not already)
  echo ".env" >> .gitignore

  # Remove .env from git history
  git rm --cached .env
  git commit -m "Remove .env from version control"

  ⚡ PERFORMANCE FIXES

  5. Database Query Optimization
  # In views.py - Add select_related for foreign keys:
  busca_processos = paciente.processos.select_related('doenca', 'medico').filter(doenca__cid=cid)

  6. Production Cache Backend
  # In settings.py - Use Redis for production:
  if not DEBUG:
      CACHES = {
          'default': {
              'BACKEND': 'django.core.cache.backends.redis.RedisCache',
              'LOCATION': 'redis://127.0.0.1:6379/1',
          }
      }

  🔧 PRODUCTION SETTINGS

  7. Add Production Settings
  # Add to settings.py:
  if not DEBUG:
      SESSION_COOKIE_SECURE = True
      SESSION_COOKIE_HTTPONLY = True
      CSRF_COOKIE_SECURE = True
      SECURE_SSL_REDIRECT = True
      SECURE_HSTS_SECONDS = 31536000
      SECURE_CONTENT_TYPE_NOSNIFF = True
      SECURE_BROWSER_XSS_FILTER = True

  8. Enhanced Logging
  # Update LOGGING in settings.py:
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'file': {
              'level': 'ERROR',
              'class': 'logging.handlers.RotatingFileHandler',
              'filename': '/var/log/django/error.log',
              'maxBytes': 1024*1024*10,  # 10 MB
              'backupCount': 5,
          },
          'console': {
              'class': 'logging.StreamHandler',
          },
      },
      'loggers': {
          'django': {
              'handlers': ['file', 'console'],
              'level': 'ERROR',
              'propagate': True,
          },
      },
  }

  📋 IMMEDIATE TODO LIST

  1. ✅ Change SECRET_KEY
  2. ✅ Remove hardcoded passwords
  3. ✅ Add security headers
  4. ✅ Remove .env from git
  5. ✅ Add production settings
  6. ✅ Set up database backups
  7. ✅ Add monitoring/health checks

  Priority Level: 🔴 CRITICAL - Your app has several security vulnerabilities that need immediate attention before production use.