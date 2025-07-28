from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doenca, Protocolo

# search_diseases
def busca_doencas(request):
    """
    AJAX endpoint for disease search functionality.
    
    Searches diseases by CID code or name using case-insensitive partial matching.
    Used for autocomplete functionality in the prescription forms.
    
    Security: No authorization check needed as this only returns public disease information.
    However, it could be enhanced with rate limiting to prevent abuse.
    """
    # disease (search keyword from request)
    doenca = request.GET.get("palavraChave", None)
    
    # Return empty list if no search term provided
    if not doenca:
        return JsonResponse([], safe=False)
        
    # search_results (filtered disease queryset)
    b = Doenca.objects.filter(Q(cid__icontains=doenca) | Q(nome__icontains=doenca))
    # diseases (list of disease dictionaries for JSON response)
    doencas = []
    for r in b:
        # new_disease (disease dictionary with CID and name)
        nova_doenca = {"cid": r.cid, "nome": r.nome}
        doencas.append(nova_doenca)

    return JsonResponse(doencas, safe=False)


# verify_first_time
@login_required
def verificar_1_vez(request):
    """
    AJAX endpoint to check if a patient needs first-time protocol requirements.
    
    Returns protocol-specific conditional data for first-time patients.
    This determines which additional forms or information are required
    based on the disease protocol.
    
    Security: Requires login but lacks input validation for CID parameter.
    Should add try/catch for DoesNotExist exceptions and validate CID format.
    """
    # received_cid (CID code from AJAX request)
    cid_recebido = request.GET.get("cid", None)
    
    if not cid_recebido:
        return JsonResponse({"error": "CID parameter required"}, status=400)
    
    try:
        # protocol (protocol object associated with the disease)
        protocolo = Protocolo.objects.get(doenca__cid=cid_recebido)
        
        # Check if "1_vez" key exists in conditional data
        if "1_vez" in protocolo.dados_condicionais:
            return JsonResponse(protocolo.dados_condicionais["1_vez"])
        else:
            # Return empty object if no first-time conditions configured
            return JsonResponse({})
            
    except Protocolo.DoesNotExist:
        return JsonResponse({"error": "Protocol not found for CID"}, status=404)
