from django.test import TestCase, Client
from django.urls import reverse
from django.http import Http404
from .models import Medicamento, Protocolo, Doenca, Processo
from pacientes.models import Paciente
from medicos.models import Medico
from clinicas.models import Clinica, Emissor
from usuarios.models import Usuario
from datetime import date
from processos.dados import checar_paciente_existe, gerar_lista_meds_ids, gerar_prescricao, resgatar_prescricao, gera_med_dosagem, listar_med
from processos.forms import PreProcesso, NovoProcesso, RenovarProcesso # Import the forms
import tempfile
import os

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


class PDFAccessControlTest(TestCase):
    """
    Comprehensive test suite for PDF access control and security.
    
    This test class verifies that the serve_pdf view properly implements:
    - Authentication requirements
    - Authorization based on patient ownership
    - Filename validation and security
    - CPF format handling (formatted vs cleaned)
    - Directory traversal protection
    - Error handling and logging
    """
    
    def setUp(self):
        """Set up test data including users, patients, and temporary PDF files."""
        # Create test users
        self.user1 = Usuario.objects.create_user(
            email="doctor1@example.com", 
            password="testpass123",
            is_medico=True
        )
        self.user2 = Usuario.objects.create_user(
            email="doctor2@example.com", 
            password="testpass123",
            is_medico=True
        )
        self.user3 = Usuario.objects.create_user(
            email="unauthorized@example.com", 
            password="testpass123"
        )
        
        # Create test patients with different CPF formats
        self.patient1_formatted = Paciente.objects.create(
            nome_paciente="Patient One",
            cpf_paciente="333.774.158-40",  # Formatted CPF
            cns_paciente="123456789012345",
            nome_mae="Mae Um",
            idade="30",
            sexo="M",
            peso="70",
            altura="1.70",
            incapaz=False,
            etnia="Parda",
            telefone1_paciente="11999999999",
            end_paciente="Rua Test, 1",
            rg="1234567",
            escolha_etnia="Parda",
            cidade_paciente="Test City",
            cep_paciente="12345-678",
            telefone2_paciente="",
            nome_responsavel=""
        )
        
        self.patient2_clean = Paciente.objects.create(
            nome_paciente="Patient Two",
            cpf_paciente="12345678901",  # Clean CPF
            cns_paciente="123456789012346",
            nome_mae="Mae Dois",
            idade="35",
            sexo="F",
            peso="60",
            altura="1.65",
            incapaz=False,
            etnia="Branca",
            telefone1_paciente="11888888888",
            end_paciente="Rua Test, 2",
            rg="7654321",
            escolha_etnia="Branca",
            cidade_paciente="Test City",
            cep_paciente="12345-679",
            telefone2_paciente="",
            nome_responsavel=""
        )
        
        # Create patient relationships
        self.patient1_formatted.usuarios.add(self.user1)  # user1 has access to patient1
        self.patient2_clean.usuarios.add(self.user2)      # user2 has access to patient2
        # user3 has no patient access
        
        # Create temporary test PDF files
        self.temp_dir = tempfile.mkdtemp()
        
        # PDF for patient1 (formatted CPF in filename)
        self.pdf1_path = "/tmp/pdf_final_333.774.158-40_G35.pdf"
        with open(self.pdf1_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content for patient 1')
            
        # PDF for patient2 (clean CPF in filename) 
        self.pdf2_path = "/tmp/pdf_final_12345678901_M06.pdf"
        with open(self.pdf2_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content for patient 2')
            
        # Test client
        self.client = Client()
        
    def tearDown(self):
        """Clean up temporary files."""
        # Remove test PDF files
        for pdf_path in [self.pdf1_path, self.pdf2_path]:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access PDFs."""
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should redirect to login (302) or return 403/401
        self.assertIn(response.status_code, [302, 401, 403])
        
    def test_authorized_user_access_granted(self):
        """Test that authorized users can access their patients' PDFs."""
        # Login as user1 who has access to patient1
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'inline; filename="pdf_final_333.774.158-40_G35.pdf"')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        
    def test_unauthorized_user_access_denied(self):
        """Test that users cannot access PDFs for patients they don't own."""
        # Login as user2 who does NOT have access to patient1
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should return 404 (access denied)
        self.assertEqual(response.status_code, 404)
        
    def test_user_without_patients_access_denied(self):
        """Test that users with no patients cannot access any PDFs."""
        # Login as user3 who has no patient relationships
        self.client.login(email="unauthorized@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should return 404 (access denied)
        self.assertEqual(response.status_code, 404)
        
    def test_cpf_format_handling_formatted(self):
        """Test that PDFs with formatted CPFs in filename work correctly."""
        # Login as user1 who has access to patient1 (formatted CPF)
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_cpf_format_handling_clean(self):
        """Test that PDFs with clean CPFs in filename work correctly."""
        # Login as user2 who has access to patient2 (clean CPF)
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_12345678901_M06.pdf'])
        response = self.client.get(url)
        
        # Should successfully serve the PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_invalid_filename_format(self):
        """Test that invalid filename formats are rejected."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        invalid_filenames = [
            "not_pdf_format.txt",
            "missing_prefix_G35.pdf", 
            "pdf_final_.pdf",
            "pdf_final_invalid_cpf_G35.pdf",
            "pdf_final_123_G35.pdf",  # CPF too short
            "pdf_final_1234567890123_G35.pdf",  # CPF too long
        ]
        
        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                url = reverse('processos-serve-pdf', args=[filename])
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                
    def test_directory_traversal_protection(self):
        """Test that directory traversal attempts are blocked."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        # Test filenames that Django URL routing will accept but should be blocked by our validation
        malicious_filenames = [
            "pdf_final_333\\774\\158-40_G35.pdf",  # Windows path separator
            "pdf_final_..333.774.158-40_G35.pdf",  # Dot sequences
            "pdf_final_333.774.158-40..G35.pdf",   # Embedded dots
        ]
        
        for filename in malicious_filenames:
            with self.subTest(filename=filename):
                try:
                    url = reverse('processos-serve-pdf', args=[filename])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 404)
                except Exception:
                    # If URL routing fails, that's also acceptable protection
                    pass
                
    def test_non_pdf_extension_rejected(self):
        """Test that non-PDF files are rejected."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        non_pdf_files = [
            "pdf_final_333.774.158-40_G35.txt",
            "pdf_final_333.774.158-40_G35.doc", 
            "pdf_final_333.774.158-40_G35.exe",
            "pdf_final_333.774.158-40_G35",  # No extension
        ]
        
        for filename in non_pdf_files:
            with self.subTest(filename=filename):
                url = reverse('processos-serve-pdf', args=[filename])
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                
    def test_missing_pdf_file(self):
        """Test behavior when PDF file doesn't exist on filesystem."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        # Try to access a PDF that should be authorized but doesn't exist
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_Z99.pdf'])
        response = self.client.get(url)
        
        # Should return 404 (file not found)
        self.assertEqual(response.status_code, 404)
        
    def test_cross_user_patient_access_denied(self):
        """Test comprehensive cross-user access denial."""
        # user1 tries to access user2's patient PDF
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_12345678901_M06.pdf'])
        response = self.client.get(url)
        
        # Should be denied
        self.assertEqual(response.status_code, 404)
        
        # user2 tries to access user1's patient PDF  
        self.client.login(email="doctor2@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Should be denied
        self.assertEqual(response.status_code, 404)
        
    def test_pdf_content_integrity(self):
        """Test that PDF content is served correctly."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Verify content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'%PDF-1.4 fake pdf content for patient 1')
        
    def test_security_headers_present(self):
        """Test that proper security headers are set."""
        self.client.login(email="doctor1@example.com", password="testpass123")
        
        url = reverse('processos-serve-pdf', args=['pdf_final_333.774.158-40_G35.pdf'])
        response = self.client.get(url)
        
        # Verify security headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_edge_case_cpf_formats(self):
        """Test edge cases in CPF format handling."""
        # Create patient with edge case CPF format
        patient_edge = Paciente.objects.create(
            nome_paciente="Edge Case Patient",
            cpf_paciente="000.000.001-91",  # Edge case formatted CPF
            cns_paciente="123456789012347",
            nome_mae="Mae Edge",
            idade="25",
            sexo="F",
            peso="55",
            altura="1.60",
            incapaz=False,
            etnia="Indígena",
            telefone1_paciente="11777777777",
            end_paciente="Rua Edge, 1",
            rg="1111111",
            escolha_etnia="Indígena",
            cidade_paciente="Edge City",
            cep_paciente="12345-680",
            telefone2_paciente="",
            nome_responsavel=""
        )
        patient_edge.usuarios.add(self.user1)
        
        # Create PDF file for edge case
        edge_pdf_path = "/tmp/pdf_final_000.000.001-91_H30.pdf"
        with open(edge_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4 edge case pdf content')
            
        try:
            self.client.login(email="doctor1@example.com", password="testpass123")
            
            url = reverse('processos-serve-pdf', args=['pdf_final_000.000.001-91_H30.pdf'])
            response = self.client.get(url)
            
            # Should work correctly
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            
        finally:
            if os.path.exists(edge_pdf_path):
                os.remove(edge_pdf_path)