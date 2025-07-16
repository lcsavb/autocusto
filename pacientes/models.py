from django.db import models
from django.conf import settings


class Paciente(models.Model):
    # English: patient_name
    nome_paciente = models.CharField(max_length=100)
    # English: age
    idade = models.CharField(max_length=100)
    # English: gender
    sexo = models.CharField(max_length=100)
    # English: mothers_name
    nome_mae = models.CharField(max_length=100)
    # English: incapable
    incapaz = models.BooleanField()
    # English: responsible_name
    nome_responsavel = models.CharField(max_length=100)
    # English: id number
    rg = models.CharField(max_length=100)
    # English: weight
    peso = models.CharField(max_length=100)
    # English: height
    altura = models.CharField(max_length=100, default="1,70m")
    # English: ethnicity_choice
    escolha_etnia = models.CharField(max_length=100)
    # English: patient brazilian social security number
    cpf_paciente = models.CharField(unique=True, max_length=14)
    # English: patient_cns
    cns_paciente = models.CharField(max_length=100)
    # English: patient_email
    email_paciente = models.EmailField(null=True)
    # English: patient_city
    cidade_paciente = models.CharField(max_length=100)
    # English: patient_address
    end_paciente = models.CharField(max_length=100)
    # English: patient_zip_code
    cep_paciente = models.CharField(max_length=100)
    # English: patient_phone1
    telefone1_paciente = models.CharField(max_length=100)
    # English: patient_phone2
    telefone2_paciente = models.CharField(max_length=100)
    # English: ethnicity
    etnia = models.CharField(max_length=100)
    # English: users
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="pacientes"
    )

    def __str__(self):
        return f"{self.nome_paciente}"
