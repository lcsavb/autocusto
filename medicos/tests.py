from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Medico, MedicoUsuario


class MedicoModelTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username="user1", password="pass"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2", password="pass"
        )

    def test_create_medico(self):
        medico = Medico.objects.create(
            nome_medico="Dr. House", crm_medico="123456", cns_medico="9876543210"
        )
        self.assertEqual(medico.nome_medico, "Dr. House")
        self.assertEqual(str(medico), "123456")

    def test_crm_medico_uniqueness(self):
        Medico.objects.create(nome_medico="Dr. A", crm_medico="111", cns_medico="222")
        with self.assertRaises(Exception):
            Medico.objects.create(
                nome_medico="Dr. B", crm_medico="111", cns_medico="333"
            )

    def test_cns_medico_uniqueness(self):
        Medico.objects.create(nome_medico="Dr. A", crm_medico="111", cns_medico="222")
        with self.assertRaises(Exception):
            Medico.objects.create(
                nome_medico="Dr. B", crm_medico="112", cns_medico="222"
            )

    def test_medico_usuario_relationship(self):
        medico = Medico.objects.create(
            nome_medico="Dr. C", crm_medico="222", cns_medico="333"
        )
        mu = MedicoUsuario.objects.create(usuario=self.user1, medico=medico)
        self.assertEqual(str(mu), f"Médico: {medico} e Usuário {self.user1}")
        self.assertIn(medico, self.user1.medicos.all())

    def test_medico_usuario_set_null(self):
        medico = Medico.objects.create(
            nome_medico="Dr. D", crm_medico="333", cns_medico="444"
        )
        mu = MedicoUsuario.objects.create(usuario=self.user2, medico=medico)
        mu.usuario = None
        mu.medico = None
        mu.save()
        self.assertIsNone(mu.usuario)
        self.assertIsNone(mu.medico)
