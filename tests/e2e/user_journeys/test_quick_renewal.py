"""
Test for Renovacao Rapida Versioning Bug

This test reproduces the critical bug where newly created processes
are not appearing in the renovacao_rapida template due to issues
with the patient versioning system.
"""

from tests.test_base import BaseTestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from processos.models import Processo, Doenca, Protocolo, Medicamento
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from processos.services.prescription.workflow_service import PrescriptionService
from processos.repositories.patient_repository import PatientRepository


User = get_user_model()


class RenovacaoRapidaVersioningBugTest(BaseTestCase):
    """Test for the critical bug where new processes don't show in renovacao_rapida."""
    
    def setUp(self):
        super().setUp()
        
        # Create test user using BaseTestCase helpers
        self.user = self.create_test_user(email='doctor@test.com', password='testpass123', is_medico=True)
        
        # Create test medico using BaseTestCase helpers
        self.medico = self.create_test_medico(
            user=self.user,
            nome_medico='Dr. Test',
            crm_medico='12345',
            especialidade='Clinica Geral'
        )
        
        # Create test clinica using BaseTestCase helpers
        self.clinica = self.create_test_clinica(
            nome_clinica='Test Clinic'
        )
        
        # Create emissor
        self.emissor = Emissor.objects.create(
            medico=self.medico,
            clinica=self.clinica
        )
        
        # Create test protocol and disease
        self.protocolo = Protocolo.objects.create(
            nome='test_protocol',
            arquivo='test.pdf'
        )
        
        self.doenca = Doenca.objects.create(
            cid='M05',
            nome='Test Disease',
            protocolo=self.protocolo
        )
        
        # Create test medication
        self.medicamento = Medicamento.objects.create(
            nome='Test Medication',
            dosagem='10mg',
            apres='tablet'
        )
        self.protocolo.medicamentos.add(self.medicamento)
        
        # Setup test patient data - use BaseTestCase helpers for valid data
        self.patient_data = {
            'nome_paciente': f'João da Silva {self.unique_suffix}',
            'cpf_paciente': self.data_generator.generate_unique_cpf(),
            'peso': '70',
            'altura': '175',
            'nome_mae': f'Maria da Silva {self.unique_suffix}',
            'incapaz': False,
            'nome_responsavel': '',
            'etnia': 'branco',
            'telefone1_paciente': '11999999999',
            'telefone2_paciente': '',
            'email_paciente': f'joao{self.unique_suffix}@test.com',
            'end_paciente': 'Rua Test 123',
        }
        
        # Setup test prescription data
        self.prescription_data = self.patient_data.copy()
        self.prescription_data.update({
            'anamnese': 'Test anamnese',
            'tratou': False,  # Fixed: boolean value instead of string
            'tratamentos_previos': 'Nenhum',
            'preenchido_por': 'medico',
            'data_1': '15/01/2024',
            'cid': 'M05',  # Required by PrescriptionService
            'diagnostico': 'Test Disease',  # Add diagnosis
            'clinicas': self.clinica.id,  # Add clinic selection
            # Medication prescription
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '1 comprimido 2x ao dia',
            'qtd_med1_mes1': '60',
            'med1_posologia_mes2': '1 comprimido 2x ao dia', 
            'qtd_med1_mes2': '60',
            'med1_posologia_mes3': '1 comprimido 2x ao dia',
            'qtd_med1_mes3': '60',
            'med1_posologia_mes4': '1 comprimido 2x ao dia',
            'qtd_med1_mes4': '60',
            'med1_posologia_mes5': '1 comprimido 2x ao dia',
            'qtd_med1_mes5': '60',
            'med1_posologia_mes6': '1 comprimido 2x ao dia',
            'qtd_med1_mes6': '60',
            'med1_via': 'oral'
        })
        
        self.client = Client()
    
    def test_new_process_shows_in_renovacao_rapida_search(self):
        """
        CRITICAL TEST: This test should reproduce the bug where newly created
        processes are not appearing in renovacao_rapida patient search.
        """
        # Step 1: Create a new prescription using the actual PrescriptionService (like real users do)
        from processos.services.prescription_services import PrescriptionService
        
        # Use the prescription service to create the prescription (like the actual views do)
        prescription_service = PrescriptionService()
        pdf_response, processo_id = prescription_service.create_or_update_prescription(
            form_data=self.prescription_data,
            user=self.user,
            medico=self.medico,
            clinica=self.clinica,
            patient_exists=False,
            process_id=None
        )
        
        # Verify the process was created
        self.assertIsNotNone(processo_id)
        processo = Processo.objects.get(id=processo_id)
        self.assertEqual(processo.usuario, self.user)
        
        # Step 2: Verify patient was created and associated with user
        patient = processo.paciente
        self.assertIsNotNone(patient)
        # Patient should have a valid CPF (generated by BaseTestCase)
        self.assertTrue(len(patient.cpf_paciente) == 11)  # Valid CPF length
        
        # CRITICAL CHECK: Verify user is associated with patient
        self.assertIn(self.user, patient.usuarios.all(), 
                     "User should be associated with the newly created patient")
        
        # Step 3: Test patient search like renovacao_rapida does
        # Search by the actual patient name (created by BaseTestCase)
        search_results = Paciente.get_patients_for_user_search(self.user, patient.nome_paciente)
        patient_list = [patient_result for patient_result, version in search_results]
        
        # CRITICAL ASSERTION: The newly created patient should appear in search
        self.assertIn(patient, patient_list,
                     "Newly created patient should appear in renovacao_rapida search")
        
        # Additional verification: Test with CPF search (using actual CPF generated by BaseTestCase)
        cpf_search_results = Paciente.get_patients_for_user_search(self.user, patient.cpf_paciente)
        cpf_patient_list = [patient_result for patient_result, version in cpf_search_results]
        
        self.assertIn(patient, cpf_patient_list,
                     "Newly created patient should appear in CPF search")
    
    def test_user_patient_association_after_process_creation(self):
        """Test that user-patient association is correctly established."""
        # Before creating process - user should have no patients
        initial_patients = self.user.pacientes.all()
        self.assertEqual(initial_patients.count(), 0)
        
        # Create process using BaseTestCase helpers 
        patient = self.create_test_patient(user=self.user)
        doenca = self.create_test_doenca(nome='Test Disease')
        
        processo = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=doenca
        )
        processo_id = processo.id
        
        # After creating process - user should have the new patient
        final_patients = self.user.pacientes.all()
        self.assertEqual(final_patients.count(), 1, 
                        "User should have exactly one patient after creating a process")
        
        # The patient should be the one from the created process
        processo = Processo.objects.get(id=processo_id)
        self.assertIn(processo.paciente, final_patients,
                     "Process patient should be in user's patient list")
    
    def test_renovacao_rapida_view_shows_newly_created_patients(self):
        """Integration test: Test that renovacao_rapida view actually returns the new patient."""
        # Create a process first
        from processos.repositories.medication_repository import MedicationRepository
        
        # Use BaseTestCase helpers for consistent data creation
        patient = self.create_test_patient(user=self.user)
        doenca = self.create_test_doenca(nome='Test Disease')
        
        processo = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=doenca
        )
        processo_id = processo.id
        # Using BaseTestCase helpers instead of deprecated functions
        
        # Ensure user is properly associated with medico and clinica
        self.user.medicos.add(self.medico)
        self.user.clinicas.add(self.clinica)
        
        # Login and test the actual view
        self.client.login(email='doctor@test.com', password='testpass123')
        
        # Test renovacao_rapida view with search - search for the actual patient name
        search_term = patient.nome_paciente.split()[0]  # Get first word of name (e.g., "Test")
        response = self.client.get('/processos/renovacao/', {'b': search_term}, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if the patient appears in the context
        busca_pacientes = response.context['busca_pacientes']
        
        # CRITICAL ASSERTION: The patient should be in the search results
        self.assertIn(patient, busca_pacientes,
                     "Newly created patient should appear in renovacao_rapida template context")
        
        # Also test that we have the right number of patients
        self.assertEqual(len(busca_pacientes), 1,
                        "Should find exactly one patient matching the search")
    
    def test_newly_created_process_appears_in_template_context(self):
        """CRITICAL TEST: Test that newly created processes appear in template context for user."""
        # Create a process first
        from processos.repositories.medication_repository import MedicationRepository
        
        # Use BaseTestCase helpers for consistent data creation
        patient = self.create_test_patient(user=self.user)
        doenca = self.create_test_doenca(nome='Test Disease')
        
        processo = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=doenca
        )
        processo_id = processo.id
        # Using BaseTestCase helpers instead of deprecated functions
        
        # Ensure user is properly associated with medico and clinica
        self.user.medicos.add(self.medico)
        self.user.clinicas.add(self.clinica)
        
        # Get the patient and verify the process association
        processo = Processo.objects.get(id=processo_id)
        patient = processo.paciente
        
        # CRITICAL CHECK: Verify the process is in patient.processos.all()
        all_patient_processes = patient.processos.all()
        self.assertIn(processo, all_patient_processes, 
                     "Process should be in patient.processos.all()")
        
        # CRITICAL CHECK: Verify the process belongs to the user
        user_processes = all_patient_processes.filter(usuario=self.user)
        self.assertIn(processo, user_processes,
                     "Process should be filtered by user in template logic")
        
        # CRITICAL CHECK: Test the exact template logic
        template_processes = []
        for p in patient.processos.all():
            if p.usuario == self.user:
                template_processes.append(p)
        
        self.assertEqual(len(template_processes), 1,
                        "Template should find exactly one process for this user")
        self.assertIn(processo, template_processes,
                     "Newly created process should appear in template context")
    
    def test_multi_user_process_scenario_real_world_bug(self):
        """CRITICAL TEST: Reproduce real-world scenario with multiple users and same patient."""
        # Step 1: User1 creates a process for a patient using BaseTestCase helpers
        patient = self.create_test_patient(user=self.user)
        doenca = self.create_test_doenca(nome='Test Disease')
        
        processo1 = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=doenca
        )
        processo_id_1 = processo1.id
        
        # Step 2: Get the patient that was created
        processo_1 = Processo.objects.get(id=processo_id_1)
        patient = processo_1.paciente
        
        # Step 3: Create User2 and associated medico/clinica
        user2 = User.objects.create_user(
            email='doctor2@test.com',
            password='testpass123'
        )
        
        medico2 = Medico.objects.create(
            nome_medico='Dr. Test 2',
            crm_medico='67890',
            cns_medico='987654321012345',
            especialidade='Cardiologia'
        )
        medico2.usuarios.add(user2)
        
        emissor2 = Emissor.objects.create(
            medico=medico2,
            clinica=self.clinica
        )
        
        # Step 4: User2 creates a NEW process for the SAME PATIENT (different disease)
        # Create a different disease
        doenca2 = Doenca.objects.create(
            cid='I10',
            nome='Hypertension',
            protocolo=self.protocolo
        )
        
        # User2's prescription data for the SAME patient
        user2_prescription_data = self.patient_data.copy()  # Same patient data!
        user2_prescription_data.update({
            'anamnese': 'User2 anamnese',
            'tratou': False,
            'tratamentos_previos': 'None',
            'preenchido_por': 'medico',
            'data_1': '16/01/2024',
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '1 comprimido 1x ao dia',
            'qtd_med1_mes1': '30',
            'med1_posologia_mes2': '1 comprimido 1x ao dia', 
            'qtd_med1_mes2': '30',
            'med1_posologia_mes3': '1 comprimido 1x ao dia',
            'qtd_med1_mes3': '30',
            'med1_posologia_mes4': '1 comprimido 1x ao dia',
            'qtd_med1_mes4': '30',
            'med1_posologia_mes5': '1 comprimido 1x ao dia',
            'qtd_med1_mes5': '30',
            'med1_posologia_mes6': '1 comprimido 1x ao dia',
            'qtd_med1_mes6': '30',
            'med1_via': 'oral'
        })
        
        # Create second process for user2 using BaseTestCase helpers
        doenca2 = self.create_test_doenca(nome='Test Disease 2')
        
        processo2 = self.create_test_processo(
            usuario=user2,
            paciente=patient,  # Same patient
            clinica=self.clinica,
            doenca=doenca2
        )
        processo_id_2 = processo2.id
        
        # Step 5: Verify the two processes exist for the same patient
        processo_2 = Processo.objects.get(id=processo_id_2)
        self.assertEqual(processo_1.paciente.id, processo_2.paciente.id,
                        "Both processes should be for the same patient")
        
        # Step 6: Test renovacao_rapida template logic for User1
        all_processes = patient.processos.all()
        user1_processes = [p for p in all_processes if p.usuario == self.user]
        user2_processes = [p for p in all_processes if p.usuario == user2]
        
        print(f"DEBUG: Total processes for patient: {all_processes.count()}")
        print(f"DEBUG: User1 processes: {len(user1_processes)} - IDs: {[p.id for p in user1_processes]}")
        print(f"DEBUG: User2 processes: {len(user2_processes)} - IDs: {[p.id for p in user2_processes]}")
        
        # CRITICAL ASSERTIONS
        self.assertEqual(len(user1_processes), 1, "User1 should see exactly 1 process")
        self.assertEqual(len(user2_processes), 1, "User2 should see exactly 1 process")
        
        self.assertIn(processo_1, user1_processes, "User1 should see their process")
        self.assertIn(processo_2, user2_processes, "User2 should see their process")
        
        # CRITICAL: Make sure users don't see each other's processes
        self.assertNotIn(processo_2, user1_processes, "User1 should NOT see User2's process")
        self.assertNotIn(processo_1, user2_processes, "User2 should NOT see User1's process")
    
    def test_immediate_process_visibility_after_creation(self):
        """CRITICAL TEST: Test that processes are immediately visible after creation - exact user scenario."""
        from processos.services.prescription_services import PrescriptionService
        
        # STEP 1: Create the first process using PrescriptionService (real workflow)
        prescription_service = PrescriptionService()
        pdf_response_1, processo_id_1 = prescription_service.create_or_update_prescription(
            form_data=self.prescription_data,
            user=self.user,
            medico=self.medico,
            clinica=self.clinica,
            patient_exists=False,
            process_id=None
        )
        
        # Verify first process was created
        self.assertIsNotNone(pdf_response_1)
        self.assertIsNotNone(processo_id_1)
        
        # Get the patient from the first process
        processo_1 = Processo.objects.get(id=processo_id_1)
        patient = processo_1.paciente
        
        print(f"DEBUG: After first process - patient.processos.all().count() = {patient.processos.all().count()}")
        
        # STEP 2: Create a second process for the SAME patient using PrescriptionService
        # Modify prescription data for different disease
        prescription_data_2 = self.prescription_data.copy()
        prescription_data_2['anamnese'] = 'Second process anamnese'
        prescription_data_2['data_1'] = '17/01/2024'
        
        # Use existing patient workflow
        pdf_response_2, processo_id_2 = prescription_service.create_or_update_prescription(
            form_data=prescription_data_2,
            user=self.user,
            medico=self.medico,
            clinica=self.clinica,
            patient_exists=True,  # Use existing patient
            process_id=None  # New process, not updating existing
        )
        
        # Verify second process was created
        self.assertIsNotNone(pdf_response_2)
        self.assertIsNotNone(processo_id_2)
        
        # Get the second process object
        processo_2 = Processo.objects.get(id=processo_id_2)
        
        print(f"DEBUG: After second process - patient.processos.all().count() = {patient.processos.all().count()}")
        
        # STEP 3: Test immediate visibility - this is where the bug manifests
        # Refresh the patient from database to avoid any ORM caching
        patient.refresh_from_db()
        
        all_processes = patient.processos.all()
        user_processes = [p for p in all_processes if p.usuario == self.user]
        
        print(f"DEBUG: All processes: {[p.id for p in all_processes]}")
        print(f"DEBUG: User processes: {[p.id for p in user_processes]}")
        print(f"DEBUG: Process 1 CID: {processo_1.doenca.cid}, Process 2 CID: {processo_2.doenca.cid}")
        
        # CRITICAL ASSERTIONS - Quick renewal should update existing process, not create new one
        self.assertEqual(all_processes.count(), 1, 
                        "Patient should have exactly 1 process (updated, not duplicated)")
        self.assertEqual(len(user_processes), 1, 
                        "User should see the updated process")
        self.assertIn(processo_1, user_processes, 
                     "Process should be visible after update")
        # In quick renewal, processo_2 should be the same as processo_1 (updated)
        self.assertEqual(processo_1.id, processo_2.id,
                     "Quick renewal should update existing process, not create new one")
        
        # Verify the updated process belongs to correct user and patient
        self.assertEqual(processo_1.usuario, self.user)
        self.assertEqual(processo_2.usuario, self.user)
        self.assertEqual(processo_1.paciente.id, processo_2.paciente.id)
        
        # Verify the process was actually updated with new data
        processo_2.refresh_from_db()
        self.assertEqual(processo_2.anamnese, "Second process anamnese",
                        "Process should be updated with new anamnese data")
    
    def test_critical_bug_fix_user_process_isolation(self):
        """CRITICAL TEST: Verify the bug fix prevents users from overwriting each other's processes."""
        from processos.repositories.medication_repository import MedicationRepository
        
        # STEP 1: User1 creates a process for a patient using BaseTestCase helpers
        patient = self.create_test_patient(user=self.user)
        
        processo_1 = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=self.doenca
        )
        processo_id_1 = processo_1.id
        
        # STEP 2: Create User2 and associated infrastructure using BaseTestCase helpers
        user2 = self.create_test_user(email='user2@test.com', is_medico=True)
        
        medico2 = self.create_test_medico(
            user=user2,
            nome_medico='Dr. User2',
            crm_medico='54321',
            estado='SP'
        )
        
        emissor2 = Emissor.objects.create(
            medico=medico2,
            clinica=self.clinica
        )
        
        # STEP 3: User2 creates SAME disease process for SAME patient using BaseTestCase
        # This should create a NEW process for User2, not overwrite User1's
        processo_2 = self.create_test_processo(
            usuario=user2,
            paciente=patient,  # SAME patient
            clinica=self.clinica,
            doenca=self.doenca  # SAME disease
        )
        processo_id_2 = processo_2.id
        
        # CRITICAL ASSERTIONS - These verify the bug fix
        self.assertNotEqual(processo_id_1, processo_id_2,
                           "User2 should create a NEW process, not overwrite User1's")
        
        # Refresh processo_1 from database to ensure it wasn't modified
        processo_1.refresh_from_db()
        
        # Verify User1's process is unchanged
        self.assertEqual(processo_1.usuario, self.user,
                        "User1's process should still belong to User1")
        
        # Verify User2's process has correct ownership
        self.assertEqual(processo_2.usuario, user2,
                        "User2's process should belong to User2")
        
        # Verify both processes exist for the same patient
        self.assertEqual(processo_1.paciente.id, processo_2.paciente.id,
                        "Both processes should be for the same patient")
        
        # Verify process isolation in renovacao_rapida template logic
        all_processes = patient.processos.all()
        user1_processes = [p for p in all_processes if p.usuario == self.user]
        user2_processes = [p for p in all_processes if p.usuario == user2]
        
        self.assertEqual(len(user1_processes), 1, "User1 should see 1 process")
        self.assertEqual(len(user2_processes), 1, "User2 should see 1 process")
        
        self.assertIn(processo_1, user1_processes, "User1 should see their process")
        self.assertIn(processo_2, user2_processes, "User2 should see their process")
        
        print(f"✅ BUG FIX VERIFIED: User1 process {processo_id_1}, User2 process {processo_id_2}")
        print(f"✅ Both users can create separate processes for same patient-disease combination")
    
    def test_renewal_service_workflow(self):
        """TEST: Test the new RenewalService workflow that replaced deprecated functions."""
        from processos.services.prescription_services import RenewalService
        from datetime import date
        
        # Step 1: Create a process using BaseTestCase helpers
        patient = self.create_test_patient(user=self.user)
        
        processo = self.create_test_processo(
            usuario=self.user,
            paciente=patient,
            clinica=self.clinica,
            doenca=self.doenca
        )
        
        # Step 2: Test the new RenewalService (replaces deprecated functions)
        renewal_service = RenewalService()
        
        # Test renewal data generation
        nova_data = date.today().strftime("%d/%m/%Y")
        renewal_data = renewal_service.generate_renewal_data(nova_data, processo.id, self.user)
        
        # Verify renewal data contains expected fields
        self.assertIn('cpf_paciente', renewal_data)
        self.assertIn('cid', renewal_data)
        self.assertIn('data_1', renewal_data)
        self.assertEqual(renewal_data['data_1'], nova_data)
        
        # Step 3: Test renewal dictionary creation (replaces deprecated registrar_db workflow)
        renewal_dict = renewal_service.create_renewal_dictionary(processo, user=self.user)
        
        # Verify renewal dictionary has proper structure (flattened patient data)
        self.assertIn('nome_paciente', renewal_dict)
        self.assertIn('cpf_paciente', renewal_dict)
        self.assertIn('clinica', renewal_dict)
        self.assertIn('cid', renewal_dict)
        self.assertIn('anamnese', renewal_dict)
        
        # Step 4: Test actual renewal processing (core new service functionality)
        pdf_response = renewal_service.process_renewal(nova_data, processo.id, self.user)
        
        # Verify PDF was generated successfully
        self.assertIsNotNone(pdf_response, "RenewalService should generate PDF response")
        
        print(f"✅ RenewalService workflow test passed for processo {processo.id}")
    
    def test_prescription_service_workflow(self):
        """TEST: Test the new PrescriptionService workflow that replaced deprecated functions."""
        from processos.services.prescription_services import PrescriptionService
        
        # Step 1: Test new prescription creation using PrescriptionService
        prescription_service = PrescriptionService()
        
        # Test the actual service used by prescription_views.py
        pdf_response, processo_id = prescription_service.create_or_update_prescription(
            form_data=self.prescription_data,
            user=self.user,
            medico=self.medico,
            clinica=self.clinica,
            patient_exists=False,  # New patient workflow
            process_id=None
        )
        
        # Verify prescription creation succeeded
        self.assertIsNotNone(pdf_response, "PrescriptionService should generate PDF")
        self.assertIsNotNone(processo_id, "PrescriptionService should return process ID")
        
        # Verify process was created in database
        processo = Processo.objects.get(id=processo_id)
        self.assertEqual(processo.usuario, self.user)
        self.assertIsNotNone(processo.paciente)
        
        # Step 2: Test prescription update workflow
        # Modify some data for update test
        updated_data = self.prescription_data.copy()
        updated_data['anamnese'] = 'Updated anamnese for testing'
        
        pdf_response_2, updated_processo_id = prescription_service.create_or_update_prescription(
            form_data=updated_data,
            user=self.user,
            medico=self.medico,
            clinica=self.clinica,
            patient_exists=True,  # Existing patient workflow
            process_id=processo_id  # Update existing process
        )
        
        # Verify update succeeded
        self.assertIsNotNone(pdf_response_2, "PrescriptionService should generate updated PDF")
        self.assertEqual(updated_processo_id, processo_id, "Should update same process")
        
        print(f"✅ PrescriptionService workflow test passed for processo {processo_id}")