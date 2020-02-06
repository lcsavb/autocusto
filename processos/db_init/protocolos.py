from django.db import transaction
import json
import glob
from processos.models import Protocolo, Doenca
import os


@transaction.atomic
def salvar_protocolos():
    os.chdir('/usr/src/autocusto/processos/db_init/')
    with open('protocolos.json', 'r') as protocolos:
        dados = json.load(protocolos)
        for chave in dados.keys():
            nome_protocolo = chave
            cids_protocolo = dados[chave]['cids']
            arquivo = dados[chave]['arquivo']
            protocolo = Protocolo(nome=nome_protocolo,arquivo=arquivo)
            print(protocolo)
            protocolo.save()
            print('salvou')
            for cid in cids_protocolo:
                doencas = Doenca.objects.filter(cid=cid)
                if doencas:
                    for doenca in doencas:
                        doenca.protocolo = protocolo
                        doenca.save()

salvar_protocolos()