# Playwright CI/CD Deployment Guide

## 📋 **Complete Guide to Deploying Playwright in CI/CD Pipelines**

This guide provides a battle-tested approach for deploying Microsoft Playwright browser automation in containerized CI/CD environments, based on resolving real-world deployment challenges.

## 🚨 **Critical Issues to Avoid**

### **❌ Chrome DevTools Protocol (CDP) Approach - DO NOT USE**

The CDP approach with custom Chrome containers **will fail** in containerized CI/CD environments due to:
- Chrome binds to `127.0.0.1:9222` instead of `0.0.0.0:9222`
- Ignores `--remote-debugging-address=0.0.0.0` startup flags
- Inter-container communication impossible
- WebSocket endpoint discovery issues
- Complex networking configuration requirements

**Symptoms of this broken approach:**
```
Connection refused to chrome container
WebSocket connection failed
Chrome not accessible from test container
```

## ✅ **Recommended Solution: Official Playwright Server**

Use Microsoft's **official Playwright server approach** with `mcr.microsoft.com/playwright` images.

### **🏗️ Docker Compose Infrastructure**

Create a `docker-compose.ci.yml` for your CI environment:

```yaml
services:
  db:
    image: postgres:17.4-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=your_app_db
    ports:
      - "5433:5432"
  
  web:
    build:
      context: .
      target: test  # Use test-specific Dockerfile target
    environment:
      - SECRET_KEY=test-secret-key-for-ci
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=your_app_db
      - SQL_USER=postgres
      - SQL_PASSWORD=postgres
      - SQL_HOST=db
      - SQL_PORT=5432
      - DEBUG=1
      - DJANGO_SETTINGS_MODULE=test_settings
      - PW_TEST_CONNECT_WS_ENDPOINT=ws://playwright-server:3000/
      - DJANGO_ALLOW_ASYNC_UNSAFE=true
      - CI=true
      - PLAYWRIGHT_HEADLESS=true
      - PLAYWRIGHT_WORKERS=1
    init: true
    ipc: host
    depends_on:
      - db
      - playwright-server
  
  playwright-server:
    image: mcr.microsoft.com/playwright:v1.54.0-noble
    ports:
      - "3000:3000"
    environment:
      - PLAYWRIGHT_RUN_ID=${GITHUB_RUN_ID:-local}
    command: 
      - sh
      - -c
      - |
        echo '=== STARTING OFFICIAL PLAYWRIGHT SERVER ==='
        echo "Container hostname: $(hostname)"
        echo "Container IP: $(hostname -i || echo 'unknown')"
        echo "Run ID: ${PLAYWRIGHT_RUN_ID}"
        echo '=== STARTING PLAYWRIGHT SERVER ==='
        npx -y playwright@1.54.0 run-server --port 3000 --host 0.0.0.0
```

### **🔧 Python Test Configuration**

#### **1. Connection Setup**

In your test base class:

```python
import asyncio
from playwright.async_api import async_playwright

class PlaywrightTestBase:
    @classmethod
    async def async_class_setup(cls):
        """Class-level browser setup using official Playwright server"""
        playwright = await async_playwright().start()
        
        # Connect to official Playwright server
        endpoint = os.environ.get('PW_TEST_CONNECT_WS_ENDPOINT', 'ws://playwright-server:3000/')
        cls.browser = await playwright.chromium.connect(endpoint)
        
        print(f"✅ Connected to Playwright server at {endpoint}")
        print(f"✅ Browser version: {cls.browser.version}")

    def setUp(self):
        super().setUp()
        
        # Python 3.11+ compatible event loop handling
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                raise
        
        # Initialize browser context and page for each test
        self.context = None
        self.page = None
        self.setup_browser()  # ← CRITICAL: This must be called

    def setup_browser(self):
        """Synchronous wrapper for async browser setup"""
        return self.loop.run_until_complete(self.async_setup_browser())

    async def async_setup_browser(self):
        """Set up browser context and page for the test"""
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()
```

#### **2. Critical Fix for `self.page = None` Issues**

**MUST HAVE**: Ensure `setup_browser()` is called in `setUp()` method. Without this, you'll get:
```
AttributeError: 'NoneType' object has no attribute 'goto'
```

#### **3. Proper Teardown**

