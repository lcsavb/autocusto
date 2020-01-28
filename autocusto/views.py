from django.shortcuts import render, redirect
from django.contrib import messages
from processos.forms import PreProcesso
from pacientes.models import Paciente
from processos.models import Processo


def home(request):
    user = request.user
    if request.method == 'GET':
        formulario = PreProcesso()
        contexto = {'formulario': formulario}
        return render(request, 'home.html', contexto)
    else:
        if user.is_authenticated:
            formulario = PreProcesso(request.POST)
            if formulario.is_valid():
                cpf_paciente = formulario.cleaned_data['cpf_paciente']
                cid = formulario.cleaned_data['cid']

                try:
                    print('paciente existe')
                    paciente = Paciente.objects.get(cpf_paciente=cpf_paciente)
                    request.session['paciente_existe'] = True
                    request.session['paciente_id'] = paciente.id
                    request.session['cid'] = cid
                    request.session['cpf_paciente'] = cpf_paciente
                except:
                    print('paciente ñ existe')
                    request.session['paciente_existe'] = False
                    request.session['cid'] = cid
                    request.session['cpf_paciente'] = cpf_paciente
                    return redirect('processos-cadastro')

                for processo in paciente.processos.all():
                    if processo.cid == cid:
                        print('cid existe')
                        #continuar aqui, o loop sai na primeira rodada por isso que não está funcionando!
                        for usuario_existente in paciente.usuarios.all():
                            if user == usuario_existente:
                                print('cid cadastrado por esse usuário')
                                request.session['processo_id'] = processo.id
                                return redirect('processos-edicao')
                            else:
                                print('cid cadastrado por outro usuário')
                                request.session['vincula_usuario'] = True
                                return redirect('processos-cadastro')
                    else:
                        return redirect('processos-cadastro')
        else:
            convite = request.POST.get('convite')
            print(convite)
            if convite.lower() == 'cgrlmeplus':
                request.session['convite_aceito'] = True
                return redirect('medicos-cadastro')
            else:
                messages.success(request, f'Código inválido')
                return redirect('home')

            return render(request, 'home.html', contexto)
