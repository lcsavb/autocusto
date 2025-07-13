from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doenca, Protocolo


@login_required
def busca_doencas(request):
    doenca = request.GET.get("palavraChave", None)
    b = Doenca.objects.filter(Q(cid__icontains=doenca) | Q(nome__icontains=doenca))
    doencas = []
    for r in b:
        nova_doenca = {"cid": r.cid, "nome": r.nome}
        doencas.append(nova_doenca)

    return JsonResponse(doencas, safe=False)


@login_required
def verificar_1_vez(request):
    cid_recebido = request.GET.get("cid", None)
    protocolo = Protocolo.objects.get(doenca__cid=cid_recebido)

    return JsonResponse(protocolo.dados_condicionais["1_vez"])
