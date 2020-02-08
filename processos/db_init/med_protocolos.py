import json
import os
from processos.models import Protocolo, Doenca, Medicamento

os.chdir('/usr/src/autocusto/processos/db_init')

orfaos = {}
n = 0
with open('med_links_cids.json', 'r') as a:
    lista = json.load(a)
    for med in lista:
        cids = lista[med][1]
        try:
            medicamento = Medicamento.objects.get(nome__icontains=med.lower())
        except:
            print(med)
        finally:
            for cid in cids:
                protocolo = Protocolo.objects.filter(doenca__cid=cid)
                if protocolo.exists():
                    p = protocolo[0]
                    p.medicamentos.add(medicamento)



