##################
# 
# Lucas, esses são os dados que você precisa extrair do banco de dados:

dados_medico = {
    'nome_medico': 'Lucas Amorim Vieira de Barros',
    'crm': '150494',
    'cns_medico': '980016293604585'
    } 

dados_paciente ={
    'nome_paciente': 'Clarice Lispector',
    'idade': '26',
    'sexo': 'feminino',
    'nome_mae': 'Páscoa Lispector',
    'incapaz': 'sim',
    'nome_responsavel': 'Pintassilgo Dumont Lispector', #implementar condicional
    'rg': '98383838309',
    'peso': '80kg',
    'altura': '160',
    'escolha_etnia': 'etnia_amarela',
    'cpf_paciente': '324234234234',
    'cns_paciente': '980013241324324',
    'email_paciente': 'claricelispector@estreladamanha.art.br',
    'cidade_paciente': 'Rio de Janeiro',
    'end_paciente': 'Rua Gávea Estrelada 1001',
    'cep_paciente': '06040-330',
    'telefone1_paciente': '021 5555-5555',
    'telefone2_paciente': '021 5666-6654'
    }

dados_clinica = {
    'nome_clinica': 'Clínica Primeira Instância',
    'cns_clinica': '8734585',
    'end_clinica': 'Rua dos Aloprados Estuprados, 343',
    'cidade_clinica': 'Caranguatatuba',
    'bairro_clinica': 'Afundalância',
    'cep_clinica': '09873-030',
    'telefone_clinica': '011 98393-93839'
    }   

dados_processo = {
    'cpf_paciente': '20384092309',
    'anamnese': 'Dor crônica intratável', #adicionar anamneses padrão vinculadas aos cids
    ### MEDICAMENTO 1
    'med1': 'abatacepte 240mg', ## Às vezes na renovação o med precisa ser alterado, alterada a posologia ou adicionado um novo
    'med1_posologia_mes1': 'Tomar 1cp 4/4 horas com leite.', #opção de clonar a posologia para os meses subsequentes
    'med1_posologia_mes2': 'x',
    'med1_posologia_mes3': 'y',
    'qtd_med1_mes1': '91', ### aqui deixar a opção de clonar as quantidades do primeiro mês, na maior parte das vezes é a mesma!
    'qtd_med1_mes2': '92',
    'qtd_med1_mes3': '93', 
    ### REPETIR CAMPOS ACIMA PARA MED2, MED3, MED4 E MED5 (ESTES OPCIONAIS!)
    'trat_previo': 'sim', ## Campo booleano
    'cid': 'M05.0',
    'tratamentos_previos': 'Ajoelhou no milho', # campo condicional, dependente do trat_previo
    'diagnostico': 'Esquizofrenia indiferenciada paranóide',
    'renovacao': False,
    'exames': True,
    'data_1': '13/05/19', ### A data geralmente é o único campo que precisa ser alterado na renovação
    'data_2': '13/06/19', ### adicionar cálculo automático + 30 e +60 dias para datas 2 e 3 respectivamente
    'data_3': '13/07/10',
    'preenchido_por': 'mae', #aqui é o campo 18 da lme, se selecionado qualquer coisa além de médico, todos os abaixo deverão estar em branco
    'adicionar_med_extra': True, # muitas vezes o paciente precisa de receitas extras, fora do processo do alto custo
    # Abaixo os campos são condicionais... Adicionar opção para múltiplos medicamentos extras
    # Esses deverão ter sua receita individual, pois nem sempre uma mesma farmácia possui
    # todos os medicamentos controlados necessários
    'med_extra': 'Med-Extra',
    'qtd_med_extra': 'qtd_med_extra',
    'posologia_med_extra': 'Posologia',
    } 

############################### Path pdf_final

PATH_PDF_FINAL = 'pdf_final_{}_{}.pdf'.format(dados_paciente['cpf_paciente'],dados_processo['cid'])


############################### DADOS CONDICIONAIS - deverá haver opção do médico defini-los
#### ou selecionar os padrões como descritos abaixo.

dados_condicionais = {}

### DOENÇA DE ALZHEIMER

exames1vez = '''
Hemograma,sódio, potássio, cálcio total, creatinina, uréia, Glicemia de jejum, 
TSH (Hormônio Tireoestimulante), ácido fólico, vitamina B12, VDRL, TGO, TGP
'''


