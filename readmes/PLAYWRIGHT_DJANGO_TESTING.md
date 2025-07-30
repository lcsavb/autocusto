# Django + Playwright Testing Infrastructure

This document outlines the complete solution for running Playwright browser tests with Django in a containerized environment, including proper authentication and session management.

## Overview

The challenge was to test Django form validation using Playwright browser automation while running in Docker containers, with proper user authentication and session state management.

## Key Components

### 1. Base Test Class: `PlaywrightLiveServerTestBase`

**File**: `/home/lucas/code/autocusto/tests/playwright_base.py`

Uses `StaticLiveServerTestCase` instead of regular `TestCase` to ensure the live server and test database share the same state, fixing authentication issues between Django test client and Playwright browser.

```python
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class PlaywrightLiveServerTestBase(StaticLiveServerTestCase):
    # Configure live server to be accessible from remote browser container
    @classmethod
    def setUpClass(cls):
        cls.host = '0.0.0.0'  # Bind to all interfaces for container access
        super().setUpClass()
        
        # Connect to remote Chromium browser in playwright-browsers container
        cls.playwright = sync_playwright().start()
        remote_browser_endpoint = 'http://172.18.0.2:9222'
        cls.browser = cls.playwright.chromium.connect_over_cdp(remote_browser_endpoint)
```

### 2. Container-Accessible URL Handling

**Problem**: Live server URLs like `http://localhost:38721` are not accessible from remote browser containers.

**Solution**: URL translation property that converts localhost/127.0.0.1/0.0.0.0 to the container hostname.

```python
@property
def accessible_live_server_url(self):
    """Get live server URL accessible from remote browser container."""
    if hasattr(self, 'live_server_url'):
        url = self.live_server_url
        return url.replace('localhost', 'web').replace('127.0.0.1', 'web').replace('0.0.0.0', 'web')
    return "http://web:8001"  # Fallback
```

### 3. Browser-Based Authentication

**Problem**: Session cookie sharing between Django test client and remote Playwright browser doesn't work reliably.

**Solution**: Direct browser authentication using Playwright to fill login forms.

```python
def authenticate_via_browser(self, email, password):
    """Perform browser-based authentication using Playwright."""
    # Navigate to home page using accessible URL
    server_url = self.accessible_live_server_url
    self.page.goto(server_url)
    self.wait_for_page_load()
    
    # Fill login form
    email_field = self.page.locator('input[name="username"]')
    password_field = self.page.locator('input[name="password"]')
    email_field.fill(email)
    password_field.fill(password)
    
    # Click login button - be specific to avoid button ambiguity
    login_form = self.page.locator('form').filter(has=self.page.locator('input[name="username"]'))
    login_button = login_form.locator('button[type="submit"]')
    login_button.click()
    self.wait_for_page_load()
    
    # Verify authentication success
    login_form_after = self.page.locator('input[name="username"]')
    if login_form_after.is_visible():
        self.fail(f"Browser authentication failed for {email}")
```

### 4. Centralized Session Data Configuration

**File**: `/home/lucas/code/autocusto/tests/test_session_data.py`

Simple dictionaries and helper functions for consistent session setup across tests.

```python
# Required session keys for different workflows
SESSION_KEYS = {
    'edicao': ['processo_id', 'cid'],
    'cadastro': ['cpf_paciente', 'cid', 'paciente_existe'], 
    'renovacao': ['processo_id', 'cid', 'data1'],
}

def get_edicao_session_data(processo_id, cid='G40.0'):
    """Get session data for edicao workflow."""
    return {
        'processo_id': processo_id,
        'cid': cid,
    }
```

### 5. Direct Session Manipulation

**Problem**: Setting session data for live server when test endpoints aren't available.

**Solution**: Direct manipulation of browser session using Django's session framework.

```python
# Get the current browser session key from cookies
cookies = self.page.context.cookies()
session_cookie = None
for cookie in cookies:
    if cookie['name'] == 'sessionid':
        session_cookie = cookie['value']
        break

if session_cookie:
    # Load the session and set the required data
    from django.contrib.sessions.backends.db import SessionStore
    session = SessionStore(session_key=session_cookie)
    
    # Set the session data using centralized config
    session_data = get_edicao_session_data(processo.id, self.doenca.cid)
    for key, value in session_data.items():
        session[key] = value
    
    session.save()
```

