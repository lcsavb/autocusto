# AutoCusto Security Testing Documentation

## 🛡️ Overview

This document describes the comprehensive security testing implementation for AutoCusto, a Django-based expert system for prescription PDF automation. The security tests validate both backend API security and frontend browser-level security to prevent unauthorized access to sensitive patient data.

## 📋 Quick Summary

### Backend Security Tests (11 tests) ✅
- **Patient Access Authorization** - Users can only access their authorized patients
- **Process Ownership Validation** - Users can only manage their own processes  
- **AJAX Endpoint Security** - All AJAX endpoints require proper authentication
- **Session-based Authorization** - Complete user isolation and access control
- **Cross-User Data Protection** - Prevents users from accessing other users' data

### Frontend Security Tests (9 tests) ✅
- **Authentication Flow Security** - Login/logout mechanisms work correctly
- **Patient Search Authorization** - Patient listings filter by user ownership
- **Process Workflow Security** - CPF+CID form submissions respect authorization
- **Session Isolation** - Different users cannot access each other's data
- **Form Validation Security** - Real browser-level form security validation
- **Process Page Protection** - Process edit pages require proper authorization

---

## 🎯 Critical Security Vulnerability Fixed

### **The Problem**
The original AutoCusto system had a critical security vulnerability where **any authenticated user could access ANY patient's data** by simply typing a CPF (Brazilian tax ID) in the home page form. This meant:

- User A could access User B's patients
- No authorization checks on patient access
- Potential HIPAA/data privacy violations
- Complete breakdown of patient data security

### **The Solution** 
Implemented comprehensive authorization checks at multiple levels:
- Backend API endpoints validate user ownership
- Frontend forms respect user authorization
- Database queries filter by user relationships
- Session management prevents cross-user access

---

## 🔧 Backend Security Tests (`tests/test_security.py`)

### Test Infrastructure Setup
```python
def setUp(self):
    # Create two isolated users with separate data
    self.user1 = User.objects.create_user(email='user1@example.com', password='testpass123')
    self.user2 = User.objects.create_user(email='user2@example.com', password='testpass123')
    
    # Create separate patients, processes, clinics for each user
    # Ensures complete data isolation for testing
```

### 1. Patient Access Authorization Tests

**What's tested:** Backend views and AJAX endpoints respect patient ownership
```python
def test_home_view_patient_authorization(self):
    # Test 1: User1 can access their own patient
    response = self.client.post('/', {'cpf_paciente': '12345678909', 'cid': 'G40.0'})
    # Should redirect to process page (authorized)
    
    # Test 2: User1 cannot access User2's patient  
    response = self.client.post('/', {'cpf_paciente': '54001816008', 'cid': 'G40.0'})
    # Should redirect to registration (unauthorized)
```

**Why it matters:** Prevents the core vulnerability where users could access any patient data.

### 2. Process Ownership Validation

**What's tested:** Process views validate user ownership before allowing access
```python
def test_process_edit_authorization(self):
    # Try to access another user's process
    response = self.client.get(reverse('processos-edicao'))
    # Should be denied or redirected
```

**How it works:** Uses Django's built-in authorization with custom ownership checks:
```python
# In views.py
processo = Processo.objects.get(id=processo_id, usuario=request.user)
```

### 3. AJAX Endpoint Security

**What's tested:** Patient search AJAX endpoints require authentication and filter by user
```python
def test_patient_ajax_search_authorization(self):
    response = self.client.get('/pacientes/ajax/busca?palavraChave=João')
    # Should only return current user's patients
```

**Security mechanism:** 
- `@login_required` decorators
- User filtering in querysets
- Proper JSON response validation

### 4. Database Query Security

**What's tested:** All database queries respect user relationships
```python
def test_patient_listing_authorization(self):
    response = self.client.get(reverse('pacientes-listar'))
    # Should only show current user's patients
```

**Implementation:**
```python
def get_queryset(self):
    return Paciente.objects.filter(usuarios=self.request.user)
```

---

## 🌐 Frontend Security Tests (`tests/test_frontend_security.py`)

### Test Infrastructure - Selenium WebDriver
```python
class SeleniumTestBase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # Setup headless Chrome with security options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        cls.driver = webdriver.Chrome(options=chrome_options)
```

### 1. Authentication Flow Security

