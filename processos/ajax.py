from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doenca, Protocolo

# English: search_diseases
def busca_doencas(request):
    # English: disease
    doenca = request.GET.get("palavraChave", None)
    # English: search_results
    b = Doenca.objects.filter(Q(cid__icontains=doenca) | Q(nome__icontains=doenca))
    # English: diseases
    doencas = []
    for r in b:
        # English: new_disease
        nova_doenca = {"cid": r.cid, "nome": r.nome}
        doencas.append(nova_doenca)

    return JsonResponse(doencas, safe=False)


# English: verify_first_time
@login_required
def verificar_1_vez(request):
    # English: received_cid
    cid_recebido = request.GET.get("cid", None)
    # English: protocol
    protocolo = Protocolo.objects.get(doenca__cid=cid_recebido)

    return JsonResponse(protocolo.dados_condicionais["1_vez"])
