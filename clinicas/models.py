from django.db import models
from medicos.models import Medico
from pacientes.models import Paciente
from django.conf import settings


class Clinica(models.Model):
    # English: clinic_name
    nome_clinica = models.CharField(max_length=200)
    # English: clinic_cns
    cns_clinica = models.CharField(max_length=7)
    # English: street_address
    logradouro = models.CharField(max_length=200)
    # English: street_number
    logradouro_num = models.CharField(max_length=6)
    # complemento = models.CharField(max_length=20)
    # English: city
    cidade = models.CharField(max_length=30)
    # English: neighborhood
    bairro = models.CharField(max_length=30)
    # English: zip_code
    cep = models.CharField(max_length=9)
    # English: clinic_phone
    telefone_clinica = models.CharField(max_length=15)
    # English: doctors
    medicos = models.ManyToManyField(Medico, through="Emissor", related_name="clinicas")
    # English: users
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="ClinicaUsuario", related_name="clinicas"
    )

    def __str__(self):
        return f"{self.nome_clinica}"


class Emissor(models.Model):
    # English: doctor
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    # English: clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    # English: patients
    pacientes = models.ManyToManyField(
        Paciente,
        through="processos.Processo",
        through_fields=("emissor", "paciente"),
        related_name="emissores",
    )

    def __str__(self):
        return (
            f"Emitido pela clínica: {self.clinica} e pelo médico com CRM: {self.medico}"
        )


class ClinicaUsuario(models.Model):
    # DUVIDA - AQUI DEVE SER SET NULL?
    # English: user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # English: clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Clínica: {self.clinica} e Usuário {self.usuario}"
