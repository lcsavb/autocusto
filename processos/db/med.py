import csv
import json
import os
from django.conf import settings
from processos.models import Medicamento



medicamentos_csv = os.path.join(settings.BASE_DIR, 'processos/db/medicamentos.csv')
def salvar_med():
    with open(medicamentos_csv, 'r') as arquivo_csv:
        leitor = csv.reader(arquivo_csv, delimiter=',')

        n = 1
        for linha in leitor:
            nome = linha[0]
            dosagem = linha[1]
            apres = linha[2]
            m = Medicamento(nome=nome, apres=apres, dosagem=dosagem)
            try:
                m.save()
            except:
                print(nome)

salvar_med()

