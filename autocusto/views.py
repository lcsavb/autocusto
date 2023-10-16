
from django.shortcuts import render, redirect
from django.contrib import messages
from processos.forms import PreProcesso
from pacientes.models import Paciente
from processos.models import Processo

def home(request):
    usuario = request.user
    if (request.method == 'GET'):
        form = PreProcesso()
        contexto = {'formulario': form}
        return render(request, 'home.html', contexto)
    elif usuario.is_authenticated:
        form = PreProcesso(request.POST)
        if form.is_valid():
            patient_cpf = form.cleaned_data['cpf_paciente']
            icd = form.cleaned_data['cid']
            try:
                patient = Paciente.objects.get(cpf_paciente=patient_cpf)
                request.session['paciente_existe'] = True
                request.session['paciente_id'] = patient.id
                request.session['cid'] = icd
                request.session['cpf_paciente'] = patient_cpf
            except:
                request.session['paciente_existe'] = False
                request.session['cid'] = icd
                request.session['cpf_paciente'] = patient_cpf
                return redirect('processos-cadastro')
            search_processes = patient.processos.filter(doenca__cid=icd)
            if search_processes.exists():
                process_registered_by_user = search_processes.filter(usuario__id=usuario.id).exists()
                if process_registered_by_user:
                    request.session['processo_id'] = search_processes.get(usuario__id=usuario.id).id
                    return redirect('processos-edicao')
                else:
                    return redirect('processos-cadastro')
            else:
                return redirect('processos-cadastro')
        else:
            form = PreProcesso(request.POST)
            contexto = {'formulario': form}
            return render(request, 'home.html', contexto)
    else:
        invitation = request.POST.get('convite')
        print(invitation)
        if (invitation.lower() == 'cgrlmeplus'):
            request.session['convite_aceito'] = True
            return redirect('medicos-cadastro')
        else:
            messages.success(request, f'Código inválido')
            return redirect('home')
        return render(request, 'home.html', contexto)
