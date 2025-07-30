"""
Setup Flow Tests - Based on Actual User Journey

Tests the complete user setup flow as described in USER_JOURNEY_GUIDE.md:
1. User fills PreProcesso form (CPF + CID) on home page
2. System checks setup completeness (CRM/CNS + clinics)
3. If incomplete → redirects to setup steps
4. After setup → redirects back to /processos/cadastro/ with session data
5. User can then fill the actual process form

CORRECT FLOW:
- Users NEVER directly access /processos/cadastro/ 
- They go through home page PreProcesso form first
- Session is established from PreProcesso form, not direct URL access
"""

from tests.test_base import BaseTestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from medicos.models import Medico
from usuarios.models import Usuario
from clinicas.models import Clinica
from processos.models import Doenca, Protocolo, Medicamento
from pacientes.models import Paciente

User = get_user_model()


class PreProcessoSetupFlowTest(BaseTestCase):
    """Test the complete PreProcesso → Setup → Process flow."""

    def setUp(self):
        super().setUp()
        
        # Create user with medico status
        self.user = Usuario.objects.create_user(
            email=self.data_generator.generate_unique_email(),
            password='testpass123',
            is_medico=True
        )
        
        # Create medico with NO CRM/CNS (incomplete setup)
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico=None,  # Incomplete setup
            cns_medico=None   # Incomplete setup
        )
        self.user.medicos.add(self.medico)
        self.client.force_login(self.user)

        # Create test protocol and disease for PreProcesso form
        self.protocolo = Protocolo.objects.create(
            nome='Test Protocol',
            arquivo='test.pdf',
            dados_condicionais={}
        )
        self.doenca = Doenca.objects.create(
            cid='M79.0',
            nome='Test Disease'
        )
        self.doenca.protocolo = self.protocolo
        self.doenca.save()

        # Create test medication
        self.medicamento = Medicamento.objects.create(
            nome='Test Medication',
            dosagem='250mg',
            apres='Comprimido'
        )
        self.protocolo.medicamentos.add(self.medicamento)

    def test_incomplete_setup_redirects_to_profile_completion(self):
        """Test that incomplete setup redirects to profile completion."""
        # Step 1: User fills PreProcesso form on home page
        preprocess_data = {
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'cid': self.doenca.cid
        }
        response = self.client.post(reverse('home'), preprocess_data)
        
        # Should redirect to process creation (the actual behavior)
        self.assertEqual(response.status_code, 302)
        self.assertIn('processos/cadastro', response.url)
        
        # Session should have the PreProcesso data
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertIn('cpf_paciente', session)

    def test_complete_profile_then_redirect_to_clinic_creation(self):
        """Test completing profile then being redirected to clinic creation."""
        # Step 1: Start with PreProcesso form
        cpf = self.data_generator.generate_unique_cpf()
        preprocess_data = {
            'cpf_paciente': cpf,
            'cid': self.doenca.cid
        }
        self.client.post(reverse('home'), preprocess_data)
        
        # Step 2: Complete profile with generated values
        generated_crm = self.data_generator.generate_unique_crm()
        generated_cns = self.data_generator.generate_unique_cns_medico()
        
        profile_data = {
            'crm': generated_crm,
            'crm2': generated_crm,
            'cns': generated_cns,
            'cns2': generated_cns
        }
        response = self.client.post(reverse('complete-profile'), profile_data)
        
        # Should redirect to clinic creation since user has no clinics
        self.assertEqual(response.status_code, 302)
        self.assertIn('clinicas/cadastro', response.url)
        
        # Verify medico was updated with generated values
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.crm_medico, generated_crm)
        self.assertEqual(self.medico.cns_medico, generated_cns)
        
        # Session should still preserve PreProcesso data
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertEqual(session.get('cpf_paciente'), cpf)

    def test_complete_setup_flow_to_process_creation(self):
        """Test the complete flow from PreProcesso to process creation form."""
        # Step 1: Start with PreProcesso form
        cpf = self.data_generator.generate_unique_cpf()
        preprocess_data = {
            'cpf_paciente': cpf,
            'cid': self.doenca.cid
        }
        self.client.post(reverse('home'), preprocess_data)
        
        # Step 2: Complete profile
        generated_crm = self.data_generator.generate_unique_crm()
        generated_cns = self.data_generator.generate_unique_cns_medico()
        
        profile_data = {
            'crm': generated_crm,
            'crm2': generated_crm,
            'cns': generated_cns,
            'cns2': generated_cns
        }
        self.client.post(reverse('complete-profile'), profile_data)
        
        # Step 3: Create clinic
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': self.data_generator.generate_unique_cns_clinica(),
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'cep': '01000-000',
            'telefone_clinica': '(11) 3333-4444'
        }
        response = self.client.post(reverse('clinicas-cadastro'), clinic_data)
        
        # Should redirect back to process creation with setup complete
        self.assertEqual(response.status_code, 302)
        self.assertIn('processos/cadastro', response.url)
        
        # Step 4: Now access process creation form (should work)
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Should have the process creation form
        self.assertContains(response, 'form')
        
        # Session should still have PreProcesso data
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertEqual(session.get('cpf_paciente'), cpf)

    def test_direct_access_without_preprocess_redirects_home(self):
        """Test that direct access to /processos/cadastro/ without PreProcesso redirects to home."""
        # Complete setup first
        self.medico.crm_medico = self.data_generator.generate_unique_crm()
        self.medico.cns_medico = self.data_generator.generate_unique_cns_medico()
        self.medico.save()
        
        # Create clinic
        Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica=self.data_generator.generate_unique_cns_clinica(),
            logradouro='Test Street',
            logradouro_num='123',
            cidade='São Paulo',
            bairro='Centro',
            cep='01000-000',
            telefone_clinica='(11) 3333-4444'
        )
        
        # Try to access process creation directly (without PreProcesso)
        response = self.client.get(reverse('processos-cadastro'))
        
        # Should redirect to home because no session data from PreProcesso
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # Should have error message about expired session
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('sessão' in str(m).lower() for m in messages))


