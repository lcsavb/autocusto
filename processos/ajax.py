from django.db.models import Q
from django.http import JsonResponse
from .models import Doenca

def busca_doencas(request):
    doenca = request.GET.get('palavraChave', None)
    b = Doenca.objects.filter(Q(cid__icontains=doenca) | Q(nome__icontains=doenca))
    doencas = []
    for r in b:
        nova_doenca = {'cid': r.cid, 'nome': r.nome}
        doencas.append(nova_doenca)
    print(doencas)


    return JsonResponse(doencas, safe=False)