"""
Playwright tests using pytest framework for better async/sync handling
"""
import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page
from usuarios.models import Usuario

User = get_user_model()


@pytest.mark.django_db
def test_home_redirects_to_login(live_server, page: Page):
    """Test that home page redirects to login when not authenticated"""
    page.goto(f"{live_server.url}/")
    
    # Should be redirected to login
    page.wait_for_url(f"{live_server.url}/login/")
    assert "/login/" in page.url


@pytest.mark.django_db
def test_login_page_elements(page: Page):
    """Test that login page has required elements"""
    page.goto("http://localhost:8001/")  # Login is at root/index
    
    # Debug: print page content
    print(f"Page title: {page.title()}")
    print(f"Page URL: {page.url}")
    
    # Should see login form elements (might need to wait or use different selectors)
    page.wait_for_selector('form', timeout=5000)  # Wait for form to appear
    
    # Find login form elements specifically
    login_email = page.locator('input[name="username"]')  # Login form email
    login_password = page.locator('input[name="password"]')  # Login form password
    
    # Also check registration form exists
    register_email = page.locator('input[name="email"]')  # Registration form email
    
    assert login_email.is_visible(), "Login email input not found"
    assert login_password.is_visible(), "Login password input not found"
    assert register_email.is_visible(), "Registration email input not found"


@pytest.mark.django_db  
def test_invalid_login(live_server, page: Page):
    """Test invalid login attempt"""
    page.goto(f"{live_server.url}/login/")
    
    page.fill('input[name="email"]', 'invalid@test.com')
    page.fill('input[name="password"]', 'wrongpassword')
    page.click('button[type="submit"]')
    
    page.wait_for_load_state('domcontentloaded', timeout=10000)
    
    # Should still be on login page with error
    assert "/login/" in page.url


@pytest.mark.django_db
def test_valid_login(live_server, page: Page):
    """Test valid login flow"""
    # Create test user
    user = Usuario.objects.create_user(
        email='testuser@test.com',
        password='testpass123'
    )
    
    page.goto(f"{live_server.url}/login/")
    
    page.fill('input[name="email"]', 'testuser@test.com')
    page.fill('input[name="password"]', 'testpass123') 
    page.click('button[type="submit"]')
    
    page.wait_for_load_state('domcontentloaded', timeout=10000)
    
    # Should be redirected away from login
    assert "/login/" not in page.url


@pytest.mark.django_db
def test_patient_access_authorization(live_server, page: Page):
    """Test that users can only access their own patients"""
    # Create test users
    user1 = Usuario.objects.create_user(
        email='user1@test.com', 
        password='testpass123'
    )
    user2 = Usuario.objects.create_user(
        email='user2@test.com',
        password='testpass123'
    )
    
    # Create patients for each user
    from pacientes.models import Paciente
    
    patient1 = Paciente.objects.create(
        usuario=user1,
        nome_paciente="Patient 1",
        cpf_paciente="11111111111"
    ,
            incapaz=False
        )
    
    patient2 = Paciente.objects.create(
        usuario=user2,
        nome_paciente="Patient 2", 
        cpf_paciente="22222222222"
    ,
            incapaz=False
        )
    
    # Login as user1
    page.goto(f"{live_server.url}/login/")
    page.fill('input[name="email"]', 'user1@test.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('domcontentloaded', timeout=10000)
    
    # Try to access user2's patient
    page.goto(f"{live_server.url}/pacientes/")
    page.wait_for_load_state('domcontentloaded', timeout=10000)
    
    content = page.content()
    
    # Should see own patient but not other user's patient
    assert "Patient 1" in content
    assert "Patient 2" not in content