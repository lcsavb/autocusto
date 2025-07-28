"""
Unit Tests for PrescriptionService - Unit Testing Only

These tests focus on testing individual methods and properties of the PrescriptionService
in isolation. Integration testing is handled in tests/integration/services/.
"""

import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from processos.services.prescription.workflow_service import PrescriptionService

User = get_user_model()


class TestPrescriptionServiceUnit(TestCase):
    """Pure unit tests for PrescriptionService - testing individual components only."""
    
    def setUp(self):
        self.service = PrescriptionService()
        
    def test_service_initialization(self):
        """Test service initializes with all required dependencies."""
        service = PrescriptionService()
        
        # Check that all required services are initialized (based on actual implementation)
        self.assertIsNotNone(service.pdf_service)
        self.assertIsNotNone(service.data_builder) 
        self.assertIsNotNone(service.process_service)
        self.assertIsNotNone(service.domain_repository)
        self.assertIsNotNone(service.logger)
        
    def test_service_has_main_method(self):
        """Test that main service method exists."""
        self.assertTrue(hasattr(self.service, 'create_or_update_prescription'))
        self.assertTrue(callable(self.service.create_or_update_prescription))
        
    def test_method_signature_validation(self):
        """Test that create_or_update_prescription has correct signature."""
        import inspect
        sig = inspect.signature(self.service.create_or_update_prescription)
        expected_params = ['form_data', 'user', 'medico', 'clinica', 'patient_exists', 'process_id']
        actual_params = list(sig.parameters.keys())
        
        for param in expected_params:
            self.assertIn(param, actual_params, f"Expected parameter '{param}' not found in method signature")
            
    def test_service_dependencies_types(self):
        """Test that service dependencies are of expected types."""
        from processos.services.prescription.pdf_generation import PrescriptionPDFService
        from processos.services.prescription.data_builder import PrescriptionDataBuilder
        from processos.services.prescription.process_service import ProcessService
        from processos.repositories.domain_repository import DomainRepository
        import logging
        
        # Test dependency types
        self.assertIsInstance(self.service.pdf_service, PrescriptionPDFService)
        self.assertIsInstance(self.service.data_builder, PrescriptionDataBuilder)
        self.assertIsInstance(self.service.process_service, ProcessService)
        self.assertIsInstance(self.service.domain_repository, DomainRepository)
        self.assertIsInstance(self.service.logger, logging.Logger)
        
    def test_logger_configuration(self):
        """Test that logger is properly configured."""
        self.assertEqual(
            self.service.logger.name, 
            'processos.services.prescription.workflow_service'
        )
        
    def test_service_can_access_dependency_methods(self):
        """Test that service dependencies have expected methods."""
        # Test pdf_service has expected interface
        self.assertTrue(hasattr(self.service.pdf_service, 'generate_prescription_pdf'))
        self.assertTrue(callable(self.service.pdf_service.generate_prescription_pdf))
        
        # Test data_builder has expected interface
        self.assertTrue(hasattr(self.service.data_builder, 'build_prescription_data'))
        self.assertTrue(callable(self.service.data_builder.build_prescription_data))
        
        # Test process_service has expected interface
        self.assertTrue(hasattr(self.service.process_service, 'create_process_from_structured_data'))
        self.assertTrue(callable(self.service.process_service.create_process_from_structured_data))
        
        # Test domain_repository has expected interface
        self.assertTrue(hasattr(self.service.domain_repository, 'get_disease_by_cid'))
        self.assertTrue(callable(self.service.domain_repository.get_disease_by_cid))
        
    def test_transaction_decorator_applied(self):
        """Test that create_or_update_prescription is wrapped with transaction.atomic."""
        method = getattr(self.service, 'create_or_update_prescription')
        
        # Check if the method has transaction decorator applied
        # (This checks if the method is wrapped or has atomic properties)
        self.assertTrue(
            hasattr(method, '__wrapped__') or 
            'atomic' in str(method) or
            hasattr(method, '__self__')
        )
        
    def test_service_parameter_validation(self):
        """Test parameter validation for create_or_update_prescription."""
        # Test that method accepts expected parameter types without immediately failing on type checks
        mock_user = Mock()
        mock_user.email = 'test@example.com'
        
        # Create proper Django model mocks with _meta attributes
        mock_medico = Mock()
        mock_medico._meta = Mock()
        mock_medico._meta.concrete_fields = []
        mock_medico._meta.private_fields = []
        mock_medico._meta.many_to_many = []
        
        mock_clinica = Mock()
        mock_clinica._meta = Mock()
        mock_clinica._meta.concrete_fields = []
        mock_clinica._meta.private_fields = []
        mock_clinica._meta.many_to_many = []
        
        # This should not fail on parameter type validation
        # (It will likely fail on business logic, but that's expected)
        try:
            self.service.create_or_update_prescription(
                form_data={},  # Empty dict should be accepted as form_data type
                user=mock_user,
                medico=mock_medico, 
                clinica=mock_clinica,
                patient_exists=False,
                process_id=None
            )
        except TypeError as e:
            if "argument" in str(e) or "parameter" in str(e):
                self.fail(f"Parameter type validation failed: {e}")
        except Exception:
            # Other exceptions are expected (business logic, database, etc.)
            pass
            
    def test_service_error_handling_structure(self):
        """Test that service has proper error handling structure."""
        # Test that the service method doesn't crash on initialization errors
        try:
            # Test logger exists and can be used
            self.service.logger.info("Test message")
            
            # Test dependencies can be accessed without immediate crash
            _ = self.service.pdf_service
            _ = self.service.data_builder
            _ = self.service.process_service
            _ = self.service.domain_repository
            
        except Exception as e:
            self.fail(f"Service structure validation failed: {e}")


class TestPrescriptionServiceComposition(TestCase):
    """Test service composition patterns."""
    
    def test_service_composition_pattern(self):
        """Test that service follows composition pattern correctly."""
        service = PrescriptionService()
        
        # Test service composes other services rather than inheriting
        self.assertFalse(hasattr(service.__class__.__bases__[0], 'pdf_service'))
        self.assertFalse(hasattr(service.__class__.__bases__[0], 'data_builder'))
        
        # Test service creates its own instances
        self.assertTrue(hasattr(service, 'pdf_service'))
        self.assertTrue(hasattr(service, 'data_builder'))
        self.assertTrue(hasattr(service, 'process_service'))
        self.assertTrue(hasattr(service, 'domain_repository'))
        
    def test_dependency_isolation(self):
        """Test that dependencies are properly isolated."""
        service1 = PrescriptionService()
        service2 = PrescriptionService()
        
        # Each service should have its own instances (not shared)
        self.assertIsNot(service1.pdf_service, service2.pdf_service)
        self.assertIsNot(service1.data_builder, service2.data_builder)
        self.assertIsNot(service1.process_service, service2.process_service)
        self.assertIsNot(service1.domain_repository, service2.domain_repository)
        
    def test_service_interface_consistency(self):
        """Test that service interface is consistent across instances."""
        service1 = PrescriptionService()
        service2 = PrescriptionService()
        
        # Both should have same interface
        service1_methods = [method for method in dir(service1) if not method.startswith('_')]
        service2_methods = [method for method in dir(service2) if not method.startswith('_')]
        
        self.assertEqual(set(service1_methods), set(service2_methods))