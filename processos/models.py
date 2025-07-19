from django.db import models
from django.conf import settings
from django.db.models import JSONField
from medicos.models import Medico
from pacientes.models import Paciente
from clinicas.models import Clinica, Emissor


# Medication
class Medicamento(models.Model):
    """Medication model storing approved medications for medical protocols"""
    # name
    nome = models.CharField(max_length=600)
    # dosage
    dosagem = models.CharField(max_length=100, blank=True)
    # presentation (tablet, capsule, injection, etc.)
    apres = models.CharField(max_length=600, blank=True)

    def __str__(self):
        return f"{self.nome} {self.dosagem} - {self.apres}"


# Protocol
class Protocolo(models.Model):
    """Medical protocol defining treatment guidelines for specific diseases"""
    # name
    nome = models.CharField(max_length=600)
    # file (PDF protocol document path)
    arquivo = models.CharField(max_length=600)
    # medications (approved medications for this protocol)
    medicamentos = models.ManyToManyField(Medicamento)
    # conditional_data (JSON storing protocol-specific form fields and validation rules)
    dados_condicionais = JSONField(null=True)

    def __str__(self):
        return f"{self.nome}"


# Disease
class Doenca(models.Model):
    """Disease model linking CID codes to medical protocols"""
    # CID code (International Classification of Diseases)
    cid = models.CharField(max_length=6, unique=True)
    # name
    nome = models.CharField(max_length=500)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, null=True, related_name="doenca"
    )

    def __str__(self):
        return f"{self.cid}"


# Process
class Processo(models.Model):
    """
    Medical process model representing a complete prescription workflow.
    
    This is the core model that ties together all entities in the prescription system:
    patient, doctor, clinic, disease, medications, and treatment history.
    
    Security: Each process is tied to a specific user (doctor) ensuring data isolation.
    Business Logic: The unique_together constraint prevents duplicate processes for
    the same user-patient-disease combination, enforcing business rules.
    """
    # anamnesis (patient history and examination notes)
    anamnese = models.TextField(max_length=600)
    # disease
    doenca = models.ForeignKey(Doenca, on_delete=models.CASCADE, null=True)
    # medications
    medicamentos = models.ManyToManyField(Medicamento)
    # prescription (JSON storing detailed medication dosages and schedules)
    prescricao = JSONField()
    # treated (whether patient was previously treated for this condition)
    tratou = models.BooleanField(default=False)
    # previous_treatments
    tratamentos_previos = models.TextField(max_length=600)
    data1 = models.DateField(null=True)
    # filled_by (who filled the form: Patient, Mother, Guardian, Doctor)
    preenchido_por = models.CharField(
        choices=(
            ("P", "Paciente"),
            ("M", "Mãe"),
            ("R", "Responsável"),
            ("M", "Médico"),
        ),
        max_length=128,
    )
    # conditional_data (protocol-specific data based on disease requirements)
    dados_condicionais = JSONField()
    # patient
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="processos"
    )
    # doctor
    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name="processos"
    )
    # clinic
    clinica = models.ForeignKey(
        Clinica, on_delete=models.CASCADE, related_name="processos"
    )
    # issuer (doctor-clinic combination for this prescription)
    emissor = models.ForeignKey(
        Emissor, on_delete=models.CASCADE, related_name="processos"
    )
    # user (the authenticated user who created this process - usually the doctor)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="processos"
    )

    class Meta:
        unique_together = ['usuario', 'paciente', 'doenca']

    def __str__(self):
        return f"{self.doenca}"
