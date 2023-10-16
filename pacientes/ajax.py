
from django.http import JsonResponse
from django.db.models import Q
from .models import Paciente

def busca_pacientes(request):
    patient = request.GET.get('palavraChave', None)
    b = Paciente.objects.filter((Q(cpf_paciente__icontains=patient) | Q(nome_paciente__icontains=patient)))
    patients = []
    for r in b:
        new_patient = {'nome_paciente': r.nome_paciente, 'cpf_paciente': r.cpf_paciente}
        patients.append(new_patient)
    return JsonResponse(patients, safe=False)
