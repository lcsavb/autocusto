from django import forms
from django.db import transaction
from datetime import datetime
from pacientes.models import Paciente
from processos.models import Processo, Protocolo, Doenca
from clinicas.models import Clinica, Emissor
from .dados import (gerar_dados_edicao_parcial,
                    associar_med,
                    gerar_prescricao,
                    gerar_dados_paciente,
                    gerar_dados_processo,
                    registrar_db,
                    preparar_modelo,
                    checar_paciente_existe)


def mostrar_med(mostrar, *args):
    dic = {'med2_mostrar': 'd-none',
           'med3_mostrar': 'd-none',
           'med4_mostrar': 'd-none',
           'med5_mostrar': 'd-none',
           }
    if mostrar:
        processo = args[0]
        n = 1
        for med in processo.medicamentos.all():
            dic[f'med{n}_mostrar'] = ''
            n = n + 1
    return dic


def ajustar_campos_condicionais(dados_paciente):
    ''' Checa se paciente é incapaz e o responsável pelo preenchimento; mostra
    os campos condicionais de acordo com a necessidade '''
    dic = {
        'responsavel_mostrar': 'd-none',
        'campo_18_mostrar': 'd-none'
    }
    if dados_paciente['email_paciente'] != '':
        dic['campo_18_mostrar'] = ''
        dados_paciente['preenchido_por'] = 'medico'
    if dados_paciente['incapaz']:
        dic['responsavel_mostrar'] = ''
    return dic, dados_paciente


class PreProcesso(forms.Form):
    cpf_paciente = forms.CharField(
        required=True, label='', max_length=14)
    cid = forms.CharField(required=True, label='')


