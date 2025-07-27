"""
PDF Generation Testing Module - Future PDFLayerService Ready

ARCHITECTURE EVOLUTION PLAN:
These tests are designed to support migration to a single PDFLayerService class:

Current: Scattered PDF functions
Future:  Single PDFLayerService class (Facade Pattern)

FUTURE SERVICE STRUCTURE:
class PDFLayerService:
    def generate_prescription_pdf(data, protocolo) → HttpResponse  # Main entry point
    def _format_data(data) → dict                                  # formatacao_data + ajustar_campo_18  
    def _fill_forms_in_memory(templates, data) → List[BytesIO]    # preencher_formularios_memory
    def _concatenate_pdfs(pdf_streams) → bytes                    # concatenar_pdfs_memory
    def _generate_fdf_content(data) → str                         # generate_fdf_content
    def _get_required_templates(protocolo, data) → List[str]      # template selection logic

MIGRATION BENEFITS:
✅ Single class to maintain and understand
✅ All PDF operations in one place
✅ Easy dependency injection (just one service)
✅ Simple test migration (one test file)
✅ Clear public vs private method separation
✅ Can evolve incrementally

EASY TEST MIGRATION:
All current tests → TestPDFLayerService(TestCase)
- Keep same test logic, just change method calls
- Current function calls become service method calls
- Add integration tests for complete workflows
"""

import os
import tempfile
import shutil
from datetime import date, datetime
from io import BytesIO
from unittest.mock import patch, mock_open, MagicMock

from django.test import TestCase, override_settings
from django.http import HttpResponse
from django.conf import settings

from processos.manejo_pdfs_memory import (
    preencher_formularios_memory,    # FUTURE: PDFLayerService._fill_forms_in_memory()
    concatenar_pdfs_memory,          # FUTURE: PDFLayerService._concatenate_pdfs() 
    formatacao_data,                 # FUTURE: PDFLayerService._format_data() (part 1)
    ajustar_campo_18,               # FUTURE: PDFLayerService._format_data() (part 2)
    GeradorPDF,                     # FUTURE: PDFLayerService.generate_prescription_pdf()
    generate_fdf_content            # FUTURE: PDFLayerService._generate_fdf_content()
)
from processos.models import Protocolo, Doenca, Medicamento, Processo
from usuarios.models import Usuario
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor


