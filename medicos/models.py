from django.db import models
from django.conf import settings


# Doctor
class Medico(models.Model):
    """
    Doctor model storing medical professional information.
    
    Business Logic: Each doctor has unique CRM (medical license) and CNS numbers.
    The relationship with users allows multiple user accounts per doctor and
    multiple doctors per user account (for complex medical practices).
    """
    # doctor_name
    nome_medico = models.CharField(max_length=200)
    # doctor_crm (Brazilian medical license number)
    crm_medico = models.CharField(max_length=10, unique=True)
    # doctor_cns (Brazilian national health system registration)
    cns_medico = models.CharField(max_length=15, unique=True)
    # users (user accounts linked to this doctor)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MedicoUsuario", related_name="medicos"
    )

    def __str__(self):
        return self.crm_medico


# DoctorUser (intermediate model for doctor-user relationship)
class MedicoUsuario(models.Model):
    """
    Intermediate model for Doctor-User many-to-many relationship.
    
    Design Note: Uses SET_NULL to preserve data integrity if either
    doctor or user records are deleted, maintaining audit trail.
    """
    # QUESTION - SHOULD THIS BE SET_NULL?
    # user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # doctor
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # Doctor: {doctor} and User {user}
        return f"Médico: {self.medico} e Usuário {self.usuario}"
