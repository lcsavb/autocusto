from django.shortcuts import render, redirect
from processos.forms import PreProcesso
from pacientes.models import Paciente
from processos.models import Processo


def redirecionar_com_get(url, nome_parametro, parametro, *args, **kwargs):
    response = redirect(url)                                                 
    cid = args[0]
    if kwargs.get('existe') == 'sim':
        response['Location'] += ('?' + nome_parametro + '=' + 
                                str(parametro) + '&existe=sim' + '&cid=' + str(cid))
    elif kwargs.get('existe') == 'nao':
        response['Location'] += ('?' + nome_parametro + '=' + 
                                str(parametro) + '&existe=nao' + '&cid=' + str(cid))

    else:
        response['Location'] += ('?' + nome_parametro + '=' + str(parametro))
    return response


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
                        return redirecionar_com_get('processos-edicao', 'id', processo.id)
                    else:
                        print('else')
                        return redirecionar_com_get('processos-cadastro', 
                                                    'cpf_paciente',
                                                    str(cpf_paciente), 
                                                    cid, 
                                                    existe='sim')
            except:
                return redirecionar_com_get('processos-cadastro',
                                            'cpf_paciente',
                                            str(cpf_paciente),
                                            cid,
                                            existe='nao'
                                            )



            
            
