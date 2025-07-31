# Playwright Test Hanging Issue - Analysis and Steps

## The Problem

The Playwright tests are hanging in the GitHub Actions CI environment. Specifically:

- **Where it hangs**: `PrescriptionFormPlaywrightBase.setUp() starting...`
- **Test affected**: `MedicationManagementTest` and other Playwright-based tests
- **Environment**: GitHub Actions CI (not local development)

## What We're Trying to Do

Run Playwright browser automation tests in CI to test the prescription form functionality. These tests need:
1. A running Django server (HTTP endpoint)
2. Playwright browser automation
3. Database access for test data

## Current Situation

### What Works ✅
- **Backend tests**: Run directly on GitHub Actions runner with `python manage.py test`
- **Database**: PostgreSQL service container works fine
- **Playwright server**: Successfully connects (version 139.0.7258.5)

### What Fails ❌
- **Playwright tests**: Hang when trying to start
- **Network check**: Shows `http://localhost:8001/ -> 000` (no server running)
- **Test execution**: Times out after 300 seconds

## Root Cause Analysis

### 1. Initial Setup (Before Our Changes)
- Tests were run inside Docker container: `docker compose exec -T web python manage.py test`
- Container runs uWSGI (WSGI socket on port 8001, not HTTP)
- `StaticLiveServerTestCase` tries to start its own HTTP server
- **Result**: Hangs because it can't start a server in the containerized environment

### 2. Our First Attempt
- Changed tests to run directly on GitHub Actions runner (like backend tests)
- Removed Docker complexity
- Started Playwright server locally
- **Result**: Still hangs at the same place

### 3. Current Understanding
The hang occurs when:
1. Test class setup completes successfully ✅
2. Instance `setUp()` is called
3. `super().setUp()` is called (which calls `StaticLiveServerTestCase.setUp()`)
4. **HANGS HERE** - `StaticLiveServerTestCase` tries to start a Django test server

## Steps Taken So Far

### Step 1: Removed Docker Execution
Changed from:
```bash
docker compose exec -T web python manage.py test
```
To:
```bash
python manage.py test
```

### Step 2: Started Playwright Server Locally
```bash
npx playwright run-server --port 3000 --host 0.0.0.0 &
```

### Step 3: Fixed Test Inheritance
- Initially changed from `PlaywrightLiveServerTestBase` to `PlaywrightTestBase`
- Then reverted back since we're now running on the host

### Step 4: Added Debugging
- Added print statements with `flush=True`
- Added network connectivity checks
- Added timeout handling

### Step 5: Database Preparation
Added migration step:
```bash
python manage.py migrate --noinput
```

## Current Status

We can see from the debug output:
```
[PLAYWRIGHT-CLASS-SETUP] Starting setUpClass for MedicationManagementTest
[PLAYWRIGHT-CLASS-SETUP] async_class_setup complete
🔧 DEBUG: PrescriptionFormPlaywrightBase.setUp() starting...
```

Then it hangs. This means:
- ✅ Class-level setup works (Playwright connection established)
- ❌ Instance-level setUp fails (StaticLiveServerTestCase can't start server)

## Key Questions

1. **Why does StaticLiveServerTestCase hang?**
   - Port binding issues?
   - Network configuration in GitHub Actions?
   - Missing dependencies?

2. **Why do backend tests work but Playwright tests don't?**
   - Backend tests don't need a live server (they test models/services directly)
   - Playwright tests need an HTTP endpoint for browser automation

3. **What's different between local and CI?**
   - Local: Can start Django dev server easily
   - CI: Something prevents StaticLiveServerTestCase from starting its server

## Next Steps to Consider

1. **Test if Playwright itself works** (without Django server)
   - Created `test_simple_playwright.py` to test basic Playwright functionality

2. **Check if it's a port binding issue**
   - StaticLiveServerTestCase uses random ports
   - Maybe GitHub Actions blocks certain port ranges?

3. **Try alternative approaches**
   - Use a pre-started Django server instead of StaticLiveServerTestCase
   - Mock the browser interactions
   - Use a different test base class

4. **Debug StaticLiveServerTestCase**
   - Add more logging to see exactly where it hangs
   - Check if it's waiting for something specific
   - Look for timeout settings

## The Fundamental Issue

The core problem is that we need:
- Django server running (for Playwright to connect to)
- But StaticLiveServerTestCase (which normally handles this) is hanging
- In CI environment specifically (works locally)

This suggests an environmental issue with how Django's test server starts in GitHub Actions.