from django import forms
from django.db import transaction
from processos.models import Processo, Protocolo, Doenca
from clinicas.models import Emissor
from autocusto.validation import isCpfValid
from .dados import (
    gerar_dados_edicao_parcial,
    associar_med,
    registrar_db,
    preparar_modelo,
    checar_paciente_existe,
)
from .seletor import seletor_campos


def mostrar_med(mostrar, *args):
    dic = {
        "med2_mostrar": "d-none",
        "med3_mostrar": "d-none",
        "med4_mostrar": "d-none",
    }
    if mostrar:
        processo = args[0]
        n = 1
        for med in processo.medicamentos.all():
            dic[f"med{n}_mostrar"] = ""
            n = n + 1
    return dic


def ajustar_campos_condicionais(dados_paciente):
    """Checa se paciente é incapaz e o responsável pelo preenchimento; mostra
    os campos condicionais de acordo com a necessidade"""
    dic = {"responsavel_mostrar": "d-none", "campo_18_mostrar": "d-none"}
    if dados_paciente["email_paciente"] != "":
        dic["campo_18_mostrar"] = ""
        dados_paciente["preenchido_por"] = "medico"
    if dados_paciente["incapaz"]:
        dic["responsavel_mostrar"] = ""
    return dic, dados_paciente


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

# Constants for form choices
REPETIR_ESCOLHAS = [(True, "Sim"), (False, "Não")]


class PreProcesso(forms.Form):
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
        cid = self.cleaned_data["cid"].upper()
        doencas = Doenca.objects.all()
        lista_cids = []
        for doenca in doencas:
            lista_cids.append(doenca.cid)
        if cid not in lista_cids:
            raise forms.ValidationError(f'CID "{cid}" incorreto!')
        return cid

    def clean_cpf_paciente(self):
        cpf_paciente = self.cleaned_data["cpf_paciente"]
        if not isCpfValid(cpf_paciente):
            raise forms.ValidationError(f"CPF {cpf_paciente} inválido!")
        return cpf_paciente


