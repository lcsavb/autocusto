
from django.db import models
from medicos.models import Medico
from pacientes.models import Paciente
from django.conf import settings

class Clinica(models.Model):
    clinic_name = models.CharField(max_length=200)
    clinic_cns = models.CharField(max_length=7)
    street = models.CharField(max_length=200)
    address_number = models.CharField(max_length=6)
    city = models.CharField(max_length=30)
    neighborhood = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=9)
    clinic_phone = models.CharField(max_length=13)
    doctors = models.ManyToManyField(Medico, through='Emissor', related_name='clinicas')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ClinicaUsuario', related_name='clinicas')

    def __str__(self):
        return f'{self.nome_clinica}'

class Emissor(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    patients = models.ManyToManyField(Paciente, through='processos.Processo', through_fields=('emissor', 'paciente'), related_name='emissores')

    def __str__(self):
        return f'Emitido pela clínica: {self.clinica} e pelo médico com CRM: {self.medico}'

class ClinicaUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    clinic = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Clínica: {self.clinica} e Usuário {self.usuario}'
