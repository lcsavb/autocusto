from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Clinica
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Fieldset


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
