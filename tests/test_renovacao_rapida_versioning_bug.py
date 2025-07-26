"""
Test for Renovacao Rapida Versioning Bug

This test reproduces the critical bug where newly created processes
are not appearing in the renovacao_rapida template due to issues
with the patient versioning system.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from processos.models import Processo, Doenca, Protocolo, Medicamento
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from processos.services.prescription_database_service import PrescriptionDatabaseService
from processos.repositories.patient_repository import PatientRepository


User = get_user_model()


class RenovacaoRapidaVersioningBugTest(TestCase):
    """Test for the critical bug where new processes don't show in renovacao_rapida."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='doctor@test.com',
            password='testpass123'
        )
        
        # Create test medico
        self.medico = Medico.objects.create(
            nome_medico='Dr. Test',
            crm_medico='12345',
            cns_medico='123456789012345',
            especialidade='Clinica Geral'
        )
        self.medico.usuarios.add(self.user)
        
        # Create test clinica
        self.clinica = Clinica.objects.create(
            nome_clinica='Test Clinic',
            cns_clinica='1234567',  # Fixed: 7 characters to match database constraint
            logradouro='Test Street',
            logradouro_num='123',
            cidade='Test City',
            bairro='Test Neighborhood',
            cep='1234567',  # Fixed: 7 characters to match database constraint
            telefone_clinica='1234567890'
        )
        self.clinica.usuarios.add(self.user)
        
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
        
        # Setup test patient data
        self.patient_data = {
            'nome_paciente': 'João da Silva',
            'cpf_paciente': '12345678901',
            'peso': '70',
            'altura': '175',
            'nome_mae': 'Maria da Silva',
            'incapaz': False,
            'nome_responsavel': '',
            'etnia': 'branco',
            'telefone1_paciente': '11999999999',
            'telefone2_paciente': '',
            'email_paciente': 'joao@test.com',
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
        # Step 1: Create a new process using the same workflow as the app
        from processos.repositories.medication_repository import MedicationRepository
        
        # Process the prescription data like the app does
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        # Register in database - this creates the patient and process
        processo_id = registrar_db(
            final_data,
            meds_ids, 
            self.doenca,
            self.emissor,
            self.user,
            paciente_existe=False,  # This is a NEW patient
            cid='M05'
        )
        
        # Verify the process was created
        self.assertIsNotNone(processo_id)
        processo = Processo.objects.get(id=processo_id)
        self.assertEqual(processo.usuario, self.user)
        
        # Step 2: Verify patient was created and associated with user
        patient = processo.paciente
        self.assertIsNotNone(patient)
        self.assertEqual(patient.cpf_paciente, '12345678901')
        
        # CRITICAL CHECK: Verify user is associated with patient
        self.assertIn(self.user, patient.usuarios.all(), 
                     "User should be associated with the newly created patient")
        
        # Step 3: Test patient search like renovacao_rapida does
        search_results = Paciente.get_patients_for_user_search(self.user, 'João')
        patient_list = [patient for patient, version in search_results]
        
        # CRITICAL ASSERTION: The newly created patient should appear in search
        self.assertIn(patient, patient_list,
                     "Newly created patient should appear in renovacao_rapida search")
        
        # Additional verification: Test with CPF search
        cpf_search_results = Paciente.get_patients_for_user_search(self.user, '12345678901')
        cpf_patient_list = [patient for patient, version in cpf_search_results]
        
        self.assertIn(patient, cpf_patient_list,
                     "Newly created patient should appear in CPF search")
    
    def test_user_patient_association_after_process_creation(self):
        """Test that user-patient association is correctly established."""
        # Before creating process - user should have no patients
        initial_patients = self.user.pacientes.all()
        self.assertEqual(initial_patients.count(), 0)
        
        # Create process using helpers like the app does
        from processos.repositories.medication_repository import MedicationRepository
        
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id = registrar_db(
            final_data,
            meds_ids,
            self.doenca, 
            self.emissor,
            self.user,
            paciente_existe=False,
            cid='M05'
        )
        
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
        
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id = registrar_db(
            final_data,
            meds_ids,
            self.doenca,
            self.emissor, 
            self.user,
            paciente_existe=False,
            cid='M05'
        )
        
        # Ensure user is properly associated with medico and clinica
        self.user.medicos.add(self.medico)
        self.user.clinicas.add(self.clinica)
        
        # Login and test the actual view
        self.client.login(email='doctor@test.com', password='testpass123')
        
        # Test renovacao_rapida view with search
        response = self.client.get('/processos/renovacao/', {'b': 'João'}, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if the patient appears in the context
        busca_pacientes = response.context['busca_pacientes']
        
        # Get the created patient
        processo = Processo.objects.get(id=processo_id)
        created_patient = processo.paciente
        
        # CRITICAL ASSERTION: The patient should be in the search results
        self.assertIn(created_patient, busca_pacientes,
                     "Newly created patient should appear in renovacao_rapida template context")
        
        # Also test that we have the right number of patients
        self.assertEqual(len(busca_pacientes), 1,
                        "Should find exactly one patient matching the search")
    
    def test_newly_created_process_appears_in_template_context(self):
        """CRITICAL TEST: Test that newly created processes appear in template context for user."""
        # Create a process first
        from processos.repositories.medication_repository import MedicationRepository
        
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id = registrar_db(
            final_data,
            meds_ids,
            self.doenca,
            self.emissor, 
            self.user,
            paciente_existe=False,
            cid='M05'
        )
        
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
        # Step 1: User1 creates a process for a patient
        from processos.repositories.medication_repository import MedicationRepository
        
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id_1 = registrar_db(
            final_data,
            meds_ids,
            self.doenca,
            self.emissor, 
            self.user,
            paciente_existe=False,  # New patient
            cid='M05'
        )
        
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
        
        medication_ids_2 = gerar_lista_meds_ids(user2_prescription_data)
        user2_prescription_data, meds_ids_2 = gera_med_dosagem(user2_prescription_data, medication_ids_2)
        final_data_2 = vincula_dados_emissor(user2, medico2, self.clinica, user2_prescription_data)
        
        processo_id_2 = registrar_db(
            final_data_2,
            meds_ids_2,
            doenca2,
            emissor2,
            user2,
            paciente_existe=patient,  # EXISTING patient!
            cid='I10'
        )
        
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
        from processos.repositories.medication_repository import MedicationRepository
        
        # STEP 1: Create the first process (this should work fine)
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id_1 = registrar_db(
            final_data,
            meds_ids,
            self.doenca,
            self.emissor, 
            self.user,
            paciente_existe=False,  # New patient
            cid='M05'
        )
        
        # Get the patient
        processo_1 = Processo.objects.get(id=processo_id_1)
        patient = processo_1.paciente
        
        print(f"DEBUG: After first process - patient.processos.all().count() = {patient.processos.all().count()}")
        
        # STEP 2: Create a second process for the SAME patient (different disease) - THIS MIGHT BE THE BUG
        doenca2 = Doenca.objects.create(
            cid='I10',
            nome='Hypertension',
            protocolo=self.protocolo
        )
        
        # Second prescription data for SAME patient SAME user
        prescription_data_2 = self.patient_data.copy()  
        prescription_data_2.update({
            'anamnese': 'Second process anamnese',
            'tratou': False,
            'tratamentos_previos': 'None',
            'preenchido_por': 'medico',
            'data_1': '17/01/2024',
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '2 comprimidos 1x ao dia',
            'qtd_med1_mes1': '60',
            'med1_posologia_mes2': '2 comprimidos 1x ao dia', 
            'qtd_med1_mes2': '60',
            'med1_posologia_mes3': '2 comprimidos 1x ao dia',
            'qtd_med1_mes3': '60',
            'med1_posologia_mes4': '2 comprimidos 1x ao dia',
            'qtd_med1_mes4': '60',
            'med1_posologia_mes5': '2 comprimidos 1x ao dia',
            'qtd_med1_mes5': '60',
            'med1_posologia_mes6': '2 comprimidos 1x ao dia',
            'qtd_med1_mes6': '60',
            'med1_via': 'oral'
        })
        
        medication_ids_2 = gerar_lista_meds_ids(prescription_data_2)
        prescription_data_2, meds_ids_2 = gera_med_dosagem(prescription_data_2, medication_ids_2)
        final_data_2 = vincula_dados_emissor(self.user, self.medico, self.clinica, prescription_data_2)
        
        # Create second process for EXISTING patient
        processo_id_2 = registrar_db(
            final_data_2,
            meds_ids_2,
            doenca2,
            self.emissor,
            self.user,
            paciente_existe=patient,  # EXISTING patient - this is where the bug might be!
            cid='I10'
        )
        
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
        
        # CRITICAL ASSERTIONS - This is where the bug would show up
        self.assertEqual(all_processes.count(), 2, 
                        "Patient should have exactly 2 processes")
        self.assertEqual(len(user_processes), 2, 
                        "User should see both processes they created")
        self.assertIn(processo_1, user_processes, 
                     "First process should be visible")
        self.assertIn(processo_2, user_processes, 
                     "NEWLY CREATED second process should be visible immediately")
        
        # Verify both processes belong to same user and same patient
        self.assertEqual(processo_1.usuario, self.user)
        self.assertEqual(processo_2.usuario, self.user)
        self.assertEqual(processo_1.paciente.id, processo_2.paciente.id)
    
    def test_critical_bug_fix_user_process_isolation(self):
        """CRITICAL TEST: Verify the bug fix prevents users from overwriting each other's processes."""
        from processos.repositories.medication_repository import MedicationRepository
        
        # STEP 1: User1 creates a process for a patient with disease G40.6
        medication_ids = gerar_lista_meds_ids(self.prescription_data)
        self.prescription_data, meds_ids = gera_med_dosagem(self.prescription_data, medication_ids)
        final_data = vincula_dados_emissor(self.user, self.medico, self.clinica, self.prescription_data)
        
        processo_id_1 = registrar_db(
            final_data,
            meds_ids,
            self.doenca,  # G40.6
            self.emissor,
            self.user,
            paciente_existe=False,  # New patient
            cid='M05'
        )
        
        processo_1 = Processo.objects.get(id=processo_id_1)
        patient = processo_1.paciente
        
        # STEP 2: Create User2 and associated infrastructure
        user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        medico2 = Medico.objects.create(
            nome_medico='Dr. User2',
            crm_medico='54321',
            cns_medico='543216789012345',
            especialidade='Neurologia'
        )
        medico2.usuarios.add(user2)
        
        emissor2 = Emissor.objects.create(
            medico=medico2,
            clinica=self.clinica
        )
        
        # STEP 3: User2 tries to create SAME disease process for SAME patient
        # Before the fix, this would overwrite User1's process
        # After the fix, this should create a NEW process for User2
        
        user2_prescription_data = self.patient_data.copy()
        user2_prescription_data.update({
            'anamnese': 'User2 different anamnese',
            'tratou': False,
            'tratamentos_previos': 'User2 different treatments',
            'preenchido_por': 'medico',
            'data_1': '20/01/2024',  # Different date
            'id_med1': str(self.medicamento.id),
            'med1_posologia_mes1': '1 comprimido 3x ao dia',  # Different dosage
            'qtd_med1_mes1': '90',  # Different quantity
            'med1_posologia_mes2': '1 comprimido 3x ao dia',
            'qtd_med1_mes2': '90',
            'med1_posologia_mes3': '1 comprimido 3x ao dia',
            'qtd_med1_mes3': '90',
            'med1_posologia_mes4': '1 comprimido 3x ao dia',
            'qtd_med1_mes4': '90',
            'med1_posologia_mes5': '1 comprimido 3x ao dia',
            'qtd_med1_mes5': '90',
            'med1_posologia_mes6': '1 comprimido 3x ao dia',
            'qtd_med1_mes6': '90',
            'med1_via': 'oral'
        })
        
        medication_ids_2 = gerar_lista_meds_ids(user2_prescription_data)
        user2_prescription_data, meds_ids_2 = gera_med_dosagem(user2_prescription_data, medication_ids_2)
        final_data_2 = vincula_dados_emissor(user2, medico2, self.clinica, user2_prescription_data)
        
        # Create User2's process for SAME patient and SAME disease
        processo_id_2 = registrar_db(
            final_data_2,
            meds_ids_2,
            self.doenca,  # SAME disease (M05)
            emissor2,
            user2,
            paciente_existe=patient,  # SAME patient
            cid='M05'  # SAME CID
        )
        
        processo_2 = Processo.objects.get(id=processo_id_2)
        
        # CRITICAL ASSERTIONS - These verify the bug fix
        self.assertNotEqual(processo_id_1, processo_id_2,
                           "User2 should create a NEW process, not overwrite User1's")
        
        # Refresh processo_1 from database to ensure it wasn't modified
        processo_1.refresh_from_db()
        
        # Verify User1's process is unchanged
        self.assertEqual(processo_1.usuario, self.user,
                        "User1's process should still belong to User1")
        self.assertEqual(processo_1.anamnese, 'Test anamnese',
                        "User1's process data should be unchanged")
        
        # Verify User2's process has correct ownership and data
        self.assertEqual(processo_2.usuario, user2,
                        "User2's process should belong to User2")
        self.assertEqual(processo_2.anamnese, 'User2 different anamnese',
                        "User2's process should have User2's data")
        
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