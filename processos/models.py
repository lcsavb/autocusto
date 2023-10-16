
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from medicos.models import Medico
from pacientes.models import Paciente
from clinicas.models import Clinica, Emissor

class Medicamento(models.Model):
    name = models.CharField(max_length=600)
    dosage = models.CharField(max_length=100, blank=True)
    drug_formulation = models.CharField(max_length=600, blank=True)

    def __str__(self):
        return f'{self.nome} {self.dosagem} - {self.apres}'

class Protocolo(models.Model):
    name = models.CharField(max_length=600)
    file = models.CharField(max_length=600)
    medications = models.ManyToManyField(Medicamento)
    conditional_data = JSONField(null=True)

    def __str__(self):
        return f'{self.nome}'

class Doenca(models.Model):
    icd = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=500)
    protocol = models.ForeignKey(Protocolo, on_delete=models.CASCADE, null=True, related_name='doenca')

    def __str__(self):
        return f'{self.cid}'

class Processo(models.Model):
    anamnesis = models.TextField(max_length=600)
    disease = models.ForeignKey(Doenca, on_delete=models.CASCADE, null=True)
    medications = models.ManyToManyField(Medicamento)
    prescription = JSONField()
    treated = models.BooleanField(default=False)
    previous_treatments = models.TextField(max_length=600)
    data1 = models.DateField(null=True)
    filled_by = models.CharField(choices=(('P', 'Paciente'), ('M', 'Mãe'), ('R', 'Responsável'), ('M', 'Médico')), max_length=128)
    conditional_data = JSONField()
    patient = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='processos')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='processos')
    clinic = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='processos')
    emissor = models.ForeignKey(Emissor, on_delete=models.CASCADE, related_name='processos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='processos')

    def __str__(self):
        return f'{self.doenca}'
