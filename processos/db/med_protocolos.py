
import json
import os
from django.conf import settings
from processos.models import Protocolo, Doenca, Medicamento
base_directory = os.path.join(settings.BASE_DIR, 'processos/db')
os.chdir(base_directory)
orphans = {}
n = 0
with open('med_links_cids.json', 'r') as a:
    list = json.load(a)
    for med in list:
        icds = list[med][1]
        try:
            search_medicines = Medicamento.objects.filter(nome__icontains=med.lower())
            for medication in search_medicines:
                for icd in icds:
                    protocol = Protocolo.objects.filter(doenca__cid=icd)
                    if protocol.exists():
                        p = protocol[0]
                        p.medicamentos.add(medication)
        except:
            print(med)
