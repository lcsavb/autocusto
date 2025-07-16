from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Clinica
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Fieldset
import re


class ClinicaFormulario(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClinicaFormulario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "clinica-cadastro"
        self.helper.form_method = "POST"
        self.helper.form_action = ""
        self.helper.attrs = {'novalidate': True}
        self.helper.add_input(Submit("submit", "Cadastrar", css_class="btn btn-primary float-right"))
        self.helper.layout = Layout(
            Row(
                Column(Field("nome_clinica", css_class="form-control"), css_class="form-group col-6 mb-4"),
                Column(Field("cns_clinica", css_class="form-control"), css_class="form-group col-2 mb-4"),
                Column(
                    Field("telefone_clinica", id="telefone", css_class="form-control"),
                    css_class="form-group col-4 mb-4",
                ),
                css_class="form-row mb-3",
            ),
            Row(
                Column(Field("cep", id="cep", css_class="form-control"), css_class="form-group col-3 mb-4"),
                Column(Field("cidade", css_class="form-control"), css_class="form-group col-4 mb-4"),
                Column(Field("bairro", css_class="form-control"), css_class="form-group col-5 mb-4"),
                css_class="form-row mb-3",
            ),
            Row(
                Column(Field("logradouro", css_class="form-control"), css_class="form-group col-8 mb-4"),
                Column(Field("logradouro_num", css_class="form-control"), css_class="form-group col-4 mb-4"),
                css_class="form-row mb-3",
            ),
        )

    def clean_telefone_clinica(self):
        telefone = self.cleaned_data.get('telefone_clinica')
        
        if not telefone:
            return telefone
            
        # Remove formatting to check actual digits
        digits_only = re.sub(r'\D', '', telefone)
        
        # Check if phone number has valid length (10-11 digits)
        if len(digits_only) < 10 or len(digits_only) > 11:
            raise ValidationError(
                _('Telefone deve conter entre 10 e 11 dígitos. Exemplos: (11) 1234-5678 ou (11) 91234-5678')
            )
        
        # Check if formatted phone exceeds database field length
        if len(telefone) > 15:
            raise ValidationError(
                _('Telefone muito longo. Use o formato (11) 1234-5678 para fixo ou (11) 91234-5678 para celular')
            )
            
        # Validate Brazilian phone number format (accept both - and . separators)
        phone_pattern = r'^\(\d{2}\) \d{4,5}[-\.]\d{4}$'
        if not re.match(phone_pattern, telefone):
            raise ValidationError(
                _('Formato de telefone inválido. Use: (11) 1234-5678 para fixo ou (11) 91234-5678 para celular')
            )
        
        return telefone

    def clean_cns_clinica(self):
        cns = self.cleaned_data.get('cns_clinica')
        
        if not cns:
            return cns
            
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', cns)
        
        # Check CNS length (must be 7 digits)
        if len(digits_only) != 7:
            raise ValidationError(
                _('CNS deve conter exatamente 7 dígitos')
            )
        
        return digits_only

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        
        if not cep:
            return cep
            
        # Validate CEP format (either 12345-678 or 12345678)
        cep_pattern = r'^\d{5}-?\d{3}$'
        if not re.match(cep_pattern, cep):
            raise ValidationError(
                _('CEP deve estar no formato 12345-678')
            )
        
        return cep

    class Meta:
        model = Clinica
        fields = [
            "cns_clinica",
            "nome_clinica",
            "logradouro",
            "logradouro_num",
            "cidade",
            "bairro",
            "cep",
            "telefone_clinica",
        ]
        labels = {
            "cns_clinica": _("CNS"),
            "nome_clinica": _("Nome"),
            "logradouro_num": _("Número"),
            "cep": _("CEP"),
            "telefone_clinica": _("Telefone"),
        }
        localizated_fields = "__all__"
