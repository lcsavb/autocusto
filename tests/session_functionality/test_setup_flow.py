"""
Comprehensive tests for setup flow functionality.

This consolidates all setup flow tests across different apps:
- Session preservation during redirects
- Multi-step setup completion
- Integration between medicos, clinicas, and processos
- User experience continuity
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from medicos.models import Medico
from usuarios.models import Usuario
from clinicas.models import Clinica
from processos.models import Doenca


class SetupFlowRedirectTest(TestCase):
    """Test setup flow redirect logic."""

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

    def test_redirect_to_profile_when_missing_crm_cns(self):
        """Test redirect to complete-profile when CRM/CNS are missing."""
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

    def test_redirect_to_clinics_when_missing_clinics(self):
        """Test redirect to clinic registration when user has no clinics."""
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
        """Test process creation when setup is complete."""
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


class SessionPreservationTest(TestCase):
    """Test session preservation during setup flow."""

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

    def test_session_preserved_during_profile_completion(self):
        """Test that session data is preserved during profile completion."""
        # Set up session data
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'M79.0'
        session['paciente_id'] = '123'
        session['data1'] = '01/01/2024'
        session['extra_data'] = 'test_value'
        session.save()

        # Complete profile
        profile_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=profile_data)
        
        # Verify session data preserved after profile completion
        self.assertEqual(self.client.session.get('paciente_existe'), True)
        self.assertEqual(self.client.session.get('cid'), 'M79.0')
        self.assertEqual(self.client.session.get('paciente_id'), '123')
        self.assertEqual(self.client.session.get('data1'), '01/01/2024')
        self.assertEqual(self.client.session.get('extra_data'), 'test_value')

    def test_session_data_types_preserved(self):
        """Test that different session data types are preserved correctly."""
        # Set up various data types in session
        session = self.client.session
        session['paciente_existe'] = True  # Boolean
        session['cid'] = 'M79.0'  # String
        session['paciente_id'] = 123  # Integer
        session['price'] = 99.99  # Float
        session['tags'] = ['tag1', 'tag2']  # List
        session['metadata'] = {'key': 'value'}  # Dict
        session.save()

        # Complete profile
        profile_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        self.client.post(reverse('complete-profile'), data=profile_data)

        # Verify all data types preserved
        self.assertEqual(self.client.session.get('paciente_existe'), True)
        self.assertEqual(self.client.session.get('cid'), 'M79.0')
        self.assertEqual(self.client.session.get('paciente_id'), 123)
        self.assertEqual(self.client.session.get('price'), 99.99)
        self.assertEqual(self.client.session.get('tags'), ['tag1', 'tag2'])
        self.assertEqual(self.client.session.get('metadata'), {'key': 'value'})

    def test_complete_setup_flow_with_session_preservation(self):
        """Test complete setup flow preserves all session data."""
        # Step 1: Start with session data (simulating process creation start)
        session = self.client.session
        session['paciente_existe'] = False
        session['cid'] = 'M79.0'
        session['cpf_paciente'] = '12345678901'
        session['data1'] = '01/01/2024'
        session['extra_field'] = 'test_value'
        session['user_settings'] = {'theme': 'dark'}
        session.save()

        # Step 2: Complete profile
        profile_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=profile_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Complete clinic registration (simulate)
        # Note: This would normally redirect to clinic form, then back to process
        # For test purposes, we verify session data is still intact
        
        # Verify all session data is preserved throughout
        self.assertEqual(self.client.session.get('paciente_existe'), False)
        self.assertEqual(self.client.session.get('cid'), 'M79.0')
        self.assertEqual(self.client.session.get('cpf_paciente'), '12345678901')
        self.assertEqual(self.client.session.get('data1'), '01/01/2024')
        self.assertEqual(self.client.session.get('extra_field'), 'test_value')
        self.assertEqual(self.client.session.get('user_settings'), {'theme': 'dark'})


class SetupFlowIntegrationTest(TestCase):
    """Test setup flow integration across apps."""

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

    def test_profile_completion_redirects_correctly(self):
        """Test profile completion redirects based on clinic existence."""
        # Test 1: No clinics - should redirect to clinic registration
        form_data = {
            'crm': '123456',
            'crm2': '123456',
            'cns': '123456789012345',
            'cns2': '123456789012345'
        }
        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('clinicas-cadastro'))
        
        # Test 2: With clinics - should redirect to process creation
        clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567'
        )
        clinica.usuarios.add(self.user)
        clinica.medicos.add(self.medico)

        # Reset medico for second test
        self.medico.crm_medico = ''
        self.medico.cns_medico = ''
        self.medico.save()

        response = self.client.post(reverse('complete-profile'), data=form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-cadastro'))

    def test_session_validation_in_process_creation(self):
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
        self.assertEqual(response.url, reverse('home'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Sessão expirada. Por favor, inicie o cadastro novamente.' in str(m) for m in messages))

        # Test missing CID
        session = self.client.session
        session['paciente_existe'] = True
        session.pop('cid', None)  # Remove CID
        session.save()

        response = self.client.get(reverse('processos-cadastro'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.' in str(m) for m in messages))

    def test_immutability_enforcement_throughout_flow(self):
        """Test that immutability is enforced throughout the setup flow."""
        # Set initial values
        self.medico.crm_medico = '999999'
        self.medico.cns_medico = '999999999999999'
        self.medico.save()

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

        # Form should show fields as disabled
        response = self.client.get(reverse('complete-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRM já definido e não pode ser alterado')
        self.assertContains(response, 'CNS já definido e não pode ser alterado')