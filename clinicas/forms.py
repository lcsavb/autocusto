from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db import models
from .models import Clinica

class ClinicaFormulario(ModelForm):
    class Meta:
        model = Clinica
        fields = ['cns_clinica', 'nome_clinica','logradouro',
                  'logradouro_num',  
                  'cidade', 'bairro', 'cep', 'telefone_clinica'
        ]
        labels = {'cns_clinica': _('Número CNS'),
                  'nome_clinica': _('Nome'),
                  'logradouro_num': _('Número'),
                  'cep': _('CEP'),
                  'telefone_clinica': _('Telefone')  
        }
        localizated_fields = '__all__'
