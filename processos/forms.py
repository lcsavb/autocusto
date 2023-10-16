
from django import forms
from django.db import transaction
from datetime import datetime
from pacientes.models import Paciente
from processos.models import Processo, Protocolo, Doenca
from clinicas.models import Clinica, Emissor
from autocusto.validation import isCpfValid
from .dados import gerar_dados_edicao_parcial, associar_med, gerar_prescricao, gerar_dados_paciente, gerar_dados_processo, registrar_db, preparar_modelo, checar_paciente_existe
from .seletor import seletor_campos

def mostrar_med(mostrar, *args):
    dic = {'med2_mostrar': 'd-none', 'med3_mostrar': 'd-none', 'med4_mostrar': 'd-none'}
    if mostrar:
        process = args[0]
        n = 1
        for med in process.medicamentos.all():
            dic[f'med{n}_mostrar'] = ''
            n = (n + 1)
    return dic

def ajustar_campos_condicionais(dados_paciente):
    ' Checa se paciente é incapaz e o responsável pelo preenchimento; mostra\n    os campos condicionais de acordo com a necessidade '
    dic = {'responsavel_mostrar': 'd-none', 'campo_18_mostrar': 'd-none'}
    if (patient_data['email_paciente'] != ''):
        dic['campo_18_mostrar'] = ''
        patient_data['preenchido_por'] = 'medico'
    if patient_data['incapaz']:
        dic['responsavel_mostrar'] = ''
    return (dic, patient_data)

class PreProcesso(forms.Form):
    patient_cpf = forms.CharField(required=True, label='', max_length=14)
    icd = forms.CharField(required=True, label='')

    def clean_cid(self):
        icd = self.cleaned_data['cid'].upper()
        diseases = Doenca.objects.all()
        icds_list = []
        for disease in diseases:
            icds_list.append(disease.cid)
        if (not (icd in icds_list)):
            raise forms.ValidationError(f'CID "{icd}" incorreto!')
        return icd

    def clean_cpf_paciente(self):
        patient_cpf = self.cleaned_data['cpf_paciente']
        if (not isCpfValid(patient_cpf)):
            raise forms.ValidationError(f'CPF {patient_cpf} inválido!')
        return patient_cpf

