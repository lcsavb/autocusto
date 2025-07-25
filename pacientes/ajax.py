import logging
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Paciente

logger = logging.getLogger(__name__)

@login_required
def busca_pacientes(request):
    search_term = request.GET.get("palavraChave", None)
    user = request.user
    
    # Use versioned patient search - handles both search_term and None cases
    patient_version_pairs = Paciente.get_patients_for_user_search(user, search_term)
    
    pacientes = []
    skipped_count = 0
    
    for patient, version in patient_version_pairs:
        # Security fix: Only return patients with valid versions - no fallback to master record
        if version:
            novo_paciente = {
                "nome_paciente": version.nome_paciente,  # Always use versioned name
                "cpf_paciente": patient.cpf_paciente,   # CPF always from master record
            }
            pacientes.append(novo_paciente)
        else:
            # Log security event: patient skipped due to missing version
            skipped_count += 1
            logger.warning(
                f"Security: Patient CPF {patient.cpf_paciente} skipped for user {user.email} "
                f"- no version access (potential data leak prevented)"
            )
    
    if skipped_count > 0:
        logger.info(f"AJAX patient search: {len(pacientes)} returned, {skipped_count} skipped for user {user.email}")
    
    return JsonResponse(pacientes, safe=False)
