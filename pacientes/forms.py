from django import forms
from django.core.exceptions import ValidationError
from .models import Paciente
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


# English: PatientRegistrationForm
class PacienteCadastroFormulario(forms.ModelForm):
    """Form for registering new patients.

    This form is a Django ModelForm, which simplifies the process of creating
    forms that interact directly with a model. It uses `crispy_forms` for
    rendering, providing a cleaner and more customizable form layout.

    Critique:
    - The form explicitly sets `form_show_errors` and `error_text_inline` to
      `False`. While this might be intended for custom error display, it can
      make debugging form validation issues harder if not handled properly in
      the templates.
    - The loop to add `form-control` class to all fields is a common pattern
      with `crispy_forms`, but it could be more concisely handled by setting
      a default template pack or using a custom layout in `FormHelper`.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # English: helper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False  # Don't show inline error messages
        self.helper.error_text_inline = False  # Don't show error text but keep visual indicators
        self.helper.add_input(Submit("submit", "Cadastrar Paciente", css_class="btn btn-primary"))

        # Apply form-control to all fields by default
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def validate_unique(self):
        """Skip CPF uniqueness validation - handled by versioning system in model layer"""
        exclude = self._get_validation_exclusions()
        if 'cpf_paciente' not in exclude:
            exclude.add('cpf_paciente')  # Don't validate CPF uniqueness at form level
        try:
            self.instance.validate_unique(exclude)
        except ValidationError as e:
            self._update_errors(e)

    class Meta:
        # English: model
        model = Paciente
        # English: fields
        fields = ["nome_paciente", "nome_mae", "cpf_paciente"]
