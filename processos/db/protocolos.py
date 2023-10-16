
from django.db import transaction
from django.conf import settings
import json
import glob
from processos.models import Protocolo, Doenca
import os
base_dir = os.path.join(settings.BASE_DIR, 'processos/db')

@transaction.atomic
def salvar_protocolos():
    os.chdir(base_dir)
    with open('protocolos.json', 'r') as protocols:
        data = json.load(protocols)
        for chave in data.keys():
            protocol_name = chave
            icds_protocol = data[chave]['cids']
            file = data[chave]['arquivo']
            protocol = Protocolo(nome=protocol_name, arquivo=file)
            print(protocol)
            protocol.save()
            print('salvou')
            for icd in icds_protocol:
                diseases = Doenca.objects.filter(cid=icd)
                if diseases:
                    for disease in diseases:
                        disease.protocolo = protocol
                        disease.save()
salvar_protocolos()
