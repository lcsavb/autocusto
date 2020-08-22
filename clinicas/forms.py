from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Clinica
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Fieldset


class ClinicaFormulario(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClinicaFormulario, self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'clinica-cadastro'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'POST'
        self.helper.form_action = ''
        self.helper.add_input(Submit('submit', 'Cadastrar'))
        self.helper.layout=Layout(
            Row(
                Column('nome_clinica',css_class='form-group col-6 mb-0'),
                Column('cns_clinica',css_class='form-group col-2 mb-0'),
                Column(Field('telefone_clinica',id='telefone'),css_class='form-group col-4 mb-0'),
                css_class='form-row'
            ),
            Fieldset(
                'Localização',
                Row(
                    Column('cidade',css_class='form-group col-6 mb-0'),
                    Column('bairro',css_class='form-group col-6 mb-0')
                ),
                Row(
                    Column(Field('cep',id='cep'),css_class='form-group col-2 mb-0'),
                    Column('logradouro',css_class='form-group col-8 mb-0'),
                    Column('logradouro_num',css_class='form-group col-2 mb-0')
                )
            )
        )

    class Meta:
        model = Clinica
        fields = ['cns_clinica', 'nome_clinica','logradouro',
                  'logradouro_num',  
                  'cidade', 'bairro', 'cep', 'telefone_clinica'
        ]
        labels = {'cns_clinica': _('CNS'),
                  'nome_clinica': _('Nome'),
                  'logradouro_num': _('Número'),
                  'cep': _('CEP'),
                  'telefone_clinica': _('Telefone')  
        }
        localizated_fields = '__all__'