```python
def tearDown(self):
    """Clean up after each test"""
    if self.page:
        self.loop.run_until_complete(self.page.close())
    if self.context:
        self.loop.run_until_complete(self.context.close())
    super().tearDown()

@classmethod  
async def async_class_teardown(cls):
    """Class-level cleanup"""
    if hasattr(cls, 'browser') and cls.browser:
        await cls.browser.close()
    if hasattr(cls, 'playwright') and cls.playwright:
        await cls.playwright.stop()
```

### **🎯 GitHub Actions CI/CD Configuration**

```yaml
name: Playwright Tests

jobs:
  playwright-tests:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Start Playwright infrastructure
      run: |
        echo "Starting Playwright testing infrastructure..."
        docker compose -f docker-compose.ci.yml up -d
        
        echo "Waiting for Playwright server..."
        sleep 15
        
        # Verify Playwright server is running
        curl -f http://localhost:3000 || (
          echo "Playwright server not responding"
          docker compose -f docker-compose.ci.yml logs playwright-server
          exit 1
        )
    
    - name: Run Playwright tests
      run: |
        docker compose -f docker-compose.ci.yml exec -T web python manage.py test \
          tests.integration.forms \
          tests.e2e.browser \
          --settings=test_settings \
          --verbosity=2 \
          --keepdb --noinput
    
    - name: Clean up
      if: always()
      run: |
        docker compose -f docker-compose.ci.yml down -v
```

### **🐛 Debugging Connection Issues**

Add these debugging steps to your CI:

```yaml
- name: Debug Playwright connection  
  run: |
    echo "Testing Playwright server connection..."
    
    # Test from host
    curl -v http://localhost:3000 || echo "Host connection failed"
    
    # Test inter-container connection
    docker compose -f docker-compose.ci.yml exec -T web curl -v http://playwright-server:3000 || echo "Container connection failed"
    
    # Container diagnostics
    docker compose -f docker-compose.ci.yml exec -T web sh -c "
      echo 'Container IP:' && hostname -I
      echo 'DNS resolution:' && nslookup playwright-server
      echo 'Port connectivity:' && nc -zv playwright-server 3000
    "
```

### **📊 Production vs Test Container Separation**

#### **Dockerfile Multi-stage Build**

```dockerfile
# Production stage - no browser dependencies
FROM python:3.11-slim as production
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app.wsgi"]

# Test stage - includes Playwright
FROM production as test
COPY requirements-test.txt .
RUN pip install -r requirements-test.txt
# Install Playwright (connects to external server, doesn't need browsers)
RUN pip install playwright
# DO NOT run: playwright install (browsers run in separate container)
```

#### **Container Size Verification**

Ensure production containers don't include test dependencies:

```bash
# Verify production image is clean
docker run --rm production-image sh -c "
  ! command -v google-chrome && echo '✅ Chrome not found (good)' || exit 1
  ! python -c 'import playwright' && echo '✅ Playwright not found (good)' || exit 1
"
```

## 🚀 **Deployment Checklist**

### **✅ Pre-deployment Verification**

- [ ] Use official `mcr.microsoft.com/playwright` image
- [ ] Playwright server binds to `0.0.0.0:3000`
- [ ] Environment variable `PW_TEST_CONNECT_WS_ENDPOINT=ws://playwright-server:3000/`
- [ ] Test container can resolve `playwright-server` hostname
- [ ] `setup_browser()` called in test `setUp()` method
- [ ] Proper async/await patterns in all test methods
- [ ] Python 3.11+ event loop compatibility
- [ ] Container health checks pass
- [ ] Production images exclude test dependencies

### **✅ Connection Verification**

```python
# Test connection in your CI
async def verify_playwright_connection():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect("ws://playwright-server:3000/")
    print(f"✅ Browser version: {browser.version}")
    await browser.close()
    await playwright.stop()
```

### **✅ Critical Docker Configuration Issues - RESOLVED**

**Based on official Playwright documentation research, these configurations are MANDATORY:**

1. **`init: true`** - Prevents zombie processes that block containers
2. **`ipc: host`** - **CRITICAL** - Prevents Chromium memory crashes and hangs
3. **`PLAYWRIGHT_WORKERS=1`** - Sequential execution prevents resource conflicts in CI
4. **`PLAYWRIGHT_HEADLESS=true`** - Forces headless mode for containers
5. **`CI=true`** - Prevents HTML report server from starting (main cause of hangs)