class TestPDFMemoryGeneration(TestCase):
    """
    Test the memory-based PDF generation system.
    
    FUTURE REFACTORING TARGET: PDFLayerService private methods
    MIGRATION PLAN: 
    - Keep this test structure but change method calls
    - test_preencher_* → test_fill_forms_in_memory_*
    - test_concatenar_* → test_concatenate_pdfs_*  
    - test_formatacao_* → test_format_data_*
    """
    
    def setUp(self):
        """Set up test data for PDF generation tests."""
        # Create test user and related entities
        self.usuario = Usuario.objects.create_user(
            email="test@example.com", 
            password="testpass123"
        )
        
        self.medico = Medico.objects.create(
            nome_medico="Dr. Test",
            crm_medico="CRM123",
            cns_medico="CNS123"
        )
        
        self.clinica = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="CNS456",
            logradouro="Test Street",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test District",
            cep="12345-678",
            telefone_clinica="11999999999"
        )
        
        self.emissor = Emissor.objects.create(
            medico=self.medico,
            clinica=self.clinica
        )
        
        self.paciente = Paciente.objects.create(
            nome_paciente="João Silva",
            cpf_paciente="12345678901",
            cns_paciente="123456789012345",
            nome_mae="Maria Silva",
            idade="30",
            sexo="M",
            peso="70",
            altura="1.75",
            incapaz=False,
            etnia="Parda",
            telefone1_paciente="11999999999",
            end_paciente="Test Address, 123",
            rg="123456789",
            escolha_etnia="Parda",
            cidade_paciente="Test City",
            cep_paciente="12345-678"
        )
        
        self.protocolo = Protocolo.objects.create(
            nome="test_protocol",
            arquivo="test_protocol.pdf",
            dados_condicionais={"field1": "value1"}
        )
        
        self.doenca = Doenca.objects.create(
            cid="G35",
            nome="Test Disease",
            protocolo=self.protocolo
        )
        
        self.medicamento = Medicamento.objects.create(
            nome="Test Medication",
            dosagem="500mg",
            apres="Tablet"
        )
        
        # Sample form data with UTF-8 characters
        self.sample_data = {
            "nome_paciente": "João Silva",
            "cpf_paciente": "12345678901",
            "cid": "G35",
            "data_1": date.today(),
            "preenchido_por": "medico",
            "telefone1_paciente": "11999999999",
            "telefone2_paciente": "11888888888",
            "email_paciente": "joao@test.com",
            "etnia": "Parda",
            "consentimento": "True",
            "relatorio": "True",
            "exames": "True"
        }
    
    def create_temp_pdf(self, content=b"%PDF-1.4\ntest pdf content\n%%EOF"):
        """Create a temporary PDF file for testing."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    @patch('processos.manejo_pdfs_memory.pypdftk.fill_form')
    @patch('os.path.exists')
    def test_preencher_formularios_memory_success(self, mock_exists, mock_fill_form):
        """
        Test successful PDF form filling in memory.
        
        FUTURE SERVICE: PDFFormFillerService.fill_forms(templates, data) → List[BytesIO]
        MIGRATION: Copy to test_pdf_form_filler_service.py::TestPDFFormFillerService
        """
        # Setup
        mock_exists.return_value = True
        temp_pdf_path = self.create_temp_pdf()
        mock_fill_form.return_value = temp_pdf_path
        
        # Test data with UTF-8 characters
        test_data = {
            "nome": "João",
            "descricao": "Descrição com acentos"
        }
        
        # Execute
        result = preencher_formularios_memory([temp_pdf_path], test_data)
        
        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], BytesIO)
        
        # Check BytesIO content
        result[0].seek(0)
        pdf_content = result[0].read()
        self.assertTrue(pdf_content.startswith(b'%PDF-'))
        
        # Note: temp file is cleaned up by the function itself

    @patch('processos.manejo_pdfs_memory.pypdftk.fill_form')
    @patch('os.path.exists')
    def test_preencher_formularios_memory_file_not_found(self, mock_exists, mock_fill_form):
        """Test PDF form filling when template doesn't exist."""
        mock_exists.return_value = False
        
        result = preencher_formularios_memory(["/nonexistent/path.pdf"], self.sample_data)
        
        self.assertEqual(result, [])
        mock_fill_form.assert_not_called()

    @patch('processos.manejo_pdfs_memory.pypdftk.fill_form')
    @patch('os.path.exists')
    def test_preencher_formularios_memory_pypdftk_error(self, mock_exists, mock_fill_form):
        """Test PDF form filling when pypdftk fails."""
        mock_exists.return_value = True
        mock_fill_form.side_effect = Exception("pypdftk error")
        
        result = preencher_formularios_memory(["/test/path.pdf"], self.sample_data)
        
        self.assertEqual(result, [])

    def test_formatacao_data(self):
        """
        Test date formatting function.
        
        FUTURE SERVICE: PDFDataFormatterService.format_prescription_dates(initial_date) → dict
        MIGRATION: Copy to test_pdf_data_formatter_service.py::TestPDFDataFormatterService
        """
        test_data = {"data_1": datetime(2024, 1, 1)}
        
        formatacao_data(test_data)
        
        # Verify original date is formatted
        self.assertEqual(test_data["data_1"], "01/01/2024")
        
        # Verify subsequent dates are created (correct calculation)
        self.assertEqual(test_data["data_2"], "31/01/2024")  # +30 days
        self.assertEqual(test_data["data_3"], "01/03/2024")  # +60 days (not 02/03)
        self.assertEqual(test_data["data_4"], "31/03/2024")  # +90 days 
        self.assertEqual(test_data["data_5"], "30/04/2024")  # +120 days
        self.assertEqual(test_data["data_6"], "30/05/2024")  # +150 days

    def test_ajustar_campo_18_medico(self):
        """Test field 18 adjustment when filled by doctor."""
        test_data = {
            "preenchido_por": "medico",
            "cpf_paciente": "12345678901",
            "telefone1_paciente": "11999999999",
            "telefone2_paciente": "11888888888",
            "email_paciente": "test@example.com",
            "etnia": "Parda"
        }
        
        ajustar_campo_18(test_data)
        
        # When filled by doctor, all fields should remain
        self.assertEqual(test_data["cpf_paciente"], "12345678901")
        self.assertEqual(test_data["telefone1_paciente"], "11999999999")
        self.assertEqual(test_data["etnia"], "Parda")

    def test_ajustar_campo_18_not_medico(self):
        """Test field 18 adjustment when not filled by doctor."""
        test_data = {
            "preenchido_por": "paciente",
            "cpf_paciente": "12345678901",
            "telefone1_paciente": "11999999999",
            "telefone2_paciente": "11888888888",
            "email_paciente": "test@example.com",
            "etnia": "Parda",
            "escolha_documento": "RG"
        }
        
        ajustar_campo_18(test_data)
        
        # Sensitive fields should be removed
        self.assertNotIn("cpf_paciente", test_data)
        self.assertNotIn("telefone1_paciente", test_data)
        self.assertNotIn("telefone2_paciente", test_data)
        self.assertNotIn("email_paciente", test_data)
        
        # These fields should be empty
        self.assertEqual(test_data["etnia"], "")
        self.assertEqual(test_data["escolha_documento"], "")

    @patch('processos.manejo_pdfs_memory.pypdftk.concat')
    def test_concatenar_pdfs_memory_single_pdf(self, mock_concat):
        """
        Test concatenation with single PDF.
        
        FUTURE SERVICE: PDFConcatenationService.concatenate(pdf_streams) → bytes
        MIGRATION: Copy to test_pdf_concatenation_service.py::TestPDFConcatenationService
        """
        pdf_content = b"%PDF-1.4\nsingle pdf content\n%%EOF"
        pdf_io = BytesIO(pdf_content)
        
        result = concatenar_pdfs_memory([pdf_io])
        
        self.assertEqual(result, pdf_content)
        mock_concat.assert_not_called()

    @patch('processos.manejo_pdfs_memory.pypdftk.concat')
    def test_concatenar_pdfs_memory_multiple_pdfs(self, mock_concat):
        """Test concatenation with multiple PDFs."""
        # Setup
        pdf1_content = b"%PDF-1.4\npdf1 content\n%%EOF"
        pdf2_content = b"%PDF-1.4\npdf2 content\n%%EOF"
        pdf1_io = BytesIO(pdf1_content)
        pdf2_io = BytesIO(pdf2_content)
        
        concatenated_content = b"%PDF-1.4\nconcatenated content\n%%EOF"
        temp_output = self.create_temp_pdf(concatenated_content)
        mock_concat.return_value = temp_output
        
        try:
            result = concatenar_pdfs_memory([pdf1_io, pdf2_io])
            
            self.assertEqual(result, concatenated_content)
            mock_concat.assert_called_once()
            
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    def test_concatenar_pdfs_memory_empty_list(self):
        """Test concatenation with empty PDF list."""
        result = concatenar_pdfs_memory([])
        self.assertIsNone(result)

    def test_generate_fdf_content_basic(self):
        """Test FDF content generation with basic data."""
        data = {
            "field1": "value1",
            "field2": "value2"
        }
        
        result = generate_fdf_content(data)
        
        self.assertIn("%FDF-1.2", result)
        self.assertIn("/T (field1)", result)
        self.assertIn("/V (value1)", result)
        self.assertIn("/T (field2)", result)
        self.assertIn("/V (value2)", result)
        self.assertIn("%%EOF", result)

    def test_generate_fdf_content_utf8_characters(self):
        """Test FDF content generation with UTF-8 characters."""
        data = {
            "nome": "João",
            "descricao": "Descrição com acentos àáâãçéêíóôõúü"
        }
        
        result = generate_fdf_content(data)
        
        self.assertIn("/T (nome)", result)
        self.assertIn("/V (João)", result)
        self.assertIn("/T (descricao)", result)
        self.assertIn("Descrição com acentos àáâãçéêíóôõúü", result)

    def test_generate_fdf_content_special_characters(self):
        """Test FDF content generation with special characters that need escaping."""
        data = {
            "field_with_parens": "Value with (parentheses)",
            "field_with_backslash": "Value with \\ backslash",
            "field_with_newline": "Value with\nnewline"
        }
        
        result = generate_fdf_content(data)
        
        self.assertIn("/V (Value with \\(parentheses\\))", result)
        self.assertIn("/V (Value with \\\\ backslash)", result)
        self.assertIn("/V (Value with\\nnewline)", result)

    def test_generate_fdf_content_none_values(self):
        """Test FDF content generation with None values."""
        data = {
            "field1": "value1",
            "field2": None,
            "field3": "value3"
        }
        
        result = generate_fdf_content(data)
        
        # Only non-None fields should be included
        self.assertIn("/T (field1)", result)
        self.assertNotIn("/T (field2)", result)
        self.assertIn("/T (field3)", result)


