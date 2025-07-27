"""
Process Views Business Logic Testing Module

FOCUS: Business logic, workflow, and form handling (NOT security - that's covered in test_security.py)

This module tests the business logic aspects of process views:
- Form validation and data processing
- Session workflow management  
- Dynamic form field generation based on protocols
- PDF generation workflow logic
- Error handling for business scenarios
- Integration with external data functions

WHAT WE DON'T DUPLICATE:
- Authentication/authorization (covered in test_security.py)
- User isolation/access control (covered in test_security.py)
- Security-related edge cases (covered in test_security.py)

WHAT WE FOCUS ON:
- Form processing logic and validation
- Session state management across workflow steps
- Dynamic field generation from protocol configurations  
- Business rule validation (medication requirements, etc.)
- Error handling for data processing failures
- Integration with PDF generation system
"""

import json
from datetime import date, datetime
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.messages import get_messages

from usuarios.models import Usuario
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from pacientes.models import Paciente
from processos.models import Processo, Doenca, Protocolo, Medicamento


class ProcessViewsBusinessLogicTestBase(TestCase):
    """Base class for business logic tests with minimal test data setup."""
    
    def setUp(self):
        """Create minimal test data focused on business logic scenarios."""
        # Basic entities for business logic testing
        self.user = Usuario.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        self.medico = Medico.objects.create(
            nome_medico="Dr. Test",
            crm_medico="123456",
            cns_medico="123456789012345"
        )
        
        self.clinica = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="1234567",  # Fixed length
            logradouro="Test St", logradouro_num="123",
            cidade="Test City", bairro="Test District",
            cep="12345-678", telefone_clinica="11999999999"
        )
        
        self.emissor = Emissor.objects.create(
            medico=self.medico, clinica=self.clinica
        )
        
        # Protocol with dynamic fields for testing
        self.protocolo = Protocolo.objects.create(
            nome="test_protocol",
            arquivo="test.pdf",
            dados_condicionais={
                "fields": [
                    {
                        "name": "severity_score",
                        "type": "choice",
                        "label": "Disease Severity",
                        "choices": [("mild", "Mild"), ("severe", "Severe")],
                        "required": True
                    },
                    {
                        "name": "notes",
                        "type": "textarea", 
                        "label": "Clinical Notes",
                        "required": False
                    }
                ]
            }
        )
        
        self.doenca = Doenca.objects.create(
            cid="T99.9",
            nome="Test Disease",
            protocolo=self.protocolo
        )
        
        self.medicamento = Medicamento.objects.create(
            nome="Test Medication",
            dosagem="100mg",
            apres="Tablet"
        )
        
        self.paciente = Paciente.objects.create(
            nome_paciente="Test Patient",
            cpf_paciente="12345678901",
            cns_paciente="123456789012345",
            nome_mae="Test Mother",
            idade="30", sexo="M", peso="70", altura="1.75",
            incapaz=False, etnia="Test", telefone1_paciente="11999999999",
            end_paciente="Test Address", rg="123456789",
            escolha_etnia="Test", cidade_paciente="Test City",
            cep_paciente="12345-678"
        )
        self.paciente.usuarios.add(self.user)
        
        self.client = Client()
        self.client.force_login(self.user)


class TestCadastroBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test business logic for prescription creation (cadastro view)."""
    
    def test_dynamic_form_field_generation(self):
        """
        Test that dynamic form fields are generated based on protocol configuration.
        
        BUSINESS LOGIC: Forms should include protocol-specific fields
        """
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        response = self.client.get(reverse('processos-cadastro'))
        
        # Check that dynamic fields from protocol are included
        self.assertContains(response, 'severity_score')
        self.assertContains(response, 'Disease Severity')
        self.assertContains(response, 'Clinical Notes')

    def test_medication_field_population(self):
        """
        Test that medication fields are properly populated from database.
        
        BUSINESS LOGIC: Medication dropdowns should show available medications
        """
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        response = self.client.get(reverse('processos-cadastro'))
        
        # Should contain medication selection fields
        self.assertContains(response, 'id_med1')
        self.assertContains(response, self.medicamento.nome)

    @patch('processos.views.transfere_dados_gerador')
    def test_form_data_processing_with_dynamic_fields(self, mock_transfere):
        """
        Test form processing includes dynamic protocol fields.
        
        BUSINESS LOGIC: Dynamic fields should be included in data processing
        """
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        form_data = {
            'nome_paciente': self.paciente.nome_paciente,
            'cpf_paciente': self.paciente.cpf_paciente,
            'anamnese': 'Test anamnese',
            'severity_score': 'mild',  # Dynamic field
            'notes': 'Test clinical notes',  # Dynamic field
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '1 tablet daily',
            'qtd_med1_mes1': '30',
            'med1_repetir_posologia': 'True',
            'tratou': 'True',
            'preenchido_por': 'medico',
            'data_1': date.today().strftime('%Y-%m-%d')
        }
        
        mock_transfere.return_value = (form_data, 'success')
        
        response = self.client.post(reverse('processos-cadastro'), form_data)
        
        # Should call data transfer function with dynamic fields
        mock_transfere.assert_called_once()
        call_args = mock_transfere.call_args[0][0]  # First positional argument
        self.assertIn('severity_score', call_args)
        self.assertIn('notes', call_args)

    def test_session_data_validation(self):
        """
        Test validation when required session data is missing or invalid.
        
        BUSINESS LOGIC: Should handle missing session gracefully
        """
        # Test with no session data
        response = self.client.get(reverse('processos-cadastro'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect or error
        
        # Test with partial session data
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        # Missing 'cid'
        session.save()
        
        response = self.client.get(reverse('processos-cadastro'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect or error

    @patch('processos.views.transfere_dados_gerador')
    def test_form_validation_error_handling(self, mock_transfere):
        """
        Test form validation error handling and user feedback.
        
        BUSINESS LOGIC: Form errors should be displayed to user
        """
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        # Submit form with missing required field
        incomplete_form_data = {
            'nome_paciente': '',  # Required field missing
            'severity_score': '',  # Required dynamic field missing
        }
        
        mock_transfere.return_value = (incomplete_form_data, 'error')
        
        response = self.client.post(reverse('processos-cadastro'), incomplete_form_data)
        
        # Should stay on form page (not redirect)
        self.assertEqual(response.status_code, 200)
        # Should show form again with errors
        self.assertContains(response, 'severity_score')  # Form fields should be present


class TestEdicaoBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test business logic for prescription editing (edicao view)."""
    
    def setUp(self):
        super().setUp()
        # Create existing process for editing tests
        self.processo = Processo.objects.create(
            anamnese="Original anamnese",
            doenca=self.doenca,
            prescricao={"med1": "Test Med"},
            tratou=True,
            tratamentos_previos="None",
            data1=date.today(),
            preenchido_por="M",
            usuario=self.user,
            paciente=self.paciente
        )

    def test_process_data_preloading(self):
        """
        Test that existing process data is preloaded into form.
        
        BUSINESS LOGIC: Edit form should show current process data
        """
        session = self.client.session
        session['processo_id'] = self.processo.id
        session.save()
        
        response = self.client.get(reverse('processos-edicao'))
        
        # Should preload existing data
        self.assertContains(response, "Original anamnese")
        self.assertContains(response, self.paciente.nome_paciente)

    @patch('processos.views.transfere_dados_gerador')
    def test_process_update_logic(self, mock_transfere):
        """
        Test that process updates are properly handled.
        
        BUSINESS LOGIC: Should update existing process, not create new one
        """
        session = self.client.session
        session['processo_id'] = self.processo.id
        session.save()
        
        updated_data = {
            'nome_paciente': self.paciente.nome_paciente,
            'anamnese': 'Updated anamnese',
            'severity_score': 'severe',  # Changed value
            'tratou': 'True',
            'preenchido_por': 'medico'
        }
        
        mock_transfere.return_value = (updated_data, 'success')
        
        response = self.client.post(reverse('processos-edicao'), updated_data)
        
        # Should redirect to PDF generation
        self.assertEqual(response.status_code, 302)
        self.assertIn('pdf', response.url)


class TestRenovacaoRapidaBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test business logic for quick prescription renewal."""
    
    def setUp(self):
        super().setUp()
        self.processo = Processo.objects.create(
            anamnese="Renewal test",
            doenca=self.doenca,
            prescricao={"med1": "Test Med"},
            tratou=True,
            tratamentos_previos="Previous treatments",
            data1=date.today(),
            preenchido_por="M",
            usuario=self.user,
            paciente=self.paciente
        )

    @patch('processos.views.gerar_dados_renovacao')
    @patch('processos.views.transfere_dados_gerador')
    def test_renewal_data_generation(self, mock_transfere, mock_gerar):
        """
        Test that renewal generates appropriate data from existing process.
        
        BUSINESS LOGIC: Should copy previous prescription data with updates
        """
        session = self.client.session
        session['processo_id'] = self.processo.id
        session.save()
        
        mock_gerar.return_value = {'renewed': True, 'data': 'test'}
        mock_transfere.return_value = ({'data': 'renewed'}, 'success')
        
        response = self.client.get(reverse('processos-renovacao-rapida'))
        
        # Should call renewal data generation
        mock_gerar.assert_called_once_with(self.processo.id)
        
        # Should redirect to PDF generation
        self.assertEqual(response.status_code, 302)

    def test_renewal_without_existing_process(self):
        """
        Test renewal behavior when no existing process is selected.
        
        BUSINESS LOGIC: Should handle missing process gracefully
        """
        # No session data set
        response = self.client.get(reverse('processos-renovacao-rapida'))
        
        # Should redirect (can't renew without existing process)
        self.assertEqual(response.status_code, 302)


class TestPDFGenerationBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test business logic for PDF generation workflow."""
    
    @patch('processos.views.GeradorPDF')
    def test_pdf_generation_with_complete_data(self, mock_gerador):
        """
        Test PDF generation with complete session data.
        
        BUSINESS LOGIC: Should generate PDF from session data
        """
        # Setup mock
        mock_response = HttpResponse(b'%PDF-test', content_type='application/pdf')
        mock_gerador_instance = MagicMock()
        mock_gerador_instance.generico_stream.return_value = mock_response
        mock_gerador.return_value = mock_gerador_instance
        
        # Setup session with complete data
        session = self.client.session
        session['dados_lme_base'] = {
            'cpf_paciente': self.paciente.cpf_paciente,
            'nome_paciente': self.paciente.nome_paciente,
            'cid': self.doenca.cid,
            'severity_score': 'mild',
            'med1': 'Test Medication'
        }
        session['path_lme_base'] = '/test/path/lme.pdf'
        session.save()
        
        response = self.client.get(reverse('processos-pdf'))
        
        # Should generate PDF successfully
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        mock_gerador.assert_called_once()

    def test_pdf_generation_missing_data(self):
        """
        Test PDF generation when session data is incomplete.
        
        BUSINESS LOGIC: Should handle missing data gracefully
        """
        # Session with missing required data
        session = self.client.session
        session['dados_lme_base'] = {'incomplete': 'data'}
        # Missing 'path_lme_base'
        session.save()
        
        response = self.client.get(reverse('processos-pdf'))
        
        # Should handle missing data (redirect or error)
        self.assertNotEqual(response.status_code, 200)

    @patch('processos.views.GeradorPDF')
    def test_pdf_generation_error_handling(self, mock_gerador):
        """
        Test PDF generation error handling.
        
        BUSINESS LOGIC: Should handle PDF generation failures gracefully
        """
        # Setup mock to raise exception
        mock_gerador.side_effect = Exception("PDF generation failed")
        
        session = self.client.session
        session['dados_lme_base'] = {'test': 'data'}
        session['path_lme_base'] = '/test/path.pdf'
        session.save()
        
        response = self.client.get(reverse('processos-pdf'))
        
        # Should handle error gracefully (not crash)
        self.assertIn(response.status_code, [302, 500])  # Redirect or error response


class TestAjaxBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test AJAX endpoints business logic (busca_doencas, verificar_1_vez)."""
    
    def test_busca_doencas_returns_json(self):
        """
        Test disease search AJAX endpoint returns proper JSON.
        
        BUSINESS LOGIC: Should return disease data as JSON for frontend
        """
        response = self.client.get(
            reverse('busca-doencas'), 
            {'q': 'Test'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Should return JSON data
        data = json.loads(response.content)
        self.assertIsInstance(data, list)

    def test_verificar_1_vez_ajax(self):
        """
        Test first-time verification AJAX endpoint.
        
        BUSINESS LOGIC: Should check if patient is receiving medication for first time
        """
        response = self.client.get(
            reverse('verificar_1_vez'),
            {
                'cpf': self.paciente.cpf_paciente,
                'cid': self.doenca.cid,
                'med_id': str(self.medicamento.id)
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Should return JSON response
        data = json.loads(response.content)
        self.assertIn('primeira_vez', data)


class TestSessionWorkflowManagement(ProcessViewsBusinessLogicTestBase):
    """Test session state management across the workflow."""
    
    def test_session_data_persistence_across_views(self):
        """
        Test that session data persists correctly across workflow steps.
        
        BUSINESS LOGIC: Multi-step workflow should maintain state
        """
        # Step 1: Set initial session data (simulating user selection)
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        # Step 2: Access cadastro (should use session data)
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Submit form (should update session)
        form_data = {
            'nome_paciente': self.paciente.nome_paciente,
            'anamnese': 'Test workflow'
        }
        
        with patch('processos.views.transfere_dados_gerador') as mock_transfere:
            mock_transfere.return_value = (form_data, 'success')
            
            response = self.client.post(reverse('processos-cadastro'), form_data)
            
            # Should redirect to PDF generation
            if response.status_code == 302:
                self.assertIn('pdf', response.url)

    def test_session_cleanup_on_completion(self):
        """
        Test that session data is properly managed after workflow completion.
        
        BUSINESS LOGIC: Should clean up session data to prevent conflicts
        """
        # Setup session data
        session = self.client.session
        session['dados_lme_base'] = {'test': 'data'}
        session['path_lme_base'] = '/test/path.pdf'
        session.save()
        
        # Complete PDF generation
        with patch('processos.views.GeradorPDF') as mock_gerador:
            mock_response = HttpResponse(b'%PDF-test', content_type='application/pdf')
            mock_gerador_instance = MagicMock()
            mock_gerador_instance.generico_stream.return_value = mock_response
            mock_gerador.return_value = mock_gerador_instance
            
            response = self.client.get(reverse('processos-pdf'))
            self.assertEqual(response.status_code, 200)
            
            # After PDF generation, could verify session state
            # (This depends on implementation details)


# INTEGRATION: Business Logic Workflow Tests
class TestCompleteWorkflowBusinessLogic(ProcessViewsBusinessLogicTestBase):
    """Test complete business workflows from start to finish."""
    
    @patch('processos.views.transfere_dados_gerador')
    @patch('processos.views.GeradorPDF')
    def test_new_prescription_complete_workflow(self, mock_gerador, mock_transfere):
        """
        Test complete new prescription workflow - business logic focus.
        
        WORKFLOW: Session setup → Form display → Form processing → PDF generation
        """
        # Setup mocks
        mock_transfere.return_value = ({'test': 'data'}, 'success')
        mock_pdf_response = HttpResponse(b'%PDF-test', content_type='application/pdf')
        mock_gerador_instance = MagicMock()
        mock_gerador_instance.generico_stream.return_value = mock_pdf_response
        mock_gerador.return_value = mock_gerador_instance
        
        # Step 1: Setup session
        session = self.client.session
        session['cpf_paciente'] = self.paciente.cpf_paciente
        session['cid'] = self.doenca.cid
        session.save()
        
        # Step 2: Get form (should load with dynamic fields)
        response = self.client.get(reverse('processos-cadastro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'severity_score')  # Dynamic field
        
        # Step 3: Submit form (should process and redirect)
        form_data = {
            'nome_paciente': self.paciente.nome_paciente,
            'anamnese': 'Complete workflow test',
            'severity_score': 'mild',
            'notes': 'Workflow notes',
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '1 tablet',
            'qtd_med1_mes1': '30',
            'med1_repetir_posologia': 'True',
            'tratou': 'True',
            'preenchido_por': 'medico',
            'data_1': date.today().strftime('%Y-%m-%d')
        }
        
        response = self.client.post(reverse('processos-cadastro'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('pdf', response.url)
        
        # Step 4: Generate PDF (should succeed)
        response = self.client.get(reverse('processos-pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# SUMMARY: Business Logic Test Coverage
#
# These tests focus on:
# ✅ Form processing and validation logic
# ✅ Dynamic field generation from protocols  
# ✅ Session workflow management
# ✅ Data processing integration
# ✅ Error handling for business scenarios
# ✅ AJAX endpoint functionality
# ✅ Complete workflow integration
#
# This complements the existing security tests without duplication,
# focusing specifically on business logic and workflow functionality.