class NovoProcesso(forms.Form):

    def __init__(self, escolhas, medicamentos, *args, **kwargs):
        super(NovoProcesso, self).__init__(*args, **kwargs)
        self.fields['clinicas'].choices = choices
        self.fields['id_med1'].choices = medications
        self.fields['id_med2'].choices = medications
        self.fields['id_med3'].choices = medications
        self.fields['id_med4'].choices = medications
        self.request = kwargs.pop('request', None)
    patient_cpf = forms.CharField(required=True, label='CPF do paciente', max_length=14, widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': 14}))
    clinics = forms.ChoiceField(widget=forms.Select(attrs={'class': 'custom-select'}), choices=[], label='Selecione a clínica')
    patient_name = forms.CharField(required=True, label='Nome do paciente')
    mother_name = forms.CharField(required=True, label='Nome da mãe')
    weight = forms.IntegerField(required=True, label='Peso (kg)')
    height = forms.IntegerField(required=True, label='Altura (centímetros)')
    patient_address = forms.CharField(required=True, label='Endereço (com complemento)')
    incapable = forms.ChoiceField(choices=((True, 'Sim'), (False, 'Não')), label='É incapaz?', initial=False, widget=forms.Select(attrs={'class': 'custom-select'}))
    responsible_name = forms.CharField(label='Nome do responsável', required=False, widget=forms.TextInput(attrs={'class': 'cond-incapaz'}))
    REPEAT_CHOICES = [(True, 'Sim'), (False, 'Não')]
    id_med1 = forms.ChoiceField(widget=forms.Select(attrs={'class': 'custom-select'}), choices=[], label='Nome')
    id_med2 = forms.ChoiceField(widget=forms.Select(attrs={'class': 'custom-select'}), choices=[], label='Nome')
    id_med3 = forms.ChoiceField(widget=forms.Select(attrs={'class': 'custom-select'}), choices=[], label='Nome')
    id_med4 = forms.ChoiceField(widget=forms.Select(attrs={'class': 'custom-select'}), choices=[], label='Nome')
    med1_route_administration = forms.CharField(required=True, label='Via administração')
    med1_posology_month1 = forms.CharField(required=True, label='Posologia')
    med1_posology_month2 = forms.CharField(required=True, label='Posologia')
    med1_posology_month3 = forms.CharField(required=True, label='Posologia')
    med1_posology_month4 = forms.CharField(required=True, label='Posologia')
    med1_posology_month5 = forms.CharField(required=True, label='Posologia')
    med1_posology_month6 = forms.CharField(required=True, label='Posologia')
    med2_posology_month1 = forms.CharField(required=False, label='Posologia')
    med2_posology_month2 = forms.CharField(required=False, label='Posologia')
    med2_posology_month3 = forms.CharField(required=False, label='Posologia')
    med2_posology_month4 = forms.CharField(required=False, label='Posologia')
    med2_posology_month5 = forms.CharField(required=False, label='Posologia')
    med2_posology_month6 = forms.CharField(required=False, label='Posologia')
    med3_posology_month1 = forms.CharField(required=False, label='Posologia')
    med3_posology_month2 = forms.CharField(required=False, label='Posologia')
    med3_posology_month3 = forms.CharField(required=False, label='Posologia')
    med3_posology_month4 = forms.CharField(required=False, label='Posologia')
    med3_posology_month5 = forms.CharField(required=False, label='Posologia')
    med3_posology_month6 = forms.CharField(required=False, label='Posologia')
    med4_posology_month1 = forms.CharField(required=False, label='Posologia')
    med4_posology_month2 = forms.CharField(required=False, label='Posologia')
    med4_posology_month3 = forms.CharField(required=False, label='Posologia')
    med4_posology_month4 = forms.CharField(required=False, label='Posologia')
    med4_posology_month5 = forms.CharField(required=False, label='Posologia')
    med4_posology_month6 = forms.CharField(required=False, label='Posologia')
    qty_med1_month1 = forms.CharField(required=True, label='Qtde. 1 mês')
    qty_med1_month2 = forms.CharField(required=True, label='Qtde. 2 mês')
    qty_med1_month3 = forms.CharField(required=True, label='Qtde. 3 mês')
    qty_med1_month4 = forms.CharField(required=True, label='Qtde. 4 mês')
    qty_med1_month5 = forms.CharField(required=True, label='Qtde. 5 mês')
    qty_med1_month6 = forms.CharField(required=True, label='Qtde. 6 mês')
    qty_med1_month1 = forms.CharField(required=False, label='Qtde. 1 mês')
    qty_med2_month2 = forms.CharField(required=False, label='Qtde. 2 mês')
    qty_med2_month3 = forms.CharField(required=False, label='Qtde. 3 mês')
    qty_med2_month4 = forms.CharField(required=False, label='Qtde. 4 mês')
    qty_med2_month5 = forms.CharField(required=False, label='Qtde. 5 mês')
    qty_med2_month6 = forms.CharField(required=False, label='Qtde. 6 mês')
    qty_med3_month1 = forms.CharField(required=False, label='Qtde. 1 mês')
    qty_med3_month2 = forms.CharField(required=False, label='Qtde. 2 mês')
    qty_med3_month3 = forms.CharField(required=False, label='Qtde. 3 mês')
    qty_med3_month4 = forms.CharField(required=False, label='Qtde. 4 mês')
    qty_med3_month5 = forms.CharField(required=False, label='Qtde. 5 mês')
    qty_med3_month6 = forms.CharField(required=False, label='Qtde. 6 mês')
    qty_med4_month1 = forms.CharField(required=False, label='Qtde. 1 mês')
    qty_med4_month2 = forms.CharField(required=False, label='Qtde. 2 mês')
    qty_med4_month3 = forms.CharField(required=False, label='Qtde. 3 mês')
    qty_med4_month4 = forms.CharField(required=False, label='Qtde. 4 mês')
    qty_med4_month5 = forms.CharField(required=False, label='Qtde. 5 mês')
    qty_med4_month6 = forms.CharField(required=False, label='Qtde. 6 mês')
    med1_repeat_posology = forms.ChoiceField(required=True, initial=True, choices=REPEAT_CHOICES, label='Repetir posologia?', widget=forms.Select(attrs={'class': 'custom-select'}))
    med2_repeat_posology = forms.ChoiceField(required=True, initial=True, choices=REPEAT_CHOICES, label='Repetir posologia?', widget=forms.Select(attrs={'class': 'custom-select'}))
    med3_repeat_posology = forms.ChoiceField(required=True, initial=True, choices=REPEAT_CHOICES, label='Repetir posologia?', widget=forms.Select(attrs={'class': 'custom-select'}))
    med4_repeat_posology = forms.ChoiceField(required=True, initial=True, choices=REPEAT_CHOICES, label='Repetir posologia?', widget=forms.Select(attrs={'class': 'custom-select'}))
    consent = forms.ChoiceField(initial={False}, label='Protocolo 1ª vez: ', choices=[(False, 'Não'), (True, 'Sim')], widget=forms.Select(attrs={'class': 'custom-select'}))
    icd = forms.CharField(required=True, label='CID', widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': 5}))
    diagnosis = forms.CharField(required=True, label='Diagnóstico', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    anamnesis = forms.CharField(required=True, label='Anamnese')
    filled_by = forms.ChoiceField(initial={'paciente'}, choices=[('paciente', 'Paciente'), ('mae', 'Mãe'), ('responsavel', 'Responsável'), ('medico', 'Médico')], widget=forms.Select(attrs={'class': 'custom-select'}))
    ethnicity = forms.ChoiceField(label='Etnia', required=False, choices=[('etnia_branca', 'Branca'), ('etnia_parda', 'Parda'), ('etnia_amarela', 'Amarela'), ('etnia_indigena', 'Indígena'), ('etnia_si', 'Sem informação')], widget=forms.Select(attrs={'class': 'custom-select cond-campo-18'}))
    patient_email = forms.EmailField(required=False, label='E-Mail', widget=forms.TextInput(attrs={'class': 'cond-campo-18'}))
    patient_phone1 = forms.CharField(required=False, label='Tel. residencial', widget=forms.TextInput(attrs={'class': 'cond-campo-18'}))
    telefone2_paciente = forms.CharField(required=False, label='Celular', widget=forms.TextInput(attrs={'class': 'cond-campo-18'}))
    treated = forms.ChoiceField(choices=((True, 'Sim'), (False, 'Não')), label='Fez tratamento prévio?', initial=False, widget=forms.Select(attrs={'class': 'custom-select'}))
    previous_treatments = forms.CharField(label='Descrição dos tratamentos prévios', required=False, widget=forms.TextInput(attrs={'class': 'cond-trat'}))
    data_1 = forms.DateField(required=True, label='Data', widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    report = forms.CharField(label='Relatório', required=False, widget=forms.Textarea(attrs={'class': 'relatorio', 'rows': '6', 'width': '100%'}))
    issue_report = forms.ChoiceField(initial={False}, label='Emissão de relatório: ', choices=[(False, 'Não'), (True, 'Sim')], widget=forms.Select(attrs={'class': 'custom-select emitir-relatorio'}))
    issue_exams = forms.ChoiceField(initial={False}, label='Emissão de exames: ', choices=[(False, 'Não'), (True, 'Sim')], widget=forms.Select(attrs={'class': 'custom-select'}))
    exams = forms.CharField(label='Exames', required=False, widget=forms.Textarea(attrs={'class': 'exames', 'rows': '6'}))

    @transaction.atomic
    def save(self, usuario, medico, meds_ids):
        data = self.cleaned_data
        clinic_id = data['clinicas']
        disease = Doenca.objects.get(cid=data['cid'])
        patient_cpf = data['cpf_paciente']
        emissor = Emissor.objects.get(medico=medico, clinica_id=clinic_id)
        patient_exists = checar_paciente_existe(patient_cpf)
        process_id = registrar_db(data, meds_ids, disease, emissor, usuario, paciente_existe=patient_exists)
        return process_id

class RenovarProcesso(NovoProcesso):
    complete_edition = forms.ChoiceField(required=True, initial={False}, choices=[(False, 'Não'), (True, 'Sim')], widget=forms.Select(attrs={'class': 'custom-select'}))

    @transaction.atomic
    def save(self, usuario, medico, processo_id, meds_ids):
        data = self.cleaned_data
        complete_edition = data['edicao_completa']
        if (complete_edition == 'True'):
            patient_cpf = data['cpf_paciente']
            patient_exists = checar_paciente_existe(patient_cpf)
            clinic_id = data['clinicas']
            disease = Doenca.objects.get(cid=data['cid'])
            emissor = Emissor.objects.get(medico=medico, clinica_id=clinic_id)
            registrar_db(data, meds_ids, disease, emissor, usuario, paciente_existe=patient_exists, cid=data['cid'])
        else:
            (dados_modificados, campos_modificados) = gerar_dados_edicao_parcial(data, process_id)
            process = preparar_modelo(Processo, **dados_modificados)
            process.save(update_fields=campos_modificados)
            associar_med(Processo.objects.get(id=process_id), meds_ids)

def extrair_campos_condicionais(formulario):
    conditional_fields = []
    for campo in form:
        if (campo.name[0:4] == 'opt_'):
            conditional_fields.append(campo)
    return conditional_fields

def fabricar_formulario(cid, renovar):
    if renovar:
        base_model = RenovarProcesso
    else:
        base_model = NovoProcesso
    protocol = Protocolo.objects.get(doenca__cid=icd)
    fields = seletor_campos(protocol)
    return type('SuperForm', (base_model,), fields)
