from django.db import models
from django.conf import settings


# Patient
class Paciente(models.Model):
    """
    Patient model storing patient information for medical prescriptions.
    
    Security: Patients are linked to specific doctors through the usuarios (users)
    ManyToManyField, ensuring data access control and patient privacy.
    
    Data Privacy: Contains sensitive personal health information (PHI) including
    CPF (Brazilian tax ID), CNS (national health card), and medical data.
    """
    # patient_name
    nome_paciente = models.CharField(max_length=100)
    # age
    idade = models.CharField(max_length=100)
    # gender
    sexo = models.CharField(max_length=100)
    # mothers_name
    nome_mae = models.CharField(max_length=100)
    # incapable (legally incapacitated, requiring guardian consent)
    incapaz = models.BooleanField()
    # responsible_name (guardian name for incapacitated patients)
    nome_responsavel = models.CharField(max_length=100)
    # id_number (Brazilian RG - state ID document)
    rg = models.CharField(max_length=100)
    # weight
    peso = models.CharField(max_length=100)
    # height
    altura = models.CharField(max_length=100, default="1,70m")
    # ethnicity_choice (patient's self-declared ethnicity choice)
    escolha_etnia = models.CharField(max_length=100)
    # patient_cpf (Brazilian social security number - unique identifier)
    cpf_paciente = models.CharField(unique=True, max_length=14)
    # patient_cns (Brazilian national health card number)
    cns_paciente = models.CharField(max_length=100)
    # patient_email
    email_paciente = models.EmailField(null=True)
    # patient_city
    cidade_paciente = models.CharField(max_length=100)
    # patient_address
    end_paciente = models.CharField(max_length=100)
    # patient_zip_code
    cep_paciente = models.CharField(max_length=100)
    # patient_phone1
    telefone1_paciente = models.CharField(max_length=100)
    # patient_phone2
    telefone2_paciente = models.CharField(max_length=100)
    # ethnicity (final ethnicity classification)
    etnia = models.CharField(max_length=100)
    # users (doctors who have access to this patient's data)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="pacientes"
    )

    def __str__(self):
        return f"{self.nome_paciente}"
