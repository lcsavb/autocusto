from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Paciente


@login_required
def busca_pacientes(request):
    search_term = request.GET.get("palavraChave", None)
    user = request.user
    
    # Use versioned patient search - handles both search_term and None cases
    patient_version_pairs = Paciente.get_patients_for_user_search(user, search_term)
    
    pacientes = []
    for patient, version in patient_version_pairs:
        # Use versioned name if available, fallback to master record
        patient_name = version.nome_paciente if version else patient.nome_paciente
        
        novo_paciente = {
            "nome_paciente": patient_name,  # Versioned name
            "cpf_paciente": patient.cpf_paciente,  # CPF always from master record
        }
        pacientes.append(novo_paciente)

    return JsonResponse(pacientes, safe=False)
