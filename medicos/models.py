from django.db import models
from django.conf import settings


class Medico(models.Model):
    # English: doctor_name
    nome_medico = models.CharField(max_length=200)
    # English: doctor_crm
    crm_medico = models.CharField(max_length=10, unique=True)
    # English: doctor_cns
    cns_medico = models.CharField(max_length=15, unique=True)
    # English: users
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MedicoUsuario", related_name="medicos"
    )

    def __str__(self):
        return self.crm_medico


class MedicoUsuario(models.Model):
    # DUVIDA - AQUI DEVE SER SET NULL?
    # English: user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # English: doctor
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Médico: {self.medico} e Usuário {self.usuario}"
