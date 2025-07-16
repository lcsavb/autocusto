from django.db import models
from django.conf import settings
from django.db.models import JSONField
from medicos.models import Medico
from pacientes.models import Paciente
from clinicas.models import Clinica, Emissor


class Medicamento(models.Model):
    nome = models.CharField(max_length=600)
    dosagem = models.CharField(max_length=100, blank=True)
    apres = models.CharField(max_length=600, blank=True)

    def __str__(self):
        return f"{self.nome} {self.dosagem} - {self.apres}"


class Protocolo(models.Model):
    nome = models.CharField(max_length=600)
    arquivo = models.CharField(max_length=600)
    medicamentos = models.ManyToManyField(Medicamento)
    dados_condicionais = JSONField(null=True)

    def __str__(self):
        return f"{self.nome}"


class Doenca(models.Model):
    cid = models.CharField(max_length=6, unique=True)
    nome = models.CharField(max_length=500)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, null=True, related_name="doenca"
    )

    def __str__(self):
        return f"{self.cid}"


class Processo(models.Model):
    anamnese = models.TextField(max_length=600)
    doenca = models.ForeignKey(Doenca, on_delete=models.CASCADE, null=True)
    medicamentos = models.ManyToManyField(Medicamento)
    prescricao = JSONField()
    tratou = models.BooleanField(default=False)
    tratamentos_previos = models.TextField(max_length=600)
    data1 = models.DateField(null=True)
    preenchido_por = models.CharField(
        choices=(
            ("P", "Paciente"),
            ("M", "Mãe"),
            ("R", "Responsável"),
            ("M", "Médico"),
        ),
        max_length=128,
    )
    dados_condicionais = JSONField()
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="processos"
    )
    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name="processos"
    )
    clinica = models.ForeignKey(
        Clinica, on_delete=models.CASCADE, related_name="processos"
    )
    emissor = models.ForeignKey(
        Emissor, on_delete=models.CASCADE, related_name="processos"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="processos"
    )

    class Meta:
        unique_together = ['usuario', 'paciente', 'doenca']

    def __str__(self):
        return f"{self.doenca}"
