"""
Basic Test Suite for PDF Services Architecture

Simple tests to verify the new service layer is working correctly.
"""

from django.test import TestCase
from django.http import HttpResponse
from datetime import datetime

from processos.pdf_operations import PDFGenerator, PDFResponseBuilder
from processos.prescription_services import PrescriptionDataFormatter, PrescriptionPDFService
from processos.models import Doenca, Protocolo


class TestPrescriptionDataFormatterBasic(TestCase):
    """Basic tests for PrescriptionDataFormatter."""
    
    def test_format_basic_functionality(self):
        """Test basic formatting functionality."""
        formatter = PrescriptionDataFormatter()
        
        data = {
            'data_1': datetime(2024, 1, 15),
            'preenchido_por': 'medico',
            'cpf_paciente': '12345678900'
        }
        
        result = formatter.format_prescription_data(data)
        
        # Should format dates
        self.assertEqual(result['data_1'], '15/01/2024')
        self.assertEqual(result['data_2'], '14/02/2024')
        
        # Should keep fields when filled by doctor
        self.assertEqual(result['cpf_paciente'], '12345678900')
    
    def test_privacy_field_removal(self):
        """Test privacy field removal."""
        formatter = PrescriptionDataFormatter()
        
        data = {
            'preenchido_por': 'paciente',
            'cpf_paciente': '12345678900',
            'telefone1_paciente': '11999999999'
        }
        
        result = formatter.format_prescription_data(data)
        
        # Should remove sensitive fields
        self.assertNotIn('cpf_paciente', result)
        self.assertNotIn('telefone1_paciente', result)


class TestPrescriptionPDFServiceBasic(TestCase):
    """Basic tests for PrescriptionPDFService."""
    
    def setUp(self):
        self.service = PrescriptionPDFService()
        
        # Create minimal test data - first create protocol, then disease
        self.protocolo = Protocolo.objects.create(
            nome='test_protocol',
            arquivo='test.pdf'
        )
        self.doenca = Doenca.objects.create(
            cid='M05',
            nome='Test Disease',
            protocolo=self.protocolo
        )
    
    def test_validate_prescription_data_valid(self):
        """Test validation with valid data."""
        data = {
            'cpf_paciente': '12345678900',
            'cid': 'M05',
            'data_1': datetime.now()
        }
        
        result = self.service._validate_prescription_data(data)
        
        self.assertTrue(result)
    
    def test_validate_prescription_data_missing_field(self):
        """Test validation with missing required field."""
        data = {
            'cpf_paciente': '12345678900',
            # Missing 'cid' and 'data_1'
        }
        
        result = self.service._validate_prescription_data(data)
        
        self.assertFalse(result)


class TestServicesImport(TestCase):
    """Test that all services can be imported without errors."""
    
    def test_import_services(self):
        """Test importing all service modules."""
        try:
            from processos.pdf_operations import (
                PDFGenerator,
                PDFResponseBuilder
            )
            from processos.prescription_services import (
                PrescriptionDataFormatter,
                PrescriptionTemplateSelector,
                PrescriptionPDFService,
                PrescriptionService,
                RenewalService
            )
            
            # If we get here, imports worked
            self.assertTrue(True)
            
        except ImportError as e:
            self.fail(f"Failed to import services: {e}")
    
    def test_instantiate_services(self):
        """Test that services can be instantiated."""
        try:
            formatter = PrescriptionDataFormatter()
            pdf_service = PrescriptionPDFService()
            pdf_generator = PDFGenerator()
            
            # Basic sanity check
            self.assertIsNotNone(formatter)
            self.assertIsNotNone(pdf_service)
            self.assertIsNotNone(pdf_generator)
            
        except Exception as e:
            self.fail(f"Failed to instantiate services: {e}")