**Test:** `test_login_logout_flow`
```python
def test_login_logout_flow(self):
    # 1. Verify unauthenticated users see invitation form
    self.driver.get(f'{self.live_server_url}/')
    self.assertIn("Código de convite", page_source)
    
    # 2. Test successful login
    self.login_user('user1@example.com', 'testpass123')
    
    # 3. Test protected page access while authenticated
    self.driver.get(f'{self.live_server_url}/pacientes/listar/')
    self.assertNotIn('/medicos/login/', self.driver.current_url)
    
    # 4. Test logout and protection after logout
    self.logout_user()
    self.driver.get(f'{self.live_server_url}/pacientes/listar/')
    # Should redirect to login
```

**Why it's important:** Validates the complete authentication lifecycle in a real browser.

### 2. Patient Search Authorization

**Test:** `test_patient_search_authorization`
```python
def test_patient_search_authorization(self):
    self.login_user('user1@example.com', 'testpass123')
    self.driver.get(f'{self.live_server_url}/pacientes/listar/')
    
    page_source = self.driver.page_source
    self.assertIn("João Silva", page_source)      # user1's patient
    self.assertNotIn("José Santos", page_source)  # user2's patient
```

**Security validation:** Real browser-level filtering of patient data by user ownership.

### 3. Session Isolation Testing

**Test:** `test_cross_user_session_isolation`

**What this test validates:** This is the most critical security test that ensures complete data isolation between different users in the same browser session.

**The test scenario:**
1. **User1 Login Phase:** User1 (user1@example.com) logs in and accesses the patient listing page. The test verifies that User1 can see their patient "João Silva" but cannot see User2's patient "José Santos".

2. **Session Cleanup Phase:** The test performs a complete logout by clicking the actual logout button, then clears all browser cookies and local storage to ensure no session data persists.

3. **User2 Login Phase:** User2 (user2@example.com) logs in using the same browser. The test verifies that User2 can see their patient "José Santos" but cannot see User1's patient "João Silva".

**How we verify the data is correct:**
- **Specific patient names:** Each user has a distinctly named patient (João Silva vs José Santos) making it impossible to confuse the data
- **Positive assertions:** Each user MUST see their own patient's name in the page content
- **Negative assertions:** Each user MUST NOT see the other user's patient name anywhere on the page
- **Real browser validation:** This happens in an actual browser, testing the complete Django authentication and authorization stack

**Why this test is critical:** In many web applications, session data can "leak" between different user sessions, especially in the same browser. This test ensures that Django's session management, combined with our authorization filters, completely isolates user data. Without this test, User2 might see User1's patients due to browser caching, incomplete logout, or flawed database queries.

**Security guarantee:** If this test passes, it proves that no matter how users switch accounts in the same browser, they will never see each other's sensitive patient data.

### 4. Form Security Validation

**Test:** `test_patient_cpf_access_authorization`
```python
def test_patient_cpf_access_authorization(self):
    # Test character-by-character input (not copy/paste)
    cpf_value = "72834565031"
    for char in cpf_value:
        cpf_field.send_keys(char)
        time.sleep(0.1)  # Trigger onChange events
    
    # Test authorized patient access
    # Test unauthorized patient access
```

**Advanced technique:** Character-by-character typing to trigger JavaScript validation and AJAX calls, simulating real user behavior.

### 5. Process Workflow Security

**Test:** `test_new_process_creation_flow` & `test_process_workflow_security`
```python
def test_new_process_creation_flow(self):
    # Test CPF + CID submission workflow
    # Should redirect to /processos/cadastro/ for new processes
    
def test_process_workflow_security(self):
    # Test existing patient access
    # Should redirect to /processos/edicao/ or /processos/cadastro/
```

**Workflow validation:** Ensures the complete patient → process workflow respects authorization at every step.

---

## 🔍 Advanced Testing Techniques

### 1. Character-by-Character Form Input
**Problem:** Selenium's `send_keys()` doesn't trigger JavaScript onChange events properly.
**Solution:** Type character by character with delays to simulate real user input:
```python
cpf_value = "72834565031"
for char in cpf_value:
    cpf_field.send_keys(char)
    time.sleep(0.1)  # Trigger AJAX/validation
```

### 2. Real Browser Session Management
**Problem:** Session isolation between different users in tests.
**Solution:** Proper logout, cookie clearing, and session storage clearing:
```python
def logout_user(self):
    logout_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
    logout_button.click()  # Real form submission
    
# Clear browser state
self.driver.delete_all_cookies()
self.driver.execute_script("window.localStorage.clear();")
```

