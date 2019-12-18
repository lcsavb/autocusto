from django import forms
from django.db import transaction
from datetime import datetime
from pacientes.models import Paciente
from medicos.models import Medico
from processos.models import Processo
from clinicas.models import Clinica


class NovoProcesso(forms.Form):
    
    def __init__(self, *args, **kwargs):
         self.request = kwargs.pop('request', None) 
         super(NovoProcesso, self).__init__(*args, **kwargs)

    # Dados do paciente
    cpf_paciente = forms.CharField(required=True, label='CPF do paciente')
    nome_paciente = forms.CharField(required=True, label='Nome do paciente')
    nome_mae = forms.CharField(required=True, label='Nome da mãe')
    peso = forms.IntegerField(required=True, label='Peso')
    altura = forms.IntegerField(required=True, label='Altura')
    incapaz = forms.ChoiceField(choices=((True, 'Sim'),
         (False, 'Não')), label='Paciente é incapaz?')
    nome_responsavel= forms.CharField(label='Nome do responsável')

    # Dados do processo
    med1 = forms.CharField(required=True, label='Medicamento')
    med1_posologia_mes1 = forms.CharField(required=True, label='Posologia')
    qtd_med1_mes1 = forms.CharField(required=True, label="Qtde. 1 mês")
    qtd_med1_mes2 = forms.CharField(required=True, label="Qtde. 2 mês")
    qtd_med1_mes3 = forms.CharField(required=True, label="Qtde. 3 mês")
    cid = forms.CharField(required=True, label='CID')
    diagnostico = forms.CharField(required=True, label='Diagnóstico')
    anamnese = forms.CharField(required=True, label='Anamnese')
    tratou = forms.ChoiceField(choices=((True, 'Sim'),
         (False, 'Não')), label='Fez tratamento prévio?')
    tratamentos_previos = forms.CharField(label='Descrição dos tratamentos prévios')
    data_1 = forms.DateField(required=True, label='Data', widget=forms.DateInput(format='%d/%m/%Y'),
         input_formats=['%d/%m/%Y',])

    @transaction.atomic
    def save(self, usuario):
        dados = self.cleaned_data
        medico = usuario.medico.pk
        cpf_paciente = dados['cpf_paciente']

        paciente_existe = Paciente.objects.filter(cpf_paciente=cpf_paciente,usuario=usuario)

        # precisa melhorar esse código - funciona, mas está nojento
        paciente = Paciente(nome_paciente=dados['nome_paciente'], 
                    cpf_paciente=dados['cpf_paciente'], peso =dados['peso'], 
                    altura=dados['altura'], nome_mae=dados['nome_mae'], 
                    incapaz=dados['incapaz'],
                    usuario_id=usuario.pk, medico_id=medico,
                    nome_responsavel=dados['nome_responsavel'])

        if paciente_existe:
             pk = paciente_existe[0].pk
             
             # repetitivo
             paciente = Paciente(id=pk, nome_paciente=dados['nome_paciente'], 
                    cpf_paciente=dados['cpf_paciente'], peso =dados['peso'], 
                    altura=dados['altura'], nome_mae=dados['nome_mae'], 
                    incapaz=dados['incapaz'],
                    usuario_id=usuario.pk, medico_id=medico,
                    nome_responsavel=dados['nome_responsavel'])  

             paciente.save(force_update=True)  
        else:
             paciente.save()
        
        paciente = Paciente.objects.get(cpf_paciente=dados['cpf_paciente'], usuario=usuario)

        processo = Processo(med1=dados['med1'], 
        med1_posologia_mes1=dados['med1_posologia_mes1'], 
        qtd_med1_mes1=dados['qtd_med1_mes1'],
        qtd_med1_mes2=dados['qtd_med1_mes2'],
        qtd_med1_mes3=dados['qtd_med1_mes3'], cid=dados['cid'],
        diagnostico=dados['diagnostico'], anamnese=dados['anamnese'],
        tratou=dados['tratou'], tratamento_previo=dados['tratamentos_previos'],
        data1=dados['data_1'], medico_id=medico, usuario_id=usuario.pk,
        paciente_id=paciente.pk)
        processo.save()

    def clean(self):
        usuario = self.request.user 
        dados = self.cleaned_data 
        cpf_paciente = dados['cpf_paciente']
        cid = dados['cid']

        paciente = Paciente.objects.filter(cpf_paciente=cpf_paciente,usuario=usuario)

        if paciente.exists():
             if Processo.objects.filter(paciente=paciente[0], cid=cid).exists():
                  raise forms.ValidationError('Processo com esse CID já existe para paciente.')

        return dados