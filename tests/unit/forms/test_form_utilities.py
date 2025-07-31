"""
Test Form Utilities - Unit tests for form utility functions.

Testing the uncovered areas from coverage report:
- Lines 30-45: mostrar_med function with existing medications
- Lines 67-79: ajustar_campos_condicionais function logic
"""

from tests.test_base import BaseTestCase
from django.test import TestCase

from processos.forms.form_utilities import mostrar_med, ajustar_campos_condicionais


class FormUtilitiesTest(BaseTestCase):
    """Test form utility functions."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

    def test_mostrar_med_no_medications(self):
        """Test mostrar_med with no existing medications (new process)."""
        # When mostrar=False (new process), all med tabs should be hidden except med1
        result = mostrar_med(False)
        
        expected = {
            "med2_mostrar": "d-none",
            "med3_mostrar": "d-none", 
            "med4_mostrar": "d-none",
        }
        
        self.assertEqual(result, expected)

    def test_mostrar_med_with_existing_medications(self):
        """Test mostrar_med with existing medications (editing process)."""
        # Create process with medications
        user = self.create_test_user(is_medico=True)
        medico = self.create_test_medico(user=user)
        patient = self.create_test_patient(user=user)
        clinica = self.create_test_clinica()
        doenca = self.create_test_doenca()
        emissor = self.create_test_emissor(medico=medico, clinica=clinica)
        
        processo = self.create_test_processo(
            usuario=user,
            paciente=patient,
            medico=medico,
            clinica=clinica,
            doenca=doenca,
            emissor=emissor
        )
        
        # Add 2 medications to the process
        med1 = self.create_test_medicamento(nome="Med 1")
        med2 = self.create_test_medicamento(nome="Med 2")
        processo.medicamentos.add(med1, med2)
        
        # When mostrar=True, should show tabs for existing medications
        result = mostrar_med(True, processo)
        
        # med1 and med2 should be visible, med3 and med4 should be hidden
        self.assertEqual(result["med2_mostrar"], "")  # Should be visible
        self.assertEqual(result["med3_mostrar"], "d-none")  # Should be hidden
        self.assertEqual(result["med4_mostrar"], "d-none")  # Should be hidden

    def test_ajustar_campos_condicionais_patient_has_email(self):
        """Test ajustar_campos_condicionais when patient has email (doctor filling form)."""
        dados_paciente = {
            "email_paciente": "patient@example.com",
            "incapaz": False
        }
        
        dic, updated_data = ajustar_campos_condicionais(dados_paciente)
        
        # Should show campo 18 (doctor form fields) and hide responsible person
        self.assertEqual(dic["campo_18_mostrar"], "")  # Visible
        self.assertEqual(dic["responsavel_mostrar"], "d-none")  # Hidden
        
        # Should set preenchido_por to "medico"
        self.assertEqual(updated_data["preenchido_por"], "medico")

    def test_ajustar_campos_condicionais_incapable_patient(self):
        """Test ajustar_campos_condicionais when patient is incapable."""
        dados_paciente = {
            "email_paciente": "",  # No email
            "incapaz": True       # Patient is incapable
        }
        
        dic, updated_data = ajustar_campos_condicionais(dados_paciente)
        
        # Should show responsible person field and hide campo 18
        self.assertEqual(dic["campo_18_mostrar"], "d-none")  # Hidden
        self.assertEqual(dic["responsavel_mostrar"], "")     # Visible
        
        # Should not modify preenchido_por (no email means not doctor-filled)
        self.assertNotIn("preenchido_por", updated_data)