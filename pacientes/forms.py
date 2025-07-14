from django import forms
from .models import Paciente


from django import forms
from .models import Paciente
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class PacienteCadastroFormulario(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Cadastrar Paciente", css_class="btn btn-primary"))

        # Apply form-control to all fields by default
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    class Meta:
        model = Paciente
        fields = ["nome_paciente", "nome_mae", "cpf_paciente"]
