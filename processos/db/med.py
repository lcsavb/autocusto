
import csv
import json
import os
from django.conf import settings
from processos.models import Medicamento
medicines_csv = os.path.join(settings.BASE_DIR, 'processos/db/medicamentos.csv')

def salvar_med():
    with open(medicines_csv, 'r') as arquivo_csv:
        reader = csv.reader(arquivo_csv, delimiter=',')
        n = 1
        for linha in reader:
            name = linha[0]
            dosage = linha[1]
            drug_formulation = linha[2]
            m = Medicamento(nome=name, apres=drug_formulation, dosagem=dosage)
            try:
                m.save()
            except:
                print(name)
salvar_med()
