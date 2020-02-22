from django.http import JsonResponse
from django.db.models import Q
from .models import Paciente

def busca_pacientes(request):
    paciente = request.GET.get('palavraChave', None)
    b = Paciente.objects.filter(Q(cpf_paciente__icontains=paciente)
                                |
                                Q(nome_paciente__icontains=paciente))
    pacientes = []
    for r in b:
        novo_paciente = {'nome_paciente': r.nome_paciente, 'cpf_paciente': r.cpf_paciente}
        pacientes.append(novo_paciente)


    return JsonResponse(pacientes, safe=False)