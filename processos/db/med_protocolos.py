import json
import os
from django.conf import settings
from processos.models import Protocolo, Doenca, Medicamento

dir_base = os.path.join(settings.BASE_DIR, 'processos/db' )

os.chdir(dir_base)

orfaos = {}
n = 0
with open('med_links_cids.json', 'r') as a:
    lista = json.load(a)
    for med in lista:
        cids = lista[med][1]
        try:
            busca_medicamentos = Medicamento.objects.filter(nome__icontains=med.lower())
            for medicamento in busca_medicamentos:
                for cid in cids:
                    protocolo = Protocolo.objects.filter(doenca__cid=cid)
                    if protocolo.exists():
                        p = protocolo[0]
                        p.medicamentos.add(medicamento)
        except:
            print(med)