## Complete Test Implementation

### Example: Medication Form Validation Test

```python
from tests.playwright_base import PlaywrightLiveServerTestBase
from tests.test_session_data import get_edicao_session_data

class MedicationManagementTest(PlaywrightLiveServerTestBase):
    def navigate_to_medication_form(self):
        # 1. Authenticate via browser
        self.authenticate_via_browser(self.test_email, 'testpass123')
        
        # 2. Create required test data
        processo = Processo.objects.create(
            usuario=self.user1,
            paciente=self.patient1,
            doenca=self.doenca
        )
        
        # 3. Set up session data
        session_data = get_edicao_session_data(processo.id, self.doenca.cid)
        cookies = self.page.context.cookies()
        session_cookie = next((c['value'] for c in cookies if c['name'] == 'sessionid'), None)
        
        if session_cookie:
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore(session_key=session_cookie)
            for key, value in session_data.items():
                session[key] = value
            session.save()
        
        # 4. Navigate to form
        edicao_url = f'{self.accessible_live_server_url}/processos/edicao/'
        self.page.goto(edicao_url)
        self.wait_for_page_load()
        
        return True
    
    def test_medication_validation_prevents_submission_all_nenhum(self):
        if not self.navigate_to_medication_form():
            self.fail("Could not navigate to medication form")
        
        # Test form validation logic
        # ... rest of test implementation
```

## Docker Configuration

Ensure your `docker-compose.yml` includes the Playwright browser container:

```yaml
playwright-browsers:
  image: mcr.microsoft.com/playwright:v1.40.0-jammy
  ports:
    - "9222:9222"  # Chrome DevTools Protocol
  command: >
    sh -c "
      Xvfb :99 -screen 0 1920x1080x24 &
      /ms-playwright/chromium-1091/chrome-linux/chrome --headless --no-sandbox --remote-debugging-address=0.0.0.0 --remote-debugging-port=9222 &
      tail -f /dev/null
    "
```

## Step-by-Step Implementation Guide

### 1. Create Base Test Class
- Inherit from `StaticLiveServerTestCase` 
- Set `cls.host = '0.0.0.0'` for container access
- Connect to remote browser via CDP
- Add `accessible_live_server_url` property

### 2. Implement Browser Authentication
- Create `authenticate_via_browser()` method
- Use Playwright to fill login forms directly
- Verify authentication success before proceeding

### 3. Set Up Session Data Management
- Create centralized session data configuration file
- Implement helper functions for different workflows
- Use direct session manipulation via browser cookies

### 4. Test Form Validation
- Navigate to protected pages after authentication
- Set up required session data for form workflows  
- Test form interactions and validation logic

## Key Benefits

✅ **Shared Database State**: StaticLiveServerTestCase ensures test and live server use same data  
✅ **Container Network Compatibility**: URL translation works across Docker containers  
✅ **Reliable Authentication**: Browser-based login works consistently  
✅ **Centralized Configuration**: Session data setup is reusable and maintainable  
✅ **Full Integration Testing**: Tests real browser interactions with Django backend  

## Common Pitfalls Avoided

❌ **Using regular TestCase**: Database state not shared with live server  
❌ **Session cookie sharing**: Doesn't work reliably between processes  
❌ **Hardcoded localhost URLs**: Not accessible from remote containers  
❌ **Complex test endpoints**: Adds unnecessary complexity  
❌ **Skipping tests on auth failure**: Should fail with clear error messages  

## Usage for Other Tests

This infrastructure can be used for any Django form testing that requires:
- User authentication
- Session state management  
- Browser interactions
- Form validation testing
- Protected page access

Simply inherit from `PlaywrightLiveServerTestBase` and use the provided authentication and session management patterns.

## Known Issues

### Medication Validation Issue
- **Issue**: The `test_medication_validation_prevents_submission_all_nenhum` test is currently failing
- **Expected Behavior**: Form should stay on same page with validation error when all medications are set to 'nenhum'
- **Actual Behavior**: Form submits successfully and redirects to `/processos/renovacao/?b=`
- **Root Cause**: Backend medication validation logic is not properly preventing submission when all medications are 'nenhum'
- **Status**: Application logic bug - needs investigation in `MedicationValidator` class
- **TODO**: Fix medication validation to properly handle 'nenhum' values as empty selections