### **✅ Common Gotchas**

1. **Missing `setup_browser()` call** → `self.page = None` errors
2. **Missing Docker `ipc: host`** → Chromium crashes and infinite hangs
3. **Missing `init: true`** → Zombie processes block containers
4. **Wrong endpoint URL** → Connection timeouts  
5. **Container networking issues** → DNS resolution failures
6. **Event loop problems** → Python 3.11+ RuntimeError
7. **Production contamination** → Bloated production images
8. **Multiple workers in CI** → Resource conflicts and flaky tests

## 🚨 **Troubleshooting Hanging Tests**

### **Issue: Tests Hang Indefinitely**
```
test_prescription_form_basic_patient_data hangs with no output
```

### **Root Causes & Solutions:**

1. **Missing Docker IPC configuration** - Add `ipc: host` to web container
2. **HTML report server blocking** - Ensure `CI=true` environment variable  
3. **Multiple workers causing conflicts** - Set `PLAYWRIGHT_WORKERS=1`
4. **Async setup issues** - Ensure `self.setup_browser()` called in `setUp()`
5. **Zombie processes** - Add `init: true` to container configuration

### **Debugging Hanging Tests:**

```yaml
# Add individual test timeouts and monitoring
- name: Run tests with timeout monitoring
  run: |
    timeout 300 docker compose -f docker-compose.ci.yml exec -T web python manage.py test \
      tests.integration.forms.test_prescription_forms.MedicationManagementTest \
      --settings=test_settings \
      --verbosity=3 \
      --keepdb --noinput
    
    if [ $? -eq 124 ]; then
      echo "🚨 Test TIMED OUT - investigating container state"
      docker compose -f docker-compose.ci.yml logs web
      docker compose -f docker-compose.ci.yml logs playwright-server
    fi
```

### **Individual Test Execution Strategy:**
Run test classes separately with timeouts to isolate hanging tests:
- `MedicationManagementTest` - 120s timeout
- `PrescriptionFormTest` - 120s timeout  
- E2E browser tests - 180s timeout

## 📈 **Expected Results**

**Successful deployment indicators:**
```
✅ Playwright server connection successful
✅ Browser version: 139.0.7258.5
✅ All tests passing with browser automation
✅ Production containers remain lightweight
✅ CI/CD pipeline completes in reasonable time
```

## 🔗 **Key Architecture**

```
GitHub Actions CI Environment:
┌─────────────────────┐    ┌───────────────────────┐
│   Web Container     │    │  Playwright Server    │
│  (Django + Tests)   │◄──►│  (Official MS Image)  │
│  - Python/Django    │    │  - Playwright Server  │
│  - Test Suite       │    │  - Port 3000          │
│  - Playwright Client│    │  - WebSocket Endpoint │
└─────────────────────┘    └───────────────────────┘
```

## 📚 **Additional Resources**

- [Official Playwright Server Documentation](https://playwright.dev/docs/test-runners)
- [Playwright Docker Images](https://mcr.microsoft.com/en-us/product/playwright/about)
- [Container Networking Best Practices](https://docs.docker.com/compose/networking/)

---

**Status**: 🔧 **ACTIVELY DEBUGGING** - Infrastructure working, resolving test hangs  
**Infrastructure**: ✅ **FULLY OPERATIONAL** - Playwright server + Docker setup complete  
**Current Issue**: Individual test timeouts implemented to prevent in
finite hangs  
**Last Updated**: 2025-08-01  
**Tested Environments**: GitHub Actions, Docker Compose, Ubuntu 22.04

## 🔄 **Latest Updates (2025-08-01)**

- ✅ **Fixed `self.page = None` errors** - Added `setup_browser()` call in base class
- ✅ **Applied critical Docker configurations** - `init: true`, `ipc: host`, `PLAYWRIGHT_WORKERS=1`
- ✅ **Infrastructure fully verified** - Server connections and networking working
- 🔧 **Implemented individual test timeouts** - Prevents infinite hangs, isolates problematic tests
- 🔧 **Added comprehensive debugging** - Timeout detection and container state monitoring