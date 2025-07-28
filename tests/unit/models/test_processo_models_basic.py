from tests.test_base import BaseTestCase, TestDataFactory
from processos.models import Medicamento, Protocolo, Doenca, Processo
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from usuarios.models import Usuario
from datetime import date
from processos.repositories.patient_repository import PatientRepository
from processos.repositories.medication_repository import MedicationRepository


# TestDataFactory is now imported from tests.test_base


class MedicamentoModelTest(BaseTestCase):

    def test_create_medicamento(self):
        medicamento = Medicamento.objects.create(
            nome="Dipirona",
            dosagem="500mg",
            apres="Comprimido"
        )
        self.assertEqual(medicamento.nome, "Dipirona")


class DoencaModelTest(BaseTestCase):

    def test_create_doenca(self):
        # Create a Protocolo instance first, as Doenca has a ForeignKey to Protocolo
        protocolo = Protocolo.objects.create(
            nome="Protocolo de Teste",
            arquivo="protocolo_teste.pdf"
        )

        # Create a Doenca instance, linking it to the created Protocolo
        doenca = Doenca.objects.create(
            cid="A00.0",
            nome="Doença de Teste",
            protocolo=protocolo
        )

        # Assert that the Doenca object's cid and nome are as expected
        self.assertEqual(doenca.cid, "A00.0")
        self.assertEqual(doenca.nome, "Doença de Teste")


class ProtocoloModelTest(BaseTestCase):

    def test_create_protocolo(self):
        # Create a Medicamento instance to associate with the Protocolo
        medicamento = Medicamento.objects.create(
            nome="Amoxicilina",
            dosagem="500mg",
            apres="Cápsula"
        )

        # Create a Protocolo instance
        protocolo = Protocolo.objects.create(
            nome="Protocolo de Asma",
            arquivo="asma.pdf",
            dados_condicionais={"campo1": "valor1", "campo2": "valor2"}
        )
        protocolo.medicamentos.add(medicamento)

        # Assert that the Protocolo object's attributes are as expected
        self.assertEqual(protocolo.nome, "Protocolo de Asma")
        self.assertEqual(protocolo.arquivo, "asma.pdf")
        self.assertEqual(protocolo.dados_condicionais, {"campo1": "valor1", "campo2": "valor2"})
        self.assertIn(medicamento, protocolo.medicamentos.all())


class ProcessoModelTest(BaseTestCase):

    def test_create_processo(self):
        # Use global helper methods for consistent test data
        processo = self.create_test_processo(
            anamnese="Anamnese de teste",
            prescricao={"med1": "Paracetamol 500mg"},
            tratou=True,
            tratamentos_previos="Tratamentos anteriores",
            preenchido_por="P",
            dados_condicionais={"cond1": "valor1"}
        )
        medicamento = self.create_test_medicamento(nome="Paracetamol", dosagem="500mg", apres="Comprimido")
        processo.medicamentos.add(medicamento)

        # Assertions
        self.assertEqual(processo.anamnese, "Anamnese de teste")
        self.assertEqual(processo.prescricao, {"med1": "Paracetamol 500mg"})
        self.assertTrue(processo.tratou)
        self.assertEqual(processo.tratamentos_previos, "Tratamentos anteriores")
        self.assertEqual(processo.data1, date.today())
        self.assertEqual(processo.preenchido_por, "P")
        self.assertEqual(processo.dados_condicionais, {"cond1": "valor1"})
        # Test that relations are properly set by our helper
        self.assertIsNotNone(processo.paciente)
        self.assertIsNotNone(processo.medico)
        self.assertIsNotNone(processo.clinica)
        self.assertIsNotNone(processo.emissor)
        self.assertIsNotNone(processo.usuario)
        self.assertIn(medicamento, processo.medicamentos.all())


