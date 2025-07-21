"""
PDF Strategies Testing Module

This module tests the PDF generation strategies that decide which additional PDF files
to include based on:
1. Disease type (e.g., Multiple Sclerosis needs EDSS scale forms)
2. Medication type (e.g., Fingolimod needs cardiac monitoring forms)
3. Dynamic form fields (e.g., pregnancy status, disability scores)

WHY THESE TESTS MATTER:
- Ensures correct PDFs are included for each patient's treatment
- Prevents missing critical medical documents 
- Validates database-driven configuration works properly
- Ensures error handling when files are missing
"""

import os
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django import forms

from processos.pdf_strategies import DataDrivenStrategy, get_conditional_fields
from processos.models import Protocolo, Doenca


class TestDataDrivenStrategy(TestCase):
    """
    WHAT THIS TESTS: The DataDrivenStrategy class that decides which extra PDF files 
    to include based on the patient's disease and medication.
    
    REAL WORLD EXAMPLE: 
    - A Multiple Sclerosis patient on Fingolimod medication would get:
      * Base LME form (always included)  
      * EDSS disability scale (disease-specific)
      * Cardiac monitoring form (medication-specific)
      * Consent form (if first prescription)
    """
    
    def setUp(self):
        """
        CREATE TEST DATA: We create a sample protocol that mimics real medical protocols.
        
        This protocol configuration says:
        - For ANY patient with this disease: include EDSS scale and disability forms
        - For Fingolimod patients: include cardiac monitoring 
        - For Natalizumab patients: include PML monitoring forms
        """
        self.protocolo = Protocolo.objects.create(
            nome="multiple_sclerosis",
            arquivo="ms_base.pdf",
            dados_condicionais={
                "disease_files": ["edss_scale.pdf", "disability_form.pdf"],
                "medications": {
                    "fingolimod": {
                        "files": ["cardiac_monitoring.pdf", "cardiac_assessment.pdf"]
                    },
                    "natalizumab": {
                        "files": ["pml_consent.pdf", "pml_monitoring.pdf"]
                    }
                }
            }
        )
        
        # Test patient data
        self.sample_lme_data = {
            "med1": "Fingolimod",  # Patient's medication
            "cpf_paciente": "12345678901",
            "cid": "G35"  # Multiple Sclerosis code
        }

    def test_strategy_finds_correct_disease_files(self):
        """
        TEST PURPOSE: Verify that disease-specific PDFs are correctly identified
        
        SCENARIO: Multiple Sclerosis patient should get EDSS scale and disability forms
        WHY IT MATTERS: Every MS patient needs these forms regardless of medication
        """
        with patch('processos.pdf_strategies.get_static_path') as mock_path, \
             patch('os.path.exists') as mock_exists:
            
            # MOCK SETUP: Pretend the PDF files exist on disk
            mock_exists.return_value = True
            mock_path.side_effect = lambda *args: f"/static/protocols/{args[-1]}"
            
            # RUN THE TEST
            strategy = DataDrivenStrategy(self.protocolo)
            disease_files = strategy.get_disease_specific_paths(self.sample_lme_data)
            
            # VERIFY RESULTS
            self.assertEqual(len(disease_files), 2, "Should find exactly 2 disease-specific files")
            self.assertIn("/static/protocols/edss_scale.pdf", disease_files)
            self.assertIn("/static/protocols/disability_form.pdf", disease_files)

    def test_strategy_finds_correct_medication_files(self):
        """
        TEST PURPOSE: Verify that medication-specific PDFs are correctly identified
        
        SCENARIO: Patient on Fingolimod should get cardiac monitoring forms
        WHY IT MATTERS: Fingolimod can cause heart problems, so cardiac monitoring is required
        """
        with patch('processos.pdf_strategies.get_static_path') as mock_path, \
             patch('os.path.exists') as mock_exists:
            
            # MOCK SETUP: Pretend the PDF files exist
            mock_exists.return_value = True
            mock_path.side_effect = lambda *args: f"/static/protocols/{args[-1]}"
            
            # RUN THE TEST
            strategy = DataDrivenStrategy(self.protocolo)
            med_files = strategy.get_medication_specific_paths(self.sample_lme_data)
            
            # VERIFY RESULTS  
            self.assertEqual(len(med_files), 2, "Fingolimod should require 2 monitoring forms")
            self.assertIn("/static/protocols/cardiac_monitoring.pdf", med_files)
            self.assertIn("/static/protocols/cardiac_assessment.pdf", med_files)

    def test_different_medication_gets_different_files(self):
        """
        TEST PURPOSE: Verify different medications get their own specific forms
        
        SCENARIO: Patient switches from Fingolimod to Natalizumab
        WHY IT MATTERS: Different drugs have different monitoring requirements
        """
        with patch('processos.pdf_strategies.get_static_path') as mock_path, \
             patch('os.path.exists') as mock_exists:
            
            mock_exists.return_value = True
            mock_path.side_effect = lambda *args: f"/static/protocols/{args[-1]}"
            
            # Test with Natalizumab instead of Fingolimod
            natalizumab_data = {**self.sample_lme_data, "med1": "Natalizumab"}
            
            strategy = DataDrivenStrategy(self.protocolo)
            med_files = strategy.get_medication_specific_paths(natalizumab_data)
            
            # Should get PML monitoring forms, not cardiac forms
            self.assertEqual(len(med_files), 2)
            self.assertIn("/static/protocols/pml_consent.pdf", med_files)
            self.assertIn("/static/protocols/pml_monitoring.pdf", med_files)
            
            # Should NOT get cardiac forms
            self.assertNotIn("/static/protocols/cardiac_monitoring.pdf", med_files)

    def test_handles_missing_pdf_files_gracefully(self):
        """
        TEST PURPOSE: Verify system handles missing PDF files without crashing
        
        SCENARIO: Configuration says to include a PDF but file doesn't exist on disk
        WHY IT MATTERS: Prevents system crashes when PDFs are accidentally deleted
        """
        with patch('processos.pdf_strategies.get_static_path') as mock_path, \
             patch('os.path.exists') as mock_exists:
            
            # MOCK SETUP: Files don't exist on disk
            mock_exists.return_value = False
            mock_path.side_effect = lambda *args: f"/static/protocols/{args[-1]}"
            
            strategy = DataDrivenStrategy(self.protocolo)
            disease_files = strategy.get_disease_specific_paths(self.sample_lme_data)
            
            # Should return empty list, not crash
            self.assertEqual(disease_files, [], "Should handle missing files gracefully")

    def test_medication_matching_is_case_insensitive(self):
        """
        TEST PURPOSE: Verify medication matching works regardless of capitalization
        
        SCENARIO: Doctor types "fingolimod" instead of "Fingolimod"
        WHY IT MATTERS: Doctors shouldn't have to worry about exact capitalization
        """
        with patch('processos.pdf_strategies.get_static_path') as mock_path, \
             patch('os.path.exists') as mock_exists:
            
            mock_exists.return_value = True
            mock_path.side_effect = lambda *args: f"/static/protocols/{args[-1]}"
            
            # Test with lowercase medication name
            lowercase_data = {**self.sample_lme_data, "med1": "fingolimod"}
            
            strategy = DataDrivenStrategy(self.protocolo)
            med_files = strategy.get_medication_specific_paths(lowercase_data)
            
            # Should still find Fingolimod configuration
            self.assertEqual(len(med_files), 2, "Case insensitive matching should work")

    def test_unknown_medication_returns_no_files(self):
        """
        TEST PURPOSE: Verify unknown medications don't cause errors
        
        SCENARIO: Patient is on a medication not in our configuration
        WHY IT MATTERS: New medications are added regularly, system should handle gracefully
        """
        unknown_data = {**self.sample_lme_data, "med1": "SomeNewDrug2024"}
        
        strategy = DataDrivenStrategy(self.protocolo)
        med_files = strategy.get_medication_specific_paths(unknown_data)
        
        # Should return empty list for unknown medication
        self.assertEqual(med_files, [], "Unknown medications should return no extra files")

    def test_empty_protocol_configuration(self):
        """
        TEST PURPOSE: Verify system works with protocols that have no extra requirements
        
        SCENARIO: Simple disease that only needs basic LME form
        WHY IT MATTERS: Not all diseases need extra monitoring forms
        """
        # Create protocol with no extra configuration
        simple_protocol = Protocolo.objects.create(
            nome="simple_condition",
            arquivo="simple.pdf",
            dados_condicionais={}  # No extra files needed
        )
        
        strategy = DataDrivenStrategy(simple_protocol)
        
        disease_files = strategy.get_disease_specific_paths(self.sample_lme_data)
        med_files = strategy.get_medication_specific_paths(self.sample_lme_data)
        
        self.assertEqual(disease_files, [], "Simple protocols should need no extra disease files")
        self.assertEqual(med_files, [], "Simple protocols should need no extra medication files")


