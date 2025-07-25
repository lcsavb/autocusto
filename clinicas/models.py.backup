from django.db import models
from medicos.models import Medico
from pacientes.models import Paciente
from django.conf import settings


# Clinic
class Clinica(models.Model):
    """
    Clinic model representing medical facilities where prescriptions are issued.
    
    Business Logic: Clinics can have multiple doctors and users. The Emissor model
    creates the doctor-clinic combinations that actually issue prescriptions.
    """
    # clinic_name
    nome_clinica = models.CharField(max_length=200)
    # clinic_cns (Brazilian national health system registration for clinic)
    cns_clinica = models.CharField(max_length=7)
    # street_address
    logradouro = models.CharField(max_length=200)
    # street_number
    logradouro_num = models.CharField(max_length=6)
    # complement (address complement - currently unused)
    # complemento = models.CharField(max_length=20)
    # city
    cidade = models.CharField(max_length=30)
    # neighborhood
    bairro = models.CharField(max_length=30)
    # zip_code
    cep = models.CharField(max_length=9)
    # clinic_phone
    telefone_clinica = models.CharField(max_length=15)
    # doctors (doctors working at this clinic)
    medicos = models.ManyToManyField(Medico, through="Emissor", related_name="clinicas")
    # users (user accounts with access to this clinic)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="ClinicaUsuario", related_name="clinicas"
    )

    def __str__(self):
        return f"{self.nome_clinica}"


# Issuer (doctor-clinic combination that can issue prescriptions)
class Emissor(models.Model):
    """
    Issuer model representing a doctor-clinic combination for prescription issuance.
    
    Business Logic: This model creates the specific doctor-clinic pairs that are
    authorized to issue prescriptions. One doctor can work at multiple clinics,
    and one clinic can have multiple doctors, creating multiple issuer combinations.
    """
    # doctor
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    # clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    # patients (patients served by this doctor-clinic combination)
    pacientes = models.ManyToManyField(
        Paciente,
        through="processos.Processo",
        through_fields=("emissor", "paciente"),
        related_name="emissores",
    )

    def __str__(self):
        # Issued by clinic: {clinic} and by doctor with CRM: {doctor}
        return (
            f"Emitido pela clínica: {self.clinica} e pelo médico com CRM: {self.medico}"
        )


# ClinicUser (intermediate model for clinic-user relationship)
class ClinicaUsuario(models.Model):
    """
    Intermediate model for Clinic-User many-to-many relationship.
    
    Design Note: Uses SET_NULL to preserve data integrity if either
    clinic or user records are deleted, maintaining audit trail.
    """
    # QUESTION - SHOULD THIS BE SET_NULL?
    # user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # Clinic: {clinic} and User {user}
        return f"Clínica: {self.clinica} e Usuário {self.usuario}"