dados_alzheimer = {
    # Mini-exame do estado mental
    'ot1': '1',
    'ot2': '1',
    'ot3': '1',
    'ot4': '1',
    'ot5': '1',
    'oe1': '1',
    'oe2': '1',
    'oe3': '1',
    'oe4': '1',
    'mi': '3', # de 0 a 3
    'ac': '4', # de 0 a 5
    'me': '3', # 0 a 3
    'n': '2', # de 0 a 2
    'r': '1', 
    'ce': '1', # 0 ou 1
    'cv': '2', # 0 a 3
    'f': '0',
    'd': '0',
    'total': 'somátoria dos anteriores',
    ### CDR
    'cdr': '51',
    ### Exames
    'exames_da_1vez': exames1vez # acrescentar sorologia para hiv se menos de 60 anos
}

#### ARTRITE REUMATÓIDE




med_ar_grupo_1 = [ 'azatioprina', 'ciclosporina', 'cloroquina', 'hidroxicloroquina', 'leflunomida',
                    'metotrexato', 'naproxeno', 'sulfassalazina' ] 

exames_ar_grupo_1 = ['VHS', 'Fator reumatóide']

exames_ar_grupo_2 = ['Hemograma', 'TGO', 'TGP', 'VHS', 'HbsAg', 'Anti-HCV', 'Fator reumatóide',
                    'Prova de Mantoux - PPD']

meds_relatorio_ar = ['abatacepte', 'etanercepte', 'golimumabe', 'rituximabe', 'tocilizumabe']


aviso_ar = '''
        Acrescentar laudo ou relatório médico da radiografia de tórax. Descrever critérios
        diagnósticos na LME
        '''
        

dados_ar = {
    'exames_ar_grupo_1': exames_ar_grupo_1,
    'exames_ar_grupo_2': exames_ar_grupo_2,
    'aviso_ar': aviso_ar
}


#### ESCLEROSE MÚLTIPLA

relatorio_nata = ''' 
Relatório médico contendo:
1. Falha terapêutica ou contraindicação ao fingolimode; 2. Se o paciente está sem receber imunomodulador 
por pelo menos 45 dias ou azatioprina por 3 meses; 3. Se paciente não foi diagnosticado com micose sistêmica 
nos últimos 6 meses, herpes grave nos últimos 3 meses, infecção por HIV, qualquer outra infecção oportunista nos últimos 
3 meses ou infecção atual ativa. 
'''

relatorio_fingo = '''
Relatório médico, contendo: A. Justificativa para interrupção do uso ou motivo da não utilização de primeira linha: 
1. Falha terapêutica à betainterferona ou ao glatirâmer ou à teriflunomida 
2. Ausência de contraindicação ao uso do fingolimode'
'''

relatorio_fumarato = '''
1. Em casos de intolerância, reações adversas ou falta de adesão à Betainterferon ou ao Glatiramer ou à
Teriflunomida;
2. Em casos de falha terapêutica ou resposta sub-ótima à Betainterferon ou ao Glatiramer ou à
Teriflunomida.
'''

dados_esclerose_multipla = {
    'edss': '3',
    'exames_em_1vez': 'Hemograma, TGO, TGP, FA, GGT, Vitamina B12, Sorologia HIV, VDRL, Bilirrubinas total e frações, TSH',
    'exames_em_renova': 'Hemograma, TGO, TGP, FA, GGT, Bilirrubinas total e frações, TSH',
    'relatorio_fingolimode_1vez': relatorio_fingo,
    'relatorio_natalizumabe_1vez': relatorio_nata,
    'relatorio_fumarato_1vez': relatorio_fumarato,
    'exames_nata_renova': 'Hemograma'}


##### Epilepsia

relatorio_epilepsia_1vez = '''
    Relatar características das crises, se há risco de recorrência superior a 60%, se apresentaram duas
    crises com intervalo superior a 24 horas e se tem diagnóstico de síndrome epiléptica específica '''

dados_epilepsia = {
    'relatorio_epilepsia_1vez': relatorio_epilepsia_1vez,
    'exames_solicitados': 'Não são obrigatórios exames, a critério do médico prescritor'
}


############# Dislipidemia


dislipidemia_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Colesterol total e frações (HDL e LDL)', 'Triglicerídeos']


fibratos_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Triglicérides']

dados_dislipidemia = {
    'ac_nicotinico_trat_previo': 'Contraindicação ao uso de estatinas',
    'dislipidemia_1vez_exames': dislipidemia_1vez_exames,
    'fibratos_1vez_exames': fibratos_1vez_exames
}

############# Dor crônica

dados_dor = {
    'eva': '5', ## de 4 a 10
    'lanns_escore': '24' ## depois completar com as categorias individuais
}