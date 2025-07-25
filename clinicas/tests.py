# English: ClinicaModelTest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
# English: Clinica
from .models import Clinica, ClinicaVersion, ClinicaUsuario
# English: ClinicaForm
from .forms import ClinicaFormulario

Usuario = get_user_model()

class ClinicaModelTest(TestCase):

    def test_create_clinica(self):
        # Create a Clinica instance with sample data
        # English: clinic
        clinica = Clinica.objects.create(
            nome_clinica="Clínica Saúde e Bem-Estar",
            cns_clinica="1234567",
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
class ClinicaFormularioTest(TestCase):

    def test_valid_form(self):
        # English: data
        data = {
            'nome_clinica': 'Clinica Teste',
            'cns_clinica': '1234567',
            'logradouro': 'Rua Teste',
            'logradouro_num': '123',
            'cidade': 'Cidade Teste',
            'bairro': 'Bairro Teste',
            'cep': '12345-678',
            'telefone_clinica': '(11) 98765-4321',
        }
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
            'cns_clinica': '1234567',
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


class CNSIntegrityTest(TransactionTestCase):
    """Test CNS field integrity and uniqueness"""
    
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
    def test_cns_unique_constraint(self):
        """Test that CNS must be unique across all clinics"""
        # Create first clinic
        clinic1 = Clinica.objects.create(
            nome_clinica="Clinic 1",
            cns_clinica="1234567"
        )
        
        # Try to create second clinic with same CNS
        with self.assertRaises(IntegrityError):
            Clinica.objects.create(
                nome_clinica="Clinic 2",
                cns_clinica="1234567"  # Same CNS
            )
    
    def test_cns_not_in_version_model(self):
        """Verify CNS is NOT stored in ClinicaVersion model"""
        # Check that ClinicaVersion doesn't have cns_clinica field
        version_fields = [f.name for f in ClinicaVersion._meta.get_fields()]
        self.assertNotIn('cns_clinica', version_fields)
    
    def test_cns_immutable_in_form(self):
        """Test that CNS cannot be changed in form when editing"""
        # Create clinic
        clinic = Clinica.objects.create(
            nome_clinica="Test Clinic",
            cns_clinica="7654321",
            logradouro="Rua Test",
            logradouro_num="123",
            cidade="Test City",
            bairro="Test",
            cep="12345-678",
            telefone_clinica="(11) 1234-5678"
        )
        
        # Create form for editing (has instance)
        form_data = {
            'nome_clinica': 'Updated Clinic',
            'cns_clinica': '9999999',  # Try to change CNS
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
        self.assertEqual(saved_clinic.cns_clinica, "7654321")  # Original CNS
        self.assertNotEqual(saved_clinic.cns_clinica, "9999999")  # Not the attempted change
    
    def test_versioning_preserves_cns_integrity(self):
        """Test that versioning system doesn't duplicate CNS"""
        # Create clinic
        clinic = Clinica.objects.create(
            nome_clinica="Version Test Clinic",
            cns_clinica="1111111"
        )
        
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
        self.assertEqual(version1.clinica.cns_clinica, "1111111")
        self.assertEqual(version2.clinica.cns_clinica, "1111111")
        self.assertEqual(version1.clinica.id, version2.clinica.id)
    
    def test_multiple_users_same_clinic_cns(self):
        """Test multiple users can access same clinic (same CNS)"""
        # Create second user
        user2 = Usuario.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create clinic
        clinic = Clinica.objects.create(
            nome_clinica="Shared Clinic",
            cns_clinica="2222222"
        )
        
        # Associate both users
        ClinicaUsuario.objects.create(usuario=self.user, clinica=clinic)
        ClinicaUsuario.objects.create(usuario=user2, clinica=clinic)
        
        # Verify both users access same clinic with same CNS
        user1_clinics = Clinica.objects.filter(usuarios=self.user)
        user2_clinics = Clinica.objects.filter(usuarios=user2)
        
        self.assertEqual(user1_clinics.first().cns_clinica, "2222222")
        self.assertEqual(user2_clinics.first().cns_clinica, "2222222")
        self.assertEqual(user1_clinics.first().id, user2_clinics.first().id)