class NovoProcesso(forms.Form):
    def __init__(self, escolhas, medicamentos, *args, **kwargs):
        super(NovoProcesso, self).__init__(*args, **kwargs)
        self.fields['clinicas'].choices = escolhas
        self.fields['id_med1'].choices = medicamentos
        self.fields['id_med2'].choices = medicamentos
        self.fields['id_med3'].choices = medicamentos
        self.fields['id_med4'].choices = medicamentos
        self.fields['id_med5'].choices = medicamentos
        self.request = kwargs.pop('request', None)

    # Dados do paciente
    cpf_paciente = forms.CharField(
        required=True, label='CPF do paciente', max_length=14)
    clinicas = forms.ChoiceField(widget=forms.Select, choices=[],
                                 label='Selecione a clínica')
    nome_paciente = forms.CharField(required=True, label='Nome do paciente')
    nome_mae = forms.CharField(required=True, label='Nome da mãe')
    peso = forms.IntegerField(required=True, label='Peso')
    altura = forms.IntegerField(required=True, label='Altura')
    end_paciente = forms.CharField(
        required=True, label='Endereço (com complemento)')
    incapaz = forms.ChoiceField(
        choices=((True, 'Sim'),
                 (False, 'Não')),
        label='Paciente é incapaz?',
        initial=False)
    nome_responsavel = forms.CharField(
        label='Nome do responsável',
        required=False)
    
    REPETIR_ESCOLHAS = [(True, 'Sim'), (False, 'Não')]

    id_med1 = forms.ChoiceField(widget=forms.Select,
        choices=[], label='Nome')
    id_med2 = forms.ChoiceField(widget=forms.Select,
        choices=[], label='Nome')
    id_med3 = forms.ChoiceField(widget=forms.Select,
        choices=[], label='Nome')
    id_med4 = forms.ChoiceField(widget=forms.Select,
        choices=[], label='Nome')
    id_med5 = forms.ChoiceField(widget=forms.Select,
        choices=[], label='Nome')

    med1_via = forms.CharField(required=True, label='Via administração')
    med1_posologia_mes1 = forms.CharField(required=True, label='Posologia')
    med1_posologia_mes2 = forms.CharField(required=False, label='Posologia')
    med1_posologia_mes3 = forms.CharField(required=False, label='Posologia')
    med2_posologia_mes1 = forms.CharField(required=False, label='Posologia')
    med2_posologia_mes2 = forms.CharField(required=False, label='Posologia')
    med2_posologia_mes3 = forms.CharField(required=False, label='Posologia')
    med3_posologia_mes1 = forms.CharField(required=False, label='Posologia')
    med3_posologia_mes2 = forms.CharField(required=False, label='Posologia')
    med3_posologia_mes3 = forms.CharField(required=False, label='Posologia')
    med4_posologia_mes1 = forms.CharField(required=False, label='Posologia')
    med4_posologia_mes2 = forms.CharField(required=False, label='Posologia')
    med4_posologia_mes3 = forms.CharField(required=False, label='Posologia')
    med5_posologia_mes1 = forms.CharField(required=False, label='Posologia')
    med5_posologia_mes2 = forms.CharField(required=False, label='Posologia')
    med5_posologia_mes3 = forms.CharField(required=False, label='Posologia')
    qtd_med1_mes1 = forms.CharField(required=True, label="Qtde. 1 mês")
    qtd_med1_mes2 = forms.CharField(required=True, label="Qtde. 2 mês")
    qtd_med1_mes3 = forms.CharField(required=True, label="Qtde. 3 mês")
    qtd_med2_mes1 = forms.CharField(required=False, label="Qtde. 1 mês")
    qtd_med2_mes2 = forms.CharField(required=False, label="Qtde. 2 mês")
    qtd_med2_mes3 = forms.CharField(required=False, label="Qtde. 3 mês")
    qtd_med3_mes1 = forms.CharField(required=False, label="Qtde. 1 mês")
    qtd_med3_mes2 = forms.CharField(required=False, label="Qtde. 2 mês")
    qtd_med3_mes3 = forms.CharField(required=False, label="Qtde. 3 mês")
    qtd_med4_mes1 = forms.CharField(required=False, label="Qtde. 1 mês")
    qtd_med4_mes2 = forms.CharField(required=False, label="Qtde. 2 mês")
    qtd_med4_mes3 = forms.CharField(required=False, label="Qtde. 3 mês")
    qtd_med5_mes1 = forms.CharField(required=False, label="Qtde. 1 mês")
    qtd_med5_mes2 = forms.CharField(required=False, label="Qtde. 2 mês")
    qtd_med5_mes3 = forms.CharField(required=False, label="Qtde. 3 mês")
    med1_repetir_posologia = forms.ChoiceField(required=True,
                                               initial=True,
                                               choices=REPETIR_ESCOLHAS,
                                               label='Repetir posologia?')
    med2_repetir_posologia = forms.ChoiceField(required=True,
                                               initial=True,
                                               choices=REPETIR_ESCOLHAS,
                                               label='Repetir posologia?')
    med3_repetir_posologia = forms.ChoiceField(required=True,
                                               initial=True,
                                               choices=REPETIR_ESCOLHAS,
                                               label='Repetir posologia?')
    med4_repetir_posologia = forms.ChoiceField(required=True,
                                               initial=True,
                                               choices=REPETIR_ESCOLHAS,
                                               label='Repetir posologia?')
    med5_repetir_posologia = forms.ChoiceField(required=True,
                                               initial=True,
                                               choices=REPETIR_ESCOLHAS,
                                               label='Repetir posologia?')

    cid = forms.CharField(required=True, label='CID')
    diagnostico = forms.CharField(required=True, label='Diagnóstico')
    anamnese = forms.CharField(required=True, label='Anamnese')
    preenchido_por = forms.ChoiceField(initial={'paciente'},
                                       choices=[('paciente', 'Paciente'),
                                                ('mae', 'Mãe'),
                                                ('responsavel', 'Responsável'),
                                                ('medico', 'Médico')])
    etnia = forms.ChoiceField(label='Etnia', required=False,
                              choices=[('etnia_branca', 'Branca'),
                                       ('etnia_parda', 'Parda'),
                                       ('etnia_amarela', 'Amarela'),
                                       ('etnia_indigena', 'Indígena'),
                                       ('etnia_si', 'Sem informação')])
    email_paciente = forms.EmailField(required=False, label='E-Mail')
    telefone1_paciente = forms.CharField(
        required=False, label='Tel. residencial')
    telefone2_paciente = forms.CharField(required=False, label='Celular')
    tratou = forms.ChoiceField(
        choices=((True, 'Sim'), (False, 'Não')),
        label='Fez tratamento prévio?',
        initial=False
    )
    tratamentos_previos = forms.CharField(
        label='Descrição dos tratamentos prévios',
        required=False
    )
    data_1 = forms.DateField(
        required=True, label='Data',
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=['%d/%m/%Y', ]
    )

    @transaction.atomic
    def save(self, usuario, medico, meds_ids):
        dados = self.cleaned_data
        clinica_id = dados['clinicas']
        doenca = Doenca.objects.get(cid=dados['cid'])
        cpf_paciente = dados['cpf_paciente']

        # adiciona dados da clínica
        emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

        paciente_existe = checar_paciente_existe(cpf_paciente)

        registrar_db(dados,meds_ids,doenca,emissor,usuario,paciente_existe=paciente_existe)


class RenovarProcesso(NovoProcesso):
    edicao_completa = forms.ChoiceField(required=True, initial={False},
                                        choices=[
        (False, 'Não'),
        (True, 'Sim') 
    ])

    @transaction.atomic
    def save(self, usuario, medico, processo_id, meds_ids):
        dados = self.cleaned_data
        edicao_completa = dados['edicao_completa']

        if edicao_completa == 'True':
            cpf_paciente = dados['cpf_paciente']
            paciente_existe = checar_paciente_existe(cpf_paciente)
            clinica_id = dados['clinicas']
            doenca = Doenca.objects.get(cid=dados['cid'])
            emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

            registrar_db(dados,meds_ids,doenca,emissor,usuario,paciente_existe=paciente_existe,cid=dados['cid'])
        else:
            dados_modificados, campos_modificados = gerar_dados_edicao_parcial(
                dados, processo_id)
            processo = preparar_modelo(Processo, **dados_modificados)
            processo.save(update_fields=campos_modificados)
            associar_med(Processo.objects.get(id=processo_id),meds_ids)