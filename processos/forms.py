from django import forms
from django.db import transaction
from datetime import datetime
from pacientes.models import Paciente
#from medicos.models import Medico
from processos.models import Processo
from clinicas.models import Clinica, Emissor


class NovoProcesso(forms.Form):
     def __init__(self, escolhas, *args, **kwargs):
         super(NovoProcesso, self).__init__(*args, **kwargs)
         self.fields['clinicas'].choices = escolhas
         self.request = kwargs.pop('request', None)        
     
     # Dados do paciente
     cpf_paciente = forms.CharField(required=True, label='CPF do paciente',max_length=14)
     clinicas = forms.ChoiceField(widget=forms.Select, choices=[],
     label='Selecione a clínica')
     nome_paciente = forms.CharField(required=True, label='Nome do paciente')
     nome_mae = forms.CharField(required=True, label='Nome da mãe')
     peso = forms.IntegerField(required=True, label='Peso')
     altura = forms.IntegerField(required=True, label='Altura')
     incapaz = forms.ChoiceField(
          choices=((True, 'Sim'),
          (False, 'Não')), 
          label='Paciente é incapaz?',
          initial=False)
     nome_responsavel= forms.CharField(
          label='Nome do responsável',
          required=False) 

     # Dados do processo
     med1 = forms.CharField(required=True, label='Medicamento')
     med1_posologia_mes1 = forms.CharField(required=True, label='Posologia')
     qtd_med1_mes1 = forms.CharField(required=True, label="Qtde. 1 mês")
     qtd_med1_mes2 = forms.CharField(required=True, label="Qtde. 2 mês")
     qtd_med1_mes3 = forms.CharField(required=True, label="Qtde. 3 mês")
     cid = forms.CharField(required=True, label='CID')
     diagnostico = forms.CharField(required=True, label='Diagnóstico')
     anamnese = forms.CharField(required=True, label='Anamnese')
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
          input_formats=['%d/%m/%Y',]
          ) 

     @transaction.atomic
     def save(self, usuario):
         dados = self.cleaned_data
         medico = usuario.medico
         clinica_id = dados['clinicas']
         
         #adicionar dados da clínica
         cpf_paciente = dados['cpf_paciente']
         emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)
         print(dados) 

         try:
              paciente_existe = Paciente.objects.get(cpf_paciente=cpf_paciente) 
         except:
              paciente_existe = False

         # precisa melhorar esse código - funciona, mas está nojento
         paciente = Paciente(nome_paciente=dados['nome_paciente'], 
                     cpf_paciente=dados['cpf_paciente'], peso =dados['peso'], 
                     altura=dados['altura'], nome_mae=dados['nome_mae'], 
                     incapaz=dados['incapaz'], nome_responsavel=dados['nome_responsavel']) 

         if paciente_existe:
              paciente = Paciente(id=paciente_existe.pk, nome_paciente=dados['nome_paciente'], 
                     cpf_paciente=dados['cpf_paciente'], peso =dados['peso'], 
                     altura=dados['altura'], nome_mae=dados['nome_mae'], 
                     incapaz=dados['incapaz'], nome_responsavel=dados['nome_responsavel'])   
              paciente.save(force_update=True)
              #adicionar aqui salvamento de processo - fazer função
              processo = Processo(med1=dados['med1'], 
                              med1_posologia_mes1=dados['med1_posologia_mes1'], 
                              qtd_med1_mes1=dados['qtd_med1_mes1'],
                              qtd_med1_mes2=dados['qtd_med1_mes2'],
                              qtd_med1_mes3=dados['qtd_med1_mes3'], cid=dados['cid'],
                              diagnostico=dados['diagnostico'], anamnese=dados['anamnese'],
                              tratou=dados['tratou'], tratamento_previo=dados['tratamentos_previos'],
                              data1=dados['data_1'], medico=emissor.medico, paciente=paciente,
                              clinica = emissor.clinica, emissor=emissor
                              )
              emissor.pacientes.add(paciente_existe) 
         else:
              paciente.save()
              
              paciente = Paciente.objects.get(cpf_paciente=cpf_paciente)


              processo = Processo(med1=dados['med1'], 
                              med1_posologia_mes1=dados['med1_posologia_mes1'], 
                              qtd_med1_mes1=dados['qtd_med1_mes1'],
                              qtd_med1_mes2=dados['qtd_med1_mes2'],
                              qtd_med1_mes3=dados['qtd_med1_mes3'], cid=dados['cid'],
                              diagnostico=dados['diagnostico'], anamnese=dados['anamnese'],
                              tratou=dados['tratou'], tratamento_previo=dados['tratamentos_previos'],
                              data1=dados['data_1'], medico=emissor.medico, paciente=paciente,
                              clinica = emissor.clinica, emissor=emissor
                              )
              processo.save()
              emissor.pacientes.add(paciente)
                    
          
     # def clean(self):
     #     usuario = self.request.user 
     #     dados = self.cleaned_data 
     #     cpf_paciente = dados['cpf_paciente']
     #     cid = dados['cid'] 

     #     paciente = Paciente.objects.filter(cpf_paciente=cpf_paciente,usuario=usuario) 

     #     if paciente.exists():
     #          if Processo.objects.filter(paciente=paciente[0], cid=cid).exists():
     #               raise forms.ValidationError('Processo com esse CID já existe para paciente.') 

     #     return dados