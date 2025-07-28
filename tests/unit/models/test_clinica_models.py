from django.db import IntegrityError
from tests.test_base import BaseTestCase, BaseTransactionTestCase, TestDataFactory
from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuario
from clinicas.forms import ClinicaFormulario


class ClinicaModelTest(BaseTestCase):

    def test_create_clinica(self):
        # Create a Clinica instance with sample data
        clinica = self.create_test_clinica(
            nome_clinica="Clínica Saúde e Bem-Estar",
            logradouro="Rua das Flores",
            logradouro_num="123",
            cidade="São Paulo",
            bairro="Centro",
            cep="01000-000",
            telefone_clinica="1122223333"
        )
        # Assert that the clinic's name matches the expected value after creation
        self.assertEqual(clinica.nome_clinica, "Clínica Saúde e Bem-Estar")


# English: ClinicaFormTest
class ClinicaFormularioTest(BaseTestCase):

    def test_valid_form(self):
        # Use global TestDataFactory for consistent data
        data = TestDataFactory.get_valid_form_data_patterns()['clinic_creation']
        data.update({
            'nome_clinica': 'Clinica Teste',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '(11) 98765-4321',
        })
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        # English: clinic
        clinica = form.save()
        self.assertEqual(clinica.nome_clinica, 'Clinica Teste')

    def test_invalid_form_missing_data(self):
        # English: data
        data = {
            'nome_clinica': '',
            'cns_clinica': TestDataFactory.get_unique_cns(),
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '(11) 98765-4321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_clinica', form.errors)

    def test_invalid_form_cns_too_long(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '12345678',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '(11) 98765-4321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cns_clinica', form.errors)

    def test_invalid_form_cns_too_short(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '123456',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '(11) 98765-4321',
        }
        # English: form
        form = ClinicaFormulario(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cns_clinica', form.errors)


class CNSIntegrityTest(BaseTransactionTestCase):
    """Test CNS field integrity and uniqueness"""
    
    def setUp(self):
        super().setUp()
        self.user = self.create_test_user()
        
    def test_cns_unique_constraint(self):
        """Test that CNS must be unique across all clinics"""
        # Create first clinic with unique CNS
        clinic1 = self.create_test_clinica(nome_clinica="Clinic 1")
        unique_cns = clinic1.cns_clinica
        
        # Try to create second clinic with same CNS
        with self.assertRaises(IntegrityError):
            Clinica.objects.create(
                nome_clinica="Clinic 2",
                cns_clinica=unique_cns  # Same CNS
            )
    
    def test_cns_not_in_version_model(self):
        """Verify CNS is NOT stored in ClinicaVersion model"""
        # Check that ClinicaVersion doesn't have cns_clinica field
        version_fields = [f.name for f in ClinicaVersion._meta.get_fields()]
        self.assertNotIn('cns_clinica', version_fields)
    
    def test_cns_immutable_in_form(self):
        """Test that CNS cannot be changed in form when editing"""
        # Create clinic with unique CNS
        clinic = self.create_test_clinica(
            nome_clinica="Test Clinic",
            logradouro="Rua Test",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test",
            cep="12345-678",
            telefone_clinica="(11) 1234-5678"
        )
        original_cns = clinic.cns_clinica
        
        # Create form for editing (has instance)
        attempted_cns = TestDataFactory.get_unique_cns()  # Different CNS
        form_data = {
            'nome_clinica': 'Updated Clinic',
            'cns_clinica': attempted_cns,  # Try to change CNS
            'logradouro': 'Rua Test',
            'logradouro_num': '123',
            'cidade': 'Test City',
            'bairro': 'Test',
            'cep': '12345-678',
            'telefone_clinica': '(11) 1234-5678'
        }
        
        form = ClinicaFormulario(data=form_data, instance=clinic)
        self.assertTrue(form.is_valid())
        
        # Save and check CNS didn't change
        saved_clinic = form.save()
        self.assertEqual(saved_clinic.cns_clinica, original_cns)  # Original CNS
        self.assertNotEqual(saved_clinic.cns_clinica, attempted_cns)  # Not the attempted change
    
    def test_versioning_preserves_cns_integrity(self):
        """Test that versioning system doesn't duplicate CNS"""
        # Create clinic
        clinic = self.create_test_clinica(nome_clinica="Version Test Clinic")
        
        # Create multiple versions
        version1 = ClinicaVersion.objects.create(
            clinica=clinic,
            nome_clinica="Version 1",
            logradouro="Street 1",
            logradouro_num="1",
            cidade="City 1",
            bairro="District 1",
            cep="11111-111",
            telefone_clinica="(11) 1111-1111",
            version_number=1,
            status='active'
        )
        
        version2 = ClinicaVersion.objects.create(
            clinica=clinic,
            nome_clinica="Version 2",
            logradouro="Street 2",
            logradouro_num="2",
            cidade="City 2",
            bairro="District 2",
            cep="22222-222",
            telefone_clinica="(22) 2222-2222",
            version_number=2,
            status='active'
        )
        
        # Verify both versions point to same clinic with same CNS
        self.assertEqual(version1.clinica.cns_clinica, clinic.cns_clinica)
        self.assertEqual(version2.clinica.cns_clinica, clinic.cns_clinica)
        self.assertEqual(version1.clinica.id, version2.clinica.id)
    
    def test_multiple_users_same_clinic_cns(self):
        """Test multiple users can access same clinic (same CNS)"""
        # Create second user
        user2 = self.create_test_user(
            email=self.data_generator.generate_unique_email()
        )
        
        # Create clinic
        clinic = self.create_test_clinica(nome_clinica="Shared Clinic")
        
        # Associate both users
        ClinicaUsuario.objects.create(usuario=self.user, clinica=clinic)
        ClinicaUsuario.objects.create(usuario=user2, clinica=clinic)
        
        # Verify both users access same clinic with same CNS
        user1_clinics = Clinica.objects.filter(usuarios=self.user)
        user2_clinics = Clinica.objects.filter(usuarios=user2)
        
        self.assertEqual(user1_clinics.first().cns_clinica, clinic.cns_clinica)
        self.assertEqual(user2_clinics.first().cns_clinica, clinic.cns_clinica)
        self.assertEqual(user1_clinics.first().id, user2_clinics.first().id)