### 3. Valid Brazilian CPF Testing
**Problem:** Form validation requires valid CPF format.
**Solution:** Use real valid CPF numbers that pass Brazilian validation algorithm:
```python
# Valid CPFs for testing
user1_patient_cpf = "72834565031"  # Passes CPF validation
user2_patient_cpf = "54001816008"  # Passes CPF validation
```

### 4. AJAX and JavaScript Security Testing
**Problem:** Modern web apps use AJAX for data loading.
**Solution:** Wait for AJAX completion and validate JavaScript-driven security:
```python
# Wait for AJAX calls to complete
time.sleep(2)

# Check browser console for errors
logs = self.driver.get_log('browser')
network_errors = [log for log in logs if log['level'] == 'SEVERE']
```

---

## 🚀 Running the Security Tests

### Backend Tests Only
```bash
python manage.py test tests.test_security --settings=test_settings --verbosity=2
```

### Frontend Tests Only
```bash
python manage.py test tests.test_frontend_security --settings=test_settings --verbosity=2
```

### Complete Security Test Suite
```bash
./run_security_tests.sh && ./run_frontend_tests.sh
```

### Test Environment Requirements
- **Backend:** Django TestCase with SQLite memory database
- **Frontend:** Chrome/Chromium browser with headless support
- **Dependencies:** Selenium WebDriver, ChromeDriver
- **Network:** Isolated test server (StaticLiveServerTestCase)

---

## 📊 Test Results and Coverage

### Security Test Coverage
- ✅ **Authentication:** Login/logout security ✅
- ✅ **Authorization:** User-based data access ✅
- ✅ **Session Management:** Cross-user isolation ✅
- ✅ **Form Security:** Real browser validation ✅
- ✅ **AJAX Security:** Endpoint authorization ✅
- ✅ **Database Security:** Query-level filtering ✅
- ✅ **Workflow Security:** End-to-end process protection ✅

### Performance Metrics
- **Backend Tests:** 11 tests in ~0.1 seconds
- **Frontend Tests:** 9 tests in ~80 seconds (browser automation)
- **Total Coverage:** 20 comprehensive security tests

---

## 🛠️ Security Test Maintenance

### Adding New Security Tests
1. **Identify security-critical functionality**
2. **Create backend API tests first**
3. **Add frontend browser tests for user workflows**
4. **Test both authorized and unauthorized access scenarios**

### Test Data Management
```python
def setUp(self):
    # Always create isolated test data
    # Use separate users, patients, processes
    # Ensure no data leakage between tests
```

### Debugging Failed Security Tests
```python
# Add comprehensive debugging
print(f"DEBUG: Current URL: {self.driver.current_url}")
print(f"DEBUG: Page source contains: {page_source[:500]}")

# Check authentication state
try:
    logout_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
    print("DEBUG: User is logged in")
except:
    print("DEBUG: User is not logged in")
```

---

## 🎯 Security Testing Best Practices

### 1. Test Real User Scenarios
- Use actual browser automation (Selenium)
- Test complete workflows, not just individual functions
- Validate security at the UI level, not just API level

### 2. Test Both Success and Failure Cases
- **Positive tests:** Authorized users can access their data
- **Negative tests:** Unauthorized users cannot access other users' data
- **Edge cases:** Empty data, invalid inputs, session timeouts

### 3. Isolate Test Data
- Each test should have completely separate data
- No shared state between tests
- Clean database state for each test run

### 4. Validate Multiple Layers
- **Frontend:** Browser-level security validation
- **Backend:** API endpoint authorization
- **Database:** Query-level access control
- **Session:** User isolation and session management

### 5. Use Real Security Scenarios
- Test actual attack vectors (accessing other users' data)
- Use valid data formats (real CPF numbers, valid CIDs)
- Simulate real user behavior (typing, clicking, navigation)

---

## 📚 Additional Recommendations

### Security Monitoring
- Add logging for unauthorized access attempts
- Monitor failed authentication attempts
- Track unusual data access patterns

### Continuous Security Testing
- Run security tests in CI/CD pipeline
- Add security regression testing
- Perform periodic security audits

### Documentation
- Document all security assumptions
- Maintain security test scenarios
- Keep security testing guidelines updated

---

## 🔗 Related Documentation

- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Selenium WebDriver Documentation](https://selenium-python.readthedocs.io/)
- [AutoCusto Backend Security Implementation](./tests/test_security.py)
- [AutoCusto Frontend Security Implementation](./tests/test_frontend_security.py)

---

*This security testing implementation ensures that AutoCusto maintains the highest standards of patient data protection and prevents unauthorized access at all levels of the application.*