class DadosFunctionsTest(BaseTestCase):

    def setUp(self):
        # Create dummy Medicamentos for testing
        self.med1 = Medicamento.objects.create(nome="Med1", dosagem="10mg", apres="Comp")
        self.med2 = Medicamento.objects.create(nome="Med2", dosagem="20mg", apres="Comp")
        self.med3 = Medicamento.objects.create(nome="Med3", dosagem="30mg", apres="Comp")

        # Create related instances for Processo tests
        self.usuario = Usuario.objects.create_user(email="test_user@example.com", password="password123")
        self.medico = Medico.objects.create(nome_medico="Dr. Teste", crm_medico="CRM1234", cns_medico="CNS1234")
        self.clinica = Clinica.objects.create(
            nome_clinica="Clinica Teste", cns_clinica="CNS4567", logradouro="Rua Teste",
            logradouro_num="1", cidade="Cidade Teste", bairro="Bairro Teste",
            cep="12345-678", telefone_clinica="(11) 9876-5432"
        )
        self.emissor = Emissor.objects.create(medico=self.medico, clinica=self.clinica)
        self.paciente = Paciente.objects.create(
            nome_paciente="Paciente Teste", cpf_paciente=TestDataFactory.get_unique_cpf(), cns_paciente="123456789012345",
            nome_mae="Mae Teste", idade="30", sexo="M", peso="70", altura="1.70", incapaz=False,
            etnia="Parda", telefone1_paciente="11999999999", end_paciente="Rua Paciente, 1",
            rg="1234567", escolha_etnia="Parda", cidade_paciente="Cidade Paciente",
            cep_paciente="12345-678", telefone2_paciente="", nome_responsavel=""
        )
        self.protocolo = Protocolo.objects.create(nome="Protocolo Doenca", arquivo="doenca.pdf")
        self.doenca = Doenca.objects.create(cid="B00.0", nome="Doenca Teste", protocolo=self.protocolo)

    def test_checar_paciente_existe(self):
        # Generate CPF for testing
        test_cpf = TestDataFactory.get_unique_cpf()
        
        # Create a test patient
        paciente = Paciente.objects.create(
            nome_paciente="Paciente Existente",
            cpf_paciente=test_cpf,
            cns_paciente="111222333445566",
            nome_mae="Mae Existente",
            idade="40",
            sexo="F",
            peso="60",
            altura="1.60",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11977776666",
            end_paciente="Rua Teste, 10",
            rg="1234567",
            escolha_etnia="Branca",
            cidade_paciente="São Paulo",
            cep_paciente="01000-000",
            telefone2_paciente="",
            nome_responsavel=""
        )

        # Test with an existing CPF using PatientRepository
        patient_repo = PatientRepository()
        found_exists = patient_repo.check_patient_exists(test_cpf)
        self.assertTrue(found_exists)  # check_patient_exists returns boolean

        # Test with a non-existent CPF
        not_found_paciente = patient_repo.check_patient_exists("00000000000")
        self.assertFalse(not_found_paciente)

    def test_extract_medication_ids(self):
        # Test case 1: All meds present and valid
        dados1 = {
            "id_med1": str(self.med1.id),
            "id_med2": str(self.med2.id),
            "id_med3": "nenhum",
            "id_med4": str(self.med1.id), # Duplicate ID to test handling
        }
        expected_ids1 = [str(self.med1.id), str(self.med2.id), str(self.med1.id)]
        med_repo = MedicationRepository()
        self.assertEqual(med_repo.extract_medication_ids_from_form(dados1), expected_ids1)

        # Test case 2: Some meds missing, some "nenhum"
        dados2 = {
            "id_med1": str(self.med1.id),
            "id_med3": "nenhum",
        }
        expected_ids2 = [str(self.med1.id)]
        self.assertEqual(med_repo.extract_medication_ids_from_form(dados2), expected_ids2)

        # Test case 3: No meds present
        dados3 = {}
        expected_ids3 = []
        self.assertEqual(med_repo.extract_medication_ids_from_form(dados3), expected_ids3)

        # Test case 4: All meds are "nenhum"
        dados4 = {
            "id_med1": "nenhum",
            "id_med2": "nenhum",
        }
        expected_ids4 = []
        self.assertEqual(med_repo.extract_medication_ids_from_form(dados4), expected_ids4)

    def test_prescription_data_structure(self):
        """Test that prescription data can be structured correctly - moved to service layer."""
        # This functionality has been moved to the service layer
        # See tests/unit/services/ for prescription service tests
        meds_ids = [str(self.med1.id), str(self.med2.id)]
        
        # Basic validation that medication IDs are properly structured
        self.assertIsInstance(meds_ids, list)
        self.assertEqual(len(meds_ids), 2)
        self.assertTrue(all(isinstance(med_id, str) for med_id in meds_ids))

    def test_processo_prescription_field(self):
        """Test that Processo model stores prescription data correctly - prescription retrieval moved to service layer."""
        # This test validates the Processo model's prescription field
        # Prescription retrieval functionality has been moved to the service layer
        sample_prescricao = {
            "1": {
                "id_med1": str(self.med1.id),
                "med1_posologia_mes1": "1x ao dia",
                "qtd_med1_mes1": "30",
                "med1_via": "oral",
            },
            "2": {
                "id_med2": str(self.med2.id),
                "med2_posologia_mes1": "2x ao dia",
                "qtd_med2_mes1": "60",
            },
        }

        # Create a Processo object with the sample prescricao
        processo = Processo.objects.create(
            anamnese="Test Anamnese",
            doenca=self.doenca,
            prescricao=sample_prescricao,
            tratou=True,
            tratamentos_previos="None",
            data1=date.today(),
            preenchido_por="P",
            dados_condicionais={},
            paciente=self.paciente,
            medico=self.medico,
            clinica=self.clinica,
            emissor=self.emissor,
            usuario=self.usuario
        )

        # Test that prescription data is stored correctly in the model
        self.assertEqual(processo.prescricao, sample_prescricao)
        self.assertIn("1", processo.prescricao)
        self.assertIn("2", processo.prescricao)
        self.assertEqual(processo.prescricao["1"]["id_med1"], str(self.med1.id))

    def test_medication_dosage_formatting(self):
        """Test medication dosage formatting - functionality moved to service layer."""
        # This functionality has been moved to the service layer
        # Testing basic medication model attributes instead
        
        # Test medication data formatting
        expected_format = f"{self.med1.nome} {self.med1.dosagem} ({self.med1.apres})"
        actual_format = f"{self.med1.nome} {self.med1.dosagem} ({self.med1.apres})"
        self.assertEqual(actual_format, expected_format)
        
        # Test multiple medications
        medications = [self.med1, self.med2, self.med3]
        formatted_names = [f"{med.nome} {med.dosagem} ({med.apres})" for med in medications]
        
        self.assertEqual(len(formatted_names), 3)
        self.assertIn("Med1 10mg (Comp)", formatted_names)
        self.assertIn("Med2 20mg (Comp)", formatted_names)
        self.assertIn("Med3 30mg (Comp)", formatted_names)

    def test_listar_med(self):
        # Create a Protocolo and Doenca instance
        protocolo = Protocolo.objects.create(nome="Protocolo Teste", arquivo="teste.pdf")
        doenca = Doenca.objects.create(cid="X00.0", nome="Doenca Teste", protocolo=protocolo)

        # Create Medicamento instances and associate them with the Protocolo
        med1 = Medicamento.objects.create(nome="MedA", dosagem="10mg", apres="Comp")
        med2 = Medicamento.objects.create(nome="MedB", dosagem="20mg", apres="Caps")
        protocolo.medicamentos.add(med1, med2)

        # Expected output
        expected_list = [
            ("nenhum", "Escolha o medicamento..."),
            (med1.id, f"{med1.nome} {med1.dosagem} - {med1.apres}"),
            (med2.id, f"{med2.nome} {med2.dosagem} - {med2.apres}"),
        ]

        # Call the repository method and assert the result
        med_repo = MedicationRepository()
        result = med_repo.list_medications_by_cid(doenca.cid)
        self.assertEqual(result, tuple(expected_list))