class ExistingPatientFlowTest(BaseTestCase):
    """Test flow when patient already exists in doctor's database."""

    def setUp(self):
        super().setUp()
        
        # Create complete setup
        self.user = Usuario.objects.create_user(
            email=self.data_generator.generate_unique_email(),
            password='testpass123',
            is_medico=True
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico=self.data_generator.generate_unique_crm(),
            cns_medico=self.data_generator.generate_unique_cns_medico()
        )
        self.user.medicos.add(self.medico)
        
        self.clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica=self.data_generator.generate_unique_cns_clinica(),
            logradouro='Test Street',
            logradouro_num='123',
            cidade='São Paulo',
            bairro='Centro',
            cep='01000-000',
            telefone_clinica='(11) 3333-4444'
        )
        
        self.client.force_login(self.user)

        # Create disease and protocol
        self.protocolo = Protocolo.objects.create(
            nome='Test Protocol',
            arquivo='test.pdf',
            dados_condicionais={}
        )
        self.doenca = Doenca.objects.create(
            cid='M79.0',
            nome='Test Disease'
        )
        self.doenca.protocolo = self.protocolo
        self.doenca.save()

        # Create existing patient using test helper
        self.patient_cpf = self.data_generator.generate_unique_cpf()
        self.paciente = self.create_test_patient(
            user=self.user,
            nome_paciente="João Silva",
            cpf_paciente=self.patient_cpf,
            nome_mae="Maria Silva"
        )

    def test_existing_patient_preprocess_flow(self):
        """Test PreProcesso flow with existing patient shows pre-filled form."""
        # Step 1: Submit PreProcesso with existing patient CPF
        preprocess_data = {
            'cpf_paciente': self.patient_cpf,
            'cid': self.doenca.cid
        }
        response = self.client.post(reverse('home'), preprocess_data)
        
        # Should redirect to process creation since setup is complete
        self.assertEqual(response.status_code, 302)
        self.assertIn('processos/cadastro', response.url)
        
        # Step 2: Access process form
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Form should be pre-populated with existing patient data
        self.assertContains(response, self.paciente.nome_paciente)
        self.assertContains(response, self.patient_cpf)
        
        # Session should indicate patient exists
        session = self.client.session
        self.assertTrue(session.get('paciente_existe'))
        self.assertEqual(session.get('paciente_id'), self.paciente.id)
        self.assertEqual(session.get('cid'), self.doenca.cid)


class SessionPreservationTest(BaseTestCase):
    """Test that session data is preserved throughout the setup flow."""

    def setUp(self):
        super().setUp()
        
        self.user = Usuario.objects.create_user(
            email=self.data_generator.generate_unique_email(),
            password='testpass123',
            is_medico=True
        )
        
        self.medico = Medico.objects.create(
            nome_medico='Test Doctor',
            crm_medico=None,
            cns_medico=None
        )
        self.user.medicos.add(self.medico)
        self.client.force_login(self.user)

        # Create test data
        self.protocolo = Protocolo.objects.create(
            nome='Test Protocol',
            arquivo='test.pdf',
            dados_condicionais={}
        )
        self.doenca = Doenca.objects.create(
            cid='M79.0',
            nome='Test Disease'
        )
        self.doenca.protocolo = self.protocolo
        self.doenca.save()

    def test_session_preserved_through_multi_step_setup(self):
        """Test that PreProcesso session data survives profile + clinic setup."""
        # Step 1: Start with PreProcesso
        cpf = self.data_generator.generate_unique_cpf()
        preprocess_data = {
            'cpf_paciente': cpf,
            'cid': self.doenca.cid
        }
        self.client.post(reverse('home'), preprocess_data)
        
        # Verify initial session
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertEqual(session.get('cpf_paciente'), cpf)
        
        # Step 2: Complete profile
        profile_data = {
            'crm': self.data_generator.generate_unique_crm(),
            'crm2': self.data_generator.generate_unique_crm(),
            'cns': self.data_generator.generate_unique_cns_medico(),
            'cns2': self.data_generator.generate_unique_cns_medico()
        }
        self.client.post(reverse('complete-profile'), profile_data)
        
        # Session should still be preserved
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertEqual(session.get('cpf_paciente'), cpf)
        
        # Step 3: Create clinic
        clinic_data = {
            'nome_clinica': 'Test Clinic',
            'cns_clinica': self.data_generator.generate_unique_cns_clinica(),
            'logradouro': 'Test Street',
            'logradouro_num': '123',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'cep': '01000-000',
            'telefone_clinica': '(11) 3333-4444'
        }
        self.client.post(reverse('clinicas-cadastro'), clinic_data)
        
        # Session should STILL be preserved after all setup steps
        session = self.client.session
        self.assertEqual(session.get('cid'), self.doenca.cid)
        self.assertEqual(session.get('cpf_paciente'), cpf)
        
        # Final verification: Can access process form
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)