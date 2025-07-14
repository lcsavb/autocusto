from django.test import TestCase
from .models import Medicamento, Protocolo, Doenca, Processo
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from usuarios.models import Usuario
from datetime import date
from processos.dados import checar_paciente_existe, gerar_lista_meds_ids, gerar_prescricao, resgatar_prescricao, gera_med_dosagem, listar_med
from processos.forms import PreProcesso, NovoProcesso, RenovarProcesso # Import the forms

class MedicamentoModelTest(TestCase):

    def test_create_medicamento(self):
        medicamento = Medicamento.objects.create(
            nome="Dipirona",
            dosagem="500mg",
            apres="Comprimido"
        )
        self.assertEqual(medicamento.nome, "Dipirona")

class DoencaModelTest(TestCase):

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

class ProtocoloModelTest(TestCase):

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

class ProcessoModelTest(TestCase):

    def test_create_processo(self):
        # Create related instances
        usuario = Usuario.objects.create_user(email="test@example.com", password="password123")
        medico = Medico.objects.create(nome_medico="Dr. Teste", crm_medico="CRM123", cns_medico="CNS123")
        clinica = Clinica.objects.create(
            nome_clinica="Clinica Teste", cns_clinica="CNS456", logradouro="Rua Teste",
            logradouro_num="1", cidade="Cidade Teste", bairro="Bairro Teste",
            cep="12345-678", telefone_clinica="11987654321"
        )
        emissor = Emissor.objects.create(medico=medico, clinica=clinica)
        paciente = Paciente.objects.create(
            nome_paciente="Paciente Teste", cpf_paciente="11122233344", cns_paciente="123456789012345",
            nome_mae="Mae Teste", idade="30", sexo="M", peso="70", altura="1.70", incapaz=False,
            etnia="Parda", telefone1_paciente="11999999999", end_paciente="Rua Paciente, 1",
            rg="1234567", escolha_etnia="Parda", cidade_paciente="Cidade Paciente",
            cep_paciente="12345-678", telefone2_paciente="", nome_responsavel=""
        )
        protocolo = Protocolo.objects.create(nome="Protocolo Doenca", arquivo="doenca.pdf")
        doenca = Doenca.objects.create(cid="B00.0", nome="Doenca Teste", protocolo=protocolo)
        medicamento = Medicamento.objects.create(nome="Paracetamol", dosagem="500mg", apres="Comprimido")

        # Create Processo instance
        processo = Processo.objects.create(
            anamnese="Anamnese de teste",
            doenca=doenca,
            prescricao={"med1": "Paracetamol 500mg"},
            tratou=True,
            tratamentos_previos="Tratamentos anteriores",
            data1=date.today(),
            preenchido_por="P",
            dados_condicionais={"cond1": "valor1"},
            paciente=paciente,
            medico=medico,
            clinica=clinica,
            emissor=emissor,
            usuario=usuario
        )
        processo.medicamentos.add(medicamento)

        # Assertions
        self.assertEqual(processo.anamnese, "Anamnese de teste")
        self.assertEqual(processo.doenca, doenca)
        self.assertEqual(processo.prescricao, {"med1": "Paracetamol 500mg"})
        self.assertTrue(processo.tratou)
        self.assertEqual(processo.tratamentos_previos, "Tratamentos anteriores")
        self.assertEqual(processo.data1, date.today())
        self.assertEqual(processo.preenchido_por, "P")
        self.assertEqual(processo.dados_condicionais, {"cond1": "valor1"})
        self.assertEqual(processo.paciente, paciente)
        self.assertEqual(processo.medico, medico)
        self.assertEqual(processo.clinica, clinica)
        self.assertEqual(processo.emissor, emissor)
        self.assertEqual(processo.usuario, usuario)
        self.assertIn(medicamento, processo.medicamentos.all())

