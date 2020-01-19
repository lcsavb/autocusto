from django.shortcuts import render, redirect
from processos.forms import PreProcesso
from pacientes.models import Paciente
from processos.models import Processo


def home(request):
    if request.method == 'GET':
        formulario = PreProcesso()
        contexto = {'formulario': formulario}
        return render(request, 'home.html', contexto)
    else:
        formulario = PreProcesso(request.POST)
        if formulario.is_valid():
            cpf_paciente = formulario.cleaned_data['cpf_paciente']
            cid = formulario.cleaned_data['cid']

            try:
                paciente = Paciente.objects.get(cpf_paciente=cpf_paciente)            
                for processo in paciente.processos.all():
                    if processo.cid == cid:
                        request.session['processo_id'] = processo.id
                        return redirect('processos-edicao')
                    else:
                        request.session['paciente_id'] = paciente.id
                        request.session['paciente_existe'] = True
                        request.session['cid'] = cid
                        return redirect('processos-cadastro')
            except:
                request.session['paciente_existe'] = False
                request.session['cid'] = cid
                request.session['cpf_paciente'] = cpf_paciente
                return redirect('processos-cadastro')
            finally:
                pass
                #adicionar mensagem de redirecionamento



            
            
