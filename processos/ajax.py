
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doenca, Protocolo

@login_required
def busca_doencas(request):
    disease = request.GET.get('palavraChave', None)
    b = Doenca.objects.filter((Q(cid__icontains=disease) | Q(nome__icontains=disease)))
    diseases = []
    for r in b:
        new_disease = {'cid': r.cid, 'nome': r.nome}
        diseases.append(new_disease)
    return JsonResponse(diseases, safe=False)

@login_required
def verificar_1_vez(request):
    cid_recebido = request.GET.get('cid', None)
    protocol = Protocolo.objects.get(doenca__cid=cid_recebido)
    return JsonResponse(protocol.dados_condicionais['1_vez'])
