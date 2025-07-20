"""
Process setup integration tests.

Consolidated from processos/test_setup_integration.py
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from usuarios.models import Usuario
from medicos.models import Medico
from clinicas.models import Clinica
from processos.models import Doenca


class ProcessSetupIntegrationTest(TestCase):
    """Test process setup integration and redirects."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_medico=True
        )
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico='',
            cns_medico=''
        )
        self.user.medicos.add(self.medico)
        self.client.login(username='test@example.com', password='testpass123')
        
        # Create test disease for process creation
        self.doenca = Doenca.objects.create(
            cid='M79.0',
            nome='Test Disease'
        )

    def test_process_creation_redirect_when_missing_crm_cns(self):
        """Test that process creation redirects when CRM/CNS are missing."""
        # Set up session data for process creation
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session['paciente_id'] = '123'
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        # Should redirect to complete-profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete-profile'))
        
        # Check info message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Complete seus dados médicos antes de criar processos.' in str(m) for m in messages))

    def test_process_creation_redirect_when_missing_clinics(self):
        """Test that process creation redirects when user has no clinics."""
        # Set CRM and CNS
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        # Set up session data for process creation
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session['paciente_id'] = '123'
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        # Should redirect to clinic registration
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('clinicas-cadastro'))
        
        # Check info message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Cadastre uma clínica antes de criar processos.' in str(m) for m in messages))

    def test_process_creation_when_setup_complete(self):
        """Test that process creation works when setup is complete."""
        # Complete setup: set CRM, CNS and create clinic
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        # Set up session data for process creation
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session['paciente_id'] = '123'
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        # Should render the process creation form
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Disease')  # Should show disease name

    def test_redirect_priority_crm_cns_over_clinics(self):
        """Test that CRM/CNS check has priority over clinic check."""
        # Create clinic but leave CRM/CNS empty
        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        # Set up session data
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        # Should redirect to complete-profile (CRM/CNS), not clinic registration
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('complete-profile'))

    def test_session_validation_requirements(self):
        """Test session validation requirements for process creation."""
        # Complete setup first
        self.medico.crm_medico = '123456'
        self.medico.cns_medico = '123456789012345'
        self.medico.save()

        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        # Test missing paciente_existe
        session = self.client.session
        session['cid'] = 'M79.0'
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-home'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Sessão expirada. Por favor, inicie o cadastro novamente.' in str(m) for m in messages))

        # Test missing CID
        session = self.client.session
        session['paciente_existe'] = True
        session.pop('cid', None)  # Remove CID
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-home'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.' in str(m) for m in messages))

    def test_complete_flow_session_preservation(self):
        """Test complete flow preserves session data throughout."""
        # Step 1: Start with session data (simulating process creation start)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'M79.0'
        session['cpf_paciente'] = '12345678901'
        session['data1'] = '01/01/2024'
        session['extra_field'] = 'test_value'
        session['user_settings'] = {'theme': 'dark'}
        session.save()

        # Step 2: Complete profile with CRM/CNS
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Complete clinic registration
        clinic_data = {
            'nome_clinica': 'Flow Test Clinic',
            'cns_clinica': '1234567'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-cadastro'))
        
        # Step 4: Verify we can now access process creation with preserved session
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Verify all session data is preserved throughout
        self.assertEqual(self.client.session.get('paciente_existe'), False)
        self.assertEqual(self.client.session.get('cid'), 'M79.0')
        self.assertEqual(self.client.session.get('cpf_paciente'), '12345678901')
        self.assertEqual(self.client.session.get('data1'), '01/01/2024')
        self.assertEqual(self.client.session.get('extra_field'), 'test_value')
        self.assertEqual(self.client.session.get('user_settings'), {'theme': 'dark'})

    def test_setup_flow_without_session_data(self):
        """Test setup flow behavior when not coming from process creation."""
        # Complete profile without session data
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Should redirect to clinic registration normally
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('clinicas-cadastro'))
        
        # Complete clinic registration without session data
        clinic_data = {
            'nome_clinica': 'No Session Clinic',
            'cns_clinica': '1234567'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Should redirect to home (not process creation) since no session
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_immutability_enforcement_throughout_process_flow(self):
        """Test that immutability is enforced throughout the process flow."""
        # Set initial values
        self.medico.crm_medico = '999999'
        self.medico.cns_medico = '999999999999999'
        self.medico.save()

        # Set up session data
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session.save()

        # Try to change values through profile completion
        form_data = {
            'crm': '123456',  # Different values
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        # Values should remain unchanged
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.crm_medico, '999999')
        self.assertEqual(self.medico.cns_medico, '999999999999999')

        # Create clinic to complete setup
        clinica = Clinica.objects.create(
            nome_clinica='Immutable Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        # Now should be able to access process creation
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
