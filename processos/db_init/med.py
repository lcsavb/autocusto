import csv
import json
from processos.models import Medicamento




def salvar_med():
    medicamentos = {}
    with open('/usr/src/autocusto/processos/db_init/medicamentos.csv', 'r') as arquivo_csv:
        leitor = csv.reader(arquivo_csv, delimiter=',')

        n = 0
        for linha in leitor:

            nome = linha[0]
            apresentacao = [f'{linha[1]} ' + f'({linha[2]})']


            if n == 0:
                novo_medicamento = {nome: apresentacao}
                medicamentos.update(novo_medicamento)
                n = n + 1
            else:
                if nome == list(medicamentos.keys())[-1]:         
                    medicamentos[nome] += apresentacao
                else:        
                    novo_medicamento = {nome: apresentacao}
                    medicamentos.update(novo_medicamento)

    for item in medicamentos.items():
        m = Medicamento(nome=item[0], apresentacoes=item[1])
        m.save()
