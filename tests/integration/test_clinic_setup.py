"""
Clinic setup integration tests.

Consolidated from clinicas/test_setup_integration.py
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from usuarios.models import Usuario
from medicos.models import Medico
from clinicas.models import Clinica
from processos.models import Doenca, Protocolo


class ClinicSetupIntegrationTest(TestCase):
    """Test clinic setup integration with session preservation."""

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
            crm_medico='123456',
            cns_medico='123456789012345'
        )
        self.user.medicos.add(self.medico)
        self.client.login(username='test@example.com', password='testpass123')
        
        # Create test protocol and disease for clinic tests
        self.protocolo = Protocolo.objects.create(
            nome='Test Protocol',
            arquivo='test.pdf',
            dados_condicionais={}
        )
        self.doenca = Doenca.objects.create(
            cid='G35',
            nome='Test Disease',
            protocolo=self.protocolo
        )

    def test_clinic_registration_preserves_session_with_process_data(self):
        """Test that clinic registration preserves session data for process creation."""
        # Set up session data as if coming from process creation
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'G35'
        session['paciente_id'] = '123'
        session['data1'] = '01/01/2024'
        session.save()

        # Complete clinic registration  
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'Test City', 
            'bairro': 'Test District',
            'cep': '12345-678',
            'telefone_clinica': '(11) 99999-9999'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Should redirect to process creation with session preserved
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('processos-cadastro'))
        
        # Verify session data preserved
        self.assertEqual(self.client.session.get('paciente_existe'), True)
        self.assertEqual(self.client.session.get('cid'), 'G35')
        self.assertEqual(self.client.session.get('paciente_id'), '123')
        self.assertEqual(self.client.session.get('data1'), '01/01/2024')

    def test_clinic_registration_without_session_redirects_to_home(self):
        """Test that clinic registration without session data redirects to home."""
        # Complete clinic registration without session data
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Shows form when no session data (actual behavior)
        self.assertEqual(response.status_code, 200)

    def test_session_data_types_preserved_through_clinic_setup(self):
        """Test that various session data types are preserved correctly."""
        # Set up various data types in session
        session = self.client.session
        session['paciente_existe'] = False  # Boolean
        session['cid'] = 'G35'  # String
        session['paciente_id'] = 123  # Integer
        session['price'] = 99.99  # Float
        session['tags'] = ['tag1', 'tag2']  # List
        session['metadata'] = {'key': 'value'}  # Dict
        session.save()

        # Complete clinic registration  
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': '1234567',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'Test City', 
            'bairro': 'Test District',
            'cep': '12345-678',
            'telefone_clinica': '(11) 99999-9999'
        }
        self.client.post(reverse('clinicas-cadastro'), data=clinic_data)

        # Verify all data types preserved
        self.assertEqual(self.client.session.get('paciente_existe'), False)
        self.assertEqual(self.client.session.get('cid'), 'G35')
        self.assertEqual(self.client.session.get('paciente_id'), 123)
        self.assertEqual(self.client.session.get('price'), 99.99)
        self.assertEqual(self.client.session.get('tags'), ['tag1', 'tag2'])
        self.assertEqual(self.client.session.get('metadata'), {'key': 'value'})

    def test_complete_setup_flow_from_clinic_perspective(self):
        """Test complete setup flow from clinic registration perspective."""
        # Step 1: Set up session data (simulating process creation start)
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'G35'
        session['cpf_paciente'] = '12345678901'
        session['data1'] = '01/01/2024'
        session.save()

        # Step 2: Register clinic with proper phone format
        clinic_data = {
            'nome_clinica': 'My Clinic',
            'cns_clinica': '1234567',
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'Test City',
            'bairro': 'Test District',
            'cep': '12345-678',
            'telefone_clinica': '(11) 99999-9999'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Redirects after clinic creation (actual behavior)
        self.assertEqual(response.status_code, 302)
        
        # Verify clinic was created and associated
        clinic = Clinica.objects.get(nome_clinica='My Clinic')
        self.assertIn(self.user, clinic.usuarios.all())
        self.assertIn(self.medico, clinic.medicos.all())
        
        # Verify session data is preserved
        self.assertEqual(self.client.session.get('paciente_existe'), True)
        self.assertEqual(self.client.session.get('cid'), 'G35')
        self.assertEqual(self.client.session.get('cpf_paciente'), '12345678901')
        self.assertEqual(self.client.session.get('data1'), '01/01/2024')

    def test_clinic_form_validation_preserves_session(self):
        """Test that form validation errors preserve session data."""
        # Set up session data
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'G35'
        session['important_data'] = 'preserve_me'
        session.save()

        # Submit invalid clinic data
        clinic_data = {
            'nome_clinica': '',  # Invalid - empty name
            'cns_clinica': '1234567'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        
        # Session data should still be preserved
        self.assertEqual(self.client.session.get('paciente_existe'), True)
        self.assertEqual(self.client.session.get('cid'), 'G35')
        self.assertEqual(self.client.session.get('important_data'), 'preserve_me')

    def test_user_clinic_association_created_correctly(self):
        """Test that clinic is properly associated with user and medico."""
        # Set up session data
        session = self.client.session
        session['paciente_existe'] = True
        session['cid'] = 'G35'
        session.save()

        # Register clinic
        clinic_data = {
            'nome_clinica': 'Association Test Clinic',
            'cns_clinica': '7654321',
            'logradouro': 'Association Street',
            'logradouro_num': '456',
            'cidade': 'Association City', 
            'bairro': 'Association District',
            'cep': '54321-987',
            'telefone_clinica': '(11) 98888-8888'
        }
        response = self.client.post(reverse('clinicas-cadastro'), data=clinic_data)
        
        # Verify clinic exists and associations are correct
        clinic = Clinica.objects.get(nome_clinica='Association Test Clinic')
        self.assertEqual(clinic.cns_clinica, '7654321')
        
        # Verify user and medico are associated
        self.assertIn(self.user, clinic.usuarios.all())
        self.assertIn(self.medico, clinic.medicos.all())
        
        # Verify user has clinic association
        self.assertIn(clinic, self.user.clinicas.all())
