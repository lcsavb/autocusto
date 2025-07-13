from django.db import transaction
from django.conf import settings
import json
from processos.models import Protocolo, Doenca
import os

base_dir = os.path.join(settings.BASE_DIR, "processos/db")


@transaction.atomic
def salvar_protocolos():
    os.chdir(base_dir)
    with open("protocolos.json", "r") as protocolos:
        dados = json.load(protocolos)
        for chave in dados.keys():
            nome_protocolo = chave
            cids_protocolo = dados[chave]["cids"]
            arquivo = dados[chave]["arquivo"]
            protocolo = Protocolo(nome=nome_protocolo, arquivo=arquivo)
            print(protocolo)
            protocolo.save()
            print("salvou")
            for cid in cids_protocolo:
                doencas = Doenca.objects.filter(cid=cid)
                if doencas:
                    for doenca in doencas:
                        doenca.protocolo = protocolo
                        doenca.save()


salvar_protocolos()
