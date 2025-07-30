"""
Basic Test Suite for PDF Services Architecture

Simple tests to verify the new service layer is working correctly.
"""

import os
from django.test import TestCase
from django.http import HttpResponse
from datetime import datetime

from processos.services.pdf_operations import PDFGenerator, PDFResponseBuilder
from processos.services.prescription_services import PrescriptionDataFormatter, PrescriptionPDFService
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
        
        result = formatter.format_prescription_date(data)
        
        # Should format dates
        self.assertEqual(result['data_1'], '15/01/2024')
        self.assertEqual(result['data_2'], '14/02/2024')
        
        # Should keep fields when filled by doctor
        self.assertEqual(result['cpf_paciente'], '12345678900')
    
    def test_data_preservation(self):
        """Test that data is preserved (no privacy removal needed as forms always filled by doctors)."""
        formatter = PrescriptionDataFormatter()
        
        data = {
            'preenchido_por': 'medico',
            'cpf_paciente': '12345678900',
            'telefone1_paciente': '11999999999'
        }
        
        result = formatter.format_prescription_date(data)
        
        # Should preserve all fields as forms are always filled by doctors
        self.assertIn('cpf_paciente', result)
        self.assertIn('telefone1_paciente', result)
        self.assertEqual(result['cpf_paciente'], '12345678900')


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


