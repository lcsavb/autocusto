"""
Smoke tests to verify the refactored architecture is working correctly.

These tests verify that:
1. Services can be imported and instantiated
2. Basic service methods work
3. View architecture changes don't break critical paths
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from processos.services.pdf_operations import PDFGenerator, PDFResponseBuilder
from processos.services.prescription_services import (
    PrescriptionDataFormatter, 
    PrescriptionTemplateSelector,
    PrescriptionPDFService,
    PrescriptionService,
    RenewalService
)
from processos.services.view_services import PrescriptionViewSetupService
from processos.models import Doenca, Protocolo


User = get_user_model()


class RefactoringSmokeTet(TestCase):
    """Smoke tests for refactored architecture."""
    
    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_all_services_can_be_imported_and_instantiated(self):
        """Test all new services can be imported and instantiated without errors."""
        # PDF Operations
        pdf_generator = PDFGenerator()
        pdf_response_builder = PDFResponseBuilder()
        
        # Prescription Services
        data_formatter = PrescriptionDataFormatter()
        template_selector = PrescriptionTemplateSelector()
        pdf_service = PrescriptionPDFService()
        prescription_service = PrescriptionService()
        renewal_service = RenewalService()
        
        # View Services
        view_setup_service = PrescriptionViewSetupService()
        
        # All services should be instantiated successfully
        self.assertIsNotNone(pdf_generator)
        self.assertIsNotNone(pdf_response_builder)
        self.assertIsNotNone(data_formatter)
        self.assertIsNotNone(template_selector)
        self.assertIsNotNone(pdf_service)
        self.assertIsNotNone(prescription_service)
        self.assertIsNotNone(renewal_service)
        self.assertIsNotNone(view_setup_service)
    
    def test_prescription_data_formatter_basic_functionality(self):
        """Test basic data formatting works."""
        formatter = PrescriptionDataFormatter()
        
        test_data = {
            'cpf_paciente': '12345678900',
            'preenchido_por': 'medico'
        }
        
        result = formatter.format_prescription_data(test_data)
        
        # Should return a dictionary
        self.assertIsInstance(result, dict)
        # Should preserve CPF when filled by doctor
        self.assertEqual(result['cpf_paciente'], '12345678900')
    
    def test_view_setup_service_structure(self):
        """Test view setup service has correct structure."""
        service = PrescriptionViewSetupService()
        
        # Should have the expected methods
        self.assertTrue(hasattr(service, 'setup_for_new_prescription'))
        self.assertTrue(hasattr(service, 'setup_for_edit_prescription'))
        self.assertTrue(callable(service.setup_for_new_prescription))
        self.assertTrue(callable(service.setup_for_edit_prescription))
    
    def test_cadastro_view_accessible(self):
        """Test that cadastro view is accessible (doesn't crash)."""
        # This will fail due to missing session data, but should not crash
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('processos-cadastro'))
        
        # Should redirect due to missing session data, not crash
        self.assertIn(response.status_code, [200, 302, 301])
    
    def test_edicao_view_accessible(self):
        """Test that edicao view is accessible (doesn't crash)."""
        # This will fail due to missing session data, but should not crash
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('processos-edicao'))
        
        # Should redirect due to missing session data, not crash
        self.assertIn(response.status_code, [200, 302, 301])
    
    def test_renovacao_rapida_view_accessible(self):
        """Test that renovacao_rapida view is accessible (doesn't crash)."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('processos-renovacao-rapida'))
        
        # Should not crash - acceptable status codes
        self.assertIn(response.status_code, [200, 302, 301])


class ServiceIntegrationSmokeTest(TestCase):
    """Test that services work together correctly."""
    
    def setUp(self):
        # Create minimal test data
        self.protocolo = Protocolo.objects.create(
            nome='test_protocol',
            arquivo='test.pdf'
        )
        self.doenca = Doenca.objects.create(
            cid='M05',
            nome='Test Disease',
            protocolo=self.protocolo
        )
    
    def test_prescription_pdf_service_validation_integration(self):
        """Test that PrescriptionPDFService validation works with other services."""
        pdf_service = PrescriptionPDFService()
        
        # Test with valid data
        valid_data = {
            'cpf_paciente': '12345678900',
            'cid': 'M05',
            'data_1': '15/01/2024'
        }
        
        # Should validate successfully
        result = pdf_service._validate_prescription_data(valid_data)
        self.assertTrue(result)
        
        # Test with invalid data
        invalid_data = {
            'cpf_paciente': '12345678900',
            # Missing required fields
        }
        
        result = pdf_service._validate_prescription_data(invalid_data)
        self.assertFalse(result)
    
    def test_data_formatter_and_template_selector_integration(self):
        """Test that data formatter and template selector work together."""
        formatter = PrescriptionDataFormatter()
        selector = PrescriptionTemplateSelector()
        
        test_data = {
            'cpf_paciente': '12345678900',
            'preenchido_por': 'medico',
            'consentimento': True
        }
        
        # Format data
        formatted_data = formatter.format_prescription_data(test_data)
        
        # Should be able to select templates with formatted data
        # This will not find actual files, but should not crash
        try:
            templates = selector.select_prescription_templates(
                self.protocolo, 
                formatted_data, 
                '/fake/path/test.pdf'
            )
            self.assertIsInstance(templates, list)
        except Exception as e:
            # Expected to fail due to missing files, but should not be import errors
            self.assertNotIn('ImportError', str(type(e)))
            self.assertNotIn('ModuleNotFoundError', str(type(e)))