class DadosFunctionsTest(TestCase):

    def setUp(self):
        # Create dummy Medicamentos for testing
        self.med1 = Medicamento.objects.create(nome="Med1", dosagem="10mg", apres="Comp")
        self.med2 = Medicamento.objects.create(nome="Med2", dosagem="20mg", apres="Comp")
        self.med3 = Medicamento.objects.create(nome="Med3", dosagem="30mg", apres="Comp")

        # Create related instances for Processo and resgatar_prescricao tests
        self.usuario = Usuario.objects.create_user(email="test_user@example.com", password="password123")
        self.medico = Medico.objects.create(nome_medico="Dr. Teste", crm_medico="CRM1234", cns_medico="CNS1234")
        self.clinica = Clinica.objects.create(
            nome_clinica="Clinica Teste", cns_clinica="CNS4567", logradouro="Rua Teste",
            logradouro_num="1", cidade="Cidade Teste", bairro="Bairro Teste",
            cep="12345-678", telefone_clinica="11987654321"
        )
        self.emissor = Emissor.objects.create(medico=self.medico, clinica=self.clinica)
        self.paciente = Paciente.objects.create(
            nome_paciente="Paciente Teste", cpf_paciente="11122233344", cns_paciente="123456789012345",
            nome_mae="Mae Teste", idade="30", sexo="M", peso="70", altura="1.70", incapaz=False,
            etnia="Parda", telefone1_paciente="11999999999", end_paciente="Rua Paciente, 1",
            rg="1234567", escolha_etnia="Parda", cidade_paciente="Cidade Paciente",
            cep_paciente="12345-678", telefone2_paciente="", nome_responsavel=""
        )
        self.protocolo = Protocolo.objects.create(nome="Protocolo Doenca", arquivo="doenca.pdf")
        self.doenca = Doenca.objects.create(cid="B00.0", nome="Doenca Teste", protocolo=self.protocolo)

    def test_checar_paciente_existe(self):
        # Create a test patient
        paciente = Paciente.objects.create(
            nome_paciente="Paciente Existente",
            cpf_paciente="99988877766",
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

        # Test with an existing CPF
        found_paciente = checar_paciente_existe("99988877766")
        self.assertEqual(found_paciente, paciente)

        # Test with a non-existent CPF
        not_found_paciente = checar_paciente_existe("00000000000")
        self.assertFalse(not_found_paciente)

    def test_gerar_lista_meds_ids(self):
        # Test case 1: All meds present and valid
        dados1 = {
            "id_med1": str(self.med1.id),
            "id_med2": str(self.med2.id),
            "id_med3": "nenhum",
            "id_med4": str(self.med1.id), # Duplicate ID to test handling
        }
        expected_ids1 = [str(self.med1.id), str(self.med2.id), str(self.med1.id)]
        self.assertEqual(gerar_lista_meds_ids(dados1), expected_ids1)

        # Test case 2: Some meds missing, some "nenhum"
        dados2 = {
            "id_med1": str(self.med1.id),
            "id_med3": "nenhum",
        }
        expected_ids2 = [str(self.med1.id)]
        self.assertEqual(gerar_lista_meds_ids(dados2), expected_ids2)

        # Test case 3: No meds present
        dados3 = {}
        expected_ids3 = []
        self.assertEqual(gerar_lista_meds_ids(dados3), expected_ids3)

        # Test case 4: All meds are "nenhum"
        dados4 = {
            "id_med1": "nenhum",
            "id_med2": "nenhum",
        }
        expected_ids4 = []
        self.assertEqual(gerar_lista_meds_ids(dados4), expected_ids4)

    def test_gerar_prescricao(self):
        meds_ids = [str(self.med1.id), str(self.med2.id)]
        dados_formulario = {
            f"med1_posologia_mes1": "1x ao dia",
            f"qtd_med1_mes1": "30",
            f"med1_posologia_mes2": "1x ao dia",
            f"qtd_med1_mes2": "30",
            f"med1_posologia_mes3": "1x ao dia",
            f"qtd_med1_mes3": "30",
            f"med1_posologia_mes4": "1x ao dia",
            f"qtd_med1_mes4": "30",
            f"med1_posologia_mes5": "1x ao dia",
            f"qtd_med1_mes5": "30",
            f"med1_posologia_mes6": "1x ao dia",
            f"qtd_med1_mes6": "30",
            "med1_via": "oral",
            f"med2_posologia_mes1": "2x ao dia",
            f"qtd_med2_mes1": "60",
            f"med2_posologia_mes2": "2x ao dia",
            f"qtd_med2_mes2": "60",
            f"med2_posologia_mes3": "2x ao dia",
            f"qtd_med2_mes3": "60",
            f"med2_posologia_mes4": "2x ao dia",
            f"qtd_med2_mes4": "60",
            f"med2_posologia_mes5": "2x ao dia",
            f"qtd_med2_mes5": "60",
            f"med2_posologia_mes6": "2x ao dia",
            f"qtd_med2_mes6": "60",
        }

        expected_prescricao = {
            1: {
                "id_med1": str(self.med1.id),
                "med1_posologia_mes1": "1x ao dia",
                "qtd_med1_mes1": "30",
                "med1_posologia_mes2": "1x ao dia",
                "qtd_med1_mes2": "30",
                "med1_posologia_mes3": "1x ao dia",
                "qtd_med1_mes3": "30",
                "med1_posologia_mes4": "1x ao dia",
                "qtd_med1_mes4": "30",
                "med1_posologia_mes5": "1x ao dia",
                "qtd_med1_mes5": "30",
                "med1_posologia_mes6": "1x ao dia",
                "qtd_med1_mes6": "30",
                "med1_via": "oral",
            },
            2: {
                "id_med2": str(self.med2.id),
                "med2_posologia_mes1": "2x ao dia",
                "qtd_med2_mes1": "60",
                "med2_posologia_mes2": "2x ao dia",
                "qtd_med2_mes2": "60",
                "med2_posologia_mes3": "2x ao dia",
                "qtd_med2_mes3": "60",
                "med2_posologia_mes4": "2x ao dia",
                "qtd_med2_mes4": "60",
                "med2_posologia_mes5": "2x ao dia",
                "qtd_med2_mes5": "60",
                "med2_posologia_mes6": "2x ao dia",
                "qtd_med2_mes6": "60",
            },
        }

        prescricao = gerar_prescricao(meds_ids, dados_formulario)
        self.assertEqual(prescricao, expected_prescricao)

    def test_resgatar_prescricao(self):
        # Prepare a sample prescricao JSON data
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

        # Create a dummy Processo object with the sample prescricao
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

        # Initialize an empty dados dictionary
        dados = {}

        # Call the function
        resgatar_prescricao(dados, processo)

        # Assertions
        self.assertEqual(dados[f"id_med{1}"], str(self.med1.id))
        self.assertEqual(dados[f"med{1}_posologia_mes{1}"], "1x ao dia")
        self.assertEqual(dados[f"qtd_med{1}_mes{1}"], "30")
        self.assertEqual(dados[f"med{1}_via"], "oral")

        self.assertEqual(dados[f"id_med{2}"], str(self.med2.id))
        self.assertEqual(dados[f"med{2}_posologia_mes{1}"], "2x ao dia")
        self.assertEqual(dados[f"qtd_med{2}_mes{1}"], "60")

    def test_gera_med_dosagem(self):
        # Prepare test data
        ids_med_formulario = [str(self.med1.id), str(self.med2.id), "nenhum", str(self.med3.id)]
        dados_formulario = {
            f"med1_posologia_mes1": "1x ao dia",
            f"qtd_med1_mes1": "30",
            f"med2_posologia_mes1": "2x ao dia",
            f"qtd_med2_mes1": "60",
            f"med3_posologia_mes1": "3x ao dia",
            f"qtd_med3_mes1": "90",
            f"med4_posologia_mes1": "4x ao dia", # This one should be ignored as id_med4 is not in ids_med_formulario
            f"qtd_med4_mes1": "120",
        }

        # Expected output
        expected_dados_formulario = dados_formulario.copy()
        expected_dados_formulario[f"med{1}"] = f"{self.med1.nome} {self.med1.dosagem} ({self.med1.apres})"
        expected_dados_formulario[f"med{2}"] = f"{self.med2.nome} {self.med2.dosagem} ({self.med2.apres})"
        expected_dados_formulario[f"med{4}"] = f"{self.med3.nome} {self.med3.dosagem} ({self.med3.apres})"

        expected_meds_ids = [str(self.med1.id), str(self.med2.id), str(self.med3.id)]

        # Call the function
        updated_dados_formulario, returned_meds_ids = gera_med_dosagem(
            dados_formulario, ids_med_formulario
        )

        # Assertions
        self.assertEqual(updated_dados_formulario, expected_dados_formulario)
        self.assertEqual(returned_meds_ids, expected_meds_ids)

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

        # Call the function and assert the result
        result = listar_med(doenca.cid)
        self.assertEqual(result, tuple(expected_list))

class PreProcessoFormTest(TestCase):
    def setUp(self):
        # Create a dummy Doenca for testing clean_cid
        self.protocolo = Protocolo.objects.create(nome="Protocolo Teste", arquivo="teste.pdf")
        self.doenca = Doenca.objects.create(cid="A00.0", nome="Doenca Teste", protocolo=self.protocolo)

    def test_valid_data(self):
        form = PreProcesso(data={'cpf_paciente': '123.456.789-00', 'cid': 'A00.0'})
        self.assertTrue(form.is_valid())

    def test_invalid_cid(self):
        form = PreProcesso(data={'cpf_paciente': '123.456.789-00', 'cid': 'Z99.9'})
        self.assertFalse(form.is_valid())
        self.assertIn('cid', form.errors)
        self.assertEqual(form.errors['cid'], ['CID "Z99.9" incorreto!'])

    def test_invalid_cpf(self):
        form = PreProcesso(data={'cpf_paciente': '123.456.789-0', 'cid': 'A00.0'}) # Invalid CPF format
        self.assertFalse(form.is_valid())
        self.assertIn('cpf_paciente', form.errors)
        self.assertEqual(form.errors['cpf_paciente'], ['CPF 123.456.789-0 inválido!'])

    def test_empty_fields(self):
        form = PreProcesso(data={'cpf_paciente': '', 'cid': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('cpf_paciente', form.errors)
        self.assertIn('cid', form.errors)
        self.assertEqual(form.errors['cpf_paciente'], ['Este campo é obrigatório.'])
        self.assertEqual(form.errors['cid'], ['Este campo é obrigatório.'])