class NovoProcesso(forms.Form):
    def __init__(self, escolhas, medicamentos, *args, **kwargs):
        super(NovoProcesso, self).__init__(*args, **kwargs)
        
        # Dynamically create medication fields to avoid repetition
        self._create_medication_fields()
        
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False  # Don't show inline error messages
        self.helper.error_text_inline = False  # Don't show error text but keep visual indicators
        self.helper.form_tag = False  # Don't wrap in form tags since we're using individual fields
        self.helper.add_input(Submit("submit", "Salvar Processo", css_class="btn btn-primary"))

        # Apply form-control to all fields by default and ensure proper error styling
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            # Ensure field supports error styling
            field.widget.attrs['data-crispy-field'] = 'true'

        self.fields["clinicas"].choices = escolhas
        for i in range(1, 5):
            self.fields[f"id_med{i}"].choices = medicamentos
        self.request = kwargs.pop("request", None)
    
    def _create_medication_fields(self):
        """Dynamically create medication-related fields to avoid repetition"""
        # Create medication selection fields
        for i in range(1, 5):
            self.fields[f"id_med{i}"] = forms.ChoiceField(
                widget=forms.Select(attrs={"class": "custom-select"}),
                choices=[],
                label="Nome",
                error_messages={'required': 'Por favor, selecione um medicamento.'}
            )
            
            # Create repetir_posologia field
            self.fields[f"med{i}_repetir_posologia"] = forms.ChoiceField(
                required=True,
                initial=True,
                choices=REPETIR_ESCOLHAS,
                label="Repetir posologia?",
                widget=forms.Select(attrs={"class": "custom-select"}),
                error_messages={'required': 'Por favor, selecione uma opção.'}
            )
            
            # Create posologia fields for each month
            for month in range(1, 7):
                is_required = (i == 1)  # Only med1 fields are required
                self.fields[f"med{i}_posologia_mes{month}"] = forms.CharField(
                    required=is_required,
                    label="Posologia",
                    error_messages={'required': 'Por favor, insira a posologia.'}
                )
                
                # Create quantity fields for each month
                self.fields[f"qtd_med{i}_mes{month}"] = forms.CharField(
                    required=is_required,
                    label=f"Qtde. {month} mês",
                    error_messages={'required': 'Por favor, insira a quantidade.'}
                )
        
        # Add the via field for med1
        self.fields["med1_via"] = forms.CharField(
            required=True,
            label="Via administração",
            error_messages={'required': 'Por favor, insira a via de administração.'}
        )

    # Dados do paciente
    cpf_paciente = forms.CharField(
        required=True,
        label="CPF do paciente",
        max_length=14,
        widget=forms.TextInput(attrs={"readonly": "readonly", "size": 14}),
        error_messages={'required': 'Por favor, insira o CPF do paciente.'}
    )
    clinicas = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "custom-select"}),
        choices=[],
        label="Selecione a clínica",
        error_messages={'required': 'Por favor, selecione uma clínica.'}
    )
    nome_paciente = forms.CharField(
        required=True, 
        label="Nome do paciente",
        error_messages={'required': 'Por favor, insira o nome do paciente.'}
    )
    nome_mae = forms.CharField(
        required=True, 
        label="Nome da mãe",
        error_messages={'required': 'Por favor, insira o nome da mãe.'}
    )
    peso = forms.IntegerField(
        required=True, 
        label="Peso (kg)",
        error_messages={'required': 'Por favor, insira o peso.'}
    )
    altura = forms.IntegerField(
        required=True, 
        label="Altura (centímetros)",
        error_messages={'required': 'Por favor, insira a altura.'}
    )
    end_paciente = forms.CharField(
        required=True, 
        label="Endereço (com complemento)",
        error_messages={'required': 'Por favor, insira o endereço.'}
    )
    incapaz = forms.ChoiceField(
        choices=((True, "Sim"), (False, "Não")),
        label="É incapaz?",
        initial=False,
        widget=forms.Select(attrs={"class": "custom-select"}),
    )
    nome_responsavel = forms.CharField(
        label="Nome do responsável",
        required=False,
        widget=forms.TextInput(attrs={"class": "cond-incapaz"}),
    )


    consentimento = forms.ChoiceField(
        initial={False},
        label="Protocolo 1ª vez: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.Select(attrs={"class": "custom-select"}),
    )

    cid = forms.CharField(
        required=True,
        label="CID",
        widget=forms.TextInput(attrs={"readonly": "readonly", "size": 5}),
        error_messages={'required': 'Por favor, insira o CID.'}
    )
    diagnostico = forms.CharField(
        required=True,
        label="Diagnóstico",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        error_messages={'required': 'Por favor, insira o diagnóstico.'}
    )
    anamnese = forms.CharField(required=True, label="Anamnese", error_messages={'required': 'Por favor, insira a anamnese.'})
    preenchido_por = forms.ChoiceField(
        initial={"paciente"},
        choices=[
            ("paciente", "Paciente"),
            ("mae", "Mãe"),
            ("responsavel", "Responsável"),
            ("medico", "Médico"),
        ],
        widget=forms.Select(attrs={"class": "custom-select"}),
    )

    etnia = forms.ChoiceField(
        label="Etnia",
        required=False,
        choices=[
            ("etnia_branca", "Branca"),
            ("etnia_parda", "Parda"),
            ("etnia_amarela", "Amarela"),
            ("etnia_indigena", "Indígena"),
            ("etnia_si", "Sem informação"),
        ],
        widget=forms.Select(attrs={"class": "custom-select cond-campo-18"}),
    )
    email_paciente = forms.EmailField(
        required=False,
        label="E-Mail",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    telefone1_paciente = forms.CharField(
        required=False,
        label="Tel. residencial",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    telefone2_paciente = forms.CharField(
        required=False,
        label="Celular",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    tratou = forms.ChoiceField(
        choices=((True, "Sim"), (False, "Não")),
        label="Fez tratamento prévio?",
        initial=False,
        widget=forms.Select(attrs={"class": "custom-select"}),
    )
    tratamentos_previos = forms.CharField(
        label="Descrição dos tratamentos prévios",
        required=False,
        widget=forms.TextInput(attrs={"class": "cond-trat"}),
    )
    data_1 = forms.DateField(
        required=True,
        label="Data",
        widget=forms.DateInput(format="%d/%m/%Y"),
        input_formats=[
            "%d/%m/%Y",
        ],
        error_messages={'required': 'Por favor, insira a data.'}
    )

    relatorio = forms.CharField(
        label="Relatório",
        required=False,
        widget=forms.Textarea(
            attrs={"class": "relatorio", "rows": "6", "width": "100%"}
        ),
    )

    emitir_relatorio = forms.ChoiceField(
        initial={False},
        label="Emissão de relatório: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.Select(attrs={"class": "custom-select emitir-relatorio"}),
    )

    emitir_exames = forms.ChoiceField(
        initial={False},
        label="Emissão de exames: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.Select(attrs={"class": "custom-select"}),
    )

    exames = forms.CharField(
        label="Exames",
        required=False,
        widget=forms.Textarea(attrs={"class": "exames", "rows": "6"}),
    )

    @transaction.atomic
    def save(self, usuario, medico, meds_ids):
        dados = self.cleaned_data
        clinica_id = dados["clinicas"]
        doenca = Doenca.objects.get(cid=dados["cid"])
        cpf_paciente = dados["cpf_paciente"]

        emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

        paciente_existe = checar_paciente_existe(cpf_paciente)

        processo_id = registrar_db(
            dados, meds_ids, doenca, emissor, usuario, paciente_existe=paciente_existe
        )

        return processo_id


class RenovarProcesso(NovoProcesso):
    edicao_completa = forms.ChoiceField(
        required=True,
        initial={False},
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.Select(attrs={"class": "custom-select"}),
        error_messages={'required': 'Por favor, selecione uma opção.'}
    )

    @transaction.atomic
    def save(self, usuario, medico, processo_id, meds_ids):
        dados = self.cleaned_data
        edicao_completa = dados["edicao_completa"]

        if edicao_completa == "True":
            cpf_paciente = dados["cpf_paciente"]
            paciente_existe = checar_paciente_existe(cpf_paciente)
            clinica_id = dados["clinicas"]
            doenca = Doenca.objects.get(cid=dados["cid"])
            emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

            registrar_db(
                dados,
                meds_ids,
                doenca,
                emissor,
                usuario,
                paciente_existe=paciente_existe,
                cid=dados["cid"],
            )
        else:
            dados_modificados, campos_modificados = gerar_dados_edicao_parcial(
                dados, processo_id
            )
            processo = preparar_modelo(Processo, **dados_modificados)
            processo.save(update_fields=campos_modificados)
            associar_med(Processo.objects.get(id=processo_id), meds_ids)


def extrair_campos_condicionais(formulario):
    campos_condicionais = []
    for campo in formulario:
        if campo.name[0:4] == "opt_":
            campos_condicionais.append(campo)
    return campos_condicionais


def fabricar_formulario(cid, renovar):
    if renovar:
        modelo_base = RenovarProcesso
    else:
        modelo_base = NovoProcesso

    protocolo = Protocolo.objects.get(doenca__cid=cid)

    campos = seletor_campos(protocolo)

    return type("SuperForm", (modelo_base,), campos)