class TestConditionalFields(TestCase):
    """
    WHAT THIS TESTS: Dynamic form fields that appear based on the medical protocol
    
    REAL WORLD EXAMPLE:
    - Multiple Sclerosis protocol needs EDSS disability score (0.0 to 10.0)
    - Pregnancy-related protocols need pregnancy status checkbox  
    - Cancer protocols need staging information
    
    WHY IT MATTERS: Different diseases need different information collected
    """
    
    def setUp(self):
        """
        CREATE TEST PROTOCOL: Mimics a real Multiple Sclerosis protocol that needs:
        - EDSS disability score (dropdown selection)
        - Pregnancy status (checkbox)  
        - Symptom duration (number input)
        - Clinical notes (text area)
        - Diagnosis date (date picker)
        """
        self.protocolo_with_fields = Protocolo.objects.create(
            nome="ms_with_fields",
            arquivo="ms_fields.pdf",
            dados_condicionais={
                "fields": [
                    {
                        "name": "edss_score",
                        "type": "choice",
                        "label": "EDSS Disability Score",
                        "required": True,
                        "choices": [("0", "0.0 - Normal"), ("1", "1.0 - Minimal"), ("2", "2.0 - Mild")],
                        "initial": "0"
                    },
                    {
                        "name": "is_pregnant",
                        "type": "boolean", 
                        "label": "Currently Pregnant",
                        "required": False,
                        "initial": False
                    },
                    {
                        "name": "symptom_months",
                        "type": "number",
                        "label": "Months Since First Symptoms", 
                        "required": True,
                        "initial": 0
                    },
                    {
                        "name": "clinical_notes",
                        "type": "textarea",
                        "label": "Additional Clinical Notes",
                        "required": False
                    }
                ]
            }
        )

    def test_creates_dropdown_field_correctly(self):
        """
        TEST PURPOSE: Verify dropdown fields (like EDSS score) are created properly
        
        SCENARIO: Doctor needs to select disability score from predefined options
        WHY IT MATTERS: Medical scores must be standardized, not free-text
        """
        fields = get_conditional_fields(self.protocolo_with_fields)
        
        # Verify the EDSS field exists and is correct type
        self.assertIn("edss_score", fields, "EDSS score field should be created")
        
        edss_field = fields["edss_score"]
        self.assertIsInstance(edss_field, forms.ChoiceField, "Should be a dropdown field")
        self.assertEqual(edss_field.label, "EDSS Disability Score")
        self.assertTrue(edss_field.required, "EDSS score should be required")
        self.assertEqual(len(edss_field.choices), 3, "Should have 3 score options")

    def test_creates_checkbox_field_correctly(self):
        """
        TEST PURPOSE: Verify checkbox fields (like pregnancy status) work properly
        
        SCENARIO: Doctor needs to check if female patient is pregnant  
        WHY IT MATTERS: Pregnancy affects medication safety and dosing
        """
        fields = get_conditional_fields(self.protocolo_with_fields)
        
        self.assertIn("is_pregnant", fields, "Pregnancy field should be created")
        
        pregnancy_field = fields["is_pregnant"]  
        self.assertIsInstance(pregnancy_field, forms.BooleanField, "Should be a checkbox field")
        self.assertEqual(pregnancy_field.label, "Currently Pregnant")
        self.assertFalse(pregnancy_field.required, "Pregnancy status should be optional")
        self.assertFalse(pregnancy_field.initial, "Should default to False")

    def test_creates_number_field_correctly(self):
        """
        TEST PURPOSE: Verify number fields (like symptom duration) work properly
        
        SCENARIO: Doctor needs to enter how many months patient has had symptoms
        WHY IT MATTERS: Disease duration affects treatment decisions
        """
        fields = get_conditional_fields(self.protocolo_with_fields)
        
        self.assertIn("symptom_months", fields, "Symptom duration field should be created")
        
        duration_field = fields["symptom_months"]
        self.assertIsInstance(duration_field, forms.FloatField, "Should be a number field") 
        self.assertEqual(duration_field.label, "Months Since First Symptoms")
        self.assertTrue(duration_field.required, "Symptom duration should be required")

    def test_creates_textarea_field_correctly(self):
        """
        TEST PURPOSE: Verify text area fields (like clinical notes) work properly
        
        SCENARIO: Doctor needs space to write detailed clinical observations
        WHY IT MATTERS: Some information doesn't fit in structured fields
        """
        fields = get_conditional_fields(self.protocolo_with_fields)
        
        self.assertIn("clinical_notes", fields, "Clinical notes field should be created")
        
        notes_field = fields["clinical_notes"]
        self.assertIsInstance(notes_field, forms.CharField, "Should be a text field")
        self.assertIsInstance(notes_field.widget, forms.Textarea, "Should use textarea widget")
        self.assertFalse(notes_field.required, "Clinical notes should be optional")

    def test_handles_protocol_with_no_extra_fields(self):
        """
        TEST PURPOSE: Verify protocols without extra fields don't cause errors
        
        SCENARIO: Simple condition that only needs basic patient information
        WHY IT MATTERS: Not all medical conditions need complex forms
        """
        simple_protocol = Protocolo.objects.create(
            nome="simple_protocol", 
            arquivo="simple.pdf",
            dados_condicionais={}  # No extra fields
        )
        
        fields = get_conditional_fields(simple_protocol)
        
        self.assertEqual(fields, {}, "Simple protocols should have no extra fields")

    def test_handles_invalid_field_types_gracefully(self):
        """
        TEST PURPOSE: Verify system handles configuration errors gracefully
        
        SCENARIO: Someone puts an invalid field type in the database configuration
        WHY IT MATTERS: Configuration errors shouldn't crash the system
        """
        protocol_with_invalid = Protocolo.objects.create(
            nome="invalid_protocol",
            arquivo="invalid.pdf", 
            dados_condicionais={
                "fields": [
                    {
                        "name": "valid_field",
                        "type": "text",
                        "label": "This field is fine"
                    },
                    {
                        "name": "invalid_field", 
                        "type": "unknown_type",  # This type doesn't exist
                        "label": "This will be ignored"
                    }
                ]
            }
        )
        
        fields = get_conditional_fields(protocol_with_invalid)
        
        # Should create valid field but skip invalid one
        self.assertIn("valid_field", fields, "Valid fields should still be created")
        self.assertNotIn("invalid_field", fields, "Invalid field types should be skipped")
        self.assertEqual(len(fields), 1, "Should have exactly 1 valid field")


# SUMMARY OF WHAT WE'RE TESTING:
# 
# 1. DataDrivenStrategy Class:
#    - Finds correct disease-specific PDFs (EDSS forms for MS patients)
#    - Finds correct medication-specific PDFs (cardiac monitoring for Fingolimod)
#    - Handles different medications correctly
#    - Deals gracefully with missing files
#    - Works with case-insensitive medication names
#    - Handles unknown medications safely
#    - Works with simple protocols that need no extra files
#
# 2. get_conditional_fields Function:
#    - Creates dropdown fields for standardized medical scores  
#    - Creates checkboxes for yes/no medical questions
#    - Creates number fields for quantitative medical data
#    - Creates text areas for clinical observations
#    - Handles protocols with no extra fields
#    - Handles configuration errors gracefully
#
# These tests ensure that:
# ✅ Patients get the right monitoring forms for their specific treatment
# ✅ Doctors get the right input fields for their specific medical protocol  
# ✅ The system doesn't crash when files are missing or configurations are wrong
# ✅ The medical workflow is flexible but standardized