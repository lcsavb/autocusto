"""
Validation Forms - Simple forms for validation and quick operations

This module contains straightforward forms focused on specific validation tasks:
- PreProcesso: CPF and CID validation for process initiation
- RenovacaoRapidaForm: Quick renewal validation
"""

from django import forms
from processos.models import Doenca
from autocusto.validation import isCpfValid
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class PreProcesso(forms.Form):
    """
    Pre-process validation form for CPF and CID validation.
    
    This form validates the initial data needed to start a prescription process:
    - Patient CPF (with validation)
    - Disease CID code (must exist in database)
    """
    cpf_paciente = forms.CharField(
        required=True, 
        label="", 
        max_length=14,
        error_messages={'required': 'Por favor, insira o CPF do paciente.'}
    )
    cid = forms.CharField(
        required=True, 
        label="",
        error_messages={'required': 'Por favor, insira o CID da doença.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False  # Don't show inline error messages
        self.helper.error_text_inline = False  # Don't show error text but keep visual indicators
        self.helper.layout = Layout(
            Field('cpf_paciente', css_class='form-control'),
            Field('cid', css_class='form-control'),
            Submit('submit', 'Buscar', css_class='btn btn-primary')
        )

    def clean_cid(self):
        """Validate CID exists in the disease database."""
        cid = self.cleaned_data["cid"].upper()
        from ..repositories.domain_repository import DomainRepository
        domain_repo = DomainRepository()
        doencas = domain_repo.get_all_diseases()
        lista_cids = [doenca.cid for doenca in doencas]
        
        if cid not in lista_cids:
            raise forms.ValidationError(f'CID "{cid}" incorreto!')
        return cid

    def clean_cpf_paciente(self):
        """Validate CPF format and checksum."""
        cpf_paciente = self.cleaned_data["cpf_paciente"]
        if not isCpfValid(cpf_paciente):
            raise forms.ValidationError(f"CPF {cpf_paciente} inválido!")
        return cpf_paciente


class RenovacaoRapidaForm(forms.Form):
    """
    Form for quick renewal process validation.
    
    This form handles validation for the renewal workflow, ensuring that
    all required fields are present and valid before processing.
    """
    processo_id = forms.CharField(
        required=True,
        label="ID do Processo",
        error_messages={'required': 'Selecione um processo para renovar.'}
    )
    data_1 = forms.DateField(
        required=True,
        label="Nova Data",
        widget=forms.DateInput(format="%d/%m/%Y"),
        input_formats=["%d/%m/%Y"],
        error_messages={'required': 'Data é obrigatória.'}
    )
    edicao = forms.BooleanField(
        required=False,
        label="Edição completa"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False
        self.helper.error_text_inline = False
    
    def clean_processo_id(self):
        """Validate process ID is not empty and is a valid integer."""
        processo_id = self.cleaned_data.get("processo_id")
        
        if not processo_id or not processo_id.strip():
            raise forms.ValidationError("Selecione um processo para renovar")
        
        try:
            # Ensure it's a valid integer
            int(processo_id.strip())
            return processo_id.strip()
        except ValueError:
            raise forms.ValidationError("ID do processo inválido")
    
    def clean_data_1(self):
        """Validate renewal date."""
        nova_data = self.cleaned_data.get("data_1")
        
        if not nova_data:
            raise forms.ValidationError("Data é obrigatória")
        
        # Could add additional date validation here (e.g., not in the past)
        return nova_data