class TestGeradorPDF(TestCase):
    """Test the GeradorPDF class."""
    
    def setUp(self):
        """Set up test data for GeradorPDF tests."""
        # Create test entities
        self.protocolo = Protocolo.objects.create(
            nome="test_protocol",
            arquivo="test_protocol.pdf",
            dados_condicionais={"field1": "value1"}
        )
        
        self.doenca = Doenca.objects.create(
            cid="G35",
            nome="Test Disease",
            protocolo=self.protocolo
        )
        
        self.medicamento = Medicamento.objects.create(
            nome="Test Medication",
            dosagem="500mg",
            apres="Tablet"
        )
        
        self.protocolo.medicamentos.add(self.medicamento)
        
        # Sample LME data
        self.lme_data = {
            "cpf_paciente": "123.456.789-01",
            "cid": "G35",
            "data_1": datetime.now(),
            "preenchido_por": "medico",
            "consentimento": "True",
            "relatorio": "True",
            "exames": "True",
            "id_med1": str(self.medicamento.id)
        }
        
        self.pdf_path = "/test/path/lme_base.pdf"

    @override_settings(
        PATH_PDF_DIR="/test/protocols/",
        PATH_RELATORIO="/test/report.pdf",
        PATH_EXAMES="/test/exams.pdf"
    )
    @patch('processos.manejo_pdfs_memory.concatenar_pdfs_memory')
    @patch('processos.manejo_pdfs_memory.preencher_formularios_memory')
    @patch('processos.manejo_pdfs_memory.DataDrivenStrategy')
    @patch('os.path.exists')
    def test_generico_stream_success(self, mock_exists, mock_strategy_class, 
                                   mock_preencher, mock_concatenar):
        """Test successful PDF generation and streaming."""
        # Setup mocks
        mock_exists.return_value = True
        
        mock_strategy = MagicMock()
        mock_strategy.get_disease_specific_paths.return_value = ["/test/disease.pdf"]
        mock_strategy.get_medication_specific_paths.return_value = ["/test/med.pdf"]
        mock_strategy_class.return_value = mock_strategy
        
        filled_pdfs = [BytesIO(b"%PDF-1.4\ntest content\n%%EOF")]
        mock_preencher.return_value = filled_pdfs
        
        final_pdf_bytes = b"%PDF-1.4\nfinal content\n%%EOF"
        mock_concatenar.return_value = final_pdf_bytes
        
        # Execute
        gerador = GeradorPDF(self.lme_data, self.pdf_path)
        response = gerador.generico_stream(self.lme_data, self.pdf_path)
        
        # Verify response
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline', response['Content-Disposition'])
        self.assertIn('pdf_final_123.456.789-01_G35.pdf', response['Content-Disposition'])
        self.assertEqual(response.content, final_pdf_bytes)
        
        # Verify strategy was created and methods were accessible
        mock_strategy_class.assert_called_once_with(self.protocolo)

    @patch('processos.manejo_pdfs_memory.Protocolo.objects.get')
    def test_generico_stream_protocol_not_found(self, mock_get_protocol):
        """Test PDF generation when protocol is not found."""
        mock_get_protocol.side_effect = Protocolo.DoesNotExist()
        
        gerador = GeradorPDF(self.lme_data, self.pdf_path)
        response = gerador.generico_stream(self.lme_data, self.pdf_path)
        
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"Protocol not found")

    @override_settings(PATH_PDF_DIR="/test/protocols/")
    @patch('processos.manejo_pdfs_memory.concatenar_pdfs_memory')
    @patch('processos.manejo_pdfs_memory.preencher_formularios_memory')
    @patch('processos.manejo_pdfs_memory.DataDrivenStrategy')
    @patch('os.path.exists')
    def test_generico_stream_no_filled_pdfs(self, mock_exists, mock_strategy_class,
                                          mock_preencher, mock_concatenar):
        """Test PDF generation when no PDFs are filled."""
        # Setup mocks
        mock_exists.return_value = True
        
        mock_strategy = MagicMock()
        mock_strategy.get_disease_specific_paths.return_value = []
        mock_strategy.get_medication_specific_paths.return_value = []
        mock_strategy_class.return_value = mock_strategy
        
        mock_preencher.return_value = []  # No filled PDFs
        
        # Execute
        gerador = GeradorPDF(self.lme_data, self.pdf_path)
        response = gerador.generico_stream(self.lme_data, self.pdf_path)
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b"PDF generation failed")

    @override_settings(PATH_PDF_DIR="/test/protocols/")
    @patch('processos.manejo_pdfs_memory.concatenar_pdfs_memory')
    @patch('processos.manejo_pdfs_memory.preencher_formularios_memory') 
    @patch('processos.manejo_pdfs_memory.DataDrivenStrategy')
    @patch('os.path.exists')
    def test_generico_stream_concatenation_fails(self, mock_exists, mock_strategy_class,
                                                mock_preencher, mock_concatenar):
        """Test PDF generation when concatenation fails."""
        # Setup mocks
        mock_exists.return_value = True
        
        mock_strategy = MagicMock()
        mock_strategy.get_disease_specific_paths.return_value = []
        mock_strategy.get_medication_specific_paths.return_value = []
        mock_strategy_class.return_value = mock_strategy
        
        filled_pdfs = [BytesIO(b"%PDF-1.4\ntest content\n%%EOF")]
        mock_preencher.return_value = filled_pdfs
        
        mock_concatenar.return_value = None  # Concatenation failed
        
        # Execute
        gerador = GeradorPDF(self.lme_data, self.pdf_path)
        response = gerador.generico_stream(self.lme_data, self.pdf_path)
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b"PDF concatenation failed")