from django import forms
from pacientes.models import Paciente
from medicos.models import Medico
from processos.models import Processo
from clinicas.models import Clinica

class NovoProcesso(forms.Form):
     # Dados da clínica
    cns_clinica = forms.CharField(label="CNS da clínica")
    nome_clinica = forms.CharField(label='Nome da clínica')

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
    medicamento1 = forms.CharField(required=True, label='Medicamento')
    posologia_med1 = forms.CharField(required=True, label='Posologia')
    qtd_med1_mes1 = forms.CharField(required=True, label="Qtde. 1 mês")
    qtd_med1_mes2 = forms.CharField(required=True, label="Qtde. 2 mês")
    qtd_med1_mes3 = forms.CharField(required=True, label="Qtde. 3 mês")
    cid = forms.CharField(required=True, label='CID')
    diagnostico = forms.CharField(required=True, label='Diagnóstico')
    anamnese = forms.CharField(required=True, label='Anamnese')
    trat_previo = forms.ChoiceField(choices=((True, 'Sim'),
         (False, 'Não')), label='Fez tratamento prévio?')
    tratamento_previo = forms.CharField(label='Descrição dos tratamentos prévios')
    data1 = forms.DateField(required=True, label='Data')






    def save(self, usuario_ativo):
        dados = self.cleaned_data

        paciente = Paciente(nome=dados['nome_paciente'], 
        cpf_paciente=dados['cpf_paciente'], peso = ['peso'],
        altura=dados['altura'], nome_mae=dados['nome_mae'], 
        incapaz=dados['incapaz'], medico_id=usuario_ativo,
        nome_responsavel=dados['nome_responsavel'])
        paciente.save()

        # Algo me diz que essa não é a melhor maneira........
        paciente_salvo = Paciente.objects.get(cpf_paciente=dados['cpf_paciente'])

        
        processo = Processo(med1=dados['medicamento1'], 
        posologia_med1=dados['posologia_med1'], qtd_med1_mes1=dados['qtd_med1_mes1'],
        qtd_med1_mes2=dados['qtd_med1_mes2'],
        qtd_med1_mes3=dados['qtd_med1_mes3'], cid=dados['cid'],
        diagnostico=dados['diagnostico'], anamnese=dados['anamnese'],
        tratou=dados['trat_previo'], tratamento_previo=dados['tratamento_previo'],
        data1=dados['data1'], medico_id=usuario_ativo, paciente_id=paciente_salvo.pk)
        processo.save()
