"""
Clean, simple tests for cadastro view redirect behavior.
Built from scratch to avoid complex test setup issues.
"""

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from medicos.models import Medico
from clinicas.models import Clinica
from processos.views import cadastro

User = get_user_model()


class CleanCadastroRedirectTest(TestCase):
    """Simple, focused tests for cadastro redirect behavior."""
    
    def setUp(self):
        """Minimal setup for testing."""
        # Create user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        
        # Create client and login
        self.client = Client()
        login_success = self.client.login(email='test@example.com', password='testpass123')
        print(f"setUp login successful: {login_success}")
        
        if not login_success:
            raise Exception("Failed to login in setUp")
    
    def test_cadastro_redirects_when_no_medico_profile(self):
        """Test: No medico profile -> should redirect somewhere."""
        # Set up session (required by view)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = '12345678901'
        session.save()
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"No medico test - Status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"No medico test - Redirect to: {response.url}")
        
        # Should redirect (either 301 or 302)
        self.assertIn(response.status_code, [301, 302])
    
    def test_cadastro_redirects_when_medico_missing_crm_cns(self):
        """Test: Medico exists but missing CRM/CNS -> should redirect to complete-profile."""
        # Verify login first
        login_success = self.client.login(email='test@example.com', password='testpass123')
        print(f"Login successful: {login_success}")
        
        # Check if user is authenticated
        response_check = self.client.get('/')
        print(f"Home page status (to verify auth): {response_check.status_code}")
        
        # Create medico with missing CRM/CNS (like new registration)
        medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico=None,  # Missing - like new registration
            cns_medico=None   # Missing - like new registration
        )
        self.user.medicos.add(medico)
        
        # Set up session (required by view)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = '12345678901'
        session.save()
        
        print(f"Session keys before request: {list(session.keys())}")
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"Missing CRM/CNS test - Status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"Missing CRM/CNS test - Redirect to: {response.url}")
        print(f"Response content length: {len(response.content)}")
        
        # Should redirect to complete-profile
        self.assertIn(response.status_code, [301, 302])
        if hasattr(response, 'url'):
            self.assertEqual(response.url, reverse('complete-profile'))
    
    def test_cadastro_redirects_when_medico_has_crm_but_no_cns(self):
        """Test: Medico has CRM but missing CNS -> should redirect to complete-profile."""
        # Create medico with CRM but missing CNS
        medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='123456',  # Has CRM
            cns_medico=None       # Missing CNS
        )
        self.user.medicos.add(medico)
        
        # Set up session (required by view)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = '12345678901'
        session.save()
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"Has CRM, missing CNS test - Status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"Has CRM, missing CNS test - Redirect to: {response.url}")
        
        # Should redirect to complete-profile
        self.assertIn(response.status_code, [301, 302])
        if hasattr(response, 'url'):
            self.assertEqual(response.url, reverse('complete-profile'))
    
    def test_cadastro_redirects_when_medico_complete_but_no_clinics(self):
        """Test: Medico complete but no clinics -> should redirect to clinic registration."""
        # Create complete medico
        medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='123456',           # Has CRM
            cns_medico='123456789012345'   # Has CNS
        )
        self.user.medicos.add(medico)
        
        # Set up session (required by view)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = '12345678901'
        session.save()
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"Complete medico, no clinics test - Status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"Complete medico, no clinics test - Redirect to: {response.url}")
        
        # Should redirect to clinics registration
        self.assertIn(response.status_code, [301, 302])
        if hasattr(response, 'url'):
            self.assertEqual(response.url, reverse('clinicas-cadastro'))
    
    def test_cadastro_renders_form_when_everything_complete(self):
        """Test: Everything complete -> should render the form."""
        # Create complete medico
        medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='123456',
            cns_medico='123456789012345'
        )
        self.user.medicos.add(medico)
        
        # Create clinic
        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567',
            logradouro='Test Street',
            logradouro_num='123',
            cidade='Test City',
            bairro='Test Neighborhood',
            cep='12345-678',
            telefone_clinica='11987654321'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(medico)
        
        # Set up session (required by view)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'H30'
        session['cpf_paciente'] = '12345678901'
        session.save()
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"Everything complete test - Status: {response.status_code}")
        print(f"Everything complete test - Content length: {len(response.content)}")
        
        # Should render the form (200 OK with content)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 1000)  # Should have substantial content
    
    def test_cadastro_requires_session_data(self):
        """Test: Missing session data -> should redirect to home."""
        # Create complete setup but no session data
        medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='123456',
            cns_medico='123456789012345'
        )
        self.user.medicos.add(medico)
        
        # No session data set up
        
        response = self.client.get('/processos/cadastro/', follow=False)
        
        print(f"No session test - Status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"No session test - Redirect to: {response.url}")
        
        # Should redirect (probably to home)
        self.assertIn(response.status_code, [301, 302])