from django.forms import ModelForm
from django import forms
from django.db import models
from .models import Clinica

class ClinicaFormulario(ModelForm):
    class Meta:
        model = Clinica
        fields = ['cns_clinica', 'nome_clinica','end_clinica',
                  'cidade', 'bairro', 'cep', 'telefone_clinica'
        ]
        