class TestPDFCleanupFunctionality(TestCase):
    """Test PDF cleanup functionality to prevent /dev/shm resource leakage."""
    
    def setUp(self):
        """Set up test environment for PDF cleanup tests."""
        self.pdf_generator = PDFGenerator()
        
        # Create test temporary files in /dev/shm for testing
        import tempfile
        import time
        
        self.test_temp_files = []
        timestamp = int(time.time() * 1000)
        
        # Create mock temporary files for testing
        for i in range(3):
            temp_path = f"/dev/shm/test_cleanup_{i}_{timestamp}.pdf"
            with open(temp_path, 'wb') as f:
                f.write(b'%PDF-1.4\nTest PDF content for cleanup testing\n%%EOF')
            self.test_temp_files.append(temp_path)
    
    def tearDown(self):
        """Clean up any remaining test files."""
        for temp_file in self.test_temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass  # Ignore cleanup errors
    
    def test_cleanup_temp_files_successful_removal(self):
        """Test that cleanup successfully removes tracked temporary files."""
        # Add test files to generator's tracking list
        self.pdf_generator.temp_files = self.test_temp_files.copy()
        
        # Verify files exist before cleanup
        for temp_file in self.test_temp_files:
            self.assertTrue(os.path.exists(temp_file), f"Test file should exist: {temp_file}")
        
        # Perform cleanup
        self.pdf_generator._cleanup_temp_files()
        
        # Verify files were removed
        for temp_file in self.test_temp_files:
            self.assertFalse(os.path.exists(temp_file), f"File should be cleaned up: {temp_file}")
        
        # Verify tracking list was cleared
        self.assertEqual(len(self.pdf_generator.temp_files), 0, "Temp files list should be empty after cleanup")
    
    def test_cleanup_temp_files_handles_missing_files(self):
        """Test that cleanup gracefully handles files that don't exist."""
        # Add non-existent files to tracking list
        non_existent_files = [
            "/dev/shm/non_existent_1.pdf",
            "/dev/shm/non_existent_2.pdf"
        ]
        self.pdf_generator.temp_files = non_existent_files.copy()
        
        # Cleanup should not raise exceptions for missing files
        try:
            self.pdf_generator._cleanup_temp_files()
            cleanup_successful = True
        except Exception:
            cleanup_successful = False
        
        self.assertTrue(cleanup_successful, "Cleanup should handle missing files gracefully")
        self.assertEqual(len(self.pdf_generator.temp_files), 0, "Temp files list should be cleared even for missing files")
    
    def test_cleanup_temp_files_handles_permission_errors(self):
        """Test that cleanup handles permission errors without crashing."""
        # Create a file and simulate permission error by making it read-only
        import tempfile
        import time
        
        timestamp = int(time.time() * 1000)
        protected_file = f"/dev/shm/protected_{timestamp}.pdf"
        
        try:
            # Create file
            with open(protected_file, 'wb') as f:
                f.write(b'%PDF-1.4\nProtected test file\n%%EOF')
            
            # Make file read-only (simulate permission issue)
            os.chmod(protected_file, 0o444)
            
            # Add to tracking list
            self.pdf_generator.temp_files = [protected_file]
            
            # Cleanup should handle permission errors gracefully
            try:
                self.pdf_generator._cleanup_temp_files()
                cleanup_completed = True
            except Exception:
                cleanup_completed = False
            
            self.assertTrue(cleanup_completed, "Cleanup should handle permission errors gracefully")
            self.assertEqual(len(self.pdf_generator.temp_files), 0, "Temp files list should be cleared even on permission errors")
            
        finally:
            # Clean up test file (restore permissions first)
            try:
                if os.path.exists(protected_file):
                    os.chmod(protected_file, 0o644)
                    os.remove(protected_file)
            except:
                pass
    
    def test_cleanup_called_on_successful_generation(self):
        """Test that cleanup is called during successful PDF generation workflow."""
        # Mock the fill_and_concatenate method to test cleanup behavior
        original_fill_forms = self.pdf_generator._fill_pdf_forms
        original_concatenate = self.pdf_generator._concatenate_pdfs
        
        # Track if cleanup was called
        cleanup_called = False
        original_cleanup = self.pdf_generator._cleanup_temp_files
        
        def mock_cleanup():
            nonlocal cleanup_called
            cleanup_called = True
            original_cleanup()
        
        def mock_fill_forms(template_paths, form_data):
            # Add test files to simulate normal operation
            self.pdf_generator.temp_files = self.test_temp_files.copy()
            return self.test_temp_files  # Return paths as if filling succeeded
        
        def mock_concatenate(pdf_paths):
            # Simulate successful concatenation
            return b'%PDF-1.4\nMocked concatenated PDF\n%%EOF'
        
        # Apply mocks
        self.pdf_generator._fill_pdf_forms = mock_fill_forms
        self.pdf_generator._concatenate_pdfs = mock_concatenate
        self.pdf_generator._cleanup_temp_files = mock_cleanup
        
        try:
            # Call fill_and_concatenate which should trigger cleanup in finally block
            result = self.pdf_generator.fill_and_concatenate(
                ["/mock/template.pdf"], 
                {"test_field": "test_value"}
            )
            
            # Verify cleanup was called
            self.assertTrue(cleanup_called, "Cleanup should be called during successful generation")
            self.assertIsNotNone(result, "Generation should return PDF bytes")
            
        finally:
            # Restore original methods
            self.pdf_generator._fill_pdf_forms = original_fill_forms
            self.pdf_generator._concatenate_pdfs = original_concatenate
            self.pdf_generator._cleanup_temp_files = original_cleanup
    
    def test_cleanup_called_on_failed_generation(self):
        """Test that cleanup is called even when PDF generation fails."""
        # Mock methods to simulate failure
        original_fill_forms = self.pdf_generator._fill_pdf_forms
        
        # Track if cleanup was called
        cleanup_called = False
        original_cleanup = self.pdf_generator._cleanup_temp_files
        
        def mock_cleanup():
            nonlocal cleanup_called
            cleanup_called = True
            original_cleanup()
        
        def mock_fill_forms_failure(template_paths, form_data):
            # Add test files to simulate partial operation before failure
            self.pdf_generator.temp_files = self.test_temp_files.copy()
            # Simulate failure by raising exception
            raise Exception("Simulated PDF generation failure")
        
        # Apply mocks
        self.pdf_generator._fill_pdf_forms = mock_fill_forms_failure
        self.pdf_generator._cleanup_temp_files = mock_cleanup
        
        # Restore original methods before making assertions
        try:
            # Call fill_and_concatenate which should fail and let exception propagate
            # but cleanup should still be called due to try/finally block
            with self.assertRaises(Exception) as context:
                self.pdf_generator.fill_and_concatenate(
                    ["/mock/template.pdf"], 
                    {"test_field": "test_value"}
                )
            
            # Verify the exception message
            self.assertEqual(str(context.exception), "Simulated PDF generation failure")
            
            # Verify cleanup was called despite failure (due to finally block)
            self.assertTrue(cleanup_called, "Cleanup should be called even when generation fails")
            
        finally:
            # Restore original methods
            self.pdf_generator._fill_pdf_forms = original_fill_forms
            self.pdf_generator._cleanup_temp_files = original_cleanup
    
    def test_temp_files_tracking_during_operation(self):
        """Test that temporary files are properly tracked during PDF operations."""
        # Mock file operations to test tracking
        import time
        
        original_fill_forms = self.pdf_generator._fill_pdf_forms
        
        def mock_fill_forms_with_tracking(template_paths, form_data):
            # Simulate adding files to temp_files list during operation
            for i, template_path in enumerate(template_paths):
                timestamp = int(time.time() * 1000)
                temp_path = f"/dev/shm/tracked_temp_{i}_{timestamp}.pdf"
                self.pdf_generator.temp_files.append(temp_path)
                
                # Create actual file for testing
                with open(temp_path, 'wb') as f:
                    f.write(b'%PDF-1.4\nTracked temp file\n%%EOF')
            
            return self.pdf_generator.temp_files
        
        self.pdf_generator._fill_pdf_forms = mock_fill_forms_with_tracking
        
        try:
            # Before operation - temp_files should be empty
            self.assertEqual(len(self.pdf_generator.temp_files), 0, "Temp files list should start empty")
            
            # Simulate PDF generation
            self.pdf_generator.fill_and_concatenate(
                ["/mock/template1.pdf", "/mock/template2.pdf"], 
                {"test_field": "test_value"}
            )
            
            # After operation - temp_files should be cleared by cleanup
            self.assertEqual(len(self.pdf_generator.temp_files), 0, "Temp files list should be cleared after operation")
            
        finally:
            # Restore original method
            self.pdf_generator._fill_pdf_forms = original_fill_forms


class TestServicesImport(TestCase):
    """Test that all services can be imported without errors."""
    
    def test_import_services(self):
        """Test importing all service modules."""
        try:
            from processos.services.pdf_operations import (
                PDFGenerator,
                PDFResponseBuilder
            )
            from processos.services.prescription_services import (
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