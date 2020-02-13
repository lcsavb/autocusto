import csv
import json
from processos.models import Medicamento




def salvar_med():
    with open('/usr/src/autocusto/processos/db_init/medicamentos.csv', 'r') as arquivo_csv:
        leitor = csv.reader(arquivo_csv, delimiter=',')

        n = 0
        for linha in leitor:
            nome = linha[0]
            dosagem = linha[1]
            apres = linha[2]
            m = Medicamento(nome=nome, apres=apres, dosagem=dosagem)
            m.save()